import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración inicial de la página
st.set_page_config(
    page_title="Calculador Geotécnico de Taludes",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (Texto forzado a color oscuro para legibilidad)
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #2c3e50; font-weight: 700; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #2980b9; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stMetric b { color: #2c3e50; font-size: 1.1rem; }
    .stMetric p { color: #34495e; margin: 4px 0; font-size: 0.95rem; }
    .dimension-box { background-color: #f1f2f6; padding: 15px; border-radius: 5px; border: 1px solid #dcdde1; margin-top: 10px; }
    .dimension-box ul { margin: 0; padding-left: 20px; color: #2f3640; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Calculador Geotécnico y Volumétrico de Taludes")
st.markdown("Herramienta interactiva para el diseño geométrico, conversión de unidades, selección de metodología y análisis de masas.")

# ==========================================
# BARRA LATERAL: CONFIGURACIÓN Y ENTRADAS
# ==========================================
st.sidebar.header("⚙️ Configuración Global")

# Selección de Metodología (Restaurada)
metodologia = st.sidebar.selectbox(
    "Metodología de Análisis:",
    ["Metodología 1: Porcentaje del Volumen", "Metodología 2: Resta Geométrica (Áreas)"]
)

# Selección de Unidades de Dimensión y Densidad
unidades_dim = st.sidebar.selectbox("Unidades de Dimensión (Geometría):", ["Metros (m)", "Centímetros (cm)"])
unidades_dens = st.sidebar.selectbox("Unidades de Densidad:", ["kg/m³", "g/cm³"])

# Selector de Unidad de Masa para Resultados (Nuevo)
unidad_masa = st.sidebar.selectbox("Mostrar Masa en:", ["Kilogramos (kg)", "Toneladas (Ton)"])

u_long = "m" if unidades_dim == "Metros (m)" else "cm"
u_dens = "kg/m³" if unidades_dens == "kg/m³" else "g/cm³"
u_masa = "kg" if unidad_masa == "Kilogramos (kg)" else "Ton"

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

# Cálculo y validación de Base Menor matemática (Restaurada)
base_menor_calculada = base_mayor_input - (pendiente_izq * altura_trap_input) - (pendiente_der * altura_trap_input)

if base_menor_calculada <= 0:
    st.error(f"❌ Error Geométrico: Las pendientes y la altura superan la Base Mayor. Incrementa B o reduce las pendientes.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.header("🔺 Configuración de la Cuña de Apoyo")
lado_cuna = st.sidebar.selectbox("Lado de incrustación de la Cuña:", ["Izquierda", "Derecha"])

altura_cuna_input = st.sidebar.number_input(
    f"Altura de la Cuña (Menor a la del trapecio) [{u_long}]", 
    min_value=0.0, 
    max_value=float(altura_trap_input), 
    value=float(altura_trap_input * 0.4), 
    step=0.1
)

# Si es Metodología 1, se requiere el porcentaje de volumen
porcentaje_vol_cuna = 0.0
if metodologia.startswith("Metodología 1"):
    porcentaje_vol_cuna = st.sidebar.number_input("Porcentaje de Volumen de la Cuña respecto al Trapecio (%)", min_value=0.0, max_value=100.0, value=15.0, step=0.5)

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
L = depth = profundidad_input * to_meters
h_cuna = altura_cuna_input * to_meters
γ_d = densidad_seca_input * to_kg_m3
b = base_menor_calculada * to_meters

# Geometría de la cuña isósceles respecto a la horizontal acoplada a la pendiente exterior
m_elegida = pendiente_izq if lado_cuna == "Izquierda" else pendiente_der
dx_cuna = m_elegida * h_cuna
b_cuna = 2 * dx_cuna  # Base total de la cuña isósceles

# Áreas del modelo original (m²)
area_rectangulo_total = B * h_rect
area_trapecio_total = ((B + b) / 2) * h_trap

# Definición de áreas y volúmenes según la metodología seleccionada
if metodologia.startswith("Metodología 1"):
    # Metodología 1: Cuña definida como fracción del volumen/área total del trapecio
    area_cuna = area_trapecio_total * (porcentaje_vol_cuna / 100.0)
    area_bloque_A = area_rectangulo_total + area_cuna
    area_bloque_B = area_trapecio_total - area_cuna
else:
    # Metodología 2: Resta geométrica real de la cuña isósceles horizontal incrustada
    area_cuna = 0.5 * b_cuna * h_cuna
    area_bloque_A = area_rectangulo_total + area_cuna
    area_bloque_B = area_trapecio_total - area_cuna

# Volúmenes finales (m³)
vol_bloque_A = area_bloque_A * L
vol_bloque_B = area_bloque_B * L
vol_total = vol_bloque_A + vol_bloque_B

# Densidades Húmedas (kg/m³)
γ_h_A = γ_d * (1 + (humedad_bloque_A / 100.0))
γ_h_B = γ_d * (1 + (humedad_bloque_B / 100.0))

# Masas Totales Húmedas (Cálculo base en kg)
masa_A_kg = vol_bloque_A * γ_h_A
masa_B_kg = vol_bloque_B * γ_h_B
masa_total_kg = masa_A_kg + masa_B_kg

# Conversión para visualización según preferencia del usuario
mass_factor = 1.0 if u_masa == "kg" else 0.001
display_masa_A = masa_A_kg * mass_factor
display_masa_B = masa_B_kg * mass_factor
display_masa_total = masa_total_kg * mass_factor

# Ajuste visual de volúmenes y áreas
v_factor = 1.0 if u_long == "m" else 1e6
u_vol = "m³" if u_long == "m" else "cm³"
u_area = "m²" if u_long == "m" else "cm²"

# Mensaje de información en pantalla
st.info(f"💡 Analizando mediante **{metodologia}**. Unidades de salida: **{u_long}** / **{u_area}** / **{u_vol}** / **{u_masa}**.")

# ==========================================
# RENDERIZADO DE MÉTRICAS / RESULTADOS
# ==========================================
st.subheader("📋 Resultados del Análisis Geotécnico - Volumétrico")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class='stMetric'>
    <b>Bloque A (Rectángulo + Cuña)</b>
    <p>Área: {area_bloque_A / (to_meters**2):,.2f} {u_area}</p>
    <p>Volumen: {vol_bloque_A * v_factor:,.2f} {u_vol}</p>
    <p>Masa Húmeda: {display_masa_A:,.3f} {u_masa}</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class='stMetric'>
    <b>Bloque B (Trapecio - Cuña)</b>
    <p>Área: {area_bloque_B / (to_meters**2):,.2f} {u_area}</p>
    <p>Volumen: {vol_bloque_B * v_factor:,.2f} {u_vol}</p>
    <p>Masa Húmeda: {display_masa_B:,.3f} {u_masa}</p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class='stMetric' style='border-left-color: #27ae60;'>
    <b>Estructura Combinada Total</b>
    <p>Área Total: {(area_rectangulo_total + area_trapecio_total) / (to_meters**2):,.2f} {u_area}</p>
    <p>Volumen Total: {vol_total * v_factor:,.2f} {u_vol}</p>
    <p>Masa Húmeda Total: {display_masa_total:,.3f} {u_masa}</p>
    </div>""", unsafe_allow_html=True)

# ==========================================
# GRÁFICA INTERACTIVA CON PLOTLY
# ==========================================
st.subheader("📐 Gráfico de la Sección Transversal (Escala Real 1:1)")

B_v = base_mayor_input
h_trap_v = altura_trap_input
h_rect_v = altura_rect_input
h_cuna_v = altura_cuna_input
dx_cuna_v = m_elegida * h_cuna_v
b_cuna_v = 2 * dx_cuna_v

# Coordenadas estáticas del Rectángulo Inferior
x_rect = [0, B_v, B_v, 0, 0]
y_rect = [0, 0, h_rect_v, h_rect_v, 0]

# Construcción de las capas visuales respetando la isósceles horizontal
if lado_cuna == "Izquierda":
    x_cuna = [0, dx_cuna_v, b_cuna_v, 0]
    y_cuna = [h_rect_v, h_rect_v + h_cuna_v, h_rect_v, h_rect_v]
    
    x_trap_remanente = [b_cuna_v, B_v, B_v - (pendiente_der * h_trap_v), pendiente_izq * h_trap_v, dx_cuna_v, b_cuna_v]
    y_trap_remanente = [h_rect_v, h_rect_v, h_rect_v + h_trap_v, h_rect_v + h_trap_v, h_rect_v + h_cuna_v, h_rect_v]
else:
    x_cuna = [B_v, B_v - dx_cuna_v, B_v - b_cuna_v, B_v]
    y_cuna = [h_rect_v, h_rect_v + h_cuna_v, h_rect_v, h_rect_v]
    
    x_trap_remanente = [0, B_v - b_cuna_v, B_v - dx_cuna_v, B_v - (pendiente_der * h_trap_v), pendiente_izq * h_trap_v, 0]
    y_trap_remanente = [h_rect_v, h_rect_v, h_rect_v + h_cuna_v, h_rect_v + h_trap_v, h_rect_v + h_trap_v, h_rect_v]

fig = go.Figure()

# 1. Capa del Rectángulo Inferior
fig.add_trace(go.Scatter(
    x=x_rect, y=y_rect, fill="toself",
    fillcolor="rgba(52, 152, 219, 0.35)", line=dict(color="#2980b9", width=2),
    name="Rectángulo Inferior (Bloque A)", mode="lines"
))

# 2. Capa del Trapecio Superior Remanente (Bloque B)
fig.add_trace(go.Scatter(
    x=x_trap_remanente, y=y_trap_remanente, fill="toself",
    fillcolor="rgba(230, 126, 34, 0.4)", line=dict(color="#d35400", width=2),
    name="Trapecio Remanente (Bloque B)", mode="lines"
))

# 3. Capa de la Cuña Isósceles Horizontal (Bloque A)
fig.add_trace(go.Scatter(
    x=x_cuna, y=y_cuna, fill="toself",
    fillcolor="rgba(46, 204, 113, 0.7)", line=dict(color="#27ae60", width=2.5, dash="dash"),
    name="Cuña Isósceles Horizontal (Bloque A)", mode="lines"
))

# Configuraciones de Aspecto Físico Real 1:1
fig.update_layout(
    xaxis=dict(title=f"Extensión Horizontal ({u_long})", gridcolor="rgba(128,128,128,0.15)", zeroline=False),
    yaxis=dict(title=f"Elevación Vertical ({u_long})", gridcolor="rgba(128,128,128,0.15)", scaleanchor="x", scaleratio=1, zeroline=False),
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    margin=dict(l=40, r=40, t=40, b=50),
    hovermode="closest"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# APARTADO DE DIMENSIONES DETALLADAS (NUEVO)
# ==========================================
st.markdown("### 📐 Acotado y Dimensiones Críticas del Perfil")
st.markdown(f"""
<div class='dimension-box'>
    <b>Reporte Métrico de las Figuras:</b>
    <ul>
        <li><b>Base Mayor General (B):</b> {base_mayor_input:,.2f} {u_long}</li>
        <li><b>Base Menor del Trapecio (b):</b> {base_menor_calculada:,.2f} {u_long} <span style='color: #7f8c8d;'>(Calculada automáticamente)</span></li>
        <li><b>Altura del Trapecio Superior:</b> {altura_trap_input:,.2f} {u_long}</li>
        <li><b>Altura del Rectángulo Inferior:</b> {altura_rect_input:,.2f} {u_long}</li>
        <li><b>Profundidad de Extrusión (L):</b> {profundidad_input:,.2f} {u_long}</li>
        <li><b>Cuña de Apoyo Involucrada ({lado_cuna}):</b>
            <ul>
                <li>Altura asignada: {altura_cuna_input:,.2f} {u_long}</li>
                <li>Base total del triángulo isósceles: {b_cuna_v:,.2f} {u_long} <span style='color: #7f8c8d;'>(Garantiza ángulos basales simétricos a la horizontal)</span></li>
                <li>Proyección horizontal por lado (dx): {dx_cuna_v:,.2f} {u_long}</li>
            </ul>
        </li>
    </ul>
</div>
""", unsafe_allow_html=True)
