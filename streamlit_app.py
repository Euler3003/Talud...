import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración inicial de la página
st.set_page_config(
    page_title="Calculador Geotécnico de Taludes",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (Texto forzado a color oscuro para que sea legible)
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #2c3e50; font-weight: 700; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #2980b9; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stMetric b { color: #2c3e50; font-size: 1.1rem; }
    .stMetric p { color: #34495e; margin: 4px 0; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Calculador Geotécnico y Volumétrico de Taludes")
st.markdown("Herramienta interactiva para el diseño geométrico, conversión de unidades y análisis de masas con cuña de apoyo incrustada.")

# ==========================================
# BARRA LATERAL: CONFIGURACIÓN Y ENTRADAS
# ==========================================
st.sidebar.header("⚙️ Configuración Global")

# 1. Selección de Unidades
unidades_dim = st.sidebar.selectbox("Unidades de Dimensión (Geometría):", ["Metros (m)", "Centímetros (cm)"])
unidades_dens = st.sidebar.selectbox("Unidades de Densidad:", ["kg/m³", "g/cm³"])

u_long = "m" if unidades_dim == "Metros (m)" else "cm"
u_dens = "kg/m³" if unidades_dens == "kg/m³" else "g/cm³"

# Factores de conversión hacia el Sistema Internacional (m, kg) para cálculo interno
to_meters = 1.0 if u_long == "m" else 0.01
to_kg_m3 = 1.0 if u_dens == "kg/m³" else 1000.0

st.sidebar.markdown("---")
st.sidebar.header("📐 Geometría Principal")

# Inputs principales adaptados a la unidad elegida
base_mayor_input = st.sidebar.number_input(f"Base Mayor del Trapecio (B) [{u_long}]", min_value=1.0, value=12.0 if u_long == "m" else 1200.0, step=0.5)
altura_trap_input = st.sidebar.number_input(f"Altura del Trapecio [{u_long}]", min_value=0.5, value=4.0 if u_long == "m" else 400.0, step=0.1)
pendiente_izq = st.sidebar.number_input("Pendiente Izquierda (H:1V)", min_value=0.1, value=1.2, step=0.1)
pendiente_der = st.sidebar.number_input("Pendiente Derecha (H:1V)", min_value=0.1, value=1.2, step=0.1)
altura_rect_input = st.sidebar.number_input(f"Altura del Rectángulo Inferior [{u_long}]", min_value=0.1, value=3.0 if u_long == "m" else 300.0, step=0.1)
profundidad_input = st.sidebar.number_input(f"Espesor / Profundidad total [{u_long}]", min_value=0.1, value=50.0 if u_long == "m" else 5000.0, step=1.0)

# Validación de Base Menor matemática
base_menor_m = (base_mayor_input * to_meters) - (pendiente_izq * altura_trap_input * to_meters) - (pendiente_der * altura_trap_input * to_meters)

if base_menor_m <= 0:
    st.error(f"❌ Error Geométrico: Las pendientes y la altura superan la Base Mayor. Incrementa B o reduce las pendientes.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.header("🔺 Configuración de la Cuña de Apoyo")
lado_cuna = st.sidebar.selectbox("Lado de incrustación de la Cuña:", ["Izquierda", "Derecha"])

# La altura de la cuña debe ser menor o igual a la del trapecio
altura_cuna_input = st.sidebar.number_input(
    f"Altura de la Cuña (Menor a la del trapecio) [{u_long}]", 
    min_value=0.0, 
    max_value=float(altura_trap_input), 
    value=float(altura_trap_input * 0.4), 
    step=0.1
)

st.sidebar.markdown("---")
st.sidebar.header("🪨 Propiedades Geotécnicas")
densidad_seca_input = st.sidebar.number_input(f"Densidad Seca Global (γd) [{u_dens}]", min_value=1.0, value=1600.0 if u_dens == "kg/m³" else 1.6, step=10.0 if u_dens == "kg/m³" else 0.1)
humedad_bloque_A = st.sidebar.number_input("Humedad Bloque A (Rectángulo + Cuña) [%]", min_value=0.0, max_value=100.0, value=12.0, step=0.5)
humedad_bloque_B = st.sidebar.number_input("Humedad Bloque B (Trapecio - Cuña) [%]", min_value=0.0, max_value=100.0, value=8.0, step=0.5)

# ==========================================
# PROCESAMIENTO Y CÁLCULOS (S.I. INTERNO)
# ==========================================
B = base_mayor_input * to_meters
h_trap = altura_trap_input * to_meters
h_rect = altura_rect_input * to_meters
L = profundidad_input * to_meters
h_cuna = altura_cuna_input * to_meters
γ_d = densidad_seca_input * to_kg_m3

# Base menor calculada en metros
b = B - (pendiente_izq * h_trap) - (pendiente_der * h_trap)

# Geometría de la cuña (Misma pendiente que el lado elegido)
m_elegida = pendiente_izq if lado_cuna == "Izquierda" else pendiente_der
b_cuna = m_elegida * h_cuna

# Áreas individuales (m²)
area_rectangulo_total = B * h_rect
area_trapecio_total = ((B + b) / 2) * h_trap
area_cuna = 0.5 * b_cuna * h_cuna

# División solicitada de bloques (Resta matemática perfecta)
area_bloque_A = area_rectangulo_total + area_cuna
area_bloque_B = area_trapecio_total - area_cuna

# Volúmenes (m³)
vol_bloque_A = area_bloque_A * L
vol_bloque_B = area_bloque_B * L
vol_total = vol_bloque_A + vol_bloque_B

# Densidades Húmedas (kg/m³) e hidratación
γ_h_A = γ_d * (1 + (humedad_bloque_A / 100.0))
γ_h_B = γ_d * (1 + (humedad_bloque_B / 100.0))

# Masas Totales Húmedas en Toneladas Métricas
masa_A_ton = (vol_bloque_A * γ_h_A) / 1000.0
masa_B_ton = (vol_bloque_B * γ_h_B) / 1000.0
masa_total_ton = masa_A_ton + masa_B_ton

# Volúmenes en la unidad visual solicitada por el usuario
v_factor = 1.0 if u_long == "m" else 1e6 # m³ a cm³
u_vol = "m³" if u_long == "m" else "cm³"
u_area = "m²" if u_long == "m" else "cm²"

# Display de Alerta Informativa de dimensiones de salida
st.info(f"💡 Mostrando resultados en **{u_long}** / **{u_area}** / **{u_vol}** según tu selección actual.")

# ==========================================
# RENDERIZADO DE MÉTRICAS / RESULTADOS (CORREGIDO COLOR)
# ==========================================
st.subheader("📋 Resultados del Análisis Geotécnico - Volumétrico")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class='stMetric'>
    <b>Bloque A (Rectángulo + Cuña)</b>
    <p>Área: {area_bloque_A / (to_meters**2):,.2f} {u_area}</p>
    <p>Volumen: {vol_bloque_A * v_factor:,.2f} {u_vol}</p>
    <p>Masa Húmeda: {masa_A_ton:,.2f} Ton</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class='stMetric'>
    <b>Bloque B (Trapecio - Cuña)</b>
    <p>Área: {area_bloque_B / (to_meters**2):,.2f} {u_area}</p>
    <p>Volumen: {vol_bloque_B * v_factor:,.2f} {u_vol}</p>
    <p>Masa Húmeda: {masa_B_ton:,.2f} Ton</p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class='stMetric' style='border-left-color: #27ae60;'>
    <b>Estructura Combinada Total</b>
    <p>Área Total: {(area_rectangulo_total + area_trapecio_total) / (to_meters**2):,.2f} {u_area}</p>
    <p>Volumen Total: {vol_total * v_factor:,.2f} {u_vol}</p>
    <p>Masa Húmeda Total: {masa_total_ton:,.2f} Ton</p>
    </div>""", unsafe_allow_html=True)

# ==========================================
# GRÁFICA INTERACTIVA CON PLOTLY (COORDENADAS INCRUSTADAS CORREGIDAS)
# ==========================================
st.subheader("📐 Gráfico de la Sección Transversal (Escala Real 1:1)")

# Convertimos las variables numéricas a la escala visual seleccionada para el gráfico (m o cm)
B_v = base_mayor_input
h_trap_v = altura_trap_input
h_rect_v = altura_rect_input
h_cuna_v = altura_cuna_input
b_cuna_v = m_elegida * h_cuna_v

# Coordenadas del Rectángulo Inferior
x_rect = [0, B_v, B_v, 0, 0]
y_rect = [0, 0, h_rect_v, h_rect_v, 0]

# Coordenadas corregidas hacia adentro
if lado_cuna == "Izquierda":
    # El talud empieza en (0, h_rect_v) y se mueve a la derecha. 
    # El triángulo inicia en (0, h_rect_v), avanza en X la distancia b_cuna_v y sube en Y la altura h_cuna_v.
    # El tercer punto baja verticalmente hasta tocar el techo del rectángulo de nuevo.
    x_cuna = [0, b_cuna_v, b_cuna_v, 0]
    y_cuna = [h_rect_v, h_rect_v + h_cuna_v, h_rect_v, h_rect_v]
    
    # El trapecio remanente (Bloque B) pierde este triángulo incrustado en su esquina inferior izquierda
    x_trap_remanente = [b_cuna_v, B_v, B_v - (pendiente_der * h_trap_v), pendiente_izq * h_trap_v, b_cuna_v, b_cuna_v]
    y_trap_remanente = [h_rect_v, h_rect_v, h_rect_v + h_trap_v, h_rect_v + h_trap_v, h_rect_v + h_cuna_v, h_rect_v]
else:
    # Lado Derecho: El talud termina en (B_v, h_rect_v) y se mueve hacia adentro (izquierda)
    x_cuna = [B_v, B_v - b_cuna_v, B_v - b_cuna_v, B_v]
    y_cuna = [h_rect_v, h_rect_v + h_cuna_v, h_rect_v, h_rect_v]
    
    # El trapecio remanente pierde su esquina inferior derecha
    x_trap_remanente = [0, B_v - b_cuna_v, B_v - b_cuna_v, B_v - (pendiente_der * h_trap_v), pendiente_izq * h_trap_v, 0]
    y_trap_remanente = [h_rect_v, h_rect_v, h_rect_v + h_cuna_v, h_rect_v + h_trap_v, h_rect_v + h_trap_v, h_rect_v]

fig = go.Figure()

# 1. Capa del Rectángulo Inferior (Bloque A - Parte 1)
fig.add_trace(go.Scatter(
    x=x_rect, y=y_rect, fill="toself",
    fillcolor="rgba(52, 152, 219, 0.35)", line=dict(color="#2980b9", width=2),
    name="Rectángulo Inferior (Bloque A)", mode="lines"
))

# 2. Capa del Trapecio Remanente Reducido (Bloque B)
fig.add_trace(go.Scatter(
    x=x_trap_remanente, y=y_trap_remanente, fill="toself",
    fillcolor="rgba(230, 126, 34, 0.4)", line=dict(color="#d35400", width=2),
    name="Trapecio Remanente (Bloque B)", mode="lines"
))

# 3. Capa de la Cuña de Apoyo Incrustada (Bloque A - Parte 2) - Dibujada encima para ver la superposición
fig.add_trace(go.Scatter(
    x=x_cuna, y=y_cuna, fill="toself",
    fillcolor="rgba(46, 204, 113, 0.7)", line=dict(color="#27ae60", width=2.5, dash="dash"),
    name="Cuña de Apoyo Incrustada (Bloque A)", mode="lines"
))

# Anotación para la base del terreno (B)
fig.add_annotation(
    x=B_v/2, y=-0.06 * (h_rect_v + h_trap_v),
    text=f"<b>B = {base_mayor_input:,.2f} {u_long}</b>",
    showarrow=False, font=dict(size=12, color="#2980b9")
)

# Configuraciones del Layout para forzar Relación de Aspecto Física real 1:1
fig.update_layout(
    xaxis=dict(title=f"Extensión Horizontal ({u_long})", gridcolor="rgba(128,128,128,0.15)", zeroline=False),
    yaxis=dict(title=f"Elevación Vertical ({u_long})", gridcolor="rgba(128,128,128,0.15)", scaleanchor="x", scaleratio=1, zeroline=False),
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    margin=dict(l=40, r=40, t=40, b=50),
    hovermode="closest"
)

# Dibujar gráfico en Streamlit
st.plotly_chart(fig, use_container_width=True)
