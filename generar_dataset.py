import os
import pandas as pd
import numpy as np

# Configurar semilla de aleatoriedad para reproducibilidad
np.random.seed(42)

# ==========================================
# 1. CATÁLOGO DE PRODUCTOS Y PRECIOS (MXN)
# ==========================================
PRODUCT_CATALOG = {
    'Hamburguesa Clásica': {'Categoria': 'Alimentos', 'Precio_Unitario': 155.00},
    'Tacos de Arrachera': {'Categoria': 'Alimentos', 'Precio_Unitario': 185.00},
    'Ensalada César': {'Categoria': 'Alimentos', 'Precio_Unitario': 120.00},
    'Pizza Peperoni': {'Categoria': 'Alimentos', 'Precio_Unitario': 145.00},
    'Club Sandwich': {'Categoria': 'Alimentos', 'Precio_Unitario': 135.00},
    'Refresco 355ml': {'Categoria': 'Bebidas', 'Precio_Unitario': 35.00},
    'Cerveza Nacional': {'Categoria': 'Bebidas', 'Precio_Unitario': 50.00},
    'Cerveza Artesanal': {'Categoria': 'Bebidas', 'Precio_Unitario': 85.00},
    'Limonada': {'Categoria': 'Bebidas', 'Precio_Unitario': 45.00},
    'Pastel de Chocolate': {'Categoria': 'Postres', 'Precio_Unitario': 90.00},
    'Flan Casero': {'Categoria': 'Postres', 'Precio_Unitario': 65.00},
    'Helado de Vainilla': {'Categoria': 'Postres', 'Precio_Unitario': 55.00}
}

# Probabilidades de compra asociadas a cada producto (suman 1.0)
PRODUCT_WEIGHTS = {
    'Hamburguesa Clásica': 0.15,
    'Tacos de Arrachera': 0.15,
    'Ensalada César': 0.08,
    'Pizza Peperoni': 0.10,
    'Club Sandwich': 0.07,
    'Refresco 355ml': 0.18,
    'Cerveza Nacional': 0.12,
    'Cerveza Artesanal': 0.05,
    'Limonada': 0.05,
    'Pastel de Chocolate': 0.02,
    'Flan Casero': 0.02,
    'Helado de Vainilla': 0.01
}

# ==========================================
# 2. GENERACIÓN DE FECHAS CON ESTACIONALIDAD
# ==========================================
def generate_dates_with_seasonality(n_rows):
    # Rango solicitado: 1 de enero de 2026 al 30 de junio de 2026
    start_date = pd.to_datetime('2026-01-01 00:00:00')
    end_date = pd.to_datetime('2026-06-30 23:59:59')
    
    total_seconds = int((end_date - start_date).total_seconds())
    
    # Generamos un pool amplio de candidatos para hacer un muestreo ponderado sin repetición
    pool_size = n_rows * 20
    random_offsets = np.random.randint(0, total_seconds, size=pool_size)
    candidate_dates = start_date + pd.to_timedelta(random_offsets, unit='s')
    
    df_temp = pd.DataFrame({'Fecha_Hora': candidate_dates})
    df_temp['weekday'] = df_temp['Fecha_Hora'].dt.weekday
    df_temp['hour'] = df_temp['Fecha_Hora'].dt.hour
    
    # Pesos basados en un patrón realista de consumo en un restaurante:
    # - Horas de comida (12:00 - 15:59): Peso alto (3.0)
    # - Tarde / lull (16:00 - 18:59): Peso bajo (1.0)
    # - Horas de cena (19:00 - 22:59): Peso máximo (4.0)
    # - Cierre / noche (23:00 - 23:59): Peso medio-bajo (1.5)
    # - Fuera de servicio (00:00 - 11:59): Peso extremadamente bajo (0.05) para registrar raras excepciones
    def get_base_weight(hour):
        if 12 <= hour < 16:
            return 3.0
        elif 16 <= hour < 19:
            return 1.0
        elif 19 <= hour < 23:
            return 4.0
        elif hour == 23:
            return 1.5
        else:
            return 0.05
            
    df_temp['weight'] = df_temp['hour'].apply(get_base_weight)
    
    # Condición de Estacionalidad: Duplicar ventas los viernes (4) y sábados (5) por la noche
    # Se consideran las horas de la noche entre las 19:00 y las 23:00 (es decir, horas 19, 20, 21, 22)
    weekend_evening = (df_temp['weekday'].isin([4, 5])) & (df_temp['hour'].isin([19, 20, 21, 22]))
    df_temp.loc[weekend_evening, 'weight'] *= 2.0
    
    # Normalización de probabilidades
    probabilities = df_temp['weight'] / df_temp['weight'].sum()
    
    # Selección de los índices de forma aleatoria sin reemplazo para asegurar marcas de tiempo únicas
    sampled_indices = np.random.choice(df_temp.index, size=n_rows, replace=False, p=probabilities)
    sampled_dates = df_temp.loc[sampled_indices, 'Fecha_Hora'].copy()
    
    # Se devuelven las fechas ordenadas cronológicamente como en un POS real
    return sorted(sampled_dates)

# ==========================================
# 3. CONSTRUCCIÓN DEL DATASET
# ==========================================
N_ROWS = 2500

# Generar marcas de tiempo
dates = generate_dates_with_seasonality(N_ROWS)

# Generar IDs de transacción consecutivos de forma alfanumérica (TXN0001 a TXN2500)
ids = [f"TXN{i:04d}" for i in range(1, N_ROWS + 1)]

# Muestreo de productos según su peso en la carta
products_sampled = np.random.choice(
    list(PRODUCT_WEIGHTS.keys()), 
    size=N_ROWS, 
    p=list(PRODUCT_WEIGHTS.values())
)

# Muestreo de cantidades con una distribución de probabilidad lógica para un restaurante
quantities = np.random.choice(
    [1, 2, 3, 4, 5], 
    size=N_ROWS, 
    p=[0.50, 0.30, 0.12, 0.05, 0.03]
)

# Muestreo de métodos de pago con su distribución comercial
payment_methods = np.random.choice(
    ['Efectivo', 'Tarjeta de Crédito', 'Tarjeta de Débito', 'Transferencia'],
    size=N_ROWS,
    p=[0.40, 0.30, 0.25, 0.05]
)

# Instanciar el DataFrame base
df = pd.DataFrame({
    'ID_Transaccion': ids,
    'Fecha_Hora': dates,
    'Producto': products_sampled,
    'Cantidad': quantities,
    'Metodo_Pago': payment_methods
})

# Mapeo de categorías y precios unitarios basados en el diccionario
df['Categoria'] = df['Producto'].apply(lambda x: PRODUCT_CATALOG[x]['Categoria'])
df['Precio_Unitario'] = df['Producto'].apply(lambda x: PRODUCT_CATALOG[x]['Precio_Unitario'])

# Asegurar orden exacto de las columnas obligatorias solicitadas
df = df[['ID_Transaccion', 'Fecha_Hora', 'Producto', 'Categoria', 'Cantidad', 'Precio_Unitario', 'Metodo_Pago']]

# ==========================================
# 4. INTRODUCCIÓN DE ANOMALÍAS (CRÍTICO)
# ==========================================

# Anomalía A: 5% de registros con valores nulos (NaN) en Metodo_Pago
# 5% de 2,500 = exactamente 125 celdas vacías
nan_payment_indices = np.random.choice(df.index, size=int(N_ROWS * 0.05), replace=False)
df.loc[nan_payment_indices, 'Metodo_Pago'] = np.nan

# Anomalía B: 3% de fechas escritas en formato de texto irregular
# 3% de 2,500 = exactamente 75 fechas sucias
# Convertimos primero la columna a texto con formato estándar ISO
df['Fecha_Hora'] = df['Fecha_Hora'].dt.strftime('%Y-%m-%d %H:%M:%S')

def apply_irregular_date_format(date_str, style_idx):
    dt = pd.to_datetime(date_str)
    if style_idx == 0:
        return dt.strftime('%Y/%m-%d')          # Formato YYYY/MM-DD (e.g., '2026/05-12')
    elif style_idx == 1:
        return dt.strftime('%d-%m-%Y')          # Formato DD-MM-YYYY (e.g., '15-04-2026')
    elif style_idx == 2:
        return dt.strftime('%d/%m/%Y %H:%M')    # Formato DD/MM/YYYY HH:MM (e.g., '15/04/2026 21:05')
    elif style_idx == 3:
        return dt.strftime('%Y.%m.%d')          # Formato YYYY.MM.DD (e.g., '2026.02.28')
    else:
        return dt.strftime('%d-%m-%y %H:%M:%S') # Formato DD-MM-YY de dos dígitos (e.g., '08-03-26 19:12:30')

irregular_date_indices = np.random.choice(df.index, size=int(N_ROWS * 0.03), replace=False)
for idx in irregular_date_indices:
    style = np.random.randint(0, 5)
    df.at[idx, 'Fecha_Hora'] = apply_irregular_date_format(df.at[idx, 'Fecha_Hora'], style)

# ==========================================
# 5. EXPORTACIÓN DEL ARCHIVO
# ==========================================
output_file = 'ventas_historicas_sucio.xlsx'
df.to_excel(output_file, index=False)

print("--------------------------------------------------")
print("PROCESO TERMINADO CON ÉXITO")
print(f"Archivo generado: {output_file}")
print(f"Dimensiones del set de datos: {df.shape}")
print(f"Nulos en Metodo_Pago: {df['Metodo_Pago'].isna().sum()} ({df['Metodo_Pago'].isna().sum() / N_ROWS * 100}%)")
print(f"Fechas sucias aplicadas: {len(irregular_date_indices)} ({len(irregular_date_indices) / N_ROWS * 100}%)")
print("--------------------------------------------------")
