import pandas as pd
import streamlit as st
import os 
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder
from scraping.scraping_site_1 import Site1Scraper
from scraping.scraping_site_2 import Site2Scraper
from data_transformation.transform_site1 import VehicleDataTransformer_site1, DEFAULT_CONFIG_1
from data_transformation.transform_site2 import VehicleDataTransformer_site2, DEFAULT_CONFIG_2
from exportToFile import WordExporter

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
        """Combina los dataframes manteniendo el orden original"""
        if df1 is not None and df2 is not None:
            df1['original_index'] = range(len(df1))
            merged_df = pd.merge(df1, df2, on='Key', how='outer', suffixes=('_site1', '_site2'))
            merged_df['original_index'] = merged_df['original_index'].fillna(merged_df['original_index'].max() + 1)
            
            merged_df['Value_editable'] = merged_df.apply(
                lambda row: row['Value_site1'] if pd.isna(row['Value_site2']) or row['Value_site2'] == 'None' 
                else row['Value_site2'],
                axis=1
            )
            
            merged_df = merged_df.rename(columns={
                'Value_site1': 'Valor Sitio 1',
                'Value_site2': 'Valor Sitio 2',
                'Value_editable': 'Valor Final'
            })
            
            return merged_df.sort_values('original_index').drop('original_index', axis=1)
                
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

    # Opciones de idioma y rutas de plantillas
    if 'language_options' not in st.session_state:
        st.session_state.language_options = {
            'Inglés': "utils/planillaIngles.docx",
            'Alemán': "utils/planillaAleman.docx"
            # Agrega más idiomas y rutas si es necesario
        }
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = list(st.session_state.language_options.keys())[0]  # Idioma por defecto

def setup_page():
    """Configura la página y el diseño inicial"""
    st.set_page_config(layout="wide")
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

def filter_dataframe(df, search_term):
    """Filtra el dataframe según el término de búsqueda"""
    if not search_term:
        return df
    mask = df['Key'].str.contains(search_term, case=False, na=False)
    return df[mask].copy()

def render_aggrid(df):
    """Renderiza la tabla usando AgGrid"""
    # Resetear el índice y hacerlo una columna
    df = df.reset_index(drop=False)
    
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # Configurar columnas
    gb.configure_column('index', 
                        header_name="Índice",
                        hide=True)  # Ocultar la columna de índice en la tabla
    gb.configure_column('Key', 
                       header_name="Característica",
                       editable=False,
                       sortable=True,
                       filter=True)
    gb.configure_column('Valor Sitio 1',
                       header_name="Valor Sitio 1",
                       editable=False)
    gb.configure_column('Valor Sitio 2',
                       header_name="Valor Sitio 2",
                       editable=False)
    gb.configure_column('Valor Final',
                       header_name="Valor Final (Editable)",
                       editable=True)
    
    # Configuraciones adicionales
    gb.configure_default_column(min_column_width=200)
    gb.configure_grid_options(domLayout='normal')
    gb.configure_selection(selection_mode='single', use_checkbox=False)
    
    grid_options = gb.build()
    
    return AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        theme='alpine',
        height=500,
        allow_unsafe_jscode=True,
        key=f"grid_{hash(str(df.index.values))}"
    )

def update_dataframe_values(original_df, updated_data):
    """
    Actualiza el DataFrame original con los valores modificados
    """
    updated_df = pd.DataFrame(updated_data)
    
    for _, row in updated_df.iterrows():
        original_idx = row['index']  # Obtener el índice original
        new_value = row['Valor Final']
        
        # Verificar si el valor ha cambiado
        if original_df.loc[original_idx, 'Valor Final'] != new_value:
            # Actualizar el DataFrame original
            original_df.loc[original_idx, 'Valor Final'] = new_value
    
    return original_df

def main():
    # Configuración inicial
    setup_page()
    init_session_state()
    
    # Renderizar inputs
    url_site1, url_site2 = render_url_inputs()
    
    # Instanciar el procesador de datos
    processor = DataProcessor()
    
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
        search_term = st.text_input(
            "🔍 Buscar por característica:",
            value=st.session_state.search_term,
            key="search_input",
            placeholder="Escriba para filtrar..."
        )
        
        # Actualizar el término de búsqueda en la sesión
        st.session_state.search_term = search_term
        
        # Filtrar y mostrar datos
        filtered_df = filter_dataframe(st.session_state.merged_df, search_term)
        if filtered_df is not None and not filtered_df.empty:
            # Obtener la respuesta de AgGrid
            grid_response = render_aggrid(filtered_df)
            
            if grid_response['data'] is not None:
                # Actualizar el DataFrame original con los cambios
                st.session_state.merged_df = update_dataframe_values(
                    st.session_state.merged_df,
                    grid_response['data']
                )
            
            # Seleccionar idioma mediante radio buttons horizontales
            st.subheader("Selecciona el idioma para la plantilla:")
            st.session_state.selected_language = st.radio(
                label="",
                options=list(st.session_state.language_options.keys()),
                index=0,
                key="language_radio",
                horizontal=True
            )


            
            # Exportar a Word
            if st.button("Transformar a Word", type="primary"):
                with st.spinner('Preparando documento...'):
                    # Obtener la ruta de la plantilla según el idioma seleccionado
                    planilla_path = st.session_state.language_options[st.session_state.selected_language]
                    exporter = WordExporter(planilla_path)
                    doc_bytes = exporter.export_to_word(st.session_state.merged_df)
                    
                    if doc_bytes:
                        st.download_button(
                            label="📥 Descargar documento Word",
                            data=doc_bytes,
                            file_name="datos_exportados.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                        st.success('¡Documento preparado! Haz clic en el botón de descarga para guardarlo.')
                    else:
                        st.error('Error al generar el documento.')
        else:
            st.info("No se encontraron resultados para la búsqueda.")

if __name__ == "__main__":
    main()