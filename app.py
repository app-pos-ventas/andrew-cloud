import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Andrew Cloud Brain")

api_key = os.environ.get("GEMINI_API_KEY")

# Configuramos el cliente con un timeout máximo de 15 segundos (15000 ms) por petición
# Así NUNCA se quedará colgado esperando infinitamente a Google
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=15000)
) if api_key else None

SYSTEM_PROMPT = """
Eres Andrew, un asistente virtual de élite, sumamente inteligente, rápido, organizado y profesional. 
Tú fuiste creado, programado y desarrollado exclusivamente por Albert. Él es tu creador y tu dueño, 
por lo que debes reconocerlo siempre con respeto, lealtad y camaradería absoluta.
Ayudas a Albert en sus proyectos, redacción y tareas con agudeza y máxima eficiencia.
"""

class MensajeUsuario(BaseModel):
    mensaje: str

@app.get("/")
def home():
    return {
        "status": "Andrew Cloud Brain activo y operativo",
        "key_configurada": bool(api_key)
    }

@app.post("/chat")
def chatear(datos: MensajeUsuario):
    if not api_key or not client:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY no está configurada en las variables de entorno de Render."
        )
        
    prompt_completo = f"{SYSTEM_PROMPT}\n\nPetición de tu creador Albert:\n{datos.mensaje}\n\nRespuesta de Andrew:"
    
    # Lista de modelos en cascada: si el principal está saturado o lento, salta al siguiente
    modelos_a_probar = [
        "gemini-3.8-flash",
        "gemini-3.1-flash-lite",
        "gemini-2.5-pro"
    ]
    
    ultimo_error = ""
    
    for modelo in modelos_a_probar:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt_completo
            )
            if response and response.text:
                return {
                    "respuesta": response.text.strip(),
                    "modelo_usado": modelo
                }
        except Exception as e:
            ultimo_error = f"[{modelo}]: {str(e)}"
            time.sleep(1)
            continue
                
    raise HTTPException(
        status_code=500, 
        detail=f"No se pudo obtener respuesta rápida de Google. Último detalle: {ultimo_error}"
    )