# -*- coding: utf-8 -*-
"""
Aplicación Streamlit para el Cálculo de Volumen de Talud.
Especializado para ingeniería civil: calcula áreas, volúmenes y grafica secciones transversales a escala.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Cálculo de Volumen de Talud",
    layout="wide",
    initial_sidebar_state="expanded"
)

def validar_datos(
    metodo: str,
    base_mayor: float,
    base_menor: float,
    altura_trapecio: float,
    pendiente_izq: float,
    pendiente_der: float,
    altura_rectangulo: float,
    profundidad: float
) -> list[str]:
    """
    Realiza las validaciones de consistencia física y geométrica de los datos de entrada.
    
    Args:
        metodo (str): Método de ingreso seleccionado ("Método 1" o "Método 2").
        base_mayor (float): Base mayor del trapecio.
        base_menor (float): Base menor del trapecio.
        altura_trapecio (float): Altura de la sección trapecio.
        pendiente_izq (float): Relación H del talud izquierdo (H:1V).
        pendiente_der (float): Relación H del talud derecho (H:1V).
        altura_rectangulo (float): Altura del bloque rectangular inferior.
        profundidad (float): Longitud / profundidad constante del talud.
        
    Returns:
        list[str]: Lista con los mensajes de error encontrados. Si está vacía, los datos son válidos.
    """
    errores = []
    
    # Validaciones generales de dimensiones no negativas o mayores que cero
    if base_mayor <= 0:
        errores.append("La base mayor debe ser estrictamente mayor que cero.")
    if altura_trapecio < 0:
        errores.append("La altura del trapecio no puede ser un valor negativo.")
    if altura_rectangulo < 0:
        errores.append("La altura del rectángulo no puede ser un valor negativo.")
    if profundidad <= 0:
        errores.append("La profundidad de la estructura debe ser mayor que cero.")
    if pendiente_izq < 0:
        errores.append("La pendiente izquierda (H:1V) no puede ser negativa.")
    if pendiente_der < 0:
        errores.append("La pendiente derecha (H:1V) no puede ser negativa.")
        
    # Validaciones específicas según el método de ingreso elegido
    if metodo == "Método 1":
        if base_mayor <= base_menor:
            errores.append("La base mayor debe ser estrictamente mayor que la base menor.")
        if base_menor <= 0:
            errores.append("La base menor debe ser mayor que cero.")
    elif metodo == "Método 2":
        if base_menor <= 0:
            errores.append("Base menor calculada es menor o igual a cero con las pendientes y dimensiones ingresadas.")
            
    return errores


def calcular_geometria_y_volumen(
    base_mayor: float,
    base_menor: float,
    altura_trapecio: float,
    altura_rectangulo: float,
    profundidad: float
) -> dict[str, float]:
    """
    Calcula las áreas y volúmenes correspondientes a la sección del talud.
    
    Args:
        base_mayor (float): Base mayor de la sección.
        base_menor (float): Base menor del trapecio superior.
        altura_trapecio (float): Altura del trapecio.
        altura_rectangulo (float): Altura del rectángulo inferior.
        profundidad (float): Profundidad constante del cuerpo tridimensional.
        
    Returns:
        dict[str, float]: Diccionario con las áreas y volúmenes calculados.
    """
    area_trapecio = ((base_mayor + base_menor) / 2.0) * altura_trapecio
    area_rectangulo = base_mayor * altura_rectangulo
    
    volumen_trapecio = area_trapecio * profundidad
    volumen_rectangulo = area_rectangulo * profundidad
    volumen_total = volumen_trapecio + volumen_rectangulo
    
    return {
        "area_trapecio": area_trapecio,
        "area_rectangulo": area_rectangulo,
        "volumen_trapecio": volumen_trapecio,
        "volumen_rectangulo": volumen_rectangulo,
        "volumen_total": volumen_total
    }

def generar_grafico_seccion(
    base_mayor: float,
    base_menor: float,
    altura_trapecio: float,
    pendiente_izq: float,
    pendiente_der: float,
    altura_rectangulo: float
) -> go.Figure:
    """
    Genera un gráfico bidimensional interactivo y a escala 1:1 de la sección transversal usando Plotly.
    """
    fig = go.Figure()

    # Definición de coordenadas para el rectángulo inferior (visto de frente)
    x_rect = [0, base_mayor, base_mayor, 0, 0]
    y_rect = [0, 0, altura_rectangulo, altura_rectangulo, 0]

    # Definición de coordenadas para el trapecio superior que descansa sobre el rectángulo
    x_trap = [
        0,
        base_mayor,
        base_mayor - (pendiente_der * altura_trapecio),
        pendiente_izq * altura_trapecio,
        0
    ]
    y_trap = [
        altura_rectangulo,
        altura_rectangulo,
        altura_rectangulo + altura_trapecio,
        altura_rectangulo + altura_trapecio,
        altura_rectangulo
    ]

    # Trazar polígono del Rectángulo Inferior
    fig.add_trace(go.Scatter(
        x=x_rect,
        y=y_rect,
        fill="toself",
        fillcolor="rgba(52, 152, 219, 0.4)",
        line=dict(color="#2980b9", width=3.5),
        mode="lines+markers",
        marker=dict(size=7, color="#1c5980"),
        name="Rectángulo Inferior (Base)"
    ))

    # Trazar polígono del Trapecio Superior
    fig.add_trace(go.Scatter(
        x=x_trap,
        y=y_trap,
        fill="toself",
        fillcolor="rgba(230, 126, 34, 0.4)",
        line=dict(color="#d35400", width=3.5),
        mode="lines+markers",
        marker=dict(size=7, color="#a04000"),
        name="Trapecio Superior (Talud)"
    ))

    # Añadir anotaciones de dimensiones clave en la gráfica (Corregido con etiquetas HTML <b>)
    fig.add_annotation(
        x=base_mayor / 2,
        y=-0.05 * (altura_rectangulo + altura_trapecio + 1),
        text=f"<b>B = {base_mayor:.2f} m</b>",
        showarrow=False,
        font=dict(size=12, color="#1c5980")
    )

    x_centro_menor = (x_trap[2] + x_trap[3]) / 2
    fig.add_annotation(
        x=x_centro_menor,
        y=altura_rectangulo + altura_trapecio + (0.04 * (altura_rectangulo + altura_trapecio + 1)),
        text=f"<b>b = {base_menor:.2f} m</b>",
        showarrow=False,
        font=dict(size=12, color="#a04000")
    )

    # Configuración avanzada del diseño de los ejes para cumplir con la escala 1:1 real
    fig.update_layout(
        title={
            'text': "<b>Sección Transversal del Talud (Escala Geométrica Real 1:1)</b>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=16, color="#2c3e50")
        },
        xaxis=dict(
            title="Ancho / Extensión Horizontal (m)",
            gridcolor="#e0e0e0",
            zeroline=True,
            zerolinecolor="#7f8c8d",
            showgrid=True
        ),
        yaxis=dict(
            title="Altura / Elevación Vertical (m)",
            gridcolor="#e0e0e0",
            zeroline=True,
            zerolinecolor="#7f8c8d",
            showgrid=True,
            scaleanchor="x",  # Vincula el eje Y al eje X para forzar aspecto 1:1
            scaleratio=1      # Un metro en X es exactamente igual a un metro en Y
        ),
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=50, r=50, t=90, b=70),
        hovermode="closest"
    )

    return fig

def main() -> None:
    """
    Función principal que orquesta la interfaz de usuario en Streamlit,
    captura los datos, ejecuta cálculos y renderiza resultados y gráficas.
    """
    st.write("<h1 style='text-align: center; color: #2c3e50;'>Cálculo de Volumen de Talud</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align: center; color: #7f8c8d;'>Herramienta profesional de ingeniería civil para el análisis volumétrico de secciones combinadas.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Selector del método de ingreso solicitado
    st.subheader("Configuración de Entrada")
    metodo = st.radio(
        "**Método de ingreso**",
        ["Método 1", "Método 2"],
        help="Método 1: Define bases y calcula automáticamente un talud en base al otro. Método 2: Define pendientes y calcula automáticamente la base menor."
    )

    st.markdown("---")

    # Inicialización de variables de control geométrico
    base_mayor = 0.0
    base_menor = 0.0
    altura_trapecio = 0.0
    pendiente_izq = 0.0
    pendiente_der = 0.0

    # Layout de columnas para organizar los parámetros de entrada según el método elegido
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Parámetros del Trapecio Superior")
        if metodo == "Método 1":
            base_mayor = st.number_input("Base mayor (m)", min_value=0.0, value=12.0, step=0.5, key="b_mayor_m1")
            base_menor = st.number_input("Base menor (m)", min_value=0.0, value=4.0, step=0.5, key="b_menor_m1")
            altura_trapecio = st.number_input("Altura del trapecio (m)", min_value=0.0, value=4.0, step=0.5, key="h_trap_m1")

            st.write("**Pendiente de UN SOLO TALUD (Relación H:1V)**")
            selector_talud = st.radio("Definir pendiente del:", ["Talud izquierdo", "Talud derecho"])

            if altura_trapecio > 0 and base_mayor > base_menor:
                max_pendiente_teorica = (base_mayor - base_menor) / altura_trapecio
            else:
                max_pendiente_teorica = 0.0

            if selector_talud == "Talud izquierdo":
                pendiente_izq = st.number_input(
                    "Pendiente izquierda (H:1V)",
                    min_value=0.0,
                    max_value=float(max_pendiente_teorica) if max_pendiente_teorica > 0 else 0.0,
                    value=float(max_pendiente_teorica / 2.0) if max_pendiente_teorica > 0 else 0.0,
                    step=0.1,
                    help="Proporción horizontal por cada unidad vertical en el lado izquierdo."
                )
                if altura_trapecio > 0:
                    pendiente_der = max_pendiente_teorica - pendiente_izq
                else:
                    pendiente_der = 0.0
                st.info(f"📐 Pendiente derecha calculada automáticamente: **{pendiente_der:.3f}H : 1V**")
            else:
                pendiente_der = st.number_input(
                    "Pendiente derecha (H:1V)",
                    min_value=0.0,
                    max_value=float(max_pendiente_teorica) if max_pendiente_teorica > 0 else 0.0,
                    value=float(max_pendiente_teorica / 2.0) if max_pendiente_teorica > 0 else 0.0,
                    step=0.1,
                    help="Proporción horizontal por cada unidad vertical en el lado derecho."
                )
                if altura_trapecio > 0:
                    pendiente_izq = max_pendiente_teorica - pendiente_der
                else:
                    pendiente_izq = 0.0
                st.info(f"📐 Pendiente izquierda calculada automáticamente: **{pendiente_izq:.3f}H : 1V**")

        elif metodo == "Método 2":
            base_mayor = st.number_input("Base mayor (m)", min_value=0.0, value=12.0, step=0.5, key="b_mayor_m2")
            altura_trapecio = st.number_input("Altura (m)", min_value=0.0, value=4.0, step=0.5, key="h_trap_m2")
            pendiente_izq = st.number_input("Pendiente izquierda (H:1V)", min_value=0.0, value=1.2, step=0.1, key="p_izq_m2")
            pendiente_der = st.number_input("Pendiente derecha (H:1V)", min_value=0.0, value=1.2, step=0.1, key="p_der_m2")

            # Cálculo automático de la base menor basado en la fórmula provista
            base_menor = base_mayor - altura_trapecio * (pendiente_izq + pendiente_der)
            
            if base_menor > 0:
                st.info(f"📐 Base menor calculada automáticamente: **{base_menor:.3f} m**")

    with col2:
        st.markdown("### Rectángulo inferior")
        altura_rectangulo = st.number_input("Altura del rectángulo (m)", min_value=0.0, value=3.0, step=0.5)
        profundidad = st.number_input("Profundidad (m)", min_value=0.0, value=50.0, step=5.0)
        
        st.caption(f"ℹ️ La base del rectángulo está acoplada estructuralmente y SIEMPRE será igual a la base mayor del trapecio (**{base_mayor:.2f} m**).")

    st.markdown("---")

    # Ejecución del bloque de validación
    lista_errores = validar_datos(
        metodo=metodo,
        base_mayor=base_mayor,
        base_menor=base_menor,
        altura_trapecio=altura_trapecio,
        pendiente_izq=pendiente_izq,
        pendiente_der=pendiente_der,
        altura_rectangulo=altura_rectangulo,
        profundidad=profundidad
    )

    if lista_errores:
        st.error("### 🛑 No se pueden procesar los resultados debido a los siguientes errores:")
        for err in lista_errores:
            st.error(f"- {err}")
    else:
        # Cálculos volumétricos y geométricos
        resultados = calcular_geometria_y_volumen(
            base_mayor=base_mayor,
            base_menor=base_menor,
            altura_trapecio=altura_trapecio,
            altura_rectangulo=altura_rectangulo,
            profundidad=profundidad
        )

        # Sección de despliegue de resultados profesionales en tarjetas/métricas
        st.write("<h3 style='color: #2c3e50;'>Resultados del Análisis Volumétrico</h3>", unsafe_allow_html=True)
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Base Mayor (B)", f"{base_mayor:.2f} m")
        m_col2.metric("Base Menor (b)", f"{base_menor:.2f} m")
        m_col3.metric("Pendiente Izquierda", f"{pendiente_izq:.2f} H:1V")
        m_col4.metric("Pendiente Derecha", f"{pendiente_der:.2f} H:1V")

        m_col5, m_col6, m_col7, m_col8 = st.columns(4)
        m_col5.metric("Área Trapecio", f"{resultados['area_trapecio']:.2f} m²")
        m_col6.metric("Área Rectángulo", f"{resultados['area_rectangulo']:.2f} m²")
        m_col7.metric("Volumen Trapecio", f"{resultados['volumen_trapecio']:.2f} m³")
        m_col8.metric("Volumen Rectángulo", f"{resultados['volumen_rectangulo']:.2f} m³")

        st.markdown("###")
        st.info(f"📊 **Volumen Total Combinado de la Estructura: {resultados['volumen_total']:.2f} m³**")
        st.markdown("---")

        # Renderizado del gráfico interactivo a escala real
        figura_seccion = generar_grafico_seccion(
            base_mayor=base_mayor,
            base_menor=base_menor,
            altura_trapecio=altura_trapecio,
            pendiente_izq=pendiente_izq,
            pendiente_der=pendiente_der,
            altura_rectangulo=altura_rectangulo
        )
        st.plotly_chart(figura_seccion, use_container_width=True)

if __name__ == "__main__":
    main()
