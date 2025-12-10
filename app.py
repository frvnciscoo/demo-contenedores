import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import io
import json



GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# ===============================
# FUNCIÓN CORRECTA PARA GEMINI 1.5
# ===============================
def analizar_imagen(image_pil):
    model = genai.GenerativeModel("gemini-1.5-flash")

    # PIL -> JPEG bytes
    buffer = io.BytesIO()
    image_pil.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()

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

    # NUEVA forma correcta de enviar imágenes en 0.8.5
    response = model.generate_content(prompt)
    st.write(response.text)

    return response.text


# ===============================
# STREAMLIT UI
# ===============================
st.title("📱 Demo Scanner Contenedores IA")
st.write("Simulación de captura TRF")

imagen_capturada = st.camera_input("Tomar foto del contenedor")

if imagen_capturada:
    st.image(imagen_capturada)

    with st.spinner("Procesando..."):
        try:
            img = Image.open(imagen_capturada)
            resultado = analizar_imagen(img)

            json_str = resultado.strip().replace("```json", "").replace("```", "")
            datos = json.loads(json_str)

            st.success("Datos extraídos")
            st.json(datos)

        except Exception as e:
            st.error(f"Error: {e}")



