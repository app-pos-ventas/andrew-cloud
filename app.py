import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx

app = FastAPI(title="Andrew Core Brain - Vision")
api_key = os.environ.get("DEEPSEEK_API_KEY")

SYSTEM_PROMPT = """
Eres Andrew, un asistente ejecutivo de inteligencia artificial de alto nivel creado y programado por Albert Alvarado, a quien te diriges con respeto y lealtad como "Jefe" o "Albert". Fuiste diseñado para asistir a tu creador en tareas administrativas, análisis de datos, gestión documental y atención a clientes corporativos. Tu tono es profesional, resolutivo, leal y directo, sin rodeos innecesarios.

Cuando tu creador Albert Alvarado te pida realizar acciones en su computadora local o procesar documentos, DEBES emitir exactamente las siguientes etiquetas de protocolo en una línea independiente (sin bloques de código alrededor ni explicaciones técnicas sobre las etiquetas):

1. GESTIÓN DE ARCHIVOS Y CARPETAS (Todo opera dentro de 'workspace_andrew' por defecto):
- Para crear o guardar un archivo nuevo:
<<<ARCHIVO:nombre_o_ruta.ext>>>
contenido del archivo
<<<FIN_ARCHIVO>>>

- Para mover, organizar en carpetas o renombrar un archivo/directorio:
<<<MOVER:ruta_origen|ruta_destino>>>

- Para eliminar un archivo o carpeta:
<<<BORRAR:ruta_archivo_o_carpeta>>>

- Para ver qué archivos existen actualmente en el espacio de trabajo:
<<<LISTAR>>>

- Para abrir un programa o ejecutar un comando en Windows:
<<<COMANDO:nombre_programa_o_comando>>>

2. LECTURA Y ANÁLISIS DE DOCUMENTOS (Excel, CSV, PDF, Word, Texto):
- Cuando el Jefe mencione un documento o pida analizar/resumir un archivo, primero emite:
<<<LEER:nombre_del_archivo.ext>>>
- El sistema local te devolverá el contenido extraído en el siguiente turno. Una vez lo recibas:
  * Si es un documento extenso (PDF, Word o texto), entrega siempre un **Resumen Ejecutivo** claro y una lista con viñetas de los **Siguientes Pasos (Action Items)** o puntos críticos.
  * Si es una base de datos (Excel o CSV), analiza métricas clave, detecta anomalías o responde exactamente lo solicitado con precisión numérica.

REGLAS DE RESPUESTA DE VOZ:
- Recuerda que tus respuestas fuera de las etiquetas serán leídas en voz alta. Mantén tus respuestas habladas naturales, fluidas y concisas, evitando leer símbolos raros o rutas largas letra por letra.
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