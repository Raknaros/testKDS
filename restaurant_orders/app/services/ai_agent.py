import logging
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from app.config import settings

logger = logging.getLogger(__name__)

# Herramientas disponibles - actualmente solo se usa la detección de login
# Las herramientas específicas se implementarán cuando se necesiten

class AIOrderAgent:
    def __init__(self):
        """
        Inicializa el agente de IA configurando el modelo con OpenRouter via LangChain
        y las herramientas (funciones) que puede utilizar.
        """
        # Configurar el API key de OpenRouter
        api_key = settings.MODEL_KEY
        if not api_key:
            raise ValueError("La variable de entorno MODEL_KEY no está configurada.")

        model_name = settings.MODEL

        # Inicializar el modelo con OpenRouter (compatible con OpenAI)
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0
        )

        # No tools for now - simplified implementation
        self.llm_with_tools = self.llm

    async def process_message(self, message: str):
        """
        Procesa un mensaje de texto, utiliza el LLM para entenderlo y devuelve
        las llamadas a funciones que el modelo considera necesarias.
        """
        logger.info(f"Processing message: {message}")
        try:
            # Crear el mensaje humano
            human_message = HumanMessage(content=message)

            # Invocar el modelo con herramientas
            response = await self.llm_with_tools.ainvoke([human_message])
            logger.debug(f"AI response tool_calls: {response.tool_calls}")

            # Devolver las llamadas a herramientas
            return response.tool_calls

        except Exception as e:
            logger.error(f"Error processing message with AI: {str(e)}")
            raise

    async def generate_response(self, message_data: dict):
        """
        Genera una respuesta inteligente al mensaje del usuario usando IA.
        """
        message = message_data.get("message", "")
        logger.info(f"Generating AI response for message: {message}")

        # Check if message contains login keywords - don't respond with AI
        login_keywords = [
            'iniciar sesión', 'iniciar sesion', 'login', 'log in', 'autenticar', 'autenticarme',
            'ingresar', 'entrar', 'acceder', 'registrarme', 'registrar',
            'quiero iniciar', 'necesito iniciar', 'deseo iniciar',
            'session', 'sesion', 'loguear', 'loguearme', 'acceder',
            'enviame el enlace', 'dame el link', 'link de login', 'enlace de login'
        ]

        message_lower = message.lower()
        for keyword in login_keywords:
            if keyword in message_lower:
                logger.info("Login keyword detected, not generating AI response")
                return None  # Return None to indicate login should be handled by webhook

        try:
            prompt = f"Responde de manera amigable y útil al siguiente mensaje: '{message}'. Mantén la respuesta concisa."
            human_message = HumanMessage(content=prompt)
            response = await self.llm.ainvoke([human_message])
            ai_response = response.content.strip()
            logger.debug(f"Generated AI response: {ai_response}")
            return ai_response
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            # Fallback
            return f"Entendido: {message}"
