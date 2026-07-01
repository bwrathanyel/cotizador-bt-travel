import streamlit as st
import sqlite3
import re
import json
from datetime import datetime, timedelta

# ======================================================
# CONFIGURACIÓN MOBILE-FIRST
# ======================================================

st.set_page_config(
    page_title="BT Travel · Cotizador",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "BT Travel · Lotus 360 · Herramienta para asesores"
    }
)

# ======================================================
# CSS MOBILE-FIRST (320px → 768px → 1024px)
# ======================================================

st.markdown("""
<style>
    /* ========== RESET & BASE MOBILE ========== */
    .stApp { background: #060b18; }
    .main { 
        padding: 0.3rem 0.4rem 1rem !important; 
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }
    
    /* ========== SCROLLBAR OCULTA ========== */
    * { -webkit-tap-highlight-color: transparent; }
    ::-webkit-scrollbar { width: 0; height: 0; }
    
    /* ========== HEADER COMPACTO ========== */
    .header-mobile {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 4px 6px;
        border-bottom: 1px solid rgba(255, 145, 0, 0.08);
        margin-bottom: 8px;
    }
    .header-mobile .logo {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        border: 2px solid rgba(255, 145, 0, 0.35);
        padding: 2px;
        background: #fff;
        flex-shrink: 0;
    }
    .header-mobile .info { flex: 1; min-width: 0; }
    .header-mobile .info h1 {
        font-size: 1rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #ff9100, #ffb74d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 !important;
        line-height: 1.2;
    }
    .header-mobile .info .sub {
        color: rgba(255, 255, 255, 0.18);
        font-size: 8px;
        letter-spacing: 0.5px;
    }
    
    /* ========== ESTADO ONLINE ========== */
    .online-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(37, 211, 102, 0.06);
        border: 1px solid rgba(37, 211, 102, 0.12);
        border-radius: 20px;
        padding: 2px 8px;
        font-size: 8px;
        color: rgba(37, 211, 102, 0.6);
        flex-shrink: 0;
    }
    .online-badge .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #25D366;
        animation: pulse-dot 2s infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.5); }
        50% { box-shadow: 0 0 0 6px rgba(37, 211, 102, 0); }
    }
    
    /* ========== CHIPS DE DESTINOS (SCROLL HORIZONTAL) ========== */
    .chips-scroll {
        display: flex;
        gap: 6px;
        overflow-x: auto;
        padding: 4px 2px 8px;
        margin-bottom: 10px;
        scrollbar-width: none;
        -webkit-overflow-scrolling: touch;
        scroll-behavior: smooth;
        scroll-snap-type: x mandatory;
    }
    .chips-scroll::-webkit-scrollbar { display: none; }
    
    .chip {
        flex: 0 0 auto;
        scroll-snap-align: start;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 24px;
        padding: 8px 14px;
        font-size: 11px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.4);
        white-space: nowrap;
        transition: all 0.2s ease;
        cursor: pointer;
        user-select: none;
        -webkit-user-select: none;
    }
    .chip:active {
        transform: scale(0.95);
        background: rgba(255, 145, 0, 0.12);
        border-color: rgba(255, 145, 0, 0.3);
        color: #fff;
    }
    .chip.active {
        background: rgba(255, 145, 0, 0.15);
        border-color: rgba(255, 145, 0, 0.35);
        color: #fff;
        font-weight: 600;
        box-shadow: 0 2px 12px rgba(255, 145, 0, 0.1);
    }
    
    /* ========== SUGERENCIA ========== */
    .sugerencia {
        background: rgba(255, 145, 0, 0.03);
        border: 1px solid rgba(255, 145, 0, 0.05);
        border-radius: 14px;
        padding: 10px 14px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .sugerencia .emoji { font-size: 22px; flex-shrink: 0; }
    .sugerencia .label {
        font-size: 7px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: rgba(255, 255, 255, 0.18);
        margin-bottom: 2px;
    }
    .sugerencia .texto {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.55);
        line-height: 1.3;
    }
    
    /* ========== FORMULARIO (TARJETAS) ========== */
    .form-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 18px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .form-card .card-header {
        font-size: 9px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: rgba(255, 145, 0, 0.5);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .form-card .card-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(255, 145, 0, 0.08);
    }
    
    /* ========== INPUTS OPTIMIZADOS PARA TOUCH ========== */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox select,
    .stDateInput input {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        color: #fff !important;
        padding: 12px 14px !important;
        font-size: 14px !important;
        min-height: 44px !important;
        -webkit-appearance: none !important;
        touch-action: manipulation !important;
    }
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stSelectbox select:focus,
    .stDateInput input:focus {
        border-color: rgba(255, 145, 0, 0.35) !important;
        box-shadow: 0 0 0 3px rgba(255, 145, 0, 0.04) !important;
        outline: none !important;
    }
    
    /* ========== LABELS ========== */
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stDateInput label {
        color: rgba(255, 255, 255, 0.25) !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        margin-bottom: 2px !important;
    }
    
    /* ========== EXPANDER (COMANDO DE VOZ) ========== */
    .stExpander {
        background: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
        border-radius: 14px !important;
        margin-bottom: 10px !important;
    }
    .stExpander summary {
        color: rgba(255, 255, 255, 0.3) !important;
        font-size: 10px !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
    }
    
    /* ========== BOTÓN PRINCIPAL (44px mínimo touch) ========== */
    .btn-cotizar {
        background: linear-gradient(135deg, #ff9100, #e65100) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #fff !important;
        box-shadow: 0 4px 20px rgba(255, 145, 0, 0.25) !important;
        width: 100% !important;
        min-height: 50px !important;
        touch-action: manipulation !important;
        transition: transform 0.1s ease !important;
        -webkit-tap-highlight-color: transparent !important;
    }
    .btn-cotizar:active {
        transform: scale(0.96) !important;
        box-shadow: 0 2px 10px rgba(255, 145, 0, 0.15) !important;
    }
    
    /* ========== BADGES ========== */
    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        margin: 4px 0;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 3px 8px;
        font-size: 8px;
        color: rgba(255, 255, 255, 0.3);
        white-space: nowrap;
    }
    .badge.promo {
        background: rgba(16, 185, 129, 0.08);
        color: #10b981;
        border-color: rgba(16, 185, 129, 0.12);
    }
    .badge.vigencia {
        background: rgba(74, 158, 255, 0.06);
        color: #4a9eff;
        border-color: rgba(74, 158, 255, 0.1);
    }
    
    /* ========== RESULTADO (TARJETA) ========== */
    .result-card {
        background: rgba(255, 255, 255, 0.015);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 14px;
        margin: 8px 0;
    }
    .result-card .hotel-name {
        font-weight: 600;
        color: #fff;
        font-size: 13px;
    }
    .result-card .pagina-tag {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 2px 8px;
        font-size: 7px;
        color: rgba(255, 255, 255, 0.15);
        flex-shrink: 0;
    }
    
    /* ========== DESGLOSE ========== */
    .desglose {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
    }
    .desglose .row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 3px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.015);
        font-size: 11px;
    }
    .desglose .row:last-child { border-bottom: none; }
    .desglose .row .lbl {
        color: rgba(255, 255, 255, 0.3);
        font-size: 10px;
    }
    .desglose .row .val {
        color: rgba(255, 255, 255, 0.55);
        font-weight: 500;
    }
    .desglose .row.total {
        border-top: 2px solid rgba(255, 145, 0, 0.15);
        padding-top: 10px;
        margin-top: 6px;
    }
    .desglose .row.total .lbl {
        color: #ffb74d;
        font-weight: 700;
        font-size: 12px;
    }
    .desglose .row.total .val {
        color: #ff9100;
        font-weight: 700;
        font-size: 20px;
    }
    
    /* ========== MÉTRICAS ========== */
    .stMetric {
        background: rgba(255, 255, 255, 0.015) !important;
        border-radius: 12px !important;
        padding: 8px 4px !important;
        border: 1px solid rgba(255, 255, 255, 0.02) !important;
    }
    .stMetric label {
        color: rgba(255, 255, 255, 0.12) !important;
        font-size: 7px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stMetric .stMetricValue {
        color: #fff !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    /* ========== DIVISOR ========== */
    .div {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 14px 0;
        opacity: 0.05;
    }
    .div::before, .div::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, #ff9100, transparent);
    }
    .div .d { color: #ff9100; font-size: 6px; }
    
    /* ========== FOOTER ========== */
    .ft {
        margin-top: 16px;
        padding-top: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.02);
        text-align: center;
        font-size: 7px;
        color: rgba(255, 255, 255, 0.04);
        letter-spacing: 1px;
    }
    
    /* ========== BREAKPOINTS ========== */
    @media (min-width: 768px) {
        .main { padding: 1rem 1.5rem 2rem !important; }
        .header-mobile .info h1 { font-size: 1.2rem !important; }
        .chip { font-size: 12px; padding: 10px 18px; }
        .form-card { padding: 18px; }
        .btn-cotizar { min-height: 52px; font-size: 16px; }
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER MOBILE
# ======================================================

st.markdown("""
<div class="header-mobile">
    <img src="https://bwrathanyel.github.io/redireccion-whatsapp/logolotus.png" class="logo" alt="Logo" width="34" height="34">
    <div class="info">
        <h1>✈️ BT Travel</h1>
        <div class="sub">Cotizador · Lotus 360</div>
    </div>
    <div class="online-badge"><span class="dot"></span> Activo</div>
</div>
""", unsafe_allow_html=True)

# ======================================================
# CHIPS DE DESTINOS (SCROLLABLE)
# ======================================================

destinos = [
    {"nombre": "Margarita", "emoji": "🏖️"},
    {"nombre": "Morrocoy", "emoji": "🐠"},
    {"nombre": "Los Roques", "emoji": "🏝️"},
    {"nombre": "Mérida", "emoji": "🚡"},
    {"nombre": "Canaima", "emoji": "💧"},
    {"nombre": "Colonia Tovar", "emoji": "🏘️"},
    {"nombre": "Costa Caribe", "emoji": "🌊"},
    {"nombre": "Los Llanos", "emoji": "🌿"},
]

if "destino_sel" not in st.session_state:
    st.session_state.destino_sel = "Margarita"

# Renderizar chips manualmente con HTML para mejor control táctil
chips_html = '<div class="chips-scroll">'
for d in destinos:
    active = "active" if d["nombre"] == st.session_state.destino_sel else ""
    chips_html += f'<div class="chip {active}" data-destino="{d["nombre"]}">{d["emoji"]} {d["nombre"]}</div>'
chips_html += '</div>'

st.markdown(chips_html, unsafe_allow_html=True)

# Usar botones invisibles sobre los chips para manejar selección
cols = st.columns(len(destinos))
for i, d in enumerate(destinos):
    with cols[i]:
        if st.button(
            f"{d['emoji']}",
            key=f"chip_{d['nombre']}",
            use_container_width=True,
            type="primary" if d["nombre"] == st.session_state.destino_sel else "secondary",
            help=d["nombre"]
        ):
            st.session_state.destino_sel = d["nombre"]
            st.rerun()

# ======================================================
# SUGERENCIA
# ======================================================

sugerencias = {
    "Margarita": {"noches": 4, "adultos": 2, "ninos": 0, "emoji": "🌴", "texto": "4 noches · 2 adultos · Playas y duty free"},
    "Morrocoy": {"noches": 2, "adultos": 2, "ninos": 2, "emoji": "🐠", "texto": "2 noches · 2 adultos + 2 niños · Ideal familias"},
    "Los Roques": {"noches": 3, "adultos": 2, "ninos": 0, "emoji": "🏝️", "texto": "3 noches · 2 adultos · Escapada romántica"},
    "Mérida": {"noches": 3, "adultos": 2, "ninos": 1, "emoji": "🚡", "texto": "3 noches · 2 adultos + 1 niño · Andes"},
    "Canaima": {"noches": 2, "adultos": 2, "ninos": 0, "emoji": "💧", "texto": "2 noches · 2 adultos · Salto Ángel"},
    "Colonia Tovar": {"noches": 2, "adultos": 2, "ninos": 0, "emoji": "🏘️", "texto": "2 noches · 2 adultos · Clima primaveral"},
    "Costa Caribe": {"noches": 3, "adultos": 2, "ninos": 2, "emoji": "🌊", "texto": "3 noches · 2 adultos + 2 niños · Todo incluido"},
    "Los Llanos": {"noches": 2, "adultos": 2, "ninos": 0, "emoji": "🌿", "texto": "2 noches · 2 adultos · Naturaleza"},
}

sug = sugerencias.get(st.session_state.destino_sel, {"noches": 3, "adultos": 2, "ninos": 0, "emoji": "✨", "texto": "Explora este destino"})

st.markdown(f"""
<div class="sugerencia">
    <span class="emoji">{sug['emoji']}</span>
    <div>
        <div class="label">💡 Sugerencia</div>
        <div class="texto">{sug['texto']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ======================================================
# FORMULARIO EN TARJETAS
# ======================================================

st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="card-header">📋 DATOS DE COTIZACIÓN</div>', unsafe_allow_html=True)

with st.form(key="form_cotizar", clear_on_submit=False):
    # Hotel
    if st.session_state.destino_sel == "Margarita":
        hoteles_margarita = [
            "Hotel Costa Caribe",
            "LD Palm Beach",
            "Hesperia Playa el Agua",
            "Margarita Village",
            "Hotel Sunsol",
            "Hotel Hesperia Isla de Margarita",
            "✏️ Otro (escribir nombre)"
        ]
        hotel_sel = st.selectbox("🏨 Hotel", options=hoteles_margarita, index=0, label_visibility="visible")
        if hotel_sel == "✏️ Otro (escribir nombre)":
            hotel_final = st.text_input("✏️ Nombre del hotel", placeholder="Ej: Hotel Miramar...", label_visibility="visible")
        else:
            hotel_final = hotel_sel
    else:
        hotel_final = st.text_input("📍 Hospedaje", value=st.session_state.destino_sel, placeholder="Nombre del lugar", label_visibility="visible")
    
    # 2 columnas para ahorrar espacio vertical
    c1, c2 = st.columns(2)
    with c1:
        noches = st.number_input("🌙 Noches", min_value=1, max_value=30, value=sug['noches'], label_visibility="visible")
        adultos = st.number_input("👤 Adultos", min_value=1, max_value=10, value=sug['adultos'], label_visibility="visible")
    with c2:
        fecha = st.date_input("📅 Check-in", value=datetime.now() + timedelta(days=7), label_visibility="visible")
        ninos = st.number_input("🧒 Niños", min_value=0, max_value=8, value=sug['ninos'], label_visibility="visible")
    
    regimen = st.selectbox("🍽️ Régimen", options=["Todos incluidos", "Media pensión", "Pensión completa", "Solo alojamiento"], label_visibility="visible")
    
    # Comando de voz colapsable
    with st.expander("🎤 Comando de voz"):
        voz = st.text_input("Escribe tu búsqueda", placeholder='Ej: "Margarita 4 adultos 2 niños 3 noches"', label_visibility="collapsed")
    
    buscar = st.form_submit_button("💰 COTIZAR AHORA", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# DIVISOR
# ======================================================

st.markdown('<div class="div"><span class="d">✦</span><span class="d">✦</span><span class="d">✦</span></div>', unsafe_allow_html=True)

# ======================================================
# LÓGICA DE BÚSQUEDA
# ======================================================

if buscar:
    destino_final = hotel_final if hotel_final else st.session_state.destino_sel
    
    # Procesar comando de voz
    if voz:
        texto = voz.lower()
        for d in destinos:
            if d["nombre"].lower() in texto:
                destino_final = d["nombre"]
                break
        nums = re.findall(r'\d+', texto)
        if len(nums) >= 1: adultos = int(nums[0])
        if len(nums) >= 2: ninos = int(nums[1])
        if len(nums) >= 3: noches = int(nums[2])
        st.toast(f"🎤 {destino_final} · {adultos}ad · {ninos}ni · {noches}n", icon="✅")
    
    if not destino_final:
        st.warning("⚠️ Escribe un lugar de hospedaje")
    else:
        with st.spinner("🔍 Buscando..."):
            try:
                conn = sqlite3.connect("pdf_busqueda.db")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT h.nombre, t.pagina, t.regimen, t.vigencia_inicio, t.vigencia_fin,
                           t.sgl, t.dbl, t.tpl, t.cdp, t.qpl, t.chd, t.inf, t.promociones, t.condiciones
                    FROM tarifas t JOIN hoteles h ON t.hotel_id = h.id
                    WHERE h.nombre LIKE ? OR h.nombre LIKE ? OR h.nombre LIKE ?
                    ORDER BY t.pagina LIMIT 12
                """, (f'%{destino_final}%', f'%{destino_final.upper()}%', f'%{destino_final.lower()}%'))
                resultados = cursor.fetchall()
                conn.close()
                
                if resultados:
                    validos = [r for r in resultados if r[5] or r[6] or r[7] or r[8] or r[9]]
                    
                    if not validos:
                        st.warning("😕 Sin tarifas para este destino")
                        st.info("💡 Prueba otro hotel o destino")
                    else:
                        st.success(f"✅ {len(validos)} ofertas · {destino_final}")
                        
                        # Badges
                        b1, b2, b3, b4 = st.columns(4)
                        with b1: st.markdown(f'<span class="badge">📍 {destino_final[:12]}</span>', unsafe_allow_html=True)
                        with b2: st.markdown(f'<span class="badge">👤 {adultos} ad</span>', unsafe_allow_html=True)
                        with b3: st.markdown(f'<span class="badge">🧒 {ninos} ni</span>', unsafe_allow_html=True)
                        with b4: st.markdown(f'<span class="badge">🌙 {noches} n</span>', unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        for idx, r in enumerate(validos):
                            hotel, pagina, reg_bd, v_ini, v_fin, sgl, dbl, tpl, cdp, qpl, chd, inf, promos_j, cond_j = r
                            
                            precio_base = dbl or sgl or tpl or cdp or qpl or 0
                            total_p = adultos + ninos
                            promos = json.loads(promos_j) if promos_j else []
                            
                            if precio_base > 0:
                                gratis = any("GRATIS" in str(p).upper() for p in promos)
                                costo_noche = (adultos * precio_base) if (gratis and ninos > 0) else (total_p * precio_base)
                                total_viaje = costo_noche * noches
                                total_txt = f"${total_viaje:,.0f} USD"
                                precio_txt = f"${precio_base:.0f}"
                                sub_txt = f"${costo_noche:.0f}"
                            else:
                                total_txt = "Consultar"
                                precio_txt = "N/A"
                                sub_txt = "N/A"
                            
                            st.markdown(f"""
                            <div class="result-card">
                                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                                    <div class="hotel-name">🏨 {hotel}</div>
                                    <span class="pagina-tag">Pág {pagina}</span>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Badges de info
                            b_html = ""
                            if v_ini: b_html += f'<span class="badge vigencia">📅 {v_ini[:5]}→{v_fin[:5] if v_fin else "Act"}</span>'
                            if reg_bd: b_html += f'<span class="badge">🍽️ {reg_bd}</span>'
                            for p in promos[:2]: b_html += f'<span class="badge promo">🎁 {p}</span>'
                            if b_html: st.markdown(f'<div class="badge-row">{b_html}</div>', unsafe_allow_html=True)
                            
                            # Precios habitación
                            ph = {}
                            if sgl: ph["SGL"] = sgl
                            if dbl: ph["DBL"] = dbl
                            if tpl: ph["TPL"] = tpl
                            if cdp: ph["CDP"] = cdp
                            if qpl: ph["QPL"] = qpl
                            if ph:
                                st.caption(" · ".join([f"{k}: ${v:.0f}" for k, v in ph.items()]))
                            
                            # Desglose
                            st.markdown(f"""
                            <div class="desglose">
                                <div class="row"><span class="lbl">💰 Precio/pers (noche)</span><span class="val">{precio_txt}</span></div>
                                <div class="row"><span class="lbl">👥 Personas</span><span class="val">{total_p} ({adultos}+{ninos})</span></div>
                                <div class="row"><span class="lbl">🌙 Noches</span><span class="val">{noches}</span></div>
                                <div class="row"><span class="lbl">🍽️ Régimen</span><span class="val">{regimen}</span></div>
                                <div class="row"><span class="lbl">Subtotal/noche</span><span class="val">{sub_txt}</span></div>
                                <div class="row total"><span class="lbl">💰 TOTAL</span><span class="val">{total_txt}</span></div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            if idx < len(validos) - 1: st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Métricas finales
                        st.markdown("---")
                        c1, c2, c3, c4, c5 = st.columns(5)
                        with c1: st.metric("📍", destino_final[:10])
                        with c2: st.metric("🌙", noches)
                        with c3: st.metric("👤", adultos)
                        with c4: st.metric("🧒", ninos)
                        with c5: st.metric("🍽️", regimen[:6])
                        
                        st.info("💡 Verifica el PDF original para confirmar tarifas exactas")
                else:
                    st.warning(f"😕 Sin resultados para '{destino_final}'")
                    st.info("💡 Verifica el nombre o prueba otro destino")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.info("💡 Ejecuta el extractor: python extractor.py")

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class="ft">
    ✦ BT Travel · Lotus 360 ✦
    <br>
    Herramienta asesores · © 2026
</div>
""", unsafe_allow_html=True)