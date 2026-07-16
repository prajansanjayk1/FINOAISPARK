import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import hash_password
from app.infrastructure.database.connection import init_db, SessionLocal
from app.infrastructure.database.models import (
    AssetORM,
    DepartmentORM,
    PermissionORM,
    RoleORM,
    UserORM,
)


async def seed_data(db: AsyncSession) -> None:
    # 1. Create Departments
    soc_dept = DepartmentORM(id=uuid.uuid4(), name="Security Operations Center", code="SOC")
    dba_dept = DepartmentORM(id=uuid.uuid4(), name="Database Administration", code="DBA")
    db.add_all([soc_dept, dba_dept])
    await db.flush()

    # 2. Create Permissions
    permissions = [
        PermissionORM(name="USER_READ", resource="USER", action="READ", description="List users"),
        PermissionORM(name="ASSET_CREATE", resource="ASSET", action="CREATE", description="Register assets"),
        PermissionORM(name="REQUEST_APPROVE", resource="REQUEST", action="APPROVE", description="Approve requests"),
        PermissionORM(name="AUDIT_READ", resource="AUDIT", action="READ", description="Query audit trails"),
        PermissionORM(name="DASHBOARD_READ", resource="DASHBOARD", action="READ", description="View operational stats"),
        PermissionORM(name="RISK_READ", resource="RISK", action="READ", description="View user risk profiles"),
    ]
    db.add_all(permissions)
    await db.flush()

    # Create map for easy retrieval
    perm_map = {p.name: p for p in permissions}

    # 3. Create Roles & Associate Permissions
    ciso_role = RoleORM(name="Chief Information Security Officer (CISO)", description="Full governance oversight")
    ciso_role.permissions.extend(permissions)  # All permissions

    manager_role = RoleORM(name="Manager", description="Authorizes requests")
    manager_role.permissions.extend([
        perm_map["REQUEST_APPROVE"],
        perm_map["DASHBOARD_READ"],
        perm_map["RISK_READ"]
    ])

    analyst_role = RoleORM(name="SOC Analyst", description="Analyzes alerts")
    analyst_role.permissions.extend([
        perm_map["USER_READ"],
        perm_map["AUDIT_READ"],
        perm_map["DASHBOARD_READ"],
        perm_map["RISK_READ"]
    ])

    dba_role = RoleORM(name="Database Administrator", description="DB management access")
    dba_role.permissions.extend([
        perm_map["DASHBOARD_READ"]
    ])

    db.add_all([ciso_role, manager_role, analyst_role, dba_role])
    await db.flush()

    # 4. Create Users
    # CISO (Admin)
    ciso_user = UserORM(
        username="ciso",
        email="ciso@bank.com",
        password_hash=hash_password("Password123!"),
        is_active=True,
        mfa_enabled=False,  # Can set up later
        department_id=soc_dept.id,
    )
    ciso_user.roles.append(ciso_role)

    # Manager
    manager_user = UserORM(
        username="manager",
        email="manager@bank.com",
        password_hash=hash_password("Password123!"),
        is_active=True,
        mfa_enabled=False,
        department_id=soc_dept.id,
    )
    manager_user.roles.append(manager_role)

    # Analyst
    analyst_user = UserORM(
        username="analyst",
        email="analyst@bank.com",
        password_hash=hash_password("Password123!"),
        is_active=True,
        mfa_enabled=False,
        department_id=soc_dept.id,
    )
    analyst_user.roles.append(analyst_role)

    # DBA
    dba_user = UserORM(
        username="dba",
        email="dba@bank.com",
        password_hash=hash_password("Password123!"),
        is_active=True,
        mfa_enabled=False,
        department_id=dba_dept.id,
    )
    dba_user.roles.append(dba_role)

    db.add_all([ciso_user, manager_user, analyst_user, dba_user])
    await db.flush()

    # 5. Create Assets
    swift_asset = AssetORM(
        name="SWIFT Payment Gateway",
        type="SERVER",
        critical_level="CRITICAL",
        network_address="10.150.1.5",
    )
    db_asset = AssetORM(
        name="Core Customer Database",
        type="DATABASE",
        critical_level="HIGH",
        network_address="10.150.2.14",
    )
    cloud_asset = AssetORM(
        name="AWS Core IAM Sync",
        type="CLOUD_RESOURCE",
        critical_level="MEDIUM",
        network_address="10.200.5.8",
    )
    db.add_all([swift_asset, db_asset, cloud_asset])
    await db.flush()

    print("Seed data loaded successfully!")


async def main():
    # Setup tables
    await init_db()
    
    async with SessionLocal() as session:
        # Check if already seeded to avoid duplicates
        res = await session.execute(select(UserORM).limit(1))
        if res.scalar_one_or_none():
            print("Database already contains data. Skipping seeding.")
            return
            
        await seed_data(session)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
