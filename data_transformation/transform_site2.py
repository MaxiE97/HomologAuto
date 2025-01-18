import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
import re

@dataclass
class VehicleDataConfig:
    """Configuración para la transformación de datos del vehículo."""
    column_mapping: Dict[str, str]
    ordered_keys: List[str]

class VehicleDataTransformer_site2:
    """Clase para transformar datos de vehículos."""

    def __init__(self, config: VehicleDataConfig):
        self.config = config

    def transform(self, df_input: pd.DataFrame) -> pd.DataFrame:
        """Método principal que orquesta la transformación de datos."""
        df = df_input.copy()
        df = self._rename_columns(df)
        df = self._process_axle_tracks(df)
        df = self._add_powered_axles(df)
        df = self._process_trailer_masses(df)
        df = self._process_mass_distribution(df)
        df = self._process_maximum_vertical_load(df)
        df = self._process_engine_manufacturer(df)
        df = self._process_max_power(df)
        df = self._process_transmission(df)
        df = self._process_drive_ratio(df)
        df= self._add_missing_keys(df)
        df = self._process_Rear_overhang(df)

        df = self._sort_and_clean(df)
        return df

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Renombra las columnas según el mapeo configurado."""
        df["Key"] = df["Key"].map(lambda x: self.config.column_mapping.get(x, x))
        return df

    def _process_axle_tracks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa y combina la información de los ejes."""
        if "Axle(s) track – 1" in df["Key"].values and "Axle(s) track – 2" in df["Key"].values:
            track1 = df[df["Key"] == "Axle(s) track – 1"]["Value"].values[0]
            track2 = df[df["Key"] == "Axle(s) track – 2"]["Value"].values[0]

            max_track1 = self._get_max_value(track1)
            max_track2 = self._get_max_value(track2)

            df = df[df["Key"] != "Axle(s) track – 2"]
            mask = df["Key"] == "Axle(s) track – 1"
            df.loc[mask, "Value"] = f"{max_track1}/{max_track2}"
            df.loc[mask, "Key"] = "Axle(s) track – 1 / 2"

        return df

    def _add_powered_axles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade información sobre ejes motorizados si no existe."""
        if "Powered axles" not in df["Key"].values:
            return pd.concat([
                df,
                pd.DataFrame({"Key": ["Powered axles"], "Value": ["1"]})
            ], ignore_index=True)
        return df


    def _add_missing_keys(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade información sobre claves faltantes si no existen en el DataFrame."""
        missing_keys = [
            "Maximum mass of combination",
            "Working principle",
            "Direct injection",
            "Pure electric",
            "Hybrid [electric] vehicle",
            "Clutch"
        ]

        # Crea nuevas filas solo para las claves que faltan
        missing_rows = [
            {"Key": key, "Value": "None"}
            for key in missing_keys if key not in df["Key"].values
        ]

        if missing_rows:
            df = pd.concat([df, pd.DataFrame(missing_rows)], ignore_index=True)

        return df


    def _process_trailer_masses(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa y combina la información de masas del remolque, tomando el máximo valor de cada par."""
        if "Braked trailer" in df["Key"].values and "Unbraked trailer" in df["Key"].values:
            # Obtiene los valores originales
            braked = df[df["Key"] == "Braked trailer"]["Value"].values[0]      # ej: "600 / 1000"
            unbraked = df[df["Key"] == "Unbraked trailer"]["Value"].values[0]  # ej: "450 / 1222"

            # Obtiene el máximo de cada par
            braked_max = self._get_max_from_pair(braked, '/')     # resultado: 1000
            unbraked_max = self._get_max_from_pair(unbraked, '/') # resultado: 1222

            # Elimina las filas originales
            df = df[~df["Key"].isin(["Braked trailer", "Unbraked trailer"])]

            # Crea una nueva fila con los máximos
            new_row = pd.DataFrame({
                "Key": ["Maximum mass of trailer – braked / unbraked"],
                "Value": [f"{braked_max}/{unbraked_max}"]  # Resultado: "1000 / 1222"
            })

            df = pd.concat([df, new_row], ignore_index=True)

        return df
    
    def _process_Rear_overhang(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa y combina la información de Rear overhang"""
        if "Rear overhang" in df["Key"].values: 
            rear = df[df["Key"] == "Rear overhang"]["Value"].values[0]      
            
            # elimina el primer "/" de "/ 869 - 869"
            rear = rear.split("/")[1]

            # guarda el nuevo valor
            df.loc[df["Key"] == "Rear overhang", "Value"] = rear
            

        return df

    #def Maximum vertical load at the coupling point for a trailer
    def _process_maximum_vertical_load(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa y transforma Maximum vertical load at the coupling point for a trailer"""
        if "Support load" in df["Key"].values:
            # Obtiene los valores originales
            vertical_values = df[df["Key"] == "Support load"]["Value"].values[0]      # ej: "600 / 1000"

            # Obtiene el máximo de cada par
            vertical_value_max = self._get_max_from_pair(vertical_values, '/')     # resultado: 1000

            # Elimina las filas originales
            df = df[~df["Key"].isin(["Support load"])]

            # Crea una nueva fila con los máximos
            new_row = pd.DataFrame({
                "Key": ["Maximum vertical load at the coupling point for a trailer"],
                "Value": [f"{vertical_value_max}"]  # Resultado: "1000 / 1222"
            })

            df = pd.concat([df, new_row], ignore_index=True)

        return df

    def _process_max_power(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa y combina la información la capacidad maxima."""
        if "Maximum net power" in df["Key"].values:
            power = df[df["Key"] == "Maximum net power"]["Value"].values[0]

            num1 = float(self._get_value_slash(power, 0))
            num2 = float(self._get_value_slash(power, 1))

            num1 = int(num1) if num1.is_integer() else num1
            num2 = int(num2) if num2.is_integer() else num2


            new_value = f"{num1}/{num2}"


            df.loc[df["Key"] == "Maximum net power", "Value"] = new_value

        return df




    def _process_mass_distribution(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa y combina la información de distribución de masas."""
        key1 = "Distribution of this mass among the axles - 1"
        key2 = "Distribution of this mass among the axles - 2"

        if key1 in df["Key"].values and key2 in df["Key"].values:
            mass1_pair = df[df["Key"] == key1]["Value"].values[0]
            mass2_pair = df[df["Key"] == key2]["Value"].values[0]

            mass1 = self._get_max_from_pair(mass1_pair, '-')
            mass2 = self._get_max_from_pair(mass2_pair, '-')

            df = df[~df["Key"].isin([key1, key2])]

            new_row_1 = pd.DataFrame({
                "Key": ["Distribution of this mass among the axles – 1 / 2"],
                "Value": [f"{mass1}/{mass2}"]
            })
            df = pd.concat([df, new_row_1], ignore_index=True)

            new_row_2 = pd.DataFrame({
                "Key": ["Technically permissible max mass on each axle – 1 / 2"],
                "Value": [f"{mass1}/{mass2}"]
            })
            df = pd.concat([df, new_row_2], ignore_index=True)

        return df

    def _process_engine_manufacturer(self, df: pd.DataFrame) -> pd.DataFrame:
      """Obtiene la marca del motor"""
      if "Brand / Type" in df["Key"].values:
        brandType = df[df["Key"] == "Brand / Type"]["Value"].values[0]

        brand = self._get_value_slash(brandType, 0)

        parts = [part.strip() for part in brandType.split("/")]
        type_Name = " / ".join(parts[1:])

        new_row = pd.DataFrame({
            "Key": ["Engine manufacturer"],
            "Value": [f"{brand}"]
        })
        df = pd.concat([df, new_row], ignore_index=True)

        new_row2 = pd.DataFrame({
              "Key": ["Engine code as marked on the enginee"],
              "Value": [f"{type_Name}"]
          })
        df = pd.concat([df, new_row2], ignore_index=True)

        df = df[~df["Key"].isin(["Brand / Type"])]
      return df


    def _process_transmission(self, df: pd.DataFrame) -> pd.DataFrame:
      """Procesa la transmission"""
      if "Transmission/IA" in df["Key"].values:
        transmission = df[df["Key"] == "Transmission/IA"]["Value"].values[0]

        transmission_value = self._get_value_slash(transmission, 0)

        if "m" in transmission_value:
          Geabox = "Manual"
        new_row = pd.DataFrame({
            "Key": ["Gearbox"],
            "Value": [f"{Geabox}"]
            })
        df = pd.concat([df, new_row], ignore_index=True)


        match = re.search(r'\d+', transmission_value)
        if match:
            Gear = int(match.group())  # Extrae el número como entero
            new_row_gear = pd.DataFrame({
                "Key": ["Gear"],
                "Value": [f"{Gear}"]
            })
        df = pd.concat([df, new_row_gear], ignore_index=True)

      return df


    def _process_drive_ratio(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa la drive ratio"""
        if "Transmission/IA" in df["Key"].values:
          drive = df[df["Key"] == "Transmission/IA"]["Value"].values[0]

          drive_value = self._get_value_slash(drive, 1)

          new_row = pd.DataFrame({
              "Key": ["Final drive ratio"],
              "Value": [f"{drive_value}"]
              })
          df = pd.concat([df, new_row], ignore_index=True)
          df = df[~df["Key"].isin(["Transmission/IA"])]

        return df

    def _sort_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ordena y limpia el DataFrame final."""
        df["Key"] = pd.Categorical(
            df["Key"],
            categories=self.config.ordered_keys,
            ordered=True
        )
        return df.sort_values("Key").reset_index(drop=True)

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
DEFAULT_CONFIG_2 = VehicleDataConfig(
    column_mapping={
        "14 Axles/Wheels": "Number of axles / wheels",
        "21 Powered axles": "Powered axles",
        "44 Distance axis 1-2": "Wheelbase",
        "47 Track Axis 1": "Axle(s) track – 1",
        "48 Track Axis 2": "Axle(s) track – 2",
        "40 Length": "Length",
        "41 Width": "Width",
        "42 Height": "Height",
        "43 Überhange f/b": "Rear overhang",
        "52 Netweight": "Mass of the vehicle with bodywork in running order",
        "Wet Weigh Kg": "Technically permissible maximum laden mass",
        "54 Axle guarantees v.": "Distribution of this mass among the axles - 1",
        "54 Axle guarantees b.": "Distribution of this mass among the axles - 2",
        "55 Roof load": "Maximum permissible roof load",
        "57 braked": "Braked trailer",
        "58 unbraked": "Unbraked trailer",
        "67 Support load": "Support load",
        "25 Brand / Type": "Brand / Type",
        "27 Capacity:": "Capacity",
        "Cylinder": "Number and arrangement of cylinders",
        "Fuel code": "Fuel",
        "28 Power / n": "Maximum net power",
        "18 Transmission/IA": "Transmission/IA",

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

