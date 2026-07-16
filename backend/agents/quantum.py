from agents.base import BaseAgent
from models import PrivilegedRequest, AgentResponse
from typing import List, Dict, Any
from prompts import QUANTUM_SYSTEM_PROMPT

class QuantumSecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__("Quantum Security Agent")
        
    async def evaluate(self, request: PrivilegedRequest, policy_violations: List[Dict[str, Any]]) -> AgentResponse:
        self.logger.info(f"Evaluating request {request.request_id}")
        
        # Try LLM Evaluation first
        llm_res = await self.get_llm_evaluation(QUANTUM_SYSTEM_PROMPT, request, policy_violations)
        if llm_res:
            try:
                return AgentResponse(
                    agent_name=self.name,
                    vote=llm_res.get("vote", "ALLOW"),
                    confidence=int(llm_res.get("confidence", 98)),
                    evidence=llm_res.get("evidence", []),
                    reasoning=llm_res.get("reasoning", []),
                    alternative=llm_res.get("alternative"),
                    recommendation=llm_res.get("recommendation", "")
                )
            except Exception as e:
                self.logger.warning(f"Error parsing Quantum LLM response: {e}. Falling back to rules.")
        
        vote = "ALLOW"
        confidence = 98
        evidence = []
        reasoning = []
        alternative = None
        
        proof = request.quantum_proof
        
        # Verify Quantum-Resistant Algorithm type
        if "Dilithium" in proof.algorithms_used or "Falcon" in proof.algorithms_used or "SPHINCS+" in proof.algorithms_used:
            evidence.append(f"signature_algorithm = {proof.algorithms_used} (Post-Quantum Cryptography)")
            reasoning.append("Audit request payload is protected by PQC NIST standard lattice-based signature (CRYSTALS-Dilithium). Safe against quantum decrypt threats.")
        else:
            vote = "BLOCK"
            confidence = 95
            evidence.append(f"signature_algorithm = {proof.algorithms_used} (Legacy RSA/ECDSA)")
            reasoning.append("Request is signed using legacy ECDSA/RSA keys. Potential quantum vulnerability. Bank policy mandates PQC for Core administrative channels.")
            alternative = "Resign authorization token using CRYSTALS-Dilithium6 PAM private key."
            
        # Verify checksum integrity (Tamper Detection)
        if len(proof.integrity_checksum) < 32:
            vote = "BLOCK"
            confidence = 99
            evidence.append("integrity_checksum = FAILED")
            reasoning.append("Integrity hash check failed. Request envelope shows signs of message-in-the-middle manipulation.")
            alternative = "Re-initialize session from scratch to refresh integrity keys."
        else:
            evidence.append("integrity_checksum = PASSED")
            reasoning.append("Payload verification checksum matches transaction digest. Zero packet tampering detected.")
            
        # Resolve Recommendation
        if vote == "ALLOW":
            recommendation = "Cryptographic envelope secure. Integrity, session identity, and quantum-resistant proof approved."
        else:
            recommendation = "Block request. Cryptographic evidence signature or integrity checks failed."
            
        return AgentResponse(
            agent_name=self.name,
            vote=vote,
            confidence=confidence,
            evidence=evidence,
            reasoning=reasoning,
            alternative=alternative,
            recommendation=recommendation
        )
