import pandas as pd

# Lista de nombres
nombres = [
    "Number of axles / wheels:",
    "Powered axles:",
    "Wheelbase :(mm)",  
    "Axle(s) track 1/ 2: (mm)",
    "Length:(mm)",
    "Width:(mm)",
    "Height:(mm)",
    "Rear overhang:(mm)",
    "Mass of the vehicle with bodywork in running order:(kg)",
    "Technically permissable maximum laden mass:(kg)",
    "Distribution of this mass among the axles – 1 / 2:(kg)",
    "Technically perm. max mass on each axle – 1 / 2:(kg)",
    "Maximum permissible roof load:(kg)",
    "Maximum mass of trailer – braked / unbraked:(kg)",
    "Maximum mass of combination:(kg)",
    "Maximum vertical load at the coupling point for a trailer:(kg)",
    "Engine manufacturer:",
    "Engine code as marked on the engine:",
    "Working principle:",
    "Direct injection:",
    "Pure electric:",
    "Hybrid [electric] vehicle:",
    "Number and arrangement of cylinders:",
    "Capacity:( cm3)",
    "Fuel:",
    "Maximum net power:( kW/min -1)",
    "Clutch (type):",
    "Gearbox (type):",
    "Gear:"
]

# Generar los códigos B1, B2, ...
codigos = [f"B{i+1}" for i in range(len(nombres))]

# Crear el DataFrame
data = {
    "Nombre": nombres,
    "Codigo": codigos
}

df_planilla = pd.DataFrame(data)



