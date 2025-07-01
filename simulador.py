import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Simulador de Comercio Internacional - Universidad ORT",
    page_icon="🇺🇾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Datos específicos de Uruguay
PAISES_DESTINO = {
    "China": {"participacion": 24, "acuerdo": "Sin acuerdo", "arancel_base": 15},
    "Brasil": {"participacion": 18, "acuerdo": "MERCOSUR", "arancel_base": 0},
    "Unión Europea": {"participacion": 14, "acuerdo": "UE-MERCOSUR (2024)", "arancel_base": 2},
    "Estados Unidos": {"participacion": 9, "acuerdo": "Sin acuerdo", "arancel_base": 12},
    "Argentina": {"participacion": 5, "acuerdo": "MERCOSUR", "arancel_base": 0},
    "México": {"participacion": 3, "acuerdo": "ACE-54", "arancel_base": 5},
    "Chile": {"participacion": 2, "acuerdo": "ACE-35", "arancel_base": 3},
    "India": {"participacion": 2, "acuerdo": "Acuerdo Marco", "arancel_base": 8},
    "Perú": {"participacion": 1, "acuerdo": "ACE-58", "arancel_base": 4},
    "Colombia": {"participacion": 1, "acuerdo": "ACE-72", "arancel_base": 6}
}

PRODUCTOS_URUGUAYOS = {
    "Celulosa": {"categoria": "Papel y pulpa", "valor_promedio": 2500, "volumen_tons": 1200},
    "Carne bovina": {"categoria": "Cárnico", "valor_promedio": 4500, "volumen_tons": 450},
    "Soja": {"categoria": "Commodities agrícolas", "valor_promedio": 500, "volumen_tons": 2400},
    "Productos lácteos": {"categoria": "Alimentarios", "valor_promedio": 3200, "volumen_tons": 180},
    "Concentrados de bebidas": {"categoria": "Bebidas", "valor_promedio": 8500, "volumen_tons": 75},
    "Arroz": {"categoria": "Commodities agrícolas", "valor_promedio": 600, "volumen_tons": 900},
    "Vehículos": {"categoria": "Automotriz", "valor_promedio": 15000, "volumen_tons": 150},
    "Subproductos cárnicos": {"categoria": "Cárnico", "valor_promedio": 2800, "volumen_tons": 120},
    "Madera": {"categoria": "Forestal", "valor_promedio": 350, "volumen_tons": 800},
    "Trigo": {"categoria": "Commodities agrícolas", "valor_promedio": 280, "volumen_tons": 500}
}

INCOTERMS_DATA = {
    "EXW": {
        "nombre": "Ex Works",
        "responsabilidad_vendedor": "Mínima - Solo entrega en fábrica",
        "transporte": "Comprador",
        "seguro": "Comprador",
        "despacho_exportacion": "Comprador",
        "despacho_importacion": "Comprador",
        "riesgo_costo": "Bajo para vendedor",
        "uso_recomendado": "Vendedores con poca experiencia internacional"
    },
    "FCA": {
        "nombre": "Free Carrier",
        "responsabilidad_vendedor": "Hasta entrega al transportista",
        "transporte": "Comprador",
        "seguro": "Comprador",
        "despacho_exportacion": "Vendedor",
        "despacho_importacion": "Comprador",
        "riesgo_costo": "Medio para vendedor",
        "uso_recomendado": "Transporte multimodal, contenedores"
    },
    "FOB": {
        "nombre": "Free On Board",
        "responsabilidad_vendedor": "Hasta carga en buque",
        "transporte": "Comprador",
        "seguro": "Comprador",
        "despacho_exportacion": "Vendedor",
        "despacho_importacion": "Comprador",
        "riesgo_costo": "Medio para vendedor",
        "uso_recomendado": "Transporte marítimo exclusivamente"
    },
    "CFR": {
        "nombre": "Cost and Freight",
        "responsabilidad_vendedor": "Incluye flete marítimo",
        "transporte": "Vendedor (hasta destino)",
        "seguro": "Comprador",
        "despacho_exportacion": "Vendedor",
        "despacho_importacion": "Comprador",
        "riesgo_costo": "Medio-alto para vendedor",
        "uso_recomendado": "Cuando vendedor tiene mejor flete"
    },
    "CIF": {
        "nombre": "Cost, Insurance and Freight",
        "responsabilidad_vendedor": "Incluye flete y seguro",
        "transporte": "Vendedor (hasta destino)",
        "seguro": "Vendedor",
        "despacho_exportacion": "Vendedor",
        "despacho_importacion": "Comprador",
        "riesgo_costo": "Alto para vendedor",
        "uso_recomendado": "Compradores con poca experiencia"
    },
    "CPT": {
        "nombre": "Carriage Paid To",
        "responsabilidad_vendedor": "Flete pagado hasta destino",
        "transporte": "Vendedor (hasta destino)",
        "seguro": "Comprador",
        "despacho_exportacion": "Vendedor",
        "despacho_importacion": "Comprador",
        "riesgo_costo": "Medio-alto para vendedor",
        "uso_recomendado": "Transporte multimodal"
    },
    "CIP": {
        "nombre": "Carriage and Insurance Paid To",
        "responsabilidad_vendedor": "Flete y seguro pagados",
        "transporte": "Vendedor (hasta destino)",
        "seguro": "Vendedor",
        "despacho_exportacion": "Vendedor",
        "despacho_importacion": "Comprador",
        "riesgo_costo": "Alto para vendedor",
        "uso_recomendado": "Transporte multimodal con seguro"
    },
    "DAP": {
        "nombre": "Delivered at Place",
        "responsabilidad_vendedor": "Hasta lugar de destino",
        "transporte": "Vendedor (completo)",
        "seguro": "Vendedor",
        "despacho_exportacion": "Vendedor",
        "despacho_importacion": "Comprador",
        "riesgo_costo": "Alto para vendedor",
        "uso_recomendado": "Vendedor con logística propia"
    },
    "DPU": {
        "nombre": "Delivered at Place Unloaded",
        "responsabilidad_vendedor": "Hasta descarga en destino",
        "transporte": "Vendedor (completo)",
        "seguro": "Vendedor",
        "despacho_exportacion": "Vendedor",
        "despacho_importacion": "Comprador",
        "riesgo_costo": "Muy alto para vendedor",
        "uso_recomendado": "Terminales específicas"
    },
    "DDP": {
        "nombre": "Delivered Duty Paid",
        "responsabilidad_vendedor": "Máxima - Todo incluido",
        "transporte": "Vendedor (completo)",
        "seguro": "Vendedor",
        "despacho_exportacion": "Vendedor",
        "despacho_importacion": "Vendedor",
        "riesgo_costo": "Máximo para vendedor",
        "uso_recomendado": "Vendedor muy experimentado"
    }
}

def calcular_costos(producto, pais_destino, valor_fob, incoterm, peso_tons):
    """Calcula los costos estimados según variables"""
    pais_info = PAISES_DESTINO[pais_destino]
    
    # Costos base
    costos = {
        "Valor FOB": valor_fob,
        "Flete marítimo": 0,
        "Seguro": 0,
        "Aranceles": 0,
        "Despacho exportación": 350,
        "Despacho importación": 0,
        "Gestión bancaria": valor_fob * 0.002,
        "Certificaciones": 180
    }
    
    # Flete estimado por destino
    fletes_base = {
        "China": 85, "Brasil": 25, "Unión Europea": 65, "Estados Unidos": 75,
        "Argentina": 20, "México": 55, "Chile": 30, "India": 90,
        "Perú": 35, "Colombia": 50
    }
    
    costos["Flete marítimo"] = fletes_base.get(pais_destino, 60) * peso_tons
    
    # Seguro (0.3% del valor CIF)
    valor_cif = valor_fob + costos["Flete marítimo"]
    costos["Seguro"] = valor_cif * 0.003
    
    # Aranceles según acuerdo comercial
    costos["Aranceles"] = valor_cif * (pais_info["arancel_base"] / 100)
    
    # Ajustes según Incoterm
    if incoterm in ["EXW"]:
        costos["Despacho exportación"] = 0
        costos["Flete marítimo"] = 0
        costos["Seguro"] = 0
    elif incoterm in ["FCA", "FOB"]:
        costos["Flete marítimo"] = 0
        costos["Seguro"] = 0
    elif incoterm in ["CFR", "CPT"]:
        costos["Seguro"] = 0
    elif incoterm in ["DAP", "DPU", "DDP"]:
        costos["Despacho importación"] = 420
    
    if incoterm == "DDP":
        # En DDP el vendedor paga los aranceles
        pass
    else:
        costos["Despacho importación"] = 280
    
    return costos

def recomendar_incoterm(producto, pais_destino, experiencia, valor_operacion):
    """Recomienda el mejor Incoterm según variables"""
    pais_info = PAISES_DESTINO[pais_destino]
    
    # Lógica de recomendación
    if experiencia == "Principiante":
        if pais_info["acuerdo"] == "MERCOSUR":
            return "FOB", "Bajo riesgo y mercado conocido"
        else:
            return "EXW", "Riesgo mínimo para comenzar"
    
    elif experiencia == "Intermedio":
        if valor_operacion < 50000:
            return "FCA", "Buena relación costo-beneficio"
        elif pais_destino in ["China", "Unión Europea"]:
            return "CFR", "Control del flete en destinos lejanos"
        else:
            return "FOB", "Estándar para operaciones medianas"
    
    else:  # Experto
        if valor_operacion > 200000:
            return "CIF", "Control total de la logística"
        elif pais_info["acuerdo"] in ["MERCOSUR", "UE-MERCOSUR (2024)"]:
            return "DAP", "Aprovechar preferencias arancelarias"
        else:
            return "CPT", "Flexibilidad en mercados complejos"

# INTERFAZ PRINCIPAL
st.title("🇺🇾 Simulador de Comercio Internacional")
st.markdown("**Universidad ORT Uruguay - Operativa y Procedimientos del Comercio Internacional**")
st.markdown("*Profesora: Mariana Correa | Carrera: Analista en Comercio Exterior*")

st.markdown("---")

# SIDEBAR - CONTROLES
st.sidebar.header("🔧 Variables de Simulación")

st.sidebar.subheader("📦 Producto y Operación")
producto_seleccionado = st.sidebar.selectbox(
    "Producto a exportar:",
    list(PRODUCTOS_URUGUAYOS.keys()),
    help="Principales productos de exportación de Uruguay"
)

valor_fob = st.sidebar.number_input(
    "Valor FOB (USD):",
    min_value=1000,
    max_value=5000000,
    value=PRODUCTOS_URUGUAYOS[producto_seleccionado]["valor_promedio"],
    step=1000,
    help="Valor Free On Board en dólares estadounidenses"
)

peso_tons = st.sidebar.number_input(
    "Peso (toneladas):",
    min_value=1.0,
    max_value=10000.0,
    value=float(PRODUCTOS_URUGUAYOS[producto_seleccionado]["volumen_tons"]),
    step=1.0,
    help="Peso total del envío en toneladas"
)

st.sidebar.subheader("🌎 Destino y Experiencia")
pais_destino = st.sidebar.selectbox(
    "País de destino:",
    list(PAISES_DESTINO.keys()),
    help="Principales socios comerciales de Uruguay"
)

experiencia = st.sidebar.selectbox(
    "Experiencia del exportador:",
    ["Principiante", "Intermedio", "Experto"],
    index=1,
    help="Nivel de experiencia en comercio internacional"
)

incoterm_manual = st.sidebar.selectbox(
    "Incoterm (opcional - manual):",
    ["Automático"] + list(INCOTERMS_DATA.keys()),
    help="Déjalo en 'Automático' para recomendación inteligente"
)

# COLUMNAS PRINCIPALES
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Información del Mercado Destino")
    
    pais_info = PAISES_DESTINO[pais_destino]
    
    # Tarjetas de información
    st.metric("Participación en exportaciones uruguayas", f"{pais_info['participacion']}%")
    
    acuerdo_color = "🟢" if "MERCOSUR" in pais_info["acuerdo"] or "UE-MERCOSUR" in pais_info["acuerdo"] else "🟡" if "ACE" in pais_info["acuerdo"] else "🔴"
    st.metric("Acuerdo comercial", f"{acuerdo_color} {pais_info['acuerdo']}")
    
    st.metric("Arancel base aplicable", f"{pais_info['arancel_base']}%")
    
    # Información del producto
    st.subheader("📦 Información del Producto")
    producto_info = PRODUCTOS_URUGUAYOS[producto_seleccionado]
    st.write(f"**Categoría:** {producto_info['categoria']}")
    st.write(f"**Valor promedio por tonelada:** USD {producto_info['valor_promedio']:,}")

with col2:
    st.subheader("🎯 Recomendación de Incoterm")
    
    if incoterm_manual == "Automático":
        incoterm_recomendado, razon = recomendar_incoterm(
            producto_seleccionado, pais_destino, experiencia, valor_fob
        )
        st.success(f"**Recomendado: {incoterm_recomendado}**")
        st.write(f"*Razón: {razon}*")
        incoterm_final = incoterm_recomendado
    else:
        incoterm_final = incoterm_manual
        st.info(f"**Seleccionado manualmente: {incoterm_manual}**")
    
    # Información del Incoterm
    inco_info = INCOTERMS_DATA[incoterm_final]
    st.markdown(f"**{inco_info['nombre']}**")
    st.write(f"**Responsabilidad vendedor:** {inco_info['responsabilidad_vendedor']}")
    st.write(f"**Transporte:** {inco_info['transporte']}")
    st.write(f"**Seguro:** {inco_info['seguro']}")
    st.write(f"**Uso recomendado:** {inco_info['uso_recomendado']}")

# CÁLCULO Y VISUALIZACIÓN DE COSTOS
st.markdown("---")
st.subheader("💰 Análisis de Costos de la Operación")

costos = calcular_costos(producto_seleccionado, pais_destino, valor_fob, incoterm_final, peso_tons)

# Crear DataFrame para mejor visualización
df_costos = pd.DataFrame([
    {"Concepto": concepto, "Valor (USD)": valor, "Porcentaje": (valor/sum(costos.values()))*100}
    for concepto, valor in costos.items()
])

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.metric("Costo Total", f"USD {sum(costos.values()):,.0f}")
    
with col2:
    margen_sugerido = sum(costos.values()) * 0.15
    st.metric("Margen sugerido (15%)", f"USD {margen_sugerido:,.0f}")
    
with col3:
    precio_venta = sum(costos.values()) + margen_sugerido
    st.metric("Precio de venta sugerido", f"USD {precio_venta:,.0f}")

# Gráficos
col1, col2 = st.columns([1, 1])

with col1:
    # Gráfico de torta
    fig_pie = px.pie(
        df_costos, 
        values='Valor (USD)', 
        names='Concepto',
        title=f"Distribución de Costos - {incoterm_final}",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Gráfico de barras
    fig_bar = px.bar(
        df_costos.sort_values('Valor (USD)', ascending=True),
        x='Valor (USD)',
        y='Concepto',
        orientation='h',
        title="Desglose de Costos (USD)",
        color='Valor (USD)',
        color_continuous_scale='Blues'
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# Tabla detallada
st.subheader("📋 Desglose Detallado de Costos")
st.dataframe(
    df_costos.style.format({
        'Valor (USD)': '{:,.0f}',
        'Porcentaje': '{:.1f}%'
    }),
    use_container_width=True
)

# COMPARATIVA DE INCOTERMS
st.markdown("---")
st.subheader("⚖️ Comparativa de Incoterms para esta Operación")

# Calcular costos para diferentes Incoterms
incoterms_principales = ["EXW", "FOB", "CFR", "CIF", "DAP"]
comparativa_data = []

for inco in incoterms_principales:
    costos_inco = calcular_costos(producto_seleccionado, pais_destino, valor_fob, inco, peso_tons)
    total_vendedor = sum(costos_inco.values())
    
    # Calcular qué paga el vendedor vs comprador según Incoterm
    if inco == "EXW":
        vendedor_paga = costos_inco["Valor FOB"] + costos_inco["Gestión bancaria"] + costos_inco["Certificaciones"]
    elif inco in ["FOB", "FCA"]:
        vendedor_paga = total_vendedor - costos_inco["Flete marítimo"] - costos_inco["Seguro"] - costos_inco["Aranceles"] - costos_inco["Despacho importación"]
    elif inco in ["CFR", "CPT"]:
        vendedor_paga = total_vendedor - costos_inco["Seguro"] - costos_inco["Aranceles"] - costos_inco["Despacho importación"]
    elif inco in ["CIF", "CIP"]:
        vendedor_paga = total_vendedor - costos_inco["Aranceles"] - costos_inco["Despacho importación"]
    else:  # DAP, DPU, DDP
        vendedor_paga = total_vendedor
    
    comparativa_data.append({
        "Incoterm": inco,
        "Vendedor paga (USD)": vendedor_paga,
        "Costo total (USD)": total_vendedor,
        "Riesgo vendedor": INCOTERMS_DATA[inco]["riesgo_costo"]
    })

df_comparativa = pd.DataFrame(comparativa_data)

# Gráfico comparativo
fig_comp = px.bar(
    df_comparativa,
    x="Incoterm",
    y="Vendedor paga (USD)",
    title="Comparativa: Costo para el Vendedor según Incoterm",
    color="Vendedor paga (USD)",
    color_continuous_scale="RdYlBu_r",
    text="Vendedor paga (USD)"
)
fig_comp.update_traces(texttemplate='%{text:$,.0f}', textposition='outside')
fig_comp.update_layout(showlegend=False)
st.plotly_chart(fig_comp, use_container_width=True)

# Tabla comparativa
st.dataframe(
    df_comparativa.style.format({
        'Vendedor paga (USD)': '${:,.0f}',
        'Costo total (USD)': '${:,.0f}'
    }),
    use_container_width=True
)

# INSIGHTS EDUCATIVOS
st.markdown("---")
st.subheader("🎓 Insights Educativos")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 💡 ¿Sabías qué?")
    
    insights = [
        f"🇺🇾 Uruguay exportó USD 12.845 millones en 2024, un crecimiento del 13%",
        f"🏭 La celulosa desplazó a la carne como principal producto de exportación",
        f"🌏 China se mantiene como principal socio comercial (24% de exportaciones)",
        f"🤝 El acuerdo UE-MERCOSUR liberalizará el 92% de las importaciones",
        f"📦 {len(PRODUCTOS_URUGUAYOS)} productos representan el 80% de las exportaciones"
    ]
    
    for insight in insights:
        st.markdown(f"- {insight}")

with col2:
    st.markdown("### 🔍 Análisis de esta Operación")
    
    # Análisis específico
    if pais_info["acuerdo"] == "MERCOSUR":
        st.success("✅ **Ventaja:** Arancel 0% por MERCOSUR")
    elif "UE-MERCOSUR" in pais_info["acuerdo"]:
        st.success("✅ **Ventaja:** Preferencias por nuevo acuerdo UE-MERCOSUR")
    elif "ACE" in pais_info["acuerdo"]:
        st.warning("⚠️ **Neutral:** Preferencias limitadas por ACE")
    else:
        st.error("❌ **Desventaja:** Sin preferencias arancelarias")
    
    # Recomendaciones
    precio_por_ton = valor_fob / peso_tons
    if precio_por_ton > 1000:
        st.info("💰 **Producto de alto valor:** Considere CIF para mayor control")
    else:
        st.info("📦 **Commodity:** FOB suele ser más eficiente")

# PIE DE PÁGINA
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Simulador de Comercio Internacional</strong><br>
    Universidad ORT Uruguay | Desarrollado para Operativa y Procedimientos del Comercio Internacional<br>
    Datos basados en información de Uruguay XXI y acuerdos comerciales vigentes (2024)</p>
</div>
""", unsafe_allow_html=True)