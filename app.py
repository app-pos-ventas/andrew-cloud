import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Andrew Cloud Brain")

api_key = os.environ.get("GEMINI_API_KEY")

# Timeout de 25 segundos (25000 ms) por intento para dar margen suficiente a la generación
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=25000)
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
    
    # Modelos vigentes con sus identificadores exactos de API
    modelos_a_probar = [
        "gemini-3.8-flash",
        "gemini-3.1-pro-preview",
        "gemini-3.1-flash-lite-preview"
    ]
    
    errores_registrados = []
    
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
            errores_registrados.append(f"[{modelo}]: {str(e)}")
            time.sleep(1)
            continue
                
    raise HTTPException(
        status_code=500, 
        detail=" | ".join(errores_registrados)
    )