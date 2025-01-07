import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
from jinja2 import Environment, Undefined
import re

# Clase personalizada para manejar claves no encontradas
class RetainUndefined(Undefined):
    def __str__(self):
        # Mantener el marcador en su forma original si no se encuentra
        return f"{{{{{self._undefined_name}}}}}"  # Regresa el marcador original con doble llave

# Configurar el entorno Jinja2 para permitir conservar claves no encontradas
jinja_env = Environment(undefined=RetainUndefined)

# Función para procesar el documento Word
def procesar_documento(nombre_plantilla, datos, nombre_salida):
    try:
        # Cargar la plantilla
        template = DocxTemplate(nombre_plantilla)

        # Aplicar el entorno Jinja2 personalizado
        template.render(datos, jinja_env=jinja_env)

        # Guardar el documento final
        template.save(nombre_salida)
        return True, nombre_salida
    except Exception as e:
        return False, str(e)    

# Interfaz de Streamlit
st.title("Generación de Documentos para Homologación")

# Inicializar el estado de la sesión
if 'editable_table' not in st.session_state:
    st.session_state.editable_table = pd.DataFrame(columns=["Clave", "Valor"])

# Crear el diccionario hardcodeado de prueba
def crear_diccionario_prueba():
    datos = {
        "A1": "Marca",
        "A2": "Tipo",
        "A3": "Variante",
        "A4": "Ejecución",
        "A5": "Modelo",
        "B1": "Número de ejes",
        "B2": "Cantidad de ruedas",
        "B3": "Ejes motrices",
        "B4": "Distancia entre ejes",
    }
    return datos

# Diccionario para pruebas iniciales
datos_prueba = crear_diccionario_prueba()

# Cargar archivo de plantilla Word
plantilla_path = "C:\\Users\\usuario\\Desktop\\ProyectosPersonalesMaxi\\autoMM\\Utils\\planilla.docx"

if st.button("Exportar documento"):
    if not st.session_state.editable_table.empty:
        with st.spinner("Generando documento..."):

            salida_path = "documento_rellenado.docx"
            exito, mensaje = procesar_documento(plantilla_path, datos_prueba, salida_path)

            if exito:
                with open(salida_path, "rb") as file:
                    st.download_button(
                        label="Descargar documento generado",
                        data=file,
                        file_name=salida_path,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                st.success(f"Documento generado exitosamente: {salida_path}")
            else:
                st.error(f"Error al generar el documento: {mensaje}")
    else:
        st.error("No hay datos disponibles para exportar. Extrae y transforma los datos primero.")


# Texto inicial para instrucciones
st.write("Ingresa los datos y genera el documento basado en la plantilla seleccionada.")
