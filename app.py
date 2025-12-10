import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import json

# ==============================
# CONFIG
# ==============================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analizar_imagen(image_pil):
    # Convertimos la imagen a bytes
    buffer = io.BytesIO()
    image_pil.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()

    prompt = """
    Actúa como un sistema OCR experto en logística. Analiza la imagen del contenedor.
    Devuelve exclusivamente un JSON con los campos:
    {
      "sigla": "",
      "numero": "",
      "dv": "",
      "max_gross_kg": "",
      "max_gross_lb": "",
      "tara_kg": "",
      "tara_lb": ""
    }

    Si un valor no se lee, usa null.
    No agregues texto fuera del JSON.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini-vision",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image", "image": image_bytes}
            ]}
        ]
    )

    return response.choices[0].message.content


# ==============================
# STREAMLIT UI
# ==============================
st.title("📦 OCR Contenedores – OpenAI (Gratis)")
st.write("Demo con modelo gpt-4o-mini-vision")

imagen_capturada = st.camera_input("Tomar foto del contenedor")

if imagen_capturada:

    st.image(imagen_capturada)

    with st.spinner("Analizando..."):
        try:
            img = Image.open(imagen_capturada)
            texto = analizar_imagen(img)

            # limpiar posibles ```json
            json_str = texto.strip().replace("```json", "").replace("```", "")
            datos = json.loads(json_str)

            st.success("Datos extraídos correctamente")
            st.json(datos)

        except Exception as e:
            st.error(f"Error leyendo JSON: {e}")
            st.write("Respuesta recibida:", texto)
