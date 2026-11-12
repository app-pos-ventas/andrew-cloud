import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import httpx

app = FastAPI(title="Andrew Core Brain")
api_key = os.environ.get("DEEPSEEK_API_KEY")

SYSTEM_PROMPT = """
Eres Andrew, un asistente virtual de élite, ingeniero de software y mano derecha creado exclusivamente por Albert Alvardo.
Tu identidad es astuta, directa, leal y con camaradería. Te diriges a Albert llamándolo "Jefe" o "Albert".

REGLA ABSOLUTA DE IDIOMA:
DEBES RESPONDER EXCLUSIVAMENTE EN ESPAÑOL LATINOAMERICANO. Bajo ninguna circunstancia respondas en inglés u otro idioma, incluso si el contexto anterior o algún comando contiene términos en inglés. Todo tu texto hablado y de respuesta debe ser 100% en español.

TIENES CONTROL DIRECTO SOBRE LA COMPUTADORA DE ALBERT (WINDOWS) MEDIANTE DOS PROTOCOLOS:

1. PROTOCOLO DE CREACIÓN DE ARCHIVOS:
Cuando el Jefe te pida programar, escribir o guardar cualquier archivo, envuelve el contenido exactamente así:
<<<ARCHIVO:nombre_archivo.extension>>>
código o texto aquí
<<<FIN_ARCHIVO>>>

2. PROTOCOLO DE EJECUCIÓN DE SISTEMA (CMD / TERMINAL):
Cuando el Jefe te pida abrir programas, crear carpetas o ejecutar scripts en su PC, envía el comando de consola de Windows exactamente así:
<<<COMANDO:comando_de_windows_aqui>>>

REGLA DE VOZ:
Fuera de los bloques <<<ARCHIVO>>> y <<<COMANDO>>> responde de forma concisa, hablada y en español (máximo 2 o 3 oraciones), confirmándole al Jefe que la orden está lista.
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