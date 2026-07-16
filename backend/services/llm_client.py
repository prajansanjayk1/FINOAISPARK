import os
import json
import logging
from config import settings

logger = logging.getLogger("nexus.services.llm_client")

# Initialize clients if keys are present
_gemini_client_initialized = False
try:
    if settings.GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_client_initialized = True
        logger.info("Gemini API Client initialized successfully.")
except Exception as e:
    logger.warning(f"Failed to initialize Gemini client: {e}")

_openai_client_initialized = False
try:
    if settings.OPENAI_API_KEY:
        from openai import OpenAI
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        _openai_client_initialized = True
        logger.info("OpenAI API Client initialized successfully.")
except Exception as e:
    logger.warning(f"Failed to initialize OpenAI client: {e}")

async def call_llm(system_prompt: str, user_prompt: str, response_format: type = None) -> dict:
    """
    Calls the configured LLM (Gemini preferred, then OpenAI) if USE_LLM is enabled.
    Otherwise, or if the call fails, returns None to trigger local rule fallback.
    """
    if not settings.USE_LLM:
        return None

    # Try Gemini First
    if _gemini_client_initialized:
        try:
            logger.info("Routing request to Google Gemini API...")
            import google.generativeai as genai
            
            # Using modern gemini-2.5-flash for rapid reasoning
            model_name = "gemini-1.5-flash"
            
            generation_config = {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
            
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=system_prompt
            )
            
            response = await model.generate_content_async(user_prompt)
            text = response.text.strip()
            
            # Parse response JSON
            data = json.loads(text)
            logger.info("Successfully received and parsed Gemini response.")
            return data
        except Exception as e:
            logger.error(f"Gemini API execution failed: {e}. Falling back...")
            
    # Try OpenAI Fallback
    if _openai_client_initialized:
        try:
            logger.info("Routing request to OpenAI API...")
            from openai import OpenAI
            import asyncio
            
            # Use gpt-4o-mini for cost-efficient fast audits
            loop = asyncio.get_event_loop()
            
            def sync_call():
                return openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                
            response = await loop.run_in_executor(None, sync_call)
            text = response.choices[0].message.content.strip()
            
            data = json.loads(text)
            logger.info("Successfully received and parsed OpenAI response.")
            return data
        except Exception as e:
            logger.error(f"OpenAI API execution failed: {e}. Falling back...")

    logger.warning("No LLM key configured or all LLM API calls failed. Falling back to local cognitive rules.")
    return None
