from docxtpl import DocxTemplate
from jinja2 import Environment, Undefined
import pandas as pd
import io

class RetainUndefined(Undefined):
    """Clase para mantener las variables no definidas en su formato original"""
    def __str__(self):
        return f"{{{{{self._undefined_name}}}}}"

class WordExporter:
    """
    Clase para manejar la exportación de datos a archivos Word usando docxtpl
    """
    def __init__(self, template_path):
        self.template_path = template_path
        self.jinja_env = Environment(undefined=RetainUndefined)

    def prepare_data_for_export(self, df):
        """
        Prepara los datos para la exportación, creando un diccionario de reemplazo
        usando los valores editados de la columna 'Valor Final'
        """
        # Tomar los valores de la columna 'Valor Final'
        valores_finales = df['Valor Final'].tolist()
        
        # Crear el diccionario de reemplazo
        replacement_dict = {
            f'B{i+1}': str(valor) if pd.notna(valor) else ''
            for i, valor in enumerate(valores_finales)
        }
        
        return replacement_dict

    def export_to_word(self, df):
        """
        Exporta los datos a un archivo Word usando la plantilla
        
        Args:
            df: DataFrame con los datos a exportar (debe tener columna 'Valor Final')
        
        Returns:
            bytes: El documento Word en formato de bytes
        """
        try:
            # Preparar los datos para el reemplazo
            context = self.prepare_data_for_export(df)
            
            # Cargar la plantilla
            doc = DocxTemplate(self.template_path)
            
            # Renderizar el documento con el contexto
            doc.render(context, jinja_env=self.jinja_env)
            
            # Guardar el documento en memoria
            output = io.BytesIO()
            doc.save(output)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            print(f"Error al exportar a Word: {e}")
            return None