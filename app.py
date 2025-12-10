import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scanner Contenedores", page_icon="🚢")

# --- TÍTULO Y DEBUG ---
st.title("🚢 Scanner TRF - Gemini IA")
st.caption(f"Librería AI versión: {genai.__version__}") # Esto nos confirmará si se actualizó

# --- CONFIGURACIÓN API KEY ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Error: No se encontró la API Key en los 'Secrets' de Streamlit.")
    st.stop()

def procesar_imagen(image):
    # Usamos el modelo más moderno y rápido
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    Eres un sistema experto en OCR de logística portuaria.
    Analiza la imagen del contenedor y extrae los siguientes datos técnicos.
    
    Reglas:
    1. Devuelve SOLAMENTE un objeto JSON válido.
    2. No uses bloques de código (```json), solo el texto plano del JSON.
    3. Si un dato no es visible, usa null.
    
    Formato JSON requerido:
    {
      "sigla": "Texto (ej: TRHU)",
      "numero": "Texto (ej: 496448)",
      "dv": "Texto (ej: 9)",
      "max_gross_kg": Entero,
      "max_gross_lb": Entero,
      "tara_kg": Entero,
      "tara_lb": Entero
    }
    """
    
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Error API: {str(e)}"

# --- INTERFAZ PRINCIPAL ---

# 1. Captura
img_file_buffer = st.camera_input("📸 Capturar Contenedor")

if img_file_buffer is not None:
    # Mostrar imagen
    image = Image.open(img_file_buffer)
    
    with st.spinner("🔄 Procesando con IA (Gemini 1.5)..."):
        try:
            # Llamada a la IA
            resultado_raw = procesar_imagen(image)
            
            # Limpieza de la respuesta (por si la IA pone comillas extrañas)
            texto_limpio = resultado_raw.replace("```json", "").replace("```", "").strip()
            
            # Convertir texto a Diccionario Python
            datos = json.loads(texto_limpio)
            
            st.success("✅ Lectura Exitosa")
            
            # 2. Formulario de Verificación
            st.markdown("---")
            st.subheader("📝 Verificar Datos")
            
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1: val_sigla = st.text_input("Sigla", datos.get("sigla", ""))
            with c2: val_num = st.text_input("Número", datos.get("numero", ""))
            with c3: val_dv = st.text_input("DV", datos.get("dv", ""))
            
            c4, c5 = st.columns(2)
            with c4: val_tara_kg = st.text_input("Tara (Kg)", str(datos.get("tara_kg", "")))
            with c5: val_mg_kg = st.text_input("Max Gross (Kg)", str(datos.get("max_gross_kg", "")))

            # 3. Botón de Acción
            st.markdown("---")
            if st.button("🚀 CONFIRMAR Y ENVIAR", type="primary"):
                st.balloons()
                st.info(f"Enviado al WMS: {val_sigla} {val_num}-{val_dv}")
                
        except json.JSONDecodeError:
            st.error("Error al interpretar los datos de la IA.")
            with st.expander("Ver respuesta cruda (Debug)"):
                st.write(resultado_raw)
        except Exception as e:
            st.error(f"Ocurrió un error inesperado: {e}")
