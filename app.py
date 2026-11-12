import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="Andrew DeepSeek Brain")

api_key = os.environ.get("DEEPSEEK_API_KEY")

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
        "status": "Andrew DeepSeek Brain activo y operativo",
        "key_configurada": bool(api_key)
    }

@app.post("/chat")
async def chatear(datos: MensajeUsuario):
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="DEEPSEEK_API_KEY no está configurada en las variables de entorno de Render."
        )
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": datos.mensaje}
        ],
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error en la API de DeepSeek: {response.text}"
                )
                
            resultado = response.json()
            texto_respuesta = resultado["choices"][0]["message"]["content"]
            return {"respuesta": texto_respuesta.strip()}
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error de conexión con DeepSeek: {str(e)}"
            )