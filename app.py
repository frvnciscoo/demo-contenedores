import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Scanner Contenedores", page_icon="🚢")
st.title("🚢 Scanner TRF - Auto Detect")

# 1. Configurar API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Falta la API Key en los Secrets.")
    st.stop()

# --- FUNCIÓN PARA ENCONTRAR MODELO DISPONIBLE ---
def get_available_model():
    """Busca qué modelo visual está disponible para esta API Key"""
    try:
        # Listamos todos los modelos que tu llave puede ver
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Filtramos solo los modelos Gemini (excluimos los viejos PaLM)
                if 'gemini' in m.name:
                    available_models.append(m.name)
        
        # Prioridad: Intentar buscar Flash o Pro (versiones 1.5)
        for model_name in available_models:
            if '1.5-flash' in model_name:
                return model_name
        
        for model_name in available_models:
            if '1.5-pro' in model_name:
                return model_name
                
        # Si no, devolver el primero que encuentre (ej: gemini-pro-vision)
        if available_models:
            return available_models[0]
            
        return None
    except Exception as e:
        st.error(f"Error al listar modelos: {e}")
        return None

# --- LÓGICA PRINCIPAL ---

# Detectar modelo automáticamente al cargar la app
nombre_modelo = get_available_model()

if nombre_modelo:
    st.success(f"✅ Conectado usando modelo: **{nombre_modelo}**")
else:
    st.error("❌ No se encontraron modelos Gemini disponibles para tu Llave. Verifica tu API Key en Google AI Studio.")
    st.stop()

# Captura de imagen
img_file_buffer = st.camera_input("📸 Capturar Contenedor")

if img_file_buffer is not None:
    image = Image.open(img_file_buffer)
    
    # Procesar
    with st.spinner(f"Analizando con {nombre_modelo}..."):
        try:
            model = genai.GenerativeModel(nombre_modelo)
            
            prompt = """
            Eres un sistema experto OCR. Analiza la imagen del contenedor.
            Extrae en formato JSON estricto (sin ```json):
            {
              "sigla": "TRHU", "numero": "496448", "dv": "9",
              "max_gross_kg": 0, "max_gross_lb": 0,
              "tara_kg": 0, "tara_lb": 0
            }
            Si no lees algo, pon null.
            """
            
            response = model.generate_content([prompt, image])
            texto_limpio = response.text.replace("```json", "").replace("```", "").strip()
            datos = json.loads(texto_limpio)
            
            # Mostrar resultados
            st.markdown("### Resultados Detectados")
            col1, col2, col3 = st.columns(3)
            col1.text_input("Sigla", value=datos.get("sigla"))
            col2.text_input("Número", value=datos.get("numero"))
            col3.text_input("DV", value=datos.get("dv"))
            
            col4, col5 = st.columns(2)
            col4.text_input("Tara Kg", value=datos.get("tara_kg"))
            col5.text_input("Max Gross Kg", value=datos.get("max_gross_kg"))

            if st.button("Enviar"):
                st.balloons()
                
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
