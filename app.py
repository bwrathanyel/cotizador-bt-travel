import streamlit as st
import sqlite3
import re
import json
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Cotizador BT Travel · Lotus 360",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================================
# CSS - DISEÑO COMPACTO Y OPTIMIZADO PARA MÓVIL
# ======================================================

st.markdown("""
<style>
    /* ========== BASE ========== */
    .stApp { background: #080c18; }
    .main { 
        background: #080c18; 
        padding: 0.6rem 0.8rem 2rem !important; 
        max-width: 100%;
    }
    header[data-testid="stHeader"] { display: none; }
    
    /* ========== SLIDER DE DESTINOS ========== */
    .destino-slider {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 6px 8px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 2px;
        flex-wrap: nowrap;
        overflow-x: auto;
        scrollbar-width: none;
        min-height: 44px;
    }
    .destino-slider::-webkit-scrollbar { display: none; }
    
    .destino-btn {
        flex: 0 0 auto;
        background: transparent !important;
        border: 1px solid transparent !important;
        color: rgba(255, 255, 255, 0.3) !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        padding: 5px 12px !important;
        border-radius: 20px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        white-space: nowrap !important;
        font-family: inherit !important;
        min-height: 30px;
        line-height: 1.2;
    }
    .destino-btn:hover {
        color: #fff !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }
    .destino-btn.activo {
        color: #fff !important;
        background: rgba(255, 145, 0, 0.15) !important;
        border-color: rgba(255, 145, 0, 0.2) !important;
        font-weight: 600;
    }
    .destino-btn .badge-destino {
        font-size: 6px;
        padding: 1px 6px;
        border-radius: 8px;
        margin-left: 4px;
        font-weight: 700;
        background: rgba(255, 145, 0, 0.1);
        color: #ff9100;
    }

    /* ========== SUGERENCIA ========== */
    .sugerencia-box {
        background: rgba(255, 145, 0, 0.04);
        border: 1px solid rgba(255, 145, 0, 0.06);
        border-radius: 14px;
        padding: 8px 14px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 4px;
        font-size: 12px;
    }
    .sugerencia-box .label {
        color: rgba(255, 255, 255, 0.25);
        font-size: 9px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .sugerencia-box .texto {
        color: rgba(255, 255, 255, 0.6);
        font-size: 12px;
    }
    .sugerencia-box .texto strong { color: #ffb74d; }

    /* ========== FORMULARIO ========== */
    .form-moderno {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 20px;
        padding: 14px 14px;
        margin-bottom: 14px;
    }
    .form-moderno .stTextInput input,
    .form-moderno .stNumberInput input,
    .form-moderno .stSelectbox select,
    .form-moderno .stDateInput input {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 10px !important;
        color: #fff !important;
        padding: 8px 12px !important;
        font-size: 13px !important;
        min-height: 36px !important;
        transition: all 0.3s ease !important;
    }
    .form-moderno .stTextInput input:focus,
    .form-moderno .stNumberInput input:focus,
    .form-moderno .stSelectbox select:focus,
    .form-moderno .stDateInput input:focus {
        border-color: rgba(255, 145, 0, 0.3) !important;
        box-shadow: 0 0 0 3px rgba(255, 145, 0, 0.04) !important;
    }
    .form-moderno .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.15);
    }
    .form-moderno label {
        color: rgba(255, 255, 255, 0.25) !important;
        font-size: 10px !important;
        font-weight: 500 !important;
        margin-bottom: 2px !important;
    }
    .form-moderno .stSelectbox div[data-baseweb="select"] {
        min-height: 36px !important;
    }
    .form-moderno .stDateInput div[data-baseweb="input"] {
        min-height: 36px !important;
    }
    .form-moderno .stNumberInput div[data-baseweb="input"] {
        min-height: 36px !important;
    }

    /* ========== BOTÓN ========== */
    .btn-cotizar {
        background: linear-gradient(135deg, #ff9100, #f57c00, #ef6c00) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 12px 20px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #fff !important;
        box-shadow: 0 4px 20px rgba(255, 145, 0, 0.2) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        min-height: 44px;
    }
    .btn-cotizar:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 28px rgba(255, 145, 0, 0.3) !important;
    }
    .btn-cotizar:active { transform: scale(0.97) !important; }

    /* ========== BADGES ========== */
    .badge-moderno {
        display: inline-block;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 14px;
        padding: 2px 10px;
        font-size: 9px;
        color: rgba(255, 255, 255, 0.25);
        margin-right: 3px;
        margin-bottom: 4px;
    }
    .badge-moderno i { color: #ff9100; margin-right: 3px; opacity: 0.5; font-size: 8px; }

    .promocion-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border-radius: 10px;
        padding: 2px 10px;
        font-size: 9px;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.06);
    }
    .vigencia-badge {
        display: inline-block;
        background: rgba(74, 158, 255, 0.07);
        color: #4a9eff;
        border-radius: 10px;
        padding: 2px 10px;
        font-size: 9px;
        font-weight: 600;
        border: 1px solid rgba(74, 158, 255, 0.05);
    }
    .temporada-badge {
        display: inline-block;
        background: rgba(255, 183, 77, 0.07);
        color: #ffb74d;
        border-radius: 10px;
        padding: 2px 10px;
        font-size: 9px;
        font-weight: 600;
        border: 1px solid rgba(255, 183, 77, 0.05);
    }

    /* ========== TARJETA DE RESULTADOS ========== */
    .result-card-moderno {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 14px 16px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }
    .result-card-moderno:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(255, 145, 0, 0.06);
    }
    .result-card-moderno .header-result {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }
    .result-card-moderno .header-result .titulo-pagina {
        font-weight: 600;
        color: #fff;
        font-size: 14px;
    }
    .result-card-moderno .pagina-badge {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 8px;
        color: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.02);
    }

    /* ========== DESGLOSE ========== */
    .desglose-box {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 14px;
        padding: 12px 16px;
        margin: 6px 0 4px;
    }
    .desglose-box .fila {
        display: flex;
        justify-content: space-between;
        padding: 3px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.02);
        font-size: 12px;
        color: rgba(255, 255, 255, 0.4);
    }
    .desglose-box .fila:last-child { border-bottom: none; }
    .desglose-box .fila .label {
        color: rgba(255, 255, 255, 0.3);
        font-size: 11px;
    }
    .desglose-box .fila .valor {
        color: rgba(255, 255, 255, 0.6);
        font-weight: 500;
        font-size: 12px;
    }
    .desglose-box .fila.total {
        border-top: 2px solid rgba(255, 145, 0, 0.1);
        padding-top: 8px;
        margin-top: 4px;
    }
    .desglose-box .fila.total .label {
        color: #ffb74d;
        font-weight: 700;
        font-size: 13px;
    }
    .desglose-box .fila.total .valor {
        color: #ff9100;
        font-weight: 700;
        font-size: 18px;
    }
    .desglose-box .formula {
        text-align: right;
        font-size: 8px;
        color: rgba(255, 255, 255, 0.04);
        margin-top: 4px;
    }

    /* ========== DIVISORES ========== */
    .divider-lotus {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 12px 0 10px;
        opacity: 0.08;
    }
    .divider-lotus::before,
    .divider-lotus::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 145, 0, 0.15), transparent);
    }
    .divider-lotus .icono-divider { color: #ff9100; font-size: 8px; }

    /* ========== TÍTULOS ========== */
    h1 {
        color: #fff !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        background: linear-gradient(135deg, #ff9100, #ffb74d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0 !important;
    }
    .sub-header {
        color: rgba(255, 255, 255, 0.08);
        font-size: 10px;
        font-weight: 400;
        margin-top: -2px;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }
    h3 {
        color: #fff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 8px !important;
    }

    /* ========== MÉTRICAS ========== */
    .stMetric {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 6px 4px;
        border: 1px solid rgba(255, 255, 255, 0.02);
    }
    .stMetric label {
        color: rgba(255, 255, 255, 0.15) !important;
        font-size: 9px !important;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .stMetric .stMetricValue {
        color: #fff !important;
        font-weight: 600 !important;
        font-size: 18px !important;
    }

    /* ========== FOOTER ========== */
    .footer-2026 {
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.02);
        text-align: center;
        font-size: 8px;
        color: rgba(255, 255, 255, 0.03);
        letter-spacing: 1px;
    }

    /* ========== RESPONSIVE ========== */
    @media (max-width: 768px) {
        .main { padding: 0.4rem 0.5rem 1.5rem !important; }
        .form-moderno { padding: 10px 10px; border-radius: 16px; }
        .result-card-moderno { padding: 10px 12px; border-radius: 14px; }
        .destino-btn { font-size: 10px !important; padding: 4px 10px !important; }
        .desglose-box { padding: 10px 12px; }
        .desglose-box .fila.total .valor { font-size: 16px; }
        h1 { font-size: 1.2rem !important; }
        .btn-cotizar { font-size: 14px !important; padding: 10px 16px !important; }
        .stMetric .stMetricValue { font-size: 16px !important; }
        .stMetric { padding: 4px 2px; }
    }
    
    @media (max-width: 400px) {
        .destino-btn { font-size: 9px !important; padding: 3px 8px !important; }
        .form-moderno { padding: 8px 8px; }
        .badge-moderno { font-size: 8px; padding: 1px 8px; }
        h1 { font-size: 1rem !important; }
        .sub-header { font-size: 9px; }
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER COMPACTO
# ======================================================

col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://bwrathanyel.github.io/redireccion-whatsapp/logolotus.png", width=40)
with col2:
    st.markdown("<h1>✈️ Cotizador BT Travel</h1>", unsafe_allow_html=True)
    st.markdown('<p class="sub-header">✨ Tarifas al instante · Lotus 360</p>', unsafe_allow_html=True)

# ======================================================
# SLIDER DE DESTINOS (MÁS COMPACTO)
# ======================================================

destinos = [
    {"nombre": "Margarita", "emoji": "🏖️", "badge": "Pop"},
    {"nombre": "Morrocoy", "emoji": "🐠", "badge": "Playas"},
    {"nombre": "Los Roques", "emoji": "🏝️", "badge": "Excl"},
    {"nombre": "Mérida", "emoji": "🚡", "badge": "Mont"},
    {"nombre": "Canaima", "emoji": "💧", "badge": "Avent"},
    {"nombre": "Colonia Tovar", "emoji": "🏘️", "badge": "Pueblo"},
    {"nombre": "Costa Caribe", "emoji": "🌊", "badge": "Hotel"},
    {"nombre": "Los Llanos", "emoji": "🌿", "badge": "Natur"},
]

if "destino_seleccionado" not in st.session_state:
    st.session_state.destino_seleccionado = "Margarita"

st.markdown('<div class="destino-slider">', unsafe_allow_html=True)
cols = st.columns(len(destinos))
for i, d in enumerate(destinos):
    with cols[i]:
        if st.button(
            f"{d['emoji']} {d['nombre']}",
            key=f"btn_{d['nombre']}",
            use_container_width=True,
            type="secondary" if d["nombre"] != st.session_state.destino_seleccionado else "primary"
        ):
            st.session_state.destino_seleccionado = d["nombre"]
            st.rerun()
        st.markdown(
            f'<div style="text-align:center;margin-top:-3px;font-size:6px;color:rgba(255,255,255,0.06);">#{d["badge"]}</div>',
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# SUGERENCIA
# ======================================================

sugerencias = {
    "Margarita": {"noches": 4, "adultos": 2, "ninos": 0, "texto": "🌴 4 noches · 2 adultos · Playas"},
    "Morrocoy": {"noches": 2, "adultos": 2, "ninos": 2, "texto": "🐠 2 noches · 2+2 niños · Familias"},
    "Los Roques": {"noches": 3, "adultos": 2, "ninos": 0, "texto": "🏝️ 3 noches · 2 adultos · Romántico"},
    "Mérida": {"noches": 3, "adultos": 2, "ninos": 1, "texto": "🚡 3 noches · 2+1 · Montaña"},
    "Canaima": {"noches": 2, "adultos": 2, "ninos": 0, "texto": "💧 2 noches · 2 adultos · Aventura"},
    "Colonia Tovar": {"noches": 2, "adultos": 2, "ninos": 0, "texto": "🏘️ 2 noches · 2 adultos · Fresas"},
    "Costa Caribe": {"noches": 3, "adultos": 2, "ninos": 2, "texto": "🌊 3 noches · 2+2 · Todo Incluido"},
    "Los Llanos": {"noches": 2, "adultos": 2, "ninos": 0, "texto": "🌿 2 noches · 2 adultos · Naturaleza"},
}

sug = sugerencias.get(st.session_state.destino_seleccionado, {"noches": 3, "adultos": 2, "ninos": 0, "texto": "✨ Explora este destino"})

st.markdown(f"""
<div class="sugerencia-box">
    <div>
        <span class="label">💡 Sugerencia</span>
        <span class="texto">{sug['texto']}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ======================================================
# FORMULARIO COMPACTO
# ======================================================

with st.container():
    st.markdown('<div class="form-moderno">', unsafe_allow_html=True)
    
    with st.form(key="formulario_cotizacion"):
        col1, col2 = st.columns(2)
        
        with col1:
            hoteles_margarita = [
                "🏨 Hotel Costa Caribe",
                "🏨 LD Palm Beach",
                "🏨 Hesperia Playa el Agua",
                "🏨 Margarita Village",
                "🏨 Hotel Sunsol",
                "🏨 Hotel Hesperia Isla de Margarita",
                "✏️ Otro"
            ]
            
            if st.session_state.destino_seleccionado == "Margarita":
                st.markdown('<p style="color:rgba(255,255,255,0.25);font-size:10px;font-weight:500;margin-bottom:2px;">🏨 Hotel</p>', unsafe_allow_html=True)
                hotel_seleccionado = st.selectbox(
                    "Hotel",
                    options=hoteles_margarita,
                    index=0,
                    label_visibility="collapsed"
                )
                
                if hotel_seleccionado == "✏️ Otro":
                    hotel_input = st.text_input(
                        "Otro hotel",
                        placeholder="Escribe el nombre",
                        label_visibility="collapsed"
                    )
                    hotel_final = hotel_input if hotel_input else ""
                else:
                    hotel_final = hotel_seleccionado.replace("🏨 ", "")
            else:
                hotel_final = st.text_input(
                    "📍 Hospedaje",
                    value=st.session_state.destino_seleccionado,
                    placeholder="Hotel o destino",
                    label_visibility="collapsed"
                )
            
            fecha_entrada = st.date_input(
                "📅 Llegada",
                value=datetime.now() + timedelta(days=7),
                label_visibility="collapsed"
            )
        
        with col2:
            noches = st.number_input(
                "🌙 Noches",
                min_value=1,
                max_value=30,
                value=sug['noches'],
                label_visibility="collapsed"
            )
            adultos = st.number_input(
                "👤 Adultos",
                min_value=1,
                max_value=10,
                value=sug['adultos'],
                label_visibility="collapsed"
            )
            ninos = st.number_input(
                "🧒 Niños",
                min_value=0,
                max_value=8,
                value=sug['ninos'],
                label_visibility="collapsed"
            )
            regimen = st.selectbox(
                "🍽️ Régimen",
                options=["Todos incluidos", "Media pensión", "Pensión completa", "Solo alojamiento"],
                label_visibility="collapsed"
            )
        
        # Comando de voz compacto
        comando_voz = st.text_input(
            "🎤 Voz",
            placeholder='Ej: "Margarita, 4 adultos, 2 niños, 3 noches"',
            label_visibility="collapsed"
        )
        
        buscar = st.form_submit_button(
            "💰 Cotizar Presupuesto",
            type="primary",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# DIVISOR
# ======================================================

st.markdown("""
<div class="divider-lotus">
    <span class="icono-divider">✦</span>
    <span class="icono-divider">✦</span>
    <span class="icono-divider">✦</span>
</div>
""", unsafe_allow_html=True)

# ======================================================
# PROCESAR BÚSQUEDA
# ======================================================

if buscar:
    if st.session_state.destino_seleccionado == "Margarita":
        if hotel_final and hotel_final != "":
            destino_final = hotel_final
        else:
            destino_final = "Margarita"
    else:
        destino_final = hotel_final if hotel_final else st.session_state.destino_seleccionado

    if comando_voz and not destino_final:
        texto = comando_voz.lower()
        for d in destinos:
            if d["nombre"].lower() in texto:
                destino_final = d["nombre"]
                break
        numeros = re.findall(r'\d+', texto)
        if len(numeros) >= 1:
            adultos = int(numeros[0]) if len(numeros) >= 1 else adultos
        if len(numeros) >= 2:
            ninos = int(numeros[1]) if len(numeros) >= 2 else ninos
        if len(numeros) >= 3:
            noches = int(numeros[2]) if len(numeros) >= 3 else noches
        st.info(f"🎤 Procesado: **{destino_final}**, {adultos} adultos, {ninos} niños, {noches} noches")

    if not destino_final:
        st.warning("⚠️ Selecciona o escribe un hospedaje")
    else:
        with st.spinner("🔍 Buscando..."):
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
                    LIMIT 10
                """, (
                    f'%{destino_final}%',
                    f'%{destino_final.upper()}%',
                    f'%{destino_final.lower()}%'
                ))
                
                resultados = cursor.fetchall()
                conn.close()
                
                if resultados:
                    resultados_validos = []
                    for row in resultados:
                        sgl, dbl, tpl, cdp, qpl = row[5], row[6], row[7], row[8], row[9]
                        if sgl or dbl or tpl or cdp or qpl:
                            resultados_validos.append(row)
                    
                    if not resultados_validos:
                        st.warning("😕 Sin tarifas disponibles para estos datos")
                        st.info("💡 Prueba con otro hotel o ajusta las fechas")
                    else:
                        st.markdown(f'<h3>✅ {len(resultados_validos)} ofertas</h3>', unsafe_allow_html=True)
                        
                        # Badges compactos
                        col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
                        with col_b1:
                            st.markdown(f'<span class="badge-moderno"><i class="fas fa-hotel"></i>{destino_final[:12]}</span>', unsafe_allow_html=True)
                        with col_b2:
                            st.markdown(f'<span class="badge-moderno"><i class="fas fa-user"></i>{adultos}</span>', unsafe_allow_html=True)
                        with col_b3:
                            st.markdown(f'<span class="badge-moderno"><i class="fas fa-child"></i>{ninos}</span>', unsafe_allow_html=True)
                        with col_b4:
                            st.markdown(f'<span class="badge-moderno"><i class="fas fa-moon"></i>{noches}</span>', unsafe_allow_html=True)
                        with col_b5:
                            st.markdown(f'<span class="badge-moderno"><i class="fas fa-utensils"></i>{"".join(regimen[:2])}</span>', unsafe_allow_html=True)
                        
                        for row in resultados_validos:
                            hotel, pagina, regimen_bd, vigencia_ini, vigencia_fin, sgl, dbl, tpl, cdp, qpl, chd, inf, promociones_json, condiciones_json = row
                            
                            precio_base = dbl or sgl or tpl or cdp or qpl or 0
                            total_personas = adultos + ninos
                            promociones = json.loads(promociones_json) if promociones_json else []
                            condiciones = json.loads(condiciones_json) if condiciones_json else []
                            
                            if precio_base > 0:
                                tiene_ninos_gratis = any("Niños gratis" in p for p in promociones) or any("GRATIS" in str(p).upper() for p in promociones)
                                
                                if tiene_ninos_gratis and ninos > 0:
                                    costo_por_noche = adultos * precio_base
                                else:
                                    costo_por_noche = total_personas * precio_base
                                
                                subtotal = costo_por_noche * noches
                                total_texto = f"${subtotal:,.2f} USD"
                                precio_mostrado = f"${precio_base:.2f} USD"
                                subtotal_texto = f"${costo_por_noche:.2f} USD"
                            else:
                                total_texto = "N/A"
                                precio_mostrado = "N/A"
                                subtotal_texto = "N/A"
                            
                            with st.container():
                                col_h1, col_h2 = st.columns([3, 1])
                                with col_h1:
                                    st.markdown(f"**🏨 {hotel}**")
                                with col_h2:
                                    st.markdown(f'<span class="pagina-badge">📄 {pagina}</span>', unsafe_allow_html=True)
                                
                                # Badges de info compactos
                                badge_html = ""
                                if vigencia_ini:
                                    badge_html += f'<span class="vigencia-badge">📅 {vigencia_ini[:5]}→{vigencia_fin[:5] if vigencia_fin else ""}</span>'
                                if regimen_bd:
                                    badge_html += f'<span class="temporada-badge">🍽️ {regimen_bd[:8]}</span>'
                                for p in promociones[:1]:
                                    badge_html += f'<span class="promocion-badge">🎁 {p[:12]}</span>'
                                if badge_html:
                                    st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin:2px 0 6px;">{badge_html}</div>', unsafe_allow_html=True)
                                
                                # Precios por habitación
                                precios_habitacion = {}
                                if sgl: precios_habitacion["SGL"] = sgl
                                if dbl: precios_habitacion["DBL"] = dbl
                                if tpl: precios_habitacion["TPL"] = tpl
                                if cdp: precios_habitacion["CDP"] = cdp
                                if qpl: precios_habitacion["QPL"] = qpl
                                
                                if precios_habitacion:
                                    habitacion_text = " | ".join([f"{hab}: ${p:.0f}" for hab, p in precios_habitacion.items()])
                                    st.caption(f"🏷️ {habitacion_text}")
                                
                                if tiene_ninos_gratis and ninos > 0:
                                    st.markdown(f'<span class="promocion-badge" style="font-size:10px;">🎁 ¡Niños gratis!</span>', unsafe_allow_html=True)
                                
                                st.markdown(f"""
                                <div class="desglose-box">
                                    <div class="fila">
                                        <span class="label">💰 Por persona/noche</span>
                                        <span class="valor">{precio_mostrado}</span>
                                    </div>
                                    <div class="fila">
                                        <span class="label">👥 Total personas</span>
                                        <span class="valor">{total_personas} ({adultos}+{ninos})</span>
                                    </div>
                                    <div class="fila" style="border-bottom:1px solid rgba(255,255,255,0.04);">
                                        <span class="label">🌙 Noches</span>
                                        <span class="valor">{noches}</span>
                                    </div>
                                    <div class="fila" style="color:rgba(255,255,255,0.4);font-size:11px;">
                                        <span class="label">Subtotal/noche</span>
                                        <span class="valor">{subtotal_texto}</span>
                                    </div>
                                    <div class="fila total">
                                        <span class="label">💰 Total</span>
                                        <span class="valor">{total_texto}</span>
                                    </div>
                                    <div class="formula">{precio_mostrado} × {total_personas} × {noches}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.divider()
                        
                        st.markdown("---")
                        st.markdown("### 📊 Resumen")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📍 Hotel", destino_final.title()[:15])
                        with col2:
                            st.metric("🌙 Noches", noches)
                        with col3:
                            st.metric("👤 Adultos", adultos)
                        with col4:
                            st.metric("🧒 Niños", ninos)
                        
                        st.info("💡 Confirma tarifas con el PDF original", icon="ℹ️")
                else:
                    st.warning(f"😕 No encontré '{destino_final}'")
                    st.info("💡 Prueba con: 'hotel', 'precio' u otro destino")
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.info("💡 Ejecuta 'python extractor.py' primero")

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class="footer-2026">
    ✦ BT Travel · Lotus 360 ✦
    <br>
    © 2026 · Carabobo, Venezuela
</div>
""", unsafe_allow_html=True)