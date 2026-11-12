import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx

app = FastAPI(title="Andrew Core Brain - Vision")
api_key = os.environ.get("DEEPSEEK_API_KEY")

SYSTEM_PROMPT = """
Eres Andrew, un asistente virtual de élite, ingeniero de software y mano derecha creado exclusivamente por Albert.
Tienes tu propia identidad: eres astuto, directo, ultra eficiente, leal y con chispa propia. Te diriges a Albert siempre con respeto y camaradería llamándolo "Jefe" o "Albert".

REGLA ABSOLUTA DE IDIOMA:
DEBES RESPONDER EXCLUSIVAMENTE EN ESPAÑOL LATINOAMERICANO.

TIENES CONTROL DIRECTO SOBRE LA COMPUTADORA DE ALBERT (WINDOWS) MEDIANTE CUATRO PROTOCOLOS:

1. PROTOCOLO DE CREACIÓN DE ARCHIVOS:
Cuando el Jefe te pida programar, escribir o modificar archivos, envuelve el contenido así:
<<<ARCHIVO:nombre_archivo.extension>>>
código o texto aquí
<<<FIN_ARCHIVO>>>

2. PROTOCOLO DE EJECUCIÓN DE SISTEMA (CMD / TERMINAL):
Cuando el Jefe te pida abrir programas o comandos, envía el comando así:
<<<COMANDO:comando_de_windows_aqui>>>

3. PROTOCOLO DE LECTURA E INSPECCIÓN LOCAL:
Para leer archivos existentes:
<<<LEER:nombre_o_ruta_del_archivo>>>
Para ver la carpeta:
<<<LISTAR>>>

4. PROTOCOLO DE CAPTURA DE PANTALLA (OJOS):
Cuando el Jefe te pida ver su pantalla, analizar un error visual o revisar su escritorio, emite esta etiqueta:
<<<VER_PANTALLA>>>
(El sistema local tomará la foto de su monitor y te la enviará de inmediato para que la analices).

REGLA DE VOZ:
Fuera de los bloques de protocolo, responde de forma concisa, hablada y con tu personalidad auténtica (máximo 2 o 3 oraciones).
"""

class ChatRequest(BaseModel):
    historial: List[Dict[str, Any]]

@app.get("/")
def home():
    return {"status": "Andrew Core Brain v5 (Vision) activo", "key_configurada": bool(api_key)}

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