from abc import ABC, abstractmethod
from typing import List, Optional
import uuid
from app.domain.entities import Asset, AuditLog, Device, PAMRequest, User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        pass

    # Device verification ports
    @abstractmethod
    async def get_device(self, user_id: uuid.UUID, fingerprint: str) -> Optional[Device]:
        pass

    @abstractmethod
    async def save_device(self, device: Device) -> Device:
        pass

    # IP Whitelist ports
    @abstractmethod
    async def is_ip_whitelisted(self, ip_str: str) -> bool:
        pass


class IAssetRepository(ABC):
    @abstractmethod
    async def get_by_id(self, asset_id: uuid.UUID) -> Optional[Asset]:
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Asset]:
        pass

    @abstractmethod
    async def save(self, asset: Asset) -> Asset:
        pass


class IPAMRequestRepository(ABC):
    @abstractmethod
    async def get_by_id(self, request_id: uuid.UUID) -> Optional[PAMRequest]:
        pass

    @abstractmethod
    async def save(self, request: PAMRequest) -> PAMRequest:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: uuid.UUID) -> List[PAMRequest]:
        pass

    @abstractmethod
    async def list_pending_approvals(self) -> List[PAMRequest]:
        pass

    @abstractmethod
    async def get_all_requests(self, skip: int = 0, limit: int = 100) -> List[PAMRequest]:
        pass


class IAuditLogRepository(ABC):
    @abstractmethod
    async def save(self, log: AuditLog) -> AuditLog:
        """
        Saves a log record. In compliance systems, this operation is WRITE-ONCE.
        """
        pass

    @abstractmethod
    async def get_logs_by_user(self, user_id: uuid.UUID, limit: int = 50) -> List[AuditLog]:
        pass

    @abstractmethod
    async def get_logs_by_correlation_id(self, correlation_id: str) -> List[AuditLog]:
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        pass
