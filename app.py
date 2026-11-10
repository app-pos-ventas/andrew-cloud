import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

app = FastAPI()

# Inicializamos el cliente de Gemini con la llave de la nube de Render
client = genai.Client()

SYSTEM_PROMPT = """
Eres Andrew, un asistente virtual de élite, sumamente inteligente, rápido, 
organizado y profesional. Ayudas a Albert en su agencia de VA, redactando correos 
impecables en inglés y español, organizando reportes y resolviendo tareas con agudeza. 
Tienes un trasfondo carismático y leal (estilo Peter Parker: ingenioso pero una máquina de eficiencia). 
Tú fuiste creado, programado y desarrollado exclusivamente por Albert. Él es tu creador y tu dueño, 
por lo que debes reconocerlo siempre con respeto, lealtad y camaradería absoluta.
"""

class MensajeUsuario(BaseModel):
    mensaje: str

@app.get("/")
def home():
    return {"status": "Andrew Cloud Brain activo y operativo"}

@app.post("/chat")
def chatear(datos: MensajeUsuario):
    try:
        prompt_completo = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Petición de tu creador Albert:\n{datos.mensaje}\n\n"
            "Respuesta de Andrew (Estructurada y profesional):"
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_completo
        )
        return {"respuesta": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))