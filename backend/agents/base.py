from abc import ABC, abstractmethod
from models import PrivilegedRequest, AgentResponse
import logging
from services.llm_client import call_llm

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"nexus.agent.{name.lower().replace(' ', '_')}")
        
    @abstractmethod
    async def evaluate(self, request: PrivilegedRequest, policy_violations: list) -> AgentResponse:
        """
        Evaluate a privileged request.
        """
        pass

    async def get_llm_evaluation(self, system_prompt: str, request: PrivilegedRequest, policy_violations: list) -> dict:
        """
        Invokes Gemini or OpenAI to perform cognitive security analysis of the active request.
        """
        from prompts import AGENT_USER_PROMPT_TEMPLATE
        
        user_prompt = AGENT_USER_PROMPT_TEMPLATE.format(
            request_id=request.request_id,
            timestamp=request.timestamp,
            username=request.user.username,
            role=request.user.role,
            department=request.user.department,
            auth_strength=request.user.auth_strength,
            trusted_device=str(request.user.trusted_device),
            ip_address=request.user.ip_address,
            action_type=request.action.type,
            command=request.action.command,
            target_system=request.action.target_system,
            criticality=request.action.criticality,
            is_maintenance_window=str(request.context.is_maintenance_window),
            change_ticket_id=request.context.change_ticket_id or "None",
            active_incident_id=request.context.active_incident_id or "None",
            system_health=request.context.system_health,
            policy_violations=str(policy_violations)
        )
        
        try:
            result = await call_llm(system_prompt, user_prompt)
            return result
        except Exception as e:
            self.logger.warning(f"Error invoking LLM for {self.name}: {e}")
            return None
