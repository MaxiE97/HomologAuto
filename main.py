import pandas as pd
import streamlit as st
from scraping.scraping_site_1 import Site1Scraper
from scraping.scraping_site_2 import Site2Scraper
from data_transformation.transform_site1 import VehicleDataTransformer_site1, DEFAULT_CONFIG_1
from data_transformation.transform_site2 import VehicleDataTransformer_site2, DEFAULT_CONFIG_2

class DataProcessor:
    """
    Clase para manejar el procesamiento y transformación de datos de vehículos
    """
    def __init__(self):
        self.site1_scraper = Site1Scraper()
        self.site2_scraper = Site2Scraper()
        self.transformer_site1 = VehicleDataTransformer_site1(DEFAULT_CONFIG_1)
        self.transformer_site2 = VehicleDataTransformer_site2(DEFAULT_CONFIG_2)

    def process_url(self, url, site_number):
        """Procesa una URL y retorna los datos transformados"""
        try:
            if site_number == 1:
                data = self.site1_scraper.scrape(url)
                return self.transformer_site1.transform(data)
            else:
                data = self.site2_scraper.scrape(url)
                return self.transformer_site2.transform(data)
        except Exception as e:
            st.error(f"Error al procesar el Sitio {site_number}: {e}")
            return None

    @staticmethod
    def merge_dataframes(df1, df2):
        """
        Combina los dataframes manteniendo el orden original y aplicando la lógica de valores
        """
        if df1 is not None and df2 is not None:
            # Crear un índice para mantener el orden original
            df1['original_index'] = range(len(df1))
            
            # Merge de los dataframes
            merged_df = pd.merge(df1, df2, on='Key', how='outer', suffixes=('_site1', '_site2'))
            
            # Rellenar el índice original para las filas nuevas
            merged_df['original_index'] = merged_df['original_index'].fillna(merged_df['original_index'].max() + 1)
            
            # Crear la columna editable con la lógica especificada
            merged_df['Value_editable'] = merged_df.apply(
                lambda row: row['Value_site1'] if pd.isna(row['Value_site2']) or row['Value_site2'] == 'None' 
                else row['Value_site2'],
                axis=1
            )
            
            # Renombrar columnas
            merged_df = merged_df.rename(columns={
                'Value_site1': 'Valor Sitio 1',
                'Value_site2': 'Valor Sitio 2',
                'Value_editable': 'Valor Final'
            })
            
            # Ordenar por el índice original y eliminarlo
            merged_df = merged_df.sort_values('original_index').drop('original_index', axis=1)
            return merged_df
            
        elif df1 is not None:
            return df1.assign(**{
                'Valor Sitio 1': df1['Value'],
                'Valor Sitio 2': None,
                'Valor Final': df1['Value']
            })[['Key', 'Valor Sitio 1', 'Valor Sitio 2', 'Valor Final']]
            
        elif df2 is not None:
            return df2.assign(**{
                'Valor Sitio 1': None,
                'Valor Sitio 2': df2['Value'],
                'Valor Final': df2['Value']
            })[['Key', 'Valor Sitio 1', 'Valor Sitio 2', 'Valor Final']]
            
        return None

def init_session_state():
    """Inicializa las variables de estado de la sesión"""
    if 'df_site1' not in st.session_state:
        st.session_state.df_site1 = None
    if 'df_site2' not in st.session_state:
        st.session_state.df_site2 = None
    if 'merged_df' not in st.session_state:
        st.session_state.merged_df = None
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ""

def setup_page():
    """Configura la página y el diseño inicial"""
    st.set_page_config(layout="wide")
    # Centrar el título usando HTML
    st.markdown("<h1 style='text-align: center;'>Extracción de datos para homologación</h1>", unsafe_allow_html=True)
    
def render_url_inputs():
    """Renderiza los campos de entrada de URL"""
    st.subheader("Ingreso de URLs")
    col1, col2 = st.columns(2)
    with col1:
        url_site1 = st.text_input("URL del Sitio 1 (Página holandesa):", key="url1")
    with col2:
        url_site2 = st.text_input("URL del Sitio 2 (Página alemana):", key="url2")
    return url_site1, url_site2

def render_search_bar():
    """Renderiza la barra de búsqueda"""
    return st.text_input(
        "🔍 Buscar por característica:",
        value=st.session_state.search_term,
        key="search_input",
        placeholder="Escriba para filtrar..."
    )

def filter_dataframe(df, search_term):
    """Filtra el dataframe según el término de búsqueda"""
    if not search_term:
        return df
    mask = df['Key'].str.contains(search_term, case=False, na=False)
    filtered_df = df[mask].copy()
    return filtered_df

def update_dataframe_with_edits(original_df, edited_df, search_term):
    """Actualiza el dataframe original con los cambios realizados en la vista filtrada"""
    if search_term:
        # Obtener los índices de las filas filtradas
        mask = original_df['Key'].str.contains(search_term, case=False, na=False)
        # Actualizar solo los valores finales de las filas filtradas
        original_df.loc[mask, 'Valor Final'] = edited_df['Valor Final'].values
    else:
        original_df['Valor Final'] = edited_df['Valor Final']
    return original_df

def main():
    # Configuración inicial
    setup_page()
    init_session_state()
    
    # Instanciar el procesador de datos
    processor = DataProcessor()
    
    # Renderizar inputs
    url_site1, url_site2 = render_url_inputs()
    
    # Procesar datos
    if st.button("Procesar URLs", type="primary"):
        if not url_site1 and not url_site2:
            st.warning("Por favor, ingrese al menos una URL para procesar los datos.")
        else:
            with st.spinner('Procesando datos...'):
                if url_site1:
                    st.session_state.df_site1 = processor.process_url(url_site1, 1)
                if url_site2:
                    st.session_state.df_site2 = processor.process_url(url_site2, 2)
                st.session_state.merged_df = processor.merge_dataframes(
                    st.session_state.df_site1, 
                    st.session_state.df_site2
                )
            st.success('¡Procesamiento completado!')
    
    # Mostrar resultados
    if st.session_state.merged_df is not None:
        st.subheader("Resultados")
        
        # Barra de búsqueda
        search_term = render_search_bar()
        st.session_state.search_term = search_term
        
        # Filtrar datos según la búsqueda
        filtered_df = filter_dataframe(st.session_state.merged_df, search_term)
        
        # Mostrar tabla
        edited_df = st.data_editor(
            filtered_df,
            disabled=["Key", "Valor Sitio 1", "Valor Sitio 2"],
            hide_index=True,
            column_config={
                "Key": st.column_config.TextColumn(
                    "Característica",
                    width="large",
                ),
                "Valor Sitio 1": st.column_config.TextColumn(
                    "Valor Sitio 1",
                    width="large",
                ),
                "Valor Sitio 2": st.column_config.TextColumn(
                    "Valor Sitio 2",
                    width="large",
                ),
                "Valor Final": st.column_config.TextColumn(
                    "Valor Final (Editable)",
                    width="large",
                ),
            },
            use_container_width=True,
            key="data_editor"
        )
        
        # Actualizar el dataframe en session_state
        st.session_state.merged_df = update_dataframe_with_edits(
            st.session_state.merged_df, 
            edited_df, 
            search_term
        )

if __name__ == "__main__":
    main()