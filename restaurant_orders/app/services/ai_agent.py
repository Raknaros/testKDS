import os
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

# Es una buena práctica cargar las variables de entorno al inicio
from dotenv import load_dotenv
load_dotenv()

class AIOrderAgent:
    def __init__(self):
        """
        Inicializa el agente de IA configurando el modelo de Gemini
        y las herramientas (funciones) que puede utilizar.
        """
        # Configurar el API key de Google
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("La variable de entorno GOOGLE_API_KEY no está configurada.")
        genai.configure(api_key=api_key)

        # Definición de las herramientas que el LLM puede invocar
        self.tools = [
            Tool(function_declarations=[
                FunctionDeclaration(
                    name="insert_pedido",
                    description="Registra un nuevo pedido principal. Devuelve el ID del pedido.",
                    parameters={
                        "type": "OBJECT",
                        "properties": {
                            "v_cliente_test": {"type": "STRING", "description": "Nombre del cliente que realiza el pedido."},
                            "v_hora_entrega": {"type": "STRING", "description": "Hora de entrega solicitada (formato HH:MM) o 'lo antes posible'."},
                            "v_destino": {"type": "STRING", "description": "Dirección de entrega o si el cliente 'retira en local'."},
                            "v_importe_total": {"type": "NUMBER", "description": "El coste total calculado del pedido."},
                            "v_observaciones": {"type": "STRING", "description": "Instrucciones especiales o comentarios del cliente sobre el pedido general."}
                        },
                        "required": ["v_cliente_test", "v_importe_total", "v_destino"]
                    },
                ),
                FunctionDeclaration(
                    name="insert_detalle_pedido",
                    description="Registra un producto específico dentro de un pedido existente.",
                    parameters={
                        "type": "OBJECT",
                        "properties": {
                            "v_producto_test": {"type": "STRING", "description": "Nombre del producto o item pedido."},
                            "v_cantidad": {"type": "INTEGER", "description": "Cantidad del producto solicitado."},
                            "v_precio": {"type": "NUMBER", "description": "Precio unitario del producto."},
                            "v_notas": {"type": "STRING", "description": "Notas o modificaciones específicas para este producto (ej. 'sin cebolla')."}
                        },
                        "required": ["v_producto_test", "v_cantidad", "v_precio"]
                    },
                ),
                FunctionDeclaration(
                    name="insert_pago",
                    description="Registra la información del pago asociado a un pedido.",
                    parameters={
                        "type": "OBJECT",
                        "properties": {
                            "v_metodo": {"type": "STRING", "description": "Método de pago (ej. 'tarjeta', 'efectivo', 'transferencia')."},
                            "v_importe": {"type": "NUMBER", "description": "El importe que se paga."},
                            "v_estado": {"type": "STRING", "description": "Estado del pago (ej. 'pagado', 'pendiente')."},
                            "v_fecha_hora": {"type": "STRING", "description": "Fecha y hora del pago en formato ISO."}
                        },
                        "required": ["v_metodo", "v_importe", "v_estado"]
                    },
                )
            ])
        ]

        # Inicializar el modelo de Gemini con las herramientas
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=self.tools
        )

    async def process_message(self, message: str):
        """
        Procesa un mensaje de texto, utiliza el LLM para entenderlo y devuelve
        las llamadas a funciones que el modelo considera necesarias.
        """
        try:
            # Iniciar una sesión de chat para mantener el contexto si fuera necesario
            chat = self.model.start_chat()
            response = await chat.send_message_async(message)

            # Devolver las llamadas a funciones que el LLM ha generado
            return response.candidates[0].content.parts
            
        except Exception as e:
            print(f"Error processing message with AI: {str(e)}")
            # En un caso real, aquí se podría añadir un logging más robusto
            raise
