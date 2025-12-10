import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import json
import base64

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analizar_imagen(img):
    import base64
    from io import BytesIO

    # Convertir PIL a base64
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    prompt = """
Extrae los siguientes valores desde la imagen de un contenedor y devuélvelos en JSON estricto:
- sigla_cnt
- nro_cnt
- dv_cnt
- tara
- max_gross
- max_payload
- cubic_capacity
Si no se ve algún dato, usar null.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{img_b64}"
                    }
                ]
            }
        ]
    )

    return response.choices[0].message["content"]



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

