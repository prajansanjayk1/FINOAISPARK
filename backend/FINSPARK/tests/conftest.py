import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.main import app
from app.core.config import settings
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import Base, RoleORM, DepartmentORM, PermissionORM

# Use an in-memory SQLite URL for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Creates an instance of the event loop for the test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a fresh, in-memory database and provides a session for a single test.
    """
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.exec_driver_sql("PRAGMA foreign_keys = ON;")
        await conn.run_sync(Base.metadata.create_all)

    # Seed roles, permissions, and departments for test compliance
    async with session_factory() as session:
        async with session.begin():
            # Seed permissions
            permissions = [
                PermissionORM(name="USER_READ", resource="USER", action="READ", description="List users"),
                PermissionORM(name="ASSET_CREATE", resource="ASSET", action="CREATE", description="Register assets"),
                PermissionORM(name="REQUEST_APPROVE", resource="REQUEST", action="APPROVE", description="Approve requests"),
                PermissionORM(name="AUDIT_READ", resource="AUDIT", action="READ", description="Query audit trails"),
                PermissionORM(name="DASHBOARD_READ", resource="DASHBOARD", action="READ", description="View stats"),
                PermissionORM(name="RISK_READ", resource="RISK", action="READ", description="View risk"),
            ]
            session.add_all(permissions)
            
            perm_map = {p.name: p for p in permissions}
            
            # Seed roles
            ciso_role = RoleORM(name="Chief Information Security Officer (CISO)", description="CISO role")
            ciso_role.permissions.extend(permissions)

            manager_role = RoleORM(name="Manager", description="Manager role")
            manager_role.permissions.extend([perm_map["REQUEST_APPROVE"]])

            soc_role = RoleORM(name="SOC Analyst", description="SOC Analyst role")
            soc_role.permissions.extend([
                perm_map["USER_READ"],
                perm_map["AUDIT_READ"],
                perm_map["DASHBOARD_READ"],
                perm_map["RISK_READ"]
            ])

            dba_role = RoleORM(name="Database Administrator", description="DBA role")
            dba_role.permissions.extend([perm_map["DASHBOARD_READ"]])

            session.add_all([ciso_role, manager_role, soc_role, dba_role])
            
            # Seed default departments
            depts = [
                DepartmentORM(name="Security Operations Center", code="SOC"),
                DepartmentORM(name="Database Administration", code="DBA"),
            ]
            session.add_all(depts)
            
    # Yield session for test execution
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Overrides the FastAPI database dependency and returns an HTTPX AsyncClient.
    """
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    
    # In HTTPX >=0.28.0, app must be passed via transport=ASGITransport(app)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()
