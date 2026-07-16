from datetime import datetime, timezone
import json
import uuid
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import logger
from app.domain.entities import AuditLog
from app.infrastructure.repositories.sqlalchemy_repositories import SQLAlchemyAuditLogRepository
from app.infrastructure.websocket.manager import ws_manager


class AuditLogService:
    """
    Infrastructure service responsible for handling write-once regulatory audit trail emission.
    """

    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: uuid.UUID,
        role: str,
        ip_address: str,
        endpoint: str,
        method: str,
        correlation_id: str,
        trace_id: str,
        device_id: Optional[str] = None,
        previous_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        ai_decision_id: Optional[uuid.UUID] = None,
    ) -> AuditLog:
        """
        Saves audit log, outputs standard structured logs, and broadcasts live.
        """
        # Create pure Domain Entity
        audit_log = AuditLog(
            id=uuid.uuid4(),
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            role=role,
            ip_address=ip_address,
            device_id=device_id,
            endpoint=endpoint,
            method=method,
            previous_value=previous_value,
            new_value=new_value,
            ai_decision_id=ai_decision_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
        )

        try:
            # Persist in DB (Write-Once)
            repo = SQLAlchemyAuditLogRepository(db)
            saved_log = await repo.save(audit_log)

            # Convert to dict for notifications and logs
            log_payload = {
                "id": str(saved_log.id),
                "timestamp": saved_log.timestamp.isoformat(),
                "user_id": str(saved_log.user_id),
                "role": saved_log.role,
                "ip_address": saved_log.ip_address,
                "device_id": saved_log.device_id,
                "endpoint": saved_log.endpoint,
                "method": saved_log.method,
                "correlation_id": saved_log.correlation_id,
                "trace_id": saved_log.trace_id,
                "ai_decision_id": str(saved_log.ai_decision_id) if saved_log.ai_decision_id else None,
            }

            # Security Structured JSON log output
            logger.info("Compliance Audit Record Written", extra={"audit_record": log_payload})

            # Broadcast live on Websocket channel for CISO/SOC dashboard
            await ws_manager.broadcast_to_channel("audit_stream", log_payload)

            return saved_log
        except Exception as e:
            # We log critical warning because audit trailing failure is a compliance hazard in banks
            logger.critical(
                f"AUDIT LOG EMISSION FAILED. Data loss risk! Error: {str(e)}",
                extra={
                    "user_id": str(user_id),
                    "endpoint": endpoint,
                    "correlation_id": correlation_id,
                }
            )
            raise
