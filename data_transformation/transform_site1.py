import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
import re

@dataclass
class VehicleDataConfig:
    """Configuración para la transformación de datos del vehículo."""
    column_mapping: Dict[str, str]
    ordered_keys: List[str]

class VehicleDataTransformer:
    """Clase para transformar datos de vehículos."""

    def __init__(self, config: VehicleDataConfig):
        self.config = config

    def transform(self, df_input: pd.DataFrame) -> pd.DataFrame:
        """Método principal que orquesta la transformación de datos."""
        df = df_input.copy()
        df = self._rename_columns(df)
        df = self.clean_values(df)
        df = self._process_axle_wheel(df)
        df = self._add_powered_axles(df)
        df = self._process_Axles_track(df)
        df = self._add_missing_keys(df)
        df = self._process_Axles_distribution(df)
        df = self._process_maximum_mass_trailer(df)
        
        

        df = self._sort_and_clean(df)
        return df

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Renombra las columnas según el mapeo configurado."""
        df["Key"] = df["Key"].map(lambda x: self.config.column_mapping.get(x, x))
        return df

    def _process_axle_wheel(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa y combina la información de los ejes y ruedas."""
        if "wheel" in df["Key"].values:
            wheel = df[df["Key"] == "wheel"]["Value"].values[0]

            new_value = f"{2}/{wheel}"

            new_row = pd.DataFrame({
                    "Key": ["Number of axles / wheels"],
                    "Value": [f"{new_value}"]
                })

            df = pd.concat([df, new_row], ignore_index=True)
        return df



    def _add_powered_axles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade información sobre ejes motorizados si no existe."""
        if "Powered axles" not in df["Key"].values:
            return pd.concat([
                df,
                pd.DataFrame({"Key": ["Powered axles"], "Value": ["1"]})
            ], ignore_index=True)
        return df


    def _process_Axles_track(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa y combina la información de las bases de los ejes."""
        if "Axle track  1" in df["Key"].values and "Axle track  2" in df["Key"].values:
          axle_1 = df[df["Key"] == "Axle track  1"]["Value"].values[0]
          axle_2 = df[df["Key"] == "Axle track  2"]["Value"].values[0]

          new_value = f"{axle_1}/{axle_2}"

          new_row = pd.DataFrame({
                  "Key": ["Axle(s) track – 1 / 2"],
                  "Value": [f"{new_value}"]
              })

          df = pd.concat([df, new_row], ignore_index=True)
        return df

    def _process_Axles_distribution(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa y combina la información de la distribución de los ejes."""
        if "Distribution of this mass among the axles – 1" in df["Key"].values and "Distribution of this mass among the axles – 2" in df["Key"].values:
          axle_1 = df[df["Key"] == "Distribution of this mass among the axles – 1"]["Value"].values[0]
          axle_2 = df[df["Key"] == "Distribution of this mass among the axles – 2"]["Value"].values[0]

          new_value = f"{axle_1}/{axle_2}"

          new_row = pd.DataFrame({
                  "Key": ["Distribution of this mass among the axles – 1 / 2"],
                  "Value": [f"{new_value}"]
              })

          df = pd.concat([df, new_row], ignore_index=True)

          new_row_2 = pd.DataFrame({
                  "Key": ["Technically permissible max mass on each axle – 1 / 2"],
                  "Value": [f"{new_value}"]
              })

          df = pd.concat([df, new_row_2], ignore_index=True)


        return df

    def _process_maximum_mass_trailer(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa y combina la información del peso máximo del camión."""
        if "Braked" in df["Key"].values and "Unbraked" in df["Key"].values:
          braked = df[df["Key"] == "Braked"]["Value"].values[0]
          unbraked = df[df["Key"] == "Unbraked"]["Value"].values[0]

          new_value = f"{braked}/{unbraked}"

          new_row = pd.DataFrame({
                  "Key": ["Maximum mass of trailer – braked / unbraked"],
                  "Value": [f"{new_value}"]
              })
          df = pd.concat([df, new_row], ignore_index=True)

        return df


    def _add_missing_keys(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade información sobre claves faltantes si no existen en el DataFrame."""
        missing_keys = [
            "Height",
            "Rear overhang",
            "Maximum permissible roof load",
            "Maximum vertical load at the coupling point for a trailer",
            "Engine code as marked on the enginee",
            "Working principle",
            "Direct injection",
            "Pure electric",
            "Hybrid [electric] vehicle",
            "Fuel",
            "Clutch",
            "Gearbox",
            "Gear",
            "Final drive ratio",
        ]

        # Crea nuevas filas solo para las claves que faltan
        missing_rows = [
            {"Key": key, "Value": "None"}
            for key in missing_keys if key not in df["Key"].values
        ]

        if missing_rows:
            df = pd.concat([df, pd.DataFrame(missing_rows)], ignore_index=True)

        return df

    def clean_values(self, df: pd.DataFrame) -> pd.DataFrame:
        def process_value(value):
            if pd.isna(value):  # Manejar valores NaN
                return value
            

            # Eliminar puntos en unidades específicas (como "kg" o "cm³")
            for unit in ['kg', 'cm³']:
                if unit in value:
                    value = value.replace('.', '') 
                    break  
            
            # Eliminar espacios y otras unidades específicas
            for unit in ['kg', 'cm³']:
                if unit in value:
                    value = value.replace(unit, '').strip()


            # Convertir cm a mm usando regex
            if 'cm' in value:
                # Encuentra el número antes de "cm" y multiplica por 10
                value = re.sub(r'(\d+)(?:\.?\d*)\s*cm', 
                              lambda m: str(int(float(m.group(1)) * 10)), 
                              value)                    
                    
            return value

        # Aplicar la transformación a la columna seleccionada
        df["Value"] = df["Value"].astype(str).apply(process_value)
        return df

    def _sort_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ordena y limpia el DataFrame final, manteniendo solo las primeras 30 filas.
        """
        df["Key"] = pd.Categorical(
            df["Key"],
            categories=self.config.ordered_keys,
            ordered=True
        )
        return df.sort_values("Key").head(30).reset_index(drop=True)

    @staticmethod
    def _get_max_value(value: str) -> str:
        """Obtiene el valor máximo de un rango."""
        return value.split("-")[-1].strip()

    @staticmethod
    def _get_value_slash(value: str, spot: int) -> str:
        """Obtiene el valor en un lugar entre las barras"""
        return value.split("/")[spot].strip()

    @staticmethod
    def _get_max_from_pair(value: str, delimitador: str) -> int:
        """Obtiene el máximo valor de un par de números separados por un delimitador.
        Si solo se pasa un número, devuelve ese número."""
        if delimitador in value:
            num1, num2 = map(int, value.split(delimitador))
            return max(num1, num2)
        else:
            return int(value)



# Configuración predeterminada
DEFAULT_CONFIG = VehicleDataConfig(
    column_mapping={
        "Eigenschappen - Aantal wielen": "wheel",
        "Afmetingen - Wielbasis": "Wheelbase",
        "As #1 - Spoorbreedte": "Axle track  1",
        "As #2 - Spoorbreedte": "Axle track  2",
        "Afmetingen - Lengte": "Length",
        "Afmetingen - Breedte": "Width",
        "Massa - Rijklaar gewicht": "Mass of the vehicle with bodywork in running order",
        "Massa - Technisch limiet massa": "Technically permissible maximum laden mass",
        "As #1 - Technisch limiet": "Distribution of this mass among the axles – 1",
        "As #2 - Technisch limiet": "Distribution of this mass among the axles – 2",
        "Trekkracht - Maximaal trekgewicht geremd":"Braked",
        "Trekkracht - Maximaal trekgewicht ongeremd":"Unbraked",
        "Massa - Maximum massa samenstelling": "Maximum mass of combination",
        "Algemeen - Merk":"Engine manufacturer",
        "Motor - Aantal cilinders": "Number and arrangement of cylinders",
        "Motor - Cilinderinhoud": "Capacity",
        "Brandstof #1 - Brandstof	": "Fuel",
        "Brandstof #1 - Vermogen": "Maximum net power",

    },
    ordered_keys=[
        "Number of axles / wheels",
        "Powered axles",
        "Wheelbase",
        "Axle(s) track – 1 / 2",
        "Length",
        "Width",
        "Height",
        "Rear overhang",
        "Mass of the vehicle with bodywork in running order",
        "Technically permissible maximum laden mass",
        "Distribution of this mass among the axles – 1 / 2",
        "Technically permissible max mass on each axle – 1 / 2",
        "Maximum permissible roof load",
        "Maximum mass of trailer – braked / unbraked",
        "Maximum mass of combination",
        "Maximum vertical load at the coupling point for a trailer",
        "Engine manufacturer",
        "Engine code as marked on the enginee",
        "Working principle",
        "Direct injection",
        "Pure electric",
        "Hybrid [electric] vehicle",
        "Number and arrangement of cylinders",
        "Capacity",
        "Fuel",
        "Maximum net power",
        "Clutch",
        "Gearbox",
        "Gear",
        "Final drive ratio",
    ]
)


