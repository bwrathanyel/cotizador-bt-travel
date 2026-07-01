import streamlit as st
import sqlite3
import re
import json
from datetime import datetime, timedelta

# ======================================================
# CONFIGURACIÓN DE PÁGINA
# ======================================================

st.set_page_config(
    page_title="Cotizador BT Travel · Lotus 360",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================================
# ESTILOS CSS PREMIUM
# ======================================================

st.markdown("""
<style>
    /* ========== BASE ========== */
    .stApp { background: #080c18; }
    .main { padding: 1rem 1.5rem 2rem !important; }
    header[data-testid="stHeader"] { display: none; }
    
    /* ========== SKIP LINK (accesibilidad) ========== */
    .skip-link {
        position: absolute;
        top: -40px;
        left: 0;
        background: #ff9100;
        color: #fff;
        padding: 8px;
        z-index: 100;
        transition: top 0.2s;
    }
    .skip-link:focus { top: 0; }
    
    /* ========== HEADER ========== */
    .lotus-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 1px solid rgba(255, 145, 0, 0.08);
    }
    .lotus-header .logo {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        border: 2px solid rgba(255, 145, 0, 0.3);
        padding: 2px;
        background: #fff;
    }
    .lotus-header h1 {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #ff9100, #ffb74d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 !important;
    }
    .lotus-header .subtitle {
        color: rgba(255, 255, 255, 0.2);
        font-size: 10px;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    
    /* ========== ESTADO EN LÍNEA ========== */
    .estado-box {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 30px;
        padding: 4px 12px;
        font-size: 10px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.4);
    }
    .dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        flex-shrink: 0;
        animation: dot-breathe 1.8s infinite;
    }
    .dot.online { background: #25D366; }
    @keyframes dot-breathe {
        0% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.5); }
        70% { box-shadow: 0 0 0 5px rgba(37, 211, 102, 0); }
        100% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); }
    }
    
    /* ========== SLIDER DE DESTINOS ========== */
    .destino-slider {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 16px;
        padding: 8px;
        margin-bottom: 16px;
    }
    .destino-slider .stButton button {
        background: transparent !important;
        border: 1px solid transparent !important;
        color: rgba(255, 255, 255, 0.3) !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        padding: 6px 10px !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
        min-height: 32px !important;
    }
    .destino-slider .stButton button:hover {
        color: #fff !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    .destino-slider .stButton button[data-selected="true"] {
        color: #fff !important;
        background: rgba(255, 145, 0, 0.12) !important;
        border-color: rgba(255, 145, 0, 0.25) !important;
        font-weight: 600 !important;
        box-shadow: 0 0 12px rgba(255, 145, 0, 0.08) !important;
    }
    
    /* ========== SUGERENCIA ========== */
    .sugerencia-box {
        background: rgba(255, 145, 0, 0.03);
        border: 1px solid rgba(255, 145, 0, 0.06);
        border-radius: 14px;
        padding: 10px 16px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .sugerencia-box .emoji { font-size: 20px; }
    .sugerencia-box .label {
        color: rgba(255, 255, 255, 0.2);
        font-size: 9px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .sugerencia-box .texto {
        color: rgba(255, 255, 255, 0.6);
        font-size: 12px;
    }
    .sugerencia-box .texto strong { color: #ffb74d; }
    
    /* ========== FORMULARIO ========== */
    .form-section {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .form-section .section-title {
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: rgba(255, 145, 0, 0.6);
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .form-section .section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(255, 145, 0, 0.08);
    }
    
    /* ========== INPUTS ========== */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox select,
    .stDateInput input {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        color: #fff !important;
        padding: 10px 14px !important;
        font-size: 13px !important;
        min-height: 40px !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stSelectbox select:focus,
    .stDateInput input:focus {
        border-color: rgba(255, 145, 0, 0.3) !important;
        box-shadow: 0 0 0 3px rgba(255, 145, 0, 0.05) !important;
    }
    .stTextInput input::placeholder { color: rgba(255, 255, 255, 0.12); }
    
    /* ========== LABELS ========== */
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stDateInput label {
        color: rgba(255, 255, 255, 0.3) !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        margin-bottom: 4px !important;
    }
    
    /* ========== BOTÓN PRINCIPAL ========== */
    .btn-cotizar {
        background: linear-gradient(135deg, #ff9100, #f57c00) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 14px 24px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #fff !important;
        box-shadow: 0 4px 20px rgba(255, 145, 0, 0.2) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        min-height: 48px;
    }
    .btn-cotizar:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 28px rgba(255, 145, 0, 0.35) !important;
    }
    .btn-cotizar:active {
        transform: scale(0.97) !important;
    }
    
    /* ========== BADGES ========== */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 3px 10px;
        font-size: 9px;
        color: rgba(255, 255, 255, 0.35);
        margin-right: 4px;
        margin-bottom: 4px;
    }
    .badge i { color: #ff9100; opacity: 0.6; font-size: 8px; }
    .badge.promo {
        background: rgba(16, 185, 129, 0.08);
        color: #10b981;
        border-color: rgba(16, 185, 129, 0.1);
    }
    .badge.vigencia {
        background: rgba(74, 158, 255, 0.06);
        color: #4a9eff;
        border-color: rgba(74, 158, 255, 0.08);
    }
    
    /* ========== RESULTADOS ========== */
    .result-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 18px;
        padding: 18px;
        margin: 10px 0;
        transition: all 0.2s ease;
    }
    .result-card:hover {
        background: rgba(255, 255, 255, 0.03);
        border-color: rgba(255, 145, 0, 0.08);
    }
    .result-card .hotel-nombre {
        font-weight: 600;
        color: #fff;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .result-card .pagina-badge {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        padding: 2px 8px;
        font-size: 8px;
        color: rgba(255, 255, 255, 0.15);
    }
    
    /* ========== DESGLOSE ========== */
    .desglose-box {
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 14px;
        padding: 14px 18px;
        margin: 8px 0;
    }
    .desglose-box .fila {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.02);
        font-size: 12px;
    }
    .desglose-box .fila:last-child { border-bottom: none; }
    .desglose-box .fila .label {
        color: rgba(255, 255, 255, 0.3);
        font-size: 11px;
    }
    .desglose-box .fila .valor {
        color: rgba(255, 255, 255, 0.6);
        font-weight: 500;
    }
    .desglose-box .fila.total {
        border-top: 2px solid rgba(255, 145, 0, 0.15);
        padding-top: 10px;
        margin-top: 6px;
    }
    .desglose-box .fila.total .label {
        color: #ffb74d;
        font-weight: 700;
        font-size: 13px;
    }
    .desglose-box .fila.total .valor {
        color: #ff9100;
        font-weight: 700;
        font-size: 20px;
    }
    .desglose-box .formula {
        text-align: right;
        font-size: 8px;
        color: rgba(255, 255, 255, 0.06);
        margin-top: 6px;
    }
    
    /* ========== DIVIDER ========== */
    .divider {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 20px 0;
        opacity: 0.06;
    }
    .divider::before,
    .divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, #ff9100, transparent);
    }
    .divider .icon { color: #ff9100; font-size: 8px; }
    
    /* ========== MÉTRICAS ========== */
    .stMetric {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 14px !important;
        padding: 10px 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
    }
    .stMetric label {
        color: rgba(255, 255, 255, 0.15) !important;
        font-size: 9px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stMetric .stMetricValue {
        color: #fff !important;
        font-weight: 600 !important;
        font-size: 20px !important;
    }
    
    /* ========== FOOTER ========== */
    .footer {
        margin-top: 24px;
        padding-top: 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.03);
        text-align: center;
        font-size: 8px;
        color: rgba(255, 255, 255, 0.06);
        letter-spacing: 1px;
    }
    
    /* ========== RESPONSIVE ========== */
    @media (max-width: 768px) {
        .main { padding: 0.5rem 0.8rem 1.5rem !important; }
        .form-section { padding: 14px; border-radius: 16px; }
        .result-card { padding: 12px; border-radius: 14px; }
        .desglose-box { padding: 10px 12px; }
        .desglose-box .fila.total .valor { font-size: 18px; }
        .lotus-header h1 { font-size: 1.2rem !important; }
        .btn-cotizar { font-size: 14px !important; padding: 12px 20px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER CON LOGO
# ======================================================

st.markdown("""
<div class="lotus-header">
    <img src="https://bwrathanyel.github.io/redireccion-whatsapp/logolotus.png" class="logo" alt="Logo Lotus 360" width="48" height="48">
    <div>
        <h1>✈️ Cotizador BT Travel</h1>
        <div class="subtitle">Tarifas al instante · Lotus 360 · Uso interno para asesores</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ======================================================
# ESTADO DEL SISTEMA
# ======================================================

col_estado, col_vacio = st.columns([1, 4])
with col_estado:
    st.markdown("""
    <div class="estado-box">
        <span class="dot online"></span>
        Sistema activo
    </div>
    """, unsafe_allow_html=True)

# ======================================================
# SLIDER DE DESTINOS
# ======================================================

destinos = [
    {"nombre": "Margarita", "emoji": "🏖️", "badge": "Popular"},
    {"nombre": "Morrocoy", "emoji": "🐠", "badge": "Playas"},
    {"nombre": "Los Roques", "emoji": "🏝️", "badge": "Exclusivo"},
    {"nombre": "Mérida", "emoji": "🚡", "badge": "Montaña"},
    {"nombre": "Canaima", "emoji": "💧", "badge": "Aventura"},
    {"nombre": "Colonia Tovar", "emoji": "🏘️", "badge": "Pueblo"},
    {"nombre": "Costa Caribe", "emoji": "🌊", "badge": "Hotel"},
    {"nombre": "Los Llanos", "emoji": "🌿", "badge": "Naturaleza"},
]

if "destino_seleccionado" not in st.session_state:
    st.session_state.destino_seleccionado = "Margarita"

st.markdown('<div class="destino-slider">', unsafe_allow_html=True)
cols = st.columns(len(destinos))
for i, d in enumerate(destinos):
    with cols[i]:
        seleccionado = d["nombre"] == st.session_state.destino_seleccionado
        if st.button(
            f"{d['emoji']} {d['nombre']}",
            key=f"destino_{d['nombre']}",
            use_container_width=True,
            type="primary" if seleccionado else "secondary"
        ):
            st.session_state.destino_seleccionado = d["nombre"]
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# SUGERENCIA INTELIGENTE
# ======================================================

sugerencias = {
    "Margarita": {"noches": 4, "adultos": 2, "ninos": 0, "emoji": "🌴", "texto": "4 noches · 2 adultos · Playas y duty free"},
    "Morrocoy": {"noches": 2, "adultos": 2, "ninos": 2, "emoji": "🐠", "texto": "2 noches · 2 adultos + 2 niños · Ideal para familias"},
    "Los Roques": {"noches": 3, "adultos": 2, "ninos": 0, "emoji": "🏝️", "texto": "3 noches · 2 adultos · Escapada romántica"},
    "Mérida": {"noches": 3, "adultos": 2, "ninos": 1, "emoji": "🚡", "texto": "3 noches · 2 adultos + 1 niño · Aventura en los Andes"},
    "Canaima": {"noches": 2, "adultos": 2, "ninos": 0, "emoji": "💧", "texto": "2 noches · 2 adultos · Expedición al Salto Ángel"},
    "Colonia Tovar": {"noches": 2, "adultos": 2, "ninos": 0, "emoji": "🏘️", "texto": "2 noches · 2 adultos · Clima primaveral y fresas"},
    "Costa Caribe": {"noches": 3, "adultos": 2, "ninos": 2, "emoji": "🌊", "texto": "3 noches · 2 adultos + 2 niños · Todo incluido"},
    "Los Llanos": {"noches": 2, "adultos": 2, "ninos": 0, "emoji": "🌿", "texto": "2 noches · 2 adultos · Naturaleza y fauna"},
}

sug = sugerencias.get(st.session_state.destino_seleccionado, {"noches": 3, "adultos": 2, "ninos": 0, "emoji": "✨", "texto": "Explora este increíble destino"})

st.markdown(f"""
<div class="sugerencia-box">
    <span class="emoji">{sug['emoji']}</span>
    <div>
        <div class="label">💡 SUGERENCIA PARA {st.session_state.destino_seleccionado.upper()}</div>
        <div class="texto">{sug['texto']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ======================================================
# FORMULARIO PRINCIPAL
# ======================================================

st.markdown('<div class="form-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 DATOS DE LA COTIZACIÓN</div>', unsafe_allow_html=True)

with st.form(key="formulario_cotizacion"):
    col1, col2 = st.columns(2)
    
    with col1:
        # Hotel específico si es Margarita
        if st.session_state.destino_seleccionado == "Margarita":
            hoteles_margarita = [
                "🏨 Hotel Costa Caribe",
                "🏨 LD Palm Beach",
                "🏨 Hesperia Playa el Agua",
                "🏨 Margarita Village",
                "🏨 Hotel Sunsol",
                "🏨 Hotel Hesperia Isla de Margarita",
                "✏️ Otro (escribir nombre)"
            ]
            
            hotel_seleccionado = st.selectbox(
                "🏨 Hotel específico",
                options=hoteles_margarita,
                index=0,
                help="Selecciona el hotel en Margarita"
            )
            
            if hotel_seleccionado == "✏️ Otro (escribir nombre)":
                hotel_final = st.text_input(
                    "✏️ Escribe el nombre del hotel",
                    placeholder="Ej: Hotel Miramar...",
                    help="Escribe el nombre exacto del hotel"
                )
            else:
                hotel_final = hotel_seleccionado.replace("🏨 ", "")
        else:
            hotel_final = st.text_input(
                "📍 Lugar de hospedaje",
                value=st.session_state.destino_seleccionado,
                placeholder="Ej: Margarita, Costa Caribe...",
                help="Escribe el nombre del lugar de hospedaje"
            )
        
        noches = st.number_input(
            "🌙 Noches de estancia",
            min_value=1,
            max_value=30,
            value=sug['noches'],
            help="¿Cuántas noches se hospedarán?"
        )
        
        regimen = st.selectbox(
            "🍽️ Régimen alimenticio",
            options=["Todos incluidos", "Media pensión", "Pensión completa", "Solo alojamiento"],
            help="Tipo de plan de alimentación"
        )
    
    with col2:
        fecha_entrada = st.date_input(
            "📅 Fecha de llegada",
            value=datetime.now() + timedelta(days=7),
            help="Selecciona la fecha de check-in"
        )
        
        adultos = st.number_input(
            "👤 Adultos",
            min_value=1,
            max_value=10,
            value=sug['adultos'],
            help="Cantidad de adultos (12+ años)"
        )
        
        ninos = st.number_input(
            "🧒 Niños",
            min_value=0,
            max_value=8,
            value=sug['ninos'],
            help="Cantidad de niños (2-11 años)"
        )
    
    # Comando de voz (opcional)
    with st.expander("🎤 Usar comando de voz (opcional)"):
        comando_voz = st.text_input(
            "🎙️ Escribe tu comando",
            placeholder='Ej: "Quiero Margarita, 4 adultos, 2 niños, 3 noches, todo incluido"',
            label_visibility="collapsed"
        )
    
    # Botón de envío
    buscar = st.form_submit_button(
        "💰 COTIZAR PRESUPUESTO",
        type="primary",
        use_container_width=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# DIVISOR
# ======================================================

st.markdown("""
<div class="divider">
    <span class="icon">✦</span>
    <span class="icon">✦</span>
    <span class="icon">✦</span>
</div>
""", unsafe_allow_html=True)

# ======================================================
# PROCESAR BÚSQUEDA
# ======================================================

if buscar:
    # Determinar destino final
    if st.session_state.destino_seleccionado == "Margarita":
        destino_final = hotel_final if hotel_final and hotel_final != "" else "Margarita"
    else:
        destino_final = hotel_final if hotel_final else st.session_state.destino_seleccionado
    
    # Procesar comando de voz
    if comando_voz and (not hotel_final or hotel_final == st.session_state.destino_seleccionado):
        texto = comando_voz.lower()
        for d in destinos:
            if d["nombre"].lower() in texto:
                destino_final = d["nombre"]
                break
        numeros = re.findall(r'\d+', texto)
        if len(numeros) >= 1: adultos = int(numeros[0])
        if len(numeros) >= 2: ninos = int(numeros[1])
        if len(numeros) >= 3: noches = int(numeros[2])
        st.info(f"🎤 Procesado: **{destino_final}** · {adultos} adultos · {ninos} niños · {noches} noches")
    
    if not destino_final:
        st.warning("⚠️ Por favor, selecciona o escribe un lugar de hospedaje")
    else:
        with st.spinner("🔍 Buscando las mejores tarifas para ti..."):
            try:
                conn = sqlite3.connect("pdf_busqueda.db")
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        h.nombre,
                        t.pagina,
                        t.regimen,
                        t.vigencia_inicio,
                        t.vigencia_fin,
                        t.sgl,
                        t.dbl,
                        t.tpl,
                        t.cdp,
                        t.qpl,
                        t.chd,
                        t.inf,
                        t.promociones,
                        t.condiciones
                    FROM tarifas t
                    JOIN hoteles h ON t.hotel_id = h.id
                    WHERE h.nombre LIKE ? OR h.nombre LIKE ? OR h.nombre LIKE ?
                    ORDER BY t.pagina
                    LIMIT 15
                """, (f'%{destino_final}%', f'%{destino_final.upper()}%', f'%{destino_final.lower()}%'))
                
                resultados = cursor.fetchall()
                conn.close()
                
                if resultados:
                    # Filtrar solo los que tienen precios
                    resultados_validos = []
                    for row in resultados:
                        sgl, dbl, tpl, cdp, qpl = row[5], row[6], row[7], row[8], row[9]
                        if sgl or dbl or tpl or cdp or qpl:
                            resultados_validos.append(row)
                    
                    if not resultados_validos:
                        st.warning("😕 No se encontraron tarifas con precios para este destino")
                        st.info("💡 Prueba con otro hotel o ajusta los parámetros de búsqueda")
                    else:
                        st.success(f"✅ {len(resultados_validos)} ofertas encontradas para **{destino_final}**")
                        
                        # Badges de resumen
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        with col_b1:
                            st.markdown(f'<span class="badge">📍 {destino_final[:15]}</span>', unsafe_allow_html=True)
                        with col_b2:
                            st.markdown(f'<span class="badge">👤 {adultos} adultos</span>', unsafe_allow_html=True)
                        with col_b3:
                            st.markdown(f'<span class="badge">🧒 {ninos} niños</span>', unsafe_allow_html=True)
                        with col_b4:
                            st.markdown(f'<span class="badge">🌙 {noches} noches</span>', unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Mostrar resultados
                        for idx, row in enumerate(resultados_validos):
                            hotel, pagina, regimen_bd, vigencia_ini, vigencia_fin, sgl, dbl, tpl, cdp, qpl, chd, inf, promociones_json, condiciones_json = row
                            
                            # Determinar precio base
                            precio_base = dbl or sgl or tpl or cdp or qpl or 0
                            total_personas = adultos + ninos
                            promociones = json.loads(promociones_json) if promociones_json else []
                            condiciones = json.loads(condiciones_json) if condiciones_json else []
                            
                            # Calcular costo
                            if precio_base > 0:
                                tiene_ninos_gratis = any("GRATIS" in str(p).upper() or "Niños gratis" in str(p) for p in promociones)
                                
                                if tiene_ninos_gratis and ninos > 0:
                                    costo_por_noche = adultos * precio_base
                                else:
                                    costo_por_noche = total_personas * precio_base
                                
                                subtotal = costo_por_noche * noches
                                total_texto = f"${subtotal:,.2f} USD"
                                precio_mostrado = f"${precio_base:.2f}"
                                subtotal_texto = f"${costo_por_noche:,.2f}"
                            else:
                                total_texto = "Consultar"
                                precio_mostrado = "N/A"
                                subtotal_texto = "N/A"
                            
                            # Tarjeta de resultado
                            st.markdown(f"""
                            <div class="result-card">
                                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                                    <div class="hotel-nombre">🏨 {hotel}</div>
                                    <span class="pagina-badge">Página {pagina}</span>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Badges
                            badge_html = ""
                            if vigencia_ini:
                                badge_html += f'<span class="badge vigencia">📅 Vigencia: {vigencia_ini[:5]} → {vigencia_fin[:5] if vigencia_fin else "Actual"}</span>'
                            if regimen_bd:
                                badge_html += f'<span class="badge">🍽️ {regimen_bd}</span>'
                            for p in promociones[:2]:
                                badge_html += f'<span class="badge promo">🎁 {p}</span>'
                            if badge_html:
                                st.markdown(f'<div style="margin:4px 0 8px;">{badge_html}</div>', unsafe_allow_html=True)
                            
                            # Precios por habitación
                            precios_habitacion = {}
                            if sgl: precios_habitacion["SGL"] = sgl
                            if dbl: precios_habitacion["DBL"] = dbl
                            if tpl: precios_habitacion["TPL"] = tpl
                            if cdp: precios_habitacion["CDP"] = cdp
                            if qpl: precios_habitacion["QPL"] = qpl
                            
                            if precios_habitacion:
                                habitacion_text = " | ".join([f"{hab}: ${p:.2f}" for hab, p in precios_habitacion.items()])
                                st.caption(f"🏷️ Precios por noche: {habitacion_text}")
                            
                            # Desglose de costos
                            st.markdown(f"""
                            <div class="desglose-box">
                                <div class="fila">
                                    <span class="label">💰 Precio por persona (noche)</span>
                                    <span class="valor">{precio_mostrado}</span>
                                </div>
                                <div class="fila">
                                    <span class="label">👥 Total personas</span>
                                    <span class="valor">{total_personas} ({adultos} adultos + {ninos} niños)</span>
                                </div>
                                <div class="fila">
                                    <span class="label">🌙 Noches</span>
                                    <span class="valor">{noches}</span>
                                </div>
                                <div class="fila">
                                    <span class="label">🍽️ Régimen</span>
                                    <span class="valor">{regimen}</span>
                                </div>
                                <div class="fila">
                                    <span class="label">Subtotal (por noche)</span>
                                    <span class="valor">{subtotal_texto}</span>
                                </div>
                                <div class="fila total">
                                    <span class="label">💰 TOTAL ESTIMADO</span>
                                    <span class="valor">{total_texto}</span>
                                </div>
                                <div class="formula">Fórmula: Precio persona × {total_personas} personas × {noches} noches</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            if idx < len(resultados_validos) - 1:
                                st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Resumen final
                        st.markdown("---")
                        st.markdown("### 📊 Resumen de la cotización")
                        col1, col2, col3, col4, col5 = st.columns(5)
                        with col1:
                            st.metric("📍 Destino", destino_final[:12])
                        with col2:
                            st.metric("🌙 Noches", noches)
                        with col3:
                            st.metric("👤 Adultos", adultos)
                        with col4:
                            st.metric("🧒 Niños", ninos)
                        with col5:
                            st.metric("🍽️ Régimen", regimen)
                        
                        st.info("💡 **Recomendación:** Revisa el PDF original para confirmar tarifas exactas y condiciones especiales.")
                else:
                    st.warning(f"😕 No se encontró información para '{destino_final}'")
                    st.info("💡 Sugerencias: verifica que el nombre esté correcto o prueba con otro destino")
                    
            except Exception as e:
                st.error(f"❌ Error al consultar la base de datos: {e}")
                st.info("💡 Asegúrate de haber ejecutado el extractor de PDF primero: `python extractor.py`")

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class="footer">
    ✦ BT Travel · Destino y Eventos Lotus 360 ✦
    <br>
    Herramienta interna para asesores · © 2026 · Carabobo, Venezuela
</div>
""", unsafe_allow_html=True)