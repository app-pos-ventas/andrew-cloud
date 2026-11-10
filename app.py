import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

app = FastAPI(title="Andrew Cloud Brain")

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

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
    
    intentos = 3
    ultimo_error = ""
    
    for intento in range(intentos):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt_completo
            )
            return {"respuesta": response.text.strip()}
        except Exception as e:
            ultimo_error = str(e)
            if "503" in ultimo_error or "UNAVAILABLE" in ultimo_error:
                time.sleep(1.5)
                continue
            else:
                break
                
    raise HTTPException(status_code=500, detail=f"Error interno en la API de GenAI tras reintentos: {ultimo_error}")