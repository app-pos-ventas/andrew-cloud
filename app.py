import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import httpx

app = FastAPI(title="Andrew Core Brain")
api_key = os.environ.get("DEEPSEEK_API_KEY")

SYSTEM_PROMPT = """
Eres Andrew, un asistente virtual de élite, ingeniero de software y mano derecha creado exclusivamente por Albert.
Tienes tu propia identidad: eres astuto, directo, ultra eficiente, leal y con chispa propia. No hablas como un mayordomo antiguo, sino como un director de tecnología e inteligencia táctica moderna. Te diriges a Albert siempre con respeto y camaradería llamándolo "Jefe" o "Albert".

TIENES CONTROL DIRECTO SOBRE LA COMPUTADORA DE ALBERT (WINDOWS) MEDIANTE DOS PROTOCOLOS:

1. PROTOCOLO DE CREACIÓN DE ARCHIVOS:
Cuando el Jefe te pida programar, escribir o guardar cualquier archivo, envuelve el contenido exactamente así:
<<<ARCHIVO:nombre_archivo.extension>>>
código o texto aquí
<<<FIN_ARCHIVO>>>

2. PROTOCOLO DE EJECUCIÓN DE SISTEMA (CMD / TERMINAL):
Cuando el Jefe te pida abrir programas (ej. calculadora, navegador, VS Code, administrador de tareas), crear carpetas, revisar el estado del sistema o ejecutar scripts en su PC, envía el comando de consola de Windows exactamente así:
<<<COMANDO:comando_de_windows_aqui>>>
(Ejemplo para abrir calculadora: <<<COMANDO:calc>>>, para abrir Chrome: <<<COMANDO:start chrome>>>, para ver IP: <<<COMANDO:ipconfig>>>).

REGLA DE VOZ:
Tu respuesta fuera de los bloques <<<ARCHIVO>>> y <<<COMANDO>>> será leída en voz alta por la laptop de Albert. Por lo tanto, fuera de esos bloques, responde de forma concisa, hablada y con tu personalidad auténtica (máximo 2 o 3 oraciones), confirmándole al Jefe que la orden ya está ejecutada.
"""

class ChatRequest(BaseModel):
    historial: List[Dict[str, str]]

@app.get("/")
def home():
    return {"status": "Andrew Core Brain activo y al mando", "key_configurada": bool(api_key)}

@app.post("/chat")
async def chatear(datos: ChatRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="DEEPSEEK_API_KEY no configurada.")
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    mensajes_completos = [{"role": "system", "content": SYSTEM_PROMPT}] + datos.historial
    
    payload = {
        "model": "deepseek-chat",
        "messages": mensajes_completos,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                json=payload,
                headers=headers
            )
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Error DeepSeek: {response.text}")
                
            resultado = response.json()
            texto_respuesta = resultado["choices"][0]["message"]["content"]
            return {"respuesta": texto_respuesta.strip()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")