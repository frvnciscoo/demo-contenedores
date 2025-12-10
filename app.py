import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import json
import re

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------
# Función que encuentra JSON aunque esté mezclado
# -----------------------
def extraer_json_seguro(texto):
    try:
        # Buscar el primer bloque {...}
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            raise ValueError("No se encontró JSON en la respuesta.")
    except Exception as e:
        raise ValueError(f"JSON inválido: {e}\nTexto recibido:\n{texto}")


def analizar_imagen(image_pil):
    # Convertir PIL → base64
    buffer = io.BytesIO()
    image_pil.save(buffer, format="JPEG")
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    prompt = """
    Extrae los siguientes datos del contenedor. SOLO devuelve un JSON sin texto adicional:
    {
      "sigla": "",
      "numero": "",
      "dv": "",
      "max_gross_kg": "",
      "max_gross_lb": "",
      "tara_kg": "",
      "tara_lb": ""
    }
    Si no se puede leer un valor, usa null.
    NO escribas nada que no sea JSON.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini-vision",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}"
                    }
                ],
            }
        ],
        max_tokens=200
    )

    return response.choices[0].message.content


# ----------------------------------------------------
# STREAMLIT
# ----------------------------------------------------
st.title("📦 OCR Contenedores – OpenAI")

imagen_capturada = st.camera_input("Tomar foto del contenedor")

if imagen_capturada:
    st.image(imagen_capturada)

    with st.spinner("Procesando..."):
        img = Image.open(imagen_capturada)

        try:
            respuesta_bruta = analizar_imagen(img)

            # Extraer JSON incluso si el modelo habló demás
            datos = extraer_json_seguro(respuesta_bruta)

            st.success("Datos extraídos del contenedor:")
            st.json(datos)

        except Exception as e:
            st.error(str(e))
            st.write("Respuesta bruta del modelo:", respuesta_bruta)
