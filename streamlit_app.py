import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración inicial de la página
st.set_page_config(
    page_title="Calculador Geotécnico de Taludes",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para legibilidad y diseño limpio
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #2c3e50; font-weight: 700; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #2980b9; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .stMetric b { color: #2c3e50; font-size: 1.1rem; }
    .stMetric p { color: #34495e; margin: 3px 0; font-size: 0.92rem; }
    .dimension-box { background-color: #f1f2f6; padding: 15px; border-radius: 5px; border: 1px solid #dcdde1; margin-top: 10px; }
    .dimension-box ul { margin: 0; padding-left: 20px; color: #2f3640; }
    .water-highlight { color: #2980b9; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Calculador Geotécnico y Volumétrico de Taludes")
st.markdown("Herramienta avanzada para diseño geométrico, análisis de humedad de ensayo y requerimiento de agua.")

# ==========================================
# BARRA LATERAL: CONFIGURACIÓN GLOBAL Y ENTRADAS
# ==========================================
st.sidebar.header("⚙️ Configuración Global")

unidades_dim = st.sidebar.selectbox("Unidades de Dimensión (Geometría):", ["Metros (m)", "Centímetros (cm)"])
unidades_dens = st.sidebar.selectbox("Unidades de Densidad:", ["kg/m³", "g/cm³"])
unidad_masa = st.sidebar.selectbox("Mostrar Masas en:", ["Kilogramos (kg)", "Toneladas (Ton)"])
unidad_agua = st.sidebar.selectbox("Mostrar Volumen de Agua Adicional en:", ["Litros (L)", "Metros Cúbicos (m³)", "Centímetros Cúbicos (cm³)"])

u_long = "m" if unidades_dim == "Metros (m)" else "cm"
u_dens = "kg/m³" if unidades_dens == "kg/m³" else "g/cm³"
u_masa = "kg" if unidad_masa == "Kilogramos (kg)" else "Ton"

to_meters = 1.0 if u_long == "m" else 0.01
to_kg_m3 = 1.0 if u_dens == "kg/m³" else 1000.0
mass_factor = 1.0 if u_masa == "kg" else 0.001

st.sidebar.markdown("---")
st.sidebar.header("📐 Geometría Principal Inicial")

metodologia_ingreso = st.sidebar.selectbox(
    "Metodología de Entrada del Trapecio:",
    ["Metodología A: Por Dimensiones de Bases", "Metodología B: Por Pendientes"]
)

base_mayor_input = st.sidebar.number_input(f"Base Mayor (B) [Trapecio y Rectángulo] [{u_long}]", min_value=1.0, value=12.0 if u_long == "m" else 1200.0, step=0.5)
altura_trap_input = st.sidebar.number_input(f"Altura del Trapecio (h) [{u_long}]", min_value=0.5, value=4.0 if u_long == "m" else 400.0, step=0.1)
altura_rect_inicial = st.sidebar.number_input(f"Altura del Rectángulo Inferior Inicial [{u_long}]", min_value=0.1, value=3.0 if u_long == "m" else 300.0, step=0.1)
profundidad_inicial = st.sidebar.number_input(f"Espesor / Profundidad Total Inicial [{u_long}]", min_value=0.1, value=50.0 if u_long == "m" else 5000.0, step=1.0)

# Procesamiento condicional de inputs según Metodología elegida
if metodologia_ingreso.startswith("Metodología A"):
    base_menor_input = st.sidebar.number_input(f"Base Menor del Trapecio (b) [{u_long}]", min_value=0.1, value=4.8 if u_long == "m" else 480.0, step=0.2)
    lado_pendiente_conocida = st.sidebar.selectbox("Elegir Pendiente a colocar manualmente:", ["Izquierda", "Derecha"])
    
    if lado_pendiente_conocida == "Izquierda":
        pendiente_izq = st.sidebar.number_input("Pendiente Izquierda Conocida (H:1V)", min_value=0.0, value=1.2, step=0.1)
        diferencia_horizontal = base_mayor_input - base_menor_input - (pendiente_izq * altura_trap_input)
        if diferencia_horizontal < 0 or altura_trap_input <= 0:
            st.sidebar.error("❌ Error: Geometría imposible. Reduce la pendiente izquierda o aumenta las bases.")
            st.stop()
        pendiente_der = diferencia_horizontal / altura_trap_input
    else:
        pendiente_der = st.sidebar.number_input("Pendiente Derecha Conocida (H:1V)", min_value=0.0, value=1.2, step=0.1)
        diferencia_horizontal = base_mayor_input - base_menor_input - (pendiente_der * altura_trap_input)
        if diferencia_horizontal < 0 or altura_trap_input <= 0:
            st.sidebar.error("❌ Error: Geometría imposible. Reduce la pendiente derecha o aumenta las bases.")
            st.stop()
        pendiente_izq = diferencia_horizontal / altura_trap_input
    
    base_menor_calculada = base_menor_input

else: # Metodología B
    pendiente_izq = st.sidebar.number_input("Pendiente Izquierda (H:1V)", min_value=0.1, value=1.2, step=0.1)
    pendiente_der = st.sidebar.number_input("Pendiente Derecha (H:1V)", min_value=0.1, value=1.2, step=0.1)
    base_menor_calculada = base_mayor_input - (pendiente_izq * altura_trap_input) - (pendiente_der * altura_trap_input)
    if base_menor_calculada <= 0:
        st.sidebar.error("❌ Error Geométrico: Las pendientes y la altura superan la Base Mayor.")
        st.stop()

st.sidebar.markdown("---")
st.sidebar.header("🔺 Configuración de la Cuña de Apoyo")
lado_cuna = st.sidebar.selectbox("Lado de incrustación de la Cuña:", ["Izquierda", "Derecha"])
altura_cuna_input = st.sidebar.number_input(f"Altura de la Cuña [{u_long}]", min_value=0.0, max_value=float(altura_trap_input), value=float(altura_trap_input * 0.4), step=0.1)

st.sidebar.markdown("---")
st.sidebar.header("🪨 Propiedades Geotécnicas y Humedades")
densidad_seca_input = st.sidebar.number_input(f"Densidad Seca (γd) [{u_dens}]", min_value=1.0, value=1600.0 if u_dens == "kg/m³" else 1.6, step=10.0 if u_dens == "kg/m³" else 0.1)

# NUEVA ENTRADA: Humedad Natural del Suelo al momento del ensayo
humedad_natural = st.sidebar.number_input("Humedad Natural en Ensayo (ω_nat) [%]", min_value=0.0, max_value=100.0, value=4.0, step=0.5)

humedad_bloque_A = st.sidebar.number_input("Humedad Objetivo - Bloque A (%)", min_value=0.0, max_value=100.0, value=12.0, step=0.5)
humedad_bloque_B = st.sidebar.number_input("Humedad Objetivo - Bloque B (%)", min_value=0.0, max_value=100.0, value=8.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.header("⚖️ Factor de Escalamiento")
factor_escala = st.sidebar.number_input("Factor de Multiplicación de Altura Trapecio (X veces):", min_value=0.1, value=2.0, step=0.5)

# ==========================================
# DEFINICIÓN DE PESTAÑAS PRINCIPALES
# ==========================================
tab_original, tab_escalado = st.tabs(["📐 Caso Original", f"🚀 Caso Escalado ({factor_escala}x)"])

# ------------------------------------------
# LÓGICA DE PROCESAMIENTO GEOTÉCNICO EXACTO
# ------------------------------------------
def calcular_y_graficar(B_in, h_trap_in, p_izq, p_der, h_rect_in, L_in, h_cuna_in, titulo_contexto):
    # Conversión al Sistema Internacional (m, kg)
    B = B_in * to_meters
    h_trap = h_trap_in * to_meters
    h_rect = h_rect_in * to_meters
    L = L_in * to_meters
    h_cuna = h_cuna_in * to_meters
    γ_d = densidad_seca_input * to_kg_m3
    
    b = B - (p_izq * h_trap) - (p_der * h_trap)
    m_elegida = p_izq if lado_cuna == "Izquierda" else p_der
    
    # Geometría de la Cuña
    dx_cuna = m_elegida * h_cuna
    b_cuna = 2 * dx_cuna
    
    # Cálculos de Áreas (m²)
    area_rectangulo_total = B * h_rect
    area_trapecio_total = ((B + b) / 2) * h_trap
    area_cuna = 0.5 * b_cuna * h_cuna
    
    area_bloque_A = area_rectangulo_total + area_cuna
    area_bloque_B = area_trapecio_total - area_cuna
    
    # Volúmenes (m³)
    vol_bloque_A = area_bloque_A * L
    vol_bloque_B = area_bloque_B * L
    vol_total = vol_bloque_A + vol_bloque_B
    
    # ====================================================
    # CÁLCULOS EXACTOS DE MASAS Y VOLUMEN DE AGUA (S.I.)
    # ====================================================
    # 1. Masa Seca (Md = Vol * γd) [kg]
    masa_seca_A_kg = vol_bloque_A * γ_d
    masa_seca_B_kg = vol_bloque_B * γ_d
    masa_seca_total_kg = masa_seca_A_kg + masa_seca_B_kg
    
    # 2. Masa a Humedad Natural (M_nat = Md * (1 + ω_nat/100)) [kg]
    masa_nat_A_kg = masa_seca_A_kg * (1 + (humedad_natural / 100.0))
    masa_nat_B_kg = masa_seca_B_kg * (1 + (humedad_natural / 100.0))
    masa_nat_total_kg = masa_nat_A_kg + masa_nat_B_kg
    
    # 3. Masa Húmeda Objetivo (M_obj = Md * (1 + ω_obj/100)) [kg]
    masa_obj_A_kg = masa_seca_A_kg * (1 + (humedad_bloque_A / 100.0))
    masa_obj_B_kg = masa_seca_B_kg * (1 + (humedad_bloque_B / 100.0))
    masa_obj_total_kg = masa_obj_A_kg + masa_obj_B_kg
    
    # 4. Agua adicional a incorporar (ΔMw = M_obj - M_nat) [kg]
    agua_kg_A = max(0.0, masa_obj_A_kg - masa_nat_A_kg)
    agua_kg_B = max(0.0, masa_obj_B_kg - masa_nat_B_kg)
    agua_kg_total = agua_kg_A + agua_kg_B
    
    # Conversión de Volumen de Agua Requerido según la preferencia elegida
    if unidad_agua == "Litros (L)":
        vol_agua_A = agua_kg_A  # 1 kg agua ≈ 1 Litro
        vol_agua_B = agua_kg_B
        vol_agua_total = agua_kg_total
        u_ag = "L"
    elif unidad_agua == "Metros Cúbicos (m³)":
        vol_agua_A = agua_kg_A / 1000.0
        vol_agua_B = agua_kg_B / 1000.0
        vol_agua_total = agua_kg_total / 1000.0
        u_ag = "m³"
    else: # cm³
        vol_agua_A = agua_kg_A * 1000.0
        vol_agua_B = agua_kg_B * 1000.0
        vol_agua_total = agua_kg_total * 1000.0
        u_ag = "cm³"

    # Factores de visualización de unidades
    v_factor = 1.0 if u_long == "m" else 1e6
    u_vol = "m³" if u_long == "m" else "cm³"
    u_area = "m²" if u_long == "m" else "cm²"
    
    # Despliegue de tarjetas de respuestas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class='stMetric'><b>Bloque A (Rectángulo + Cuña)</b>
        <p>Volumen: {vol_bloque_A * v_factor:,.2f} {u_vol}</p>
        <hr style='margin: 4px 0;'>
        <p><b>Masa Seca (M_d):</b> {masa_seca_A_kg * mass_factor:,.3f} {u_masa}</p>
        <p><b>Masa a Humedad Nat ({humedad_natural}%):</b> {masa_nat_A_kg * mass_factor:,.3f} {u_masa}</p>
        <p><b>Masa Húmeda Obj ({humedad_bloque_A}%):</b> {masa_obj_A_kg * mass_factor:,.3f} {u_masa}</p>
        <p class='water-highlight'>💧 Agua a incorporar: {vol_agua_A:,.2f} {u_ag}</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""<div class='stMetric'><b>Bloque B (Trapecio - Cuña)</b>
        <p>Volumen: {vol_bloque_B * v_factor:,.2f} {u_vol}</p>
        <hr style='margin: 4px 0;'>
        <p><b>Masa Seca (M_d):</b> {masa_seca_B_kg * mass_factor:,.3f} {u_masa}</p>
        <p><b>Masa a Humedad Nat ({humedad_natural}%):</b> {masa_nat_B_kg * mass_factor:,.3f} {u_masa}</p>
        <p><b>Masa Húmeda Obj ({humedad_bloque_B}%):</b> {masa_obj_B_kg * mass_factor:,.3f} {u_masa}</p>
        <p class='water-highlight'>💧 Agua a incorporar: {vol_agua_B:,.2f} {u_ag}</p>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""<div class='stMetric' style='border-left-color: #27ae60;'><b>Estructura Combinada Total</b>
        <p>Volumen Total: {vol_total * v_factor:,.2f} {u_vol}</p>
        <hr style='margin: 4px 0;'>
        <p><b>Masa Seca Total:</b> {masa_seca_total_kg * mass_factor:,.3f} {u_masa}</p>
        <p><b>Masa a Humedad Nat Total:</b> {masa_nat_total_kg * mass_factor:,.3f} {u_masa}</p>
        <p><b>Masa Húmeda Objetivo Total:</b> {masa_obj_total_kg * mass_factor:,.3f} {u_masa}</p>
        <p class='water-highlight'>💧 Agua Total a incorporar: {vol_agua_total:,.2f} {u_ag}</p>
        </div>""", unsafe_allow_html=True)
        
    # Coordenadas Plotly en Escala Visual
    x_rect = [0, B_in, B_in, 0, 0]
    y_rect = [0, 0, h_rect_in, h_rect_in, 0]
    dx_cuna_v = m_elegida * h_cuna_in
    b_cuna_v = 2 * dx_cuna_v
    b_v = B_in - (p_izq * h_trap_in) - (p_der * h_trap_in)
    
    if lado_cuna == "Izquierda":
        x_cuna = [0, dx_cuna_v, b_cuna_v, 0]
        y_cuna = [h_rect_in, h_rect_in + h_cuna_in, h_rect_in, h_rect_in]
        x_trap_rem = [b_cuna_v, B_in, B_in - (p_der * h_trap_in), p_izq * h_trap_in, dx_cuna_v, b_cuna_v]
        y_trap_rem = [h_rect_in, h_rect_in, h_rect_in + h_trap_in, h_rect_in + h_trap_in, h_rect_in + h_cuna_in, h_rect_in]
    else:
        x_cuna = [B_in, B_in - dx_cuna_v, B_in - b_cuna_v, B_in]
        y_cuna = [h_rect_in, h_rect_in + h_cuna_in, h_rect_in, h_rect_in]
        x_trap_rem = [0, B_in - b_cuna_v, B_in - dx_cuna_v, B_in - (p_der * h_trap_in), p_izq * h_trap_in, 0]
        y_trap_rem = [h_rect_in, h_rect_in, h_rect_in + h_cuna_in, h_rect_in + h_trap_in, h_rect_in + h_trap_in, h_rect_in]
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_rect, y=y_rect, fill="toself", fillcolor="rgba(52, 152, 219, 0.35)", line=dict(color="#2980b9", width=2), name="Rectángulo Inferior (Bloque A)", mode="lines"))
    fig.add_trace(go.Scatter(x=x_trap_rem, y=y_trap_rem, fill="toself", fillcolor="rgba(230, 126, 34, 0.4)", line=dict(color="#d35400", width=2), name="Trapecio Remanente (Bloque B)", mode="lines"))
    fig.add_trace(go.Scatter(x=x_cuna, y=y_cuna, fill="toself", fillcolor="rgba(46, 204, 113, 0.7)", line=dict(color="#27ae60", width=2.5, dash="dash"), name="Cuña Isósceles Horizontal (Bloque A)", mode="lines"))
    
    fig.update_layout(
        xaxis=dict(title=f"Extensión Horizontal ({u_long})", gridcolor="rgba(128,128,128,0.15)", zeroline=False),
        yaxis=dict(title=f"Elevación Vertical ({u_long})", gridcolor="rgba(128,128,128,0.15)", scaleanchor="x", scaleratio=1, zeroline=False),
        template="plotly_white", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=40, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Reporte de Cotas y Parámetros
    st.markdown("### 📐 Reporte de Geometría y Humedad de Ensayo")
    st.markdown(f"""
    <div class='dimension-box'>
        <b>Resumen del Análisis ({titulo_contexto}):</b>
        <ul>
            <li><b>Base Mayor General (B):</b> {B_in:,.2f} {u_long} | <b>Base Menor Calculada (b):</b> {b_v:,.2f} {u_long}</li>
            <li><b>Altura del Trapecio:</b> {h_trap_in:,.2f} {u_long} | <b>Altura Rectángulo Inferior:</b> {h_rect_in:,.2f} {u_long}</li>
            <li><b>Pendientes:</b> Izquierda: {p_izq:,.2f} H:1V | Derecha: {p_der:,.2f} H:1V</li>
            <li><b>Cuña ({lado_cuna}):</b> Base: {b_cuna_v:,.2f} {u_long} | Altura: {h_cuna_in:,.2f} {u_long}</li>
            <li><b>Parámetros de Humedad Usados:</b> Humedad Natural al Ensayo ($\omega_{{nat}}$) = {humedad_natural}% | Objetivo A = {humedad_bloque_A}% | Objetivo B = {humedad_bloque_B}%</li>
            <li><b>Volumen Total de Agua a Adicionar para Acondicionar el Suelo:</b> <span style='color: #2980b9; font-weight: bold;'>{vol_agua_total:,.2f} {u_ag}</span></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# PESTAÑA 1: CASO ORIGINAL
# ------------------------------------------
with tab_original:
    st.subheader("📋 Análisis del Perfil de Talud Original")
    calcular_y_graficar(
        B_in=base_mayor_input,
        h_trap_in=altura_trap_input,
        p_izq=pendiente_izq,
        p_der=pendiente_der,
        h_rect_in=altura_rect_inicial,
        L_in=profundidad_inicial,
        h_cuna_in=altura_cuna_input,
        titulo_contexto="Geometría Original"
    )

# ------------------------------------------
# PESTAÑA 2: CASO ESCALADO (X VECES)
# ------------------------------------------
with tab_escalado:
    st.subheader(f"🚀 Escalamiento Geométrico Automático ({factor_escala}x)")
    st.info(f"El trapecio y la cuña se han multiplicado por **{factor_escala}**. Modifica manualmente la altura del rectángulo y el espesor para este caso:")
    
    altura_rect_esc = st.number_input(f"Coloca manualmente: Altura del Rectángulo Inferior (Escalado) [{u_long}]", min_value=0.1, value=float(altura_rect_inicial), key="h_rect_esc")
    profundidad_esc = st.number_input(f"Coloca manualmente: Espesor / Profundidad Total (Escalado) [{u_long}]", min_value=0.1, value=float(profundidad_inicial), key="L_esc")
    
    base_mayor_escalada = base_mayor_input * factor_escala
    altura_trap_escalada = altura_trap_input * factor_escala
    altura_cuna_escalada = altura_cuna_input * factor_escala
    
    calcular_y_graficar(
        B_in=base_mayor_escalada,
        h_trap_in=altura_trap_escalada,
        p_izq=pendiente_izq,
        p_der=pendiente_der,
        h_rect_in=altura_rect_esc,
        L_in=profundidad_esc,
        h_cuna_in=altura_cuna_escalada,
        titulo_contexto=f"Geometría Escalada {factor_escala}x"
    )
