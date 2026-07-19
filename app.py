import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.io as pio

# Configuración de gráficas Plotly
pio.templates.default = "plotly_white"
valora_colors = ['#112A46', '#8B9CA7', '#1f77b4', '#d62728']
pio.templates["valora"] = pio.templates["plotly_white"]
pio.templates["valora"].layout.colorway = valora_colors
pio.templates.default = "valora"

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==============================================================================
st.set_page_config(
    page_title="Valora+ | Inteligencia Comercial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Integración de Identidad Corporativa
st.sidebar.image("logo_valora.svg", use_container_width=True)
st.sidebar.markdown("---")

# Estilizado personalizado para interfaz premium
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

/* Personalización del contenedor de la aplicación */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 95%;
}

/* Pestañas (Tabs) estilizadas */
div[data-baseweb="tab-list"] {
    background-color: #F0F2F6;
    padding: 8px;
    border-radius: 12px;
    margin-bottom: 20px;
}

div[data-baseweb="tab"] {
    font-family: 'Outfit', 'Inter', sans-serif;
    color: #112A46;
    font-weight: 600;
    padding: 10px 20px;
    border-radius: 8px;
    transition: all 0.3s ease;
}

div[data-baseweb="tab"]:hover {
    color: #112A46;
    background-color: rgba(17, 42, 70, 0.05);
}

div[aria-selected="true"] {
    color: #112A46 !important;
    background-color: rgba(17, 42, 70, 0.1) !important;
}

/* Sobrescribir tipografía y pesos equilibrados */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', 'Inter', sans-serif;
    font-weight: 500;
    color: #112A46;
}
h1, h2, h3, h4, h5, h6 {
    font-weight: 700;
    color: #112A46;
}

/* Ocultar elementos por defecto de Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Helper para tarjetas KPI ejecutivas en HTML
def make_kpi_card(title, value, subtitle, border_color="#112A46"):
    return f"""
    <div style="
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 20px 25px;
        color: #112A46;
        border-left: 5px solid {border_color};
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
        border-top: 1px solid #F0F2F6;
        border-right: 1px solid #F0F2F6;
        border-bottom: 1px solid #F0F2F6;
        margin-bottom: 15px;
    ">
        <p style="margin: 0; font-size: 0.85rem; color: #8B9CA7; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">{title}</p>
        <h2 style="margin: 8px 0 2px 0; font-size: 2.2rem; font-weight: 800; color: #112A46; line-height: 1;">{value}</h2>
        <p style="margin: 0; font-size: 0.8rem; color: #8B9CA7; font-weight: 400; opacity: 0.85;">{subtitle}</p>
    </div>
    """

# Helper para tarjetas de recomendación prescriptiva (Receta de Acción)
def make_recommendation_card(title, value, recommendation, border_color="#112A46", icon=""):
    icon_html = f'<span style="font-size: 1.25rem;">{icon}</span>' if icon else ''
    return f"""
    <div style="
        background-color: #FFFFFF;
        border: 1px solid #F0F2F6;
        border-top: 5px solid {border_color};
        padding: 22px;
        border-radius: 8px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 15px;
    ">
        <div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                {icon_html}
                <p style="margin: 0; font-size: 0.85rem; color: #8B9CA7; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600;">{title}</p>
            </div>
            <h3 style="margin: 8px 0; font-size: 1.25rem; font-weight: 700; color: #112A46; line-height: 1.2;">{value}</h3>
        </div>
        <p style="margin: 10px 0 0 0; font-size: 0.85rem; color: #112A46; line-height: 1.4; border-top: 1px solid #F0F2F6; padding-top: 10px;">
            {recommendation}
        </p>
    </div>
    """

# ==============================================================================
# PIPELINE ETL (EXTRACCIÓN, TRANSFORMACIÓN Y LIMPIEZA)
# ==============================================================================
@st.cache_data
def load_and_clean_data(file_path):
    # Cargar el archivo sucio original de Excel
    df = pd.read_excel(file_path)
    
    # 1. Limpieza de Fecha_Hora: Forzar la conversión a datetime (manejando formatos mezclados)
    df['Fecha_Hora'] = pd.to_datetime(df['Fecha_Hora'], format='mixed', errors='coerce')
    
    # 2. Rellenado de nulos en Metodo_Pago con la etiqueta 'No Registrado'
    df['Metodo_Pago'] = df['Metodo_Pago'].fillna("No Registrado")
    
    # 3. Creación de columna Total_Venta (Cantidad * Precio_Unitario)
    df['Total_Venta'] = df['Cantidad'] * df['Precio_Unitario']
    
    # 4. Extraer Día de la Semana en español
    weekday_map = {
        0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
        4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
    }
    df['Dia_Semana'] = df['Fecha_Hora'].dt.weekday.map(weekday_map)
    
    # Ordenar categóricamente los días para graficarlos en orden cronológico correcto
    ordered_days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    df['Dia_Semana'] = pd.Categorical(df['Dia_Semana'], categories=ordered_days, ordered=True)
    
    return df

# Validar existencia del archivo de datos
data_file = 'ventas_historicas_sucio.xlsx'
if not os.path.exists(data_file):
    st.error(f"❌ El archivo '{data_file}' no se encuentra en el directorio actual. Por favor, ejecuta primero 'generar_dataset.py'.")
    st.stop()

# Ejecutar el Pipeline ETL
df_clean = load_and_clean_data(data_file)

# Filtro interactivo de Categoria
categories_list = ["Todas"] + list(df_clean['Categoria'].unique())
selected_category = st.sidebar.selectbox(
    "Selecciona una Categoría:",
    options=categories_list,
    index=0
)

# Aplicación del filtro al dataset
if selected_category != "Todas":
    df_filtered = df_clean[df_clean['Categoria'] == selected_category]
else:
    df_filtered = df_clean

# Mensaje de ayuda en el sidebar
st.sidebar.markdown(f"""
<div style="
    background-color: rgba(17, 42, 70, 0.03); 
    border: 1px solid #F0F2F6; 
    padding: 15px; 
    border-radius: 8px; 
    margin-top: 30px;
">
    <p style="margin: 0; font-size: 0.8rem; color: #112A46;">
        <b>Tip de análisis:</b> El filtro seleccionado afecta tanto al <b>Análisis Histórico</b> como a las <b>Proyecciones Futuras</b> en tiempo real.
    </p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# HEADER PRINCIPAL (FRONTEND EXECUTIVE STYLE)
# ==============================================================================
st.markdown("""
<div style="
    background: #FFFFFF;
    border: 1px solid #F0F2F6;
    padding: 25px 30px;
    border-radius: 16px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
    margin-bottom: 30px;
">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 2.3rem; font-weight: 700; color: #112A46;">Valora+ | Inteligencia Comercial</h1>
            <p style="margin: 5px 0 0 0; color: #8B9CA7; font-size: 1.0rem; font-weight: 400;">Módulo Predictivo y Prescriptivo para toma de decisiones</p>
        </div>
        <div style="text-align: right; margin-top: 10px;">
            <span style="background: rgba(17, 42, 70, 0.05); color: #112A46; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; border: 1px solid #F0F2F6;">DATA INTELLIGENCE ONLINE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# DEFINICIÓN DE TABS (PESTAÑAS)
# ==============================================================================
tab_historico, tab_proyeccion = st.tabs(["Análisis Histórico", "Proyección Futura"])

# ------------------------------------------------------------------------------
# PESTAÑA HISTÓRICA
# ------------------------------------------------------------------------------
with tab_historico:
    if df_filtered.empty:
        st.warning("No hay datos históricos disponibles para el filtro seleccionado.")
    else:
        # 1. KPIs
        total_revenue = df_filtered['Total_Venta'].sum()
        total_transactions = df_filtered.shape[0]
        avg_ticket = total_revenue / total_transactions if total_transactions > 0 else 0

        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1:
            st.markdown(make_kpi_card(
                title="Ingreso Bruto Total",
                value=f"${total_revenue:,.2f}",
                subtitle="Monto total acumulado de ventas brutas",
                border_color="#00D1B2"
            ), unsafe_allow_html=True)

        with kpi_col2:
            st.markdown(make_kpi_card(
                title="Transacciones Totales",
                value=f"{total_transactions:,}",
                subtitle="Número de órdenes de servicio registradas",
                border_color="#8A2387"
            ), unsafe_allow_html=True)

        with kpi_col3:
            st.markdown(make_kpi_card(
                title="Ticket Promedio",
                value=f"${avg_ticket:,.2f}",
                subtitle="Consumo promedio estimado por orden",
                border_color="#F64F59"
            ), unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # 2. Gráficas Fila 2
        col_chart_a, col_chart_b = st.columns(2)
        with col_chart_a:
            df_day = df_filtered.groupby('Dia_Semana', observed=False)['Total_Venta'].sum().reset_index()
            fig_day = px.bar(
                df_day,
                x='Dia_Semana',
                y='Total_Venta',
                labels={'Dia_Semana': 'Día', 'Total_Venta': 'Ventas ($ MXN)'},
                title='<b>Ingreso por Día de la Semana</b> (Resalta picos del fin de semana)',
                color='Total_Venta',
                color_continuous_scale=[[0, '#101730'], [0.3, '#00A896'], [1, '#00D1B2']]
            )
            fig_day.update_layout(
                margin=dict(l=20, r=20, t=55, b=20),
                height=360,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#E2E8F0',
                coloraxis_showscale=False,
                title_font_size=16
            )
            fig_day.update_yaxes(gridcolor='rgba(255,255,255,0.05)', title='')
            fig_day.update_xaxes(title='')
            st.plotly_chart(fig_day, use_container_width=True)

        with col_chart_b:
            df_payment = df_filtered.groupby('Metodo_Pago', observed=False).size().reset_index(name='Transacciones')
            fig_payment = px.pie(
                df_payment,
                names='Metodo_Pago',
                values='Transacciones',
                title='<b>Distribución por Método de Pago</b> (Preferencias de clientes)',
                hole=0.45,
                color_discrete_sequence=['#00D1B2', '#8A2387', '#34495e', '#E67E22', '#7f8c8d']
            )
            fig_payment.update_layout(
                margin=dict(l=20, r=20, t=55, b=20),
                height=360,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#E2E8F0',
                title_font_size=16,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_payment, use_container_width=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # 3. Gráficas Fila 3
        col_prod_top, col_prod_bottom = st.columns(2)
        df_prod = df_filtered.groupby('Producto')['Cantidad'].sum().reset_index()

        with col_prod_top:
            df_top = df_prod.nlargest(5, 'Cantidad').sort_values(by='Cantidad', ascending=True)
            fig_top = px.bar(
                df_top,
                x='Cantidad',
                y='Producto',
                orientation='h',
                title='<b>Top 5 Productos Más Vendidos</b> (Productos Estrella)',
                labels={'Cantidad': 'Unidades', 'Producto': ''},
                color='Cantidad',
                color_continuous_scale=[[0, '#351c4a'], [1, '#8A2387']]
            )
            fig_top.update_layout(
                margin=dict(l=20, r=20, t=55, b=20),
                height=320,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#E2E8F0',
                coloraxis_showscale=False,
                title_font_size=16
            )
            fig_top.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
            st.plotly_chart(fig_top, use_container_width=True)

        with col_prod_bottom:
            df_bottom = df_prod.nsmallest(5, 'Cantidad').sort_values(by='Cantidad', ascending=False)
            fig_bottom = px.bar(
                df_bottom,
                x='Cantidad',
                y='Producto',
                orientation='h',
                title='<b>Top 5 Productos Menos Vendidos</b> (Inventario Muerto)',
                labels={'Cantidad': 'Unidades', 'Producto': ''},
                color='Cantidad',
                color_continuous_scale=[[0, '#F64F59'], [1, '#b33939']]
            )
            fig_bottom.update_layout(
                margin=dict(l=20, r=20, t=55, b=20),
                height=320,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#E2E8F0',
                coloraxis_showscale=False,
                title_font_size=16
            )
            fig_bottom.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
            st.plotly_chart(fig_bottom, use_container_width=True)

# ------------------------------------------------------------------------------
# PESTAÑA PROYECCIÓN
# ------------------------------------------------------------------------------
with tab_proyeccion:
    st.markdown("<h2 style='color:#112A46; font-weight:700; margin-top:0; margin-bottom:15px;'>Proyección a 7 Días y Receta de Acción</h2>", unsafe_allow_html=True)
    
    if df_filtered.empty:
        st.warning("No hay datos disponibles para calcular las proyecciones.")
    else:
        # ==========================================
        # LÓGICA DE PRONÓSTICO (FORECASTING)
        # ==========================================
        # 1. Agrupar las ventas históricas por fecha calendario exacta para obtener ingresos diarios
        df_daily_totals = df_filtered.groupby(df_filtered['Fecha_Hora'].dt.date)['Total_Venta'].sum().reset_index()
        df_daily_totals.columns = ['Fecha', 'Total_Venta']
        df_daily_totals['Fecha'] = pd.to_datetime(df_daily_totals['Fecha'])
        
        # 2. Mapear cada fecha al Día de la Semana
        weekday_map = {
            0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
            4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
        }
        df_daily_totals['Dia_Semana'] = df_daily_totals['Fecha'].dt.weekday.map(weekday_map)
        
        # 3. Calcular el promedio de ventas diarias para cada día de la semana
        df_avg_weekday = df_daily_totals.groupby('Dia_Semana', observed=False)['Total_Venta'].mean().reset_index()
        ordered_days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        df_avg_weekday['Dia_Semana'] = pd.Categorical(df_avg_weekday['Dia_Semana'], categories=ordered_days, ordered=True)
        df_avg_weekday = df_avg_weekday.sort_values('Dia_Semana').reset_index(drop=True)
        
        # 4. Generar los 3 escenarios proyectados para la semana
        df_projection = pd.DataFrame({
            'Día': df_avg_weekday['Dia_Semana'],
            'Pesimista (85%)': df_avg_weekday['Total_Venta'] * 0.85,
            'Base (100%)': df_avg_weekday['Total_Venta'],
            'Optimista (115%)': df_avg_weekday['Total_Venta'] * 1.15
        })
        
        # Melt para estructurar formato largo requerido por Plotly Express
        df_melted = df_projection.melt(
            id_vars=['Día'],
            value_vars=['Pesimista (85%)', 'Base (100%)', 'Optimista (115%)'],
            var_name='Escenario',
            value_name='Ingresos'
        )
        
        # Visualizar gráfico de líneas de escenarios
        fig_line = px.line(
            df_melted,
            x='Día',
            y='Ingresos',
            color='Escenario',
            title='<b>Pronóstico de Ingresos Semanales por Escenario</b>',
            labels={'Ingresos': 'Ingresos Proyectados ($ MXN)', 'Día': ''},
            color_discrete_map={
                'Pesimista (85%)': '#F64F59',      # Rojo vibrante
                'Base (100%)': '#85929E',          # Gris-azul elegante
                'Optimista (115%)': '#00D1B2'       # Verde azulado
            },
            markers=True
        )
        
        fig_line.update_layout(
            margin=dict(l=20, r=20, t=55, b=20),
            height=380,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#E2E8F0',
            legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5),
            title_font_size=16
        )
        fig_line.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
        fig_line.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
        
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        
        # ==========================================
        # RECETA DE ACCIÓN (ANALÍTICA PRESCRIPTIVA)
        # ==========================================
        st.markdown("<h3 style='color:#112A46; font-weight:700; margin-bottom:20px;'>Receta de Acción Basada en Datos</h3>", unsafe_allow_html=True)
        
        # Cálculo de Tarjeta 1: Producto más vendido e inventario a 7 días (Escenario Base)
        df_prod_counts = df_filtered.groupby('Producto')['Cantidad'].sum().reset_index()
        if not df_prod_counts.empty:
            top_prod_row = df_prod_counts.nlargest(1, 'Cantidad').iloc[0]
            top_product = top_prod_row['Producto']
            top_prod_total_qty = top_prod_row['Cantidad']
            
            # Calcular semanas en el set de datos para obtener promedio semanal
            min_date = df_filtered['Fecha_Hora'].min()
            max_date = df_filtered['Fecha_Hora'].max()
            total_days = max(1, (max_date - min_date).days)
            total_weeks = total_days / 7.0
            
            avg_weekly_units = top_prod_total_qty / total_weeks
            expected_units_needed = int(np.round(avg_weekly_units))
            
            t1_val = f"{expected_units_needed} unidades"
            t1_desc = f"Asegurar stock de {expected_units_needed} unidades de <b>{top_product}</b> para la próxima semana (Escenario Base)."
        else:
            t1_val = "N/A"
            t1_desc = "No hay datos de productos suficientes para generar una recomendación."
            
        # Cálculo de Tarjeta 2: Producto menos vendido (Prevención de Merma)
        if not df_prod_counts.empty:
            bottom_prod_row = df_prod_counts.nsmallest(1, 'Cantidad').iloc[0]
            bottom_product = bottom_prod_row['Producto']
            
            t2_val = bottom_product
            t2_desc = f"<b>{bottom_product}</b> es el producto de menor rotación. Se recomienda detener su compra o lanzar promoción para liquidar inventario."
        else:
            t2_val = "N/A"
            t2_desc = "No hay datos de productos suficientes para generar una recomendación."
            
        # Cálculo de Tarjeta 3: Optimización de Personal (Día pico)
        if not df_avg_weekday.empty:
            peak_day_row = df_avg_weekday.nlargest(1, 'Total_Venta').iloc[0]
            peak_day = peak_day_row['Dia_Semana']
            
            t3_val = f"Refuerzo el {peak_day}"
            t3_desc = f"El <b>{peak_day}</b> tiene el mayor ingreso proyectado. Reforzar el personal del turno vespertino/nocturno (19:00 - 23:00) para optimizar el servicio."
        else:
            t3_val = "N/A"
            t3_desc = "No hay datos suficientes de comportamiento semanal para generar una recomendación."

        # Desplegar las tarjetas prescriptivas en 3 columnas
        rec_col1, rec_col2, rec_col3 = st.columns(3)
        
        with rec_col1:
            st.markdown(make_recommendation_card(
                title="Inventario Estrella",
                value=t1_val,
                recommendation=t1_desc,
                border_color="#8A2387",  # Púrpura
                icon=""
            ), unsafe_allow_html=True)
            
        with rec_col2:
            st.markdown(make_recommendation_card(
                title="Prevención de Merma",
                value=t2_val,
                recommendation=t2_desc,
                border_color="#F64F59",  # Rojo
                icon=""
            ), unsafe_allow_html=True)
            
        with rec_col3:
            st.markdown(make_recommendation_card(
                title="Optimización de Personal",
                value=t3_val,
                recommendation=t3_desc,
                border_color="#00D1B2",  # Verde azulado
                icon=""
            ), unsafe_allow_html=True)

# Versión 1.1 - Ajuste de Tema Claro y Estandarización de Marca

