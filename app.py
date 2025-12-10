import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import json
import base64

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analizar_imagen(image_pil):
    # Convertir a JPEG
    buffer = io.BytesIO()
    image_pil.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()

    # Base64
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    prompt = """
    Actúa como un sistema OCR experto en logística. Analiza la imagen del contenedor.
    Extrae estrictamente en formato JSON los siguientes campos:
    - sigla
    - numero
    - dv
    - max_gross_kg
    - max_gross_lb
    - tara_kg
    - tara_lb
    Si un valor no es legible, usa null. Solo JSON.
    """

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                    {
                        "type": "input_image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": img_b64
                        }
                    }
                ]
            }
        ]
    )

    return response.output_text


st.title("📦 OCR Contenedores - IA")
st.write("Captura el contenedor y extraemos los datos automáticamente.")

imagen = st.camera_input("Tomar foto del contenedor")

if imagen:
    img = Image.open(imagen)

    with st.spinner("Procesando imagen..."):
        texto = analizar_imagen(img)

        try:
            limpio = texto.strip().replace("```json", "").replace("```", "")
            datos = json.loads(limpio)
            st.success("Datos detectados")
            st.json(datos)
        except Exception as e:
            st.error(f"Error leyendo JSON: {e}")
            st.code(texto)
