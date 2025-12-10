import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- CONFIGURACIÓN ---
# Aquí va tu API Key de Google (se consigue gratis en aistudio.google.com para pruebas)
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

def analizar_imagen(image):
    model = genai.GenerativeModel('gemini-1.5-flash') # Modelo rápido y barato
    
    prompt = """
    Actúa como un sistema OCR experto en logística. Analiza la imagen del contenedor.
    Extrae estrictamente en formato JSON los siguientes campos:
    - sigla (ej: TRHU)
    - numero (ej: 496448)
    - dv (dígito verificador, ej: 9)
    - max_gross_kg (solo el numero)
    - max_gross_lb (solo el numero)
    - tara_kg (solo el numero)
    - tara_lb (solo el numero)
    
    Si un valor no es legible, pon null. No des explicaciones, solo el JSON.
    """
    
    response = model.generate_content([prompt, image])
    return response.text

# --- INTERFAZ DEL PMV (Streamlit) ---
st.title("📱 Demo Scanner Contenedores IA")
st.write("Simulación de captura en dispositivo TRF")

# 1. Captura
imagen_capturada = st.camera_input("Tomar foto del contenedor")

if imagen_capturada:
    st.image(imagen_capturada, caption="Foto capturada")
    
    with st.spinner('Procesando con IA...'):
        # Convertir imagen para la API
        img = Image.open(imagen_capturada)
        
        # Llamar a Gemini
        try:
            resultado_texto = analizar_imagen(img)
            # Limpiar el texto para obtener solo el JSON
            json_str = resultado_texto.strip().replace('```json', '').replace('```', '')
            datos = json.loads(json_str)
            
            st.success("¡Datos extraídos!")
            st.divider()
            
            # 2. Verificación Humana (Formulario editable)
            st.subheader("Verificar Datos")
            
            col1, col2, col3 = st.columns(3)
            sigla = col1.text_input("Sigla", value=datos.get("sigla", ""))
            numero = col2.text_input("Número", value=datos.get("numero", ""))
            dv = col3.text_input("DV", value=datos.get("dv", ""))
            
            st.markdown("---")
            col4, col5 = st.columns(2)
            max_kg = col4.number_input("Max Gross (Kg)", value=int(datos.get("max_gross_kg", 0)))
            tara_kg = col5.number_input("Tara (Kg)", value=int(datos.get("tara_kg", 0)))
            
            # 3. Envío
            st.markdown("---")
            if st.button("✅ CONFIRMAR Y ENVIAR A WMS"):
                st.balloons()
                st.info(f"Enviando datos: {sigla} {numero}-{dv} | Tara: {tara_kg}")
                # Aquí iría el código real para enviar a tu base de datos
                
        except Exception as e:

            st.error(f"Error en la lectura: {e}")


