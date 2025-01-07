import pandas as pd
import streamlit as st
from scraping.scraping_site_1 import Site1Scraper
from scraping.scraping_site_2 import Site2Scraper
from data_transformation.transform_site1 import VehicleDataTransformer_site1, DEFAULT_CONFIG_1
from data_transformation.transform_site2 import VehicleDataTransformer_site2, DEFAULT_CONFIG_2

# Instanciar scraper y transformadores
site1_scraper = Site1Scraper()
site2_scraper = Site2Scraper()
vehicle_data_transformer_site1 = VehicleDataTransformer_site1(DEFAULT_CONFIG_1)
vehicle_data_transformer_site2 = VehicleDataTransformer_site2(DEFAULT_CONFIG_2)

# Título de la aplicación
st.title("Extracción de datos para homologación")

# Sección para ingresar URLs
st.subheader("Ingreso de URLs")
url_site1 = st.text_input("Ingrese la URL del Sitio 1:", "")
url_site2 = st.text_input("Ingrese la URL del Sitio 2:", "")

# Contenedores para las tablas
st.subheader("Resultados")

# Botón único para procesar
if st.button("Procesar URLs"):
    if not url_site1 and not url_site2:
        st.warning("Por favor, ingrese al menos una URL para procesar los datos.")
    else:
        # Procesar URL del Sitio 1 si está disponible
        if url_site1:
            try:
                st.write("Procesando datos del Sitio 1...")
                data_site1 = site1_scraper.scrape(url_site1)
                df_site1 = vehicle_data_transformer_site1.transform(data_site1)
                st.write("Datos transformados del Sitio 1:")
                st.dataframe(df_site1)
            except Exception as e:
                st.error(f"Error al procesar el Sitio 1: {e}")
        else:
            st.info("No se ingresó URL para el Sitio 1.")

        # Procesar URL del Sitio 2 si está disponible
        if url_site2:
            try:
                st.write("Procesando datos del Sitio 2...")
                data_site2 = site2_scraper.scrape(url_site2)
                df_site2 = vehicle_data_transformer_site2.transform(data_site2)
                st.write("Datos transformados del Sitio 2:")
                st.dataframe(df_site2)
            except Exception as e:
                st.error(f"Error al procesar el Sitio 2: {e}")
        else:
            st.info("No se ingresó URL para el Sitio 2.")
