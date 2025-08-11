from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI

class AIOrderAgent:
    def __init__(self):
        # Inicializar el modelo de lenguaje
        self.llm = ChatOpenAI(temperature=0)
        
        # Definir el prompt para procesar pedidos
        self.prompt = PromptTemplate(
            input_variables=["message"],
            template="""
            Analiza el siguiente mensaje de pedido de comida y extrae la información estructurada:
            Mensaje: {message}
            
            Extrae:
            1. Nombre del cliente
            2. Items pedidos (con cantidades)
            3. Instrucciones especiales
            4. Hora de entrega (si se especifica)
            """
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    async def process_message(self, message: str):
        try:
            # Procesar el mensaje con el modelo
            result = await self.chain.arun(message=message)
            
            # Aquí deberías parsear la respuesta del modelo
            # y convertirla en una estructura de datos útil
            # Este es un ejemplo simplificado
            parsed_result = self._parse_llm_response(result)
            
            return parsed_result
        except Exception as e:
            print(f"Error processing message with AI: {str(e)}")
            raise

    def _parse_llm_response(self, response: str):
        # Este método debe implementarse para parsear la respuesta del LLM
        # y convertirla en un formato estructurado
        # Este es un ejemplo simplificado
        return {
            "customer_name": "Nombre extraído",
            "items": [],
            "special_instructions": "",
            "scheduled_time": None
        }
