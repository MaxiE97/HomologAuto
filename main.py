import pandas as pd
import streamlit as st
from utils.campos_planilla import df_planilla
from scraping.scraping_site_1 import Site1Scraper


#--------------------------- PARTE DE NORMALIZACIÓN--------------------------------------------------   

def normalize_keys(df):
    """
    Normaliza las claves del DataFrame convirtiéndolas a minúsculas y reemplazando caracteres especiales.
    """
    df["Clave"] = df["Clave"].str.lower().str.replace(r'\W+', '_', regex=True)
    return df

def transformar_dataframe(df):
    """
    Aplica transformaciones al DataFrame según reglas específicas.
    """
    reglas = {
        'algemeen_merk': lambda valor: 'BMW' if valor == 'Bmw' else valor,
    }

    def aplicar_reglas(row):
        clave = row["Clave"]
        valor = row["Valor"]

        # Aplicar reglas específicas
        if clave in reglas:
            return reglas[clave](valor)

        # Transformar valores de cm a mm
        if isinstance(valor, str) and valor.endswith('cm'):
            try:
                return str(int(valor.replace('cm', '').strip()) * 10)
            except ValueError:
                return valor

        # Procesar valores que terminan en 'kg'
        if isinstance(valor, str) and valor.endswith('kg'):
            # Eliminar puntos solo si el valor termina en 'kg'
            valor = valor.replace('.', '').replace('kg', '').strip()
            return valor

        return valor

    df["Valor"] = df.apply(aplicar_reglas, axis=1)
    return df



#--------------------------- INTERFAZ CON STREAMLIT------------------------------------   
st.title("Extracción datos para homologación")

if 'editable_table' not in st.session_state:
    st.session_state.editable_table = pd.DataFrame(columns=["Clave", "Valor"])

if 'editable_table_planilla' not in st.session_state:
    st.session_state.editable_table_planilla = df_planilla.copy()

url = st.text_input("Ingresa primer enlace de la página web:")
site1_scraper = Site1Scraper()


if st.button("Extraer y transformar datos"):
    if url:
        with st.spinner("Extrayendo y transformando datos..."):
            result = site1_scraper.scrape(url)

            if isinstance(result, str):
                st.error(result)
            else:
                normalized_df = normalize_keys(result)
                transformed_df = transformar_dataframe(normalized_df)

                st.session_state.editable_table = transformed_df
    else:
        st.error("Por favor, introduce un enlace válido.")

if not st.session_state.editable_table.empty:
    st.success("Datos extraídos y transformados con éxito.")

    # Mostrar tabla editable principal
    edited_table = st.data_editor(
        st.session_state.editable_table,
        use_container_width=True,
    )

 #---------------------------MAPEO DE DATOS--------------------------------------------------   


# Diccionario de mapeo entre claves extraídas y campos de df_planilla
mapeo_claves = {
    "afmetingen_wielbasis": "Wheelbase :(mm)",
    "as_1_spoorbreedte / as_2_spoorbreedte": "Axle(s) track 1/ 2: (mm)",
    "afmetingen_lengte": "Length:(mm)",
    "afmetingen_breedte": "Width:(mm)",
    "massa_rijklaar_gewicht": "Mass of the vehicle with bodywork in running order:(kg)",
    "massa_technisch_limiet_massa": "Technically permissable maximum laden mass:(kg)",
    "as_1_technisch_limiet / as_2_technisch_limiet": "Distribution of this mass among the axles – 1 / 2:(kg)",
    "as_1_technisch_limiet / as_2_technisch_limiet": "Technically perm. max mass on each axle – 1 / 2:(kg)",
    "trekkracht_maximaal_trekgewicht_geremd / trekkracht_maximaal_trekgewicht_ongeremd": "Maximum mass of trailer – braked / unbraked:(kg)",
    "massa_maximum_massa_samenstelling": "Maximum mass of combination:(kg)",
    "algemeen_merk": "Engine manufacturer:",
    "motor_motorcode": "Engine code as marked on the engine:",
    "motor_aantal_cilinders": "Number and arrangement of cylinders:",
    
    


    # Más mapeos aquí
}

# Solo ejecuta si la tabla extraída está lista
if "editable_table" in st.session_state and not st.session_state.editable_table.empty:
    # Inicializar la columna "Datos" si no existe
    if "Datos" not in st.session_state.editable_table_planilla.columns:
        st.session_state.editable_table_planilla["Datos"] = None

    # Iterar sobre el mapeo de claves
    for clave_extraida, campo_planilla in mapeo_claves.items():
        if " / " in clave_extraida:  # Detectar clave compuesta
            subclaves = clave_extraida.split(" / ")
            valores = []
            for subclave in subclaves:
                valor = (
                    st.session_state.editable_table.loc[
                        st.session_state.editable_table["Clave"] == subclave, "Valor"
                    ].iloc[0]
                    if subclave in st.session_state.editable_table["Clave"].values
                    else "N/A"  # Valor predeterminado si falta la clave
                )
                valores.append(valor)
            valor_correspondiente = " / ".join(valores)  # Combinar valores con separador
        else:  # Caso simple
            valor_correspondiente = (
                st.session_state.editable_table.loc[
                    st.session_state.editable_table["Clave"] == clave_extraida, "Valor"
                ].iloc[0]
                if clave_extraida in st.session_state.editable_table["Clave"].values
                else None
            )

        # Asignar el valor a la fila correspondiente en df_planilla
        st.session_state.editable_table_planilla.loc[
            st.session_state.editable_table_planilla["Nombre"] == campo_planilla, "Datos"
        ] = valor_correspondiente

    # Mostrar la tabla actualizada
    st.success("df_planilla actualizado con los datos extraídos.")
    st.data_editor(
        st.session_state.editable_table_planilla,
        use_container_width=True,
    )




