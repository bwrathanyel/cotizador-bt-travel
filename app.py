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
# CSS - DISEÑO MODERNO
# ======================================================

st.markdown("""
<style>
    .stApp { background: #080c18; }
    .main { background: #080c18; padding: 1rem 1.5rem 3rem; }
    header[data-testid="stHeader"] { display: none; }
    
    .destino-slider {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 30px;
        padding: 12px 16px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 4px;
        flex-wrap: nowrap;
        overflow-x: auto;
        scrollbar-width: none;
    }
    .destino-slider::-webkit-scrollbar { display: none; }
    
    .destino-btn {
        flex: 0 0 auto;
        background: transparent !important;
        border: 1px solid transparent !important;
        color: rgba(255, 255, 255, 0.35) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
        border-radius: 30px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        white-space: nowrap !important;
        font-family: inherit !important;
    }
    .destino-btn:hover {
        color: #fff !important;
        background: rgba(255, 255, 255, 0.06) !important;
        transform: translateY(-2px);
    }
    .destino-btn.activo {
        color: #fff !important;
        background: rgba(255, 145, 0, 0.15) !important;
        border-color: rgba(255, 145, 0, 0.25) !important;
    }
    .destino-btn .badge-destino {
        font-size: 7px;
        padding: 2px 10px;
        border-radius: 12px;
        margin-left: 8px;
        font-weight: 700;
        background: rgba(255, 145, 0, 0.12);
        color: #ff9100;
    }

    .sugerencia-box {
        background: linear-gradient(135deg, rgba(255, 145, 0, 0.06), rgba(255, 145, 0, 0.01));
        border: 1px solid rgba(255, 145, 0, 0.08);
        border-radius: 20px;
        padding: 16px 22px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 8px;
    }
    .sugerencia-box .label {
        color: rgba(255, 255, 255, 0.3);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    .sugerencia-box .texto {
        color: rgba(255, 255, 255, 0.75);
        font-size: 14px;
    }
    .sugerencia-box .texto strong { color: #ffb74d; }

    .form-moderno {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 32px;
        padding: 32px 28px;
        margin-bottom: 24px;
    }
    .form-moderno .stTextInput input,
    .form-moderno .stNumberInput input,
    .form-moderno .stSelectbox select,
    .form-moderno .stDateInput input {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 14px !important;
        color: #fff !important;
        padding: 12px 18px !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }
    .form-moderno .stTextInput input:focus,
    .form-moderno .stNumberInput input:focus,
    .form-moderno .stSelectbox select:focus,
    .form-moderno .stDateInput input:focus {
        border-color: rgba(255, 145, 0, 0.3) !important;
        box-shadow: 0 0 0 4px rgba(255, 145, 0, 0.05) !important;
    }
    .form-moderno .stTextInput input::placeholder { color: rgba(255, 255, 255, 0.15); }
    .form-moderno label {
        color: rgba(255, 255, 255, 0.3) !important;
        font-size: 11px !important;
        font-weight: 500 !important;
    }

    .btn-cotizar {
        background: linear-gradient(135deg, #ff9100, #f57c00, #ef6c00) !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 20px 32px !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        color: #fff !important;
        box-shadow: 0 8px 40px rgba(255, 145, 0, 0.25) !important;
        transition: all 0.4s ease !important;
        width: 100% !important;
    }
    .btn-cotizar:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 56px rgba(255, 145, 0, 0.4) !important;
    }
    .btn-cotizar:active { transform: scale(0.96) !important; }

    .badge-moderno {
        display: inline-block;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 10px;
        color: rgba(255, 255, 255, 0.3);
        margin-right: 4px;
    }
    .badge-moderno i { color: #ff9100; margin-right: 4px; opacity: 0.6; }

    .promocion-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border-radius: 14px;
        padding: 3px 12px;
        font-size: 10px;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.08);
    }
    .vigencia-badge {
        display: inline-block;
        background: rgba(74, 158, 255, 0.08);
        color: #4a9eff;
        border-radius: 14px;
        padding: 3px 12px;
        font-size: 10px;
        font-weight: 600;
        border: 1px solid rgba(74, 158, 255, 0.06);
    }
    .temporada-badge {
        display: inline-block;
        background: rgba(255, 183, 77, 0.08);
        color: #ffb74d;
        border-radius: 14px;
        padding: 3px 12px;
        font-size: 10px;
        font-weight: 600;
        border: 1px solid rgba(255, 183, 77, 0.06);
    }

    .result-card-moderno {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 24px;
        padding: 24px 26px;
        margin: 16px 0;
        transition: all 0.4s ease;
    }
    .result-card-moderno:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(255, 145, 0, 0.08);
        transform: translateY(-4px);
    }
    .result-card-moderno .header-result {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .result-card-moderno .header-result .titulo-pagina {
        font-weight: 600;
        color: #fff;
        font-size: 16px;
    }
    .result-card-moderno .pagina-badge {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 9px;
        color: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.03);
    }

    .desglose-box {
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 20px;
        padding: 20px 24px;
        margin: 12px 0 8px;
    }
    .desglose-box .fila {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.02);
        font-size: 13px;
        color: rgba(255, 255, 255, 0.5);
    }
    .desglose-box .fila:last-child { border-bottom: none; }
    .desglose-box .fila .label {
        color: rgba(255, 255, 255, 0.35);
        font-size: 12px;
    }
    .desglose-box .fila .valor {
        color: rgba(255, 255, 255, 0.7);
        font-weight: 500;
        font-size: 13px;
    }
    .desglose-box .fila .badge-precio {
        background: rgba(255, 145, 0, 0.08);
        color: #ff9100;
        font-size: 8px;
        padding: 2px 10px;
        border-radius: 12px;
        margin-left: 6px;
        font-weight: 600;
    }
    .desglose-box .fila.total {
        border-top: 2px solid rgba(255, 145, 0, 0.12);
        padding-top: 12px;
        margin-top: 6px;
    }
    .desglose-box .fila.total .label {
        color: #ffb74d;
        font-weight: 700;
        font-size: 14px;
    }
    .desglose-box .fila.total .valor {
        color: #ff9100;
        font-weight: 700;
        font-size: 22px;
    }
    .desglose-box .formula {
        text-align: right;
        font-size: 9px;
        color: rgba(255, 255, 255, 0.06);
        margin-top: 6px;
    }

    .divider-lotus {
        display: flex;
        align-items: center;
        gap: 20px;
        margin: 28px 0 22px;
        opacity: 0.12;
    }
    .divider-lotus::before,
    .divider-lotus::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 145, 0, 0.2), transparent);
    }
    .divider-lotus .icono-divider { color: #ff9100; font-size: 10px; }

    h1 {
        color: #fff !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
        background: linear-gradient(135deg, #ff9100, #ffb74d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0 !important;
    }
    .sub-header {
        color: rgba(255, 255, 255, 0.12);
        font-size: 13px;
        font-weight: 400;
        margin-top: -2px;
        margin-bottom: 22px;
        letter-spacing: 1px;
    }
    h3 {
        color: #fff !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        margin-bottom: 14px !important;
    }

    .stMetric {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        padding: 12px 8px;
        border: 1px solid rgba(255, 255, 255, 0.02);
        transition: all 0.3s ease;
    }
    .stMetric:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(255, 145, 0, 0.05);
        transform: translateY(-2px);
    }
    .stMetric label {
        color: rgba(255, 255, 255, 0.2) !important;
        font-size: 10px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stMetric .stMetricValue {
        color: #fff !important;
        font-weight: 600 !important;
        font-size: 22px !important;
    }

    .footer-2026 {
        margin-top: 32px;
        padding-top: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.02);
        text-align: center;
        font-size: 9px;
        color: rgba(255, 255, 255, 0.04);
        letter-spacing: 1.5px;
    }

    @media (max-width: 768px) {
        .main { padding: 0.5rem 0.8rem 2rem; }
        .form-moderno { padding: 18px 14px; border-radius: 24px; }
        .result-card-moderno { padding: 16px 16px; border-radius: 20px; }
        .destino-btn { font-size: 11px !important; padding: 6px 12px !important; }
        .desglose-box { padding: 14px 16px; }
        .desglose-box .fila.total .valor { font-size: 18px; }
        h1 { font-size: 1.4rem !important; }
        .btn-cotizar { font-size: 15px !important; padding: 16px 20px !important; border-radius: 20px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================

col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://bwrathanyel.github.io/redireccion-whatsapp/logolotus.png", width=60)
with col2:
    st.markdown("<h1>✈️ Cotizador BT Travel</h1>", unsafe_allow_html=True)
    st.markdown('<p class="sub-header">✨ Dashboard de tarifas · Destino y Eventos Lotus 360 🌴</p>', unsafe_allow_html=True)

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
        if st.button(
            f"{d['emoji']} {d['nombre']}",
            key=f"btn_{d['nombre']}",
            use_container_width=True,
            type="secondary" if d["nombre"] != st.session_state.destino_seleccionado else "primary"
        ):
            st.session_state.destino_seleccionado = d["nombre"]
            st.rerun()
        st.markdown(
            f'<div style="text-align:center;margin-top:-4px;font-size:7px;color:rgba(255,255,255,0.08);">#{d["badge"]}</div>',
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# SUGERENCIA
# ======================================================

sugerencias = {
    "Margarita": {"noches": 4, "adultos": 2, "ninos": 0, "texto": "🌴 4 noches · 2 adultos · Playas y duty free"},
    "Morrocoy": {"noches": 2, "adultos": 2, "ninos": 2, "texto": "🐠 2 noches · 2 adultos + 2 niños · Ideal para familias"},
    "Los Roques": {"noches": 3, "adultos": 2, "ninos": 0, "texto": "🏝️ 3 noches · 2 adultos · Escapada romántica"},
    "Mérida": {"noches": 3, "adultos": 2, "ninos": 1, "texto": "🚡 3 noches · 2 adultos + 1 niño · Aventura en los Andes"},
    "Canaima": {"noches": 2, "adultos": 2, "ninos": 0, "texto": "💧 2 noches · 2 adultos · Expedición al Salto Ángel"},
    "Colonia Tovar": {"noches": 2, "adultos": 2, "ninos": 0, "texto": "🏘️ 2 noches · 2 adultos · Clima primaveral y fresas"},
    "Costa Caribe": {"noches": 3, "adultos": 2, "ninos": 2, "texto": "🌊 3 noches · 2 adultos + 2 niños · Todo incluido"},
    "Los Llanos": {"noches": 2, "adultos": 2, "ninos": 0, "texto": "🌿 2 noches · 2 adultos · Naturaleza y fauna"},
}

sug = sugerencias.get(st.session_state.destino_seleccionado, {"noches": 3, "adultos": 2, "ninos": 0, "texto": "✨ Explora este destino"})

st.markdown(f"""
<div class="sugerencia-box">
    <div>
        <span class="label">💡 Sugerencia para {st.session_state.destino_seleccionado}</span>
        <div class="texto">{sug['texto']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ======================================================
# FORMULARIO
# ======================================================

with st.container():
    st.markdown('<div class="form-moderno">', unsafe_allow_html=True)
    st.markdown("### 📝 Datos del viaje")

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
                "✏️ Otro (escribir nombre)"
            ]
            
            if st.session_state.destino_seleccionado == "Margarita":
                st.markdown('<p style="color:rgba(255,255,255,0.3);font-size:11px;font-weight:500;margin-bottom:2px;">🏨 Selecciona el hotel</p>', unsafe_allow_html=True)
                hotel_seleccionado = st.selectbox(
                    "🏨 Hotel en Margarita",
                    options=hoteles_margarita,
                    index=0,
                    label_visibility="collapsed"
                )
                
                if hotel_seleccionado == "✏️ Otro (escribir nombre)":
                    hotel_input = st.text_input(
                        "✏️ Escribe el nombre del hotel",
                        placeholder="Ej: Hotel Miramar, Posada La Mar...",
                        label_visibility="collapsed"
                    )
                    hotel_final = hotel_input if hotel_input else ""
                else:
                    hotel_final = hotel_seleccionado.replace("🏨 ", "")
                
                if hotel_final:
                    st.caption(f"📍 Hotel seleccionado: **{hotel_final}**")
                else:
                    st.caption("📍 Selecciona un hotel")
            else:
                hotel_final = st.text_input(
                    "📍 Lugar de Hospedaje",
                    value=st.session_state.destino_seleccionado,
                    placeholder="Ej: Margarita, Costa Caribe..."
                )
            
            fecha_entrada = st.date_input(
                "📅 Fecha de llegada",
                value=datetime.now() + timedelta(days=7)
            )
            noches = st.number_input(
                "🌙 Noches de estancia",
                min_value=1,
                max_value=30,
                value=sug['noches']
            )

        with col2:
            adultos = st.number_input(
                "👤 Adultos",
                min_value=1,
                max_value=10,
                value=sug['adultos']
            )
            ninos = st.number_input(
                "🧒 Niños",
                min_value=0,
                max_value=8,
                value=sug['ninos']
            )
            regimen = st.selectbox(
                "🍽️ Régimen alimenticio",
                options=["Todos incluidos", "Media pensión", "Pensión completa", "Solo alojamiento"]
            )

        st.caption("🎤 O usa el comando de voz")
        comando_voz = st.text_input(
            "🎙️ Comando de voz",
            placeholder='Ej: "Quiero Margarita, 4 adultos, 2 niños, 3 noches"',
            label_visibility="collapsed"
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
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
        st.warning("⚠️ Selecciona o escribe un lugar de hospedaje")
    else:
        with st.spinner("🔍 Buscando tarifas..."):
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
                    # FILTRAR: solo mostrar ofertas con al menos un precio
                    resultados_validos = []
                    for row in resultados:
                        sgl, dbl, tpl, cdp, qpl = row[5], row[6], row[7], row[8], row[9]
                        if sgl or dbl or tpl or cdp or qpl:
                            resultados_validos.append(row)
                    
                    if not resultados_validos:
                        st.warning("😕 Se encontraron hoteles pero no hay tarifas disponibles para los datos ingresados.")
                        st.info("💡 Intenta con otro hotel o ajusta las fechas.")
                    else:
                        st.markdown(f'<h3>✅ {len(resultados_validos)} ofertas encontradas</h3>', unsafe_allow_html=True)
                        
                        col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
                        with col_b1:
                            st.markdown(f'<span class="badge-moderno"><i class="fas fa-hotel"></i> {destino_final}</span>', unsafe_allow_html=True)
                        with col_b2:
                            st.markdown(f'<span class="badge-moderno"><i class="fas fa-user"></i> {adultos} adultos</span>', unsafe_allow_html=True)
                        with col_b3:
                            st.markdown(f'<span class="badge-moderno"><i class="fas fa-child"></i> {ninos} niños</span>', unsafe_allow_html=True)
                        with col_b4:
                            st.markdown(f'<span class="badge-moderno"><i class="fas fa-moon"></i> {noches} noches</span>', unsafe_allow_html=True)
                        with col_b5:
                            st.markdown(f'<span class="badge-moderno"><i class="fas fa-utensils"></i> {regimen}</span>', unsafe_allow_html=True)
                        
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
                                total_texto = "Calcular manualmente"
                                precio_mostrado = "N/A"
                                subtotal_texto = "N/A"
                            
                            with st.container():
                                col_h1, col_h2 = st.columns([3, 1])
                                with col_h1:
                                    st.markdown(f"**🏨 {hotel}**")
                                with col_h2:
                                    st.markdown(f'<span class="pagina-badge">📄 Página {pagina}</span>', unsafe_allow_html=True)
                                
                                st.markdown(f"""
                                <div style="display:flex;flex-wrap:wrap;gap:6px;margin:4px 0 10px;">
                                    <span class="vigencia-badge">📅 {vigencia_ini or 'N/A'} - {vigencia_fin or 'N/A'}</span>
                                    <span class="temporada-badge">🍽️ {regimen_bd or 'N/A'}</span>
                                    {"".join([f'<span class="promocion-badge">🎁 {p}</span>' for p in promociones])}
                                    {"".join([f'<span class="temporada-badge">📌 {c}</span>' for c in condiciones])}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                precios_habitacion = {}
                                if sgl: precios_habitacion["SGL"] = sgl
                                if dbl: precios_habitacion["DBL"] = dbl
                                if tpl: precios_habitacion["TPL"] = tpl
                                if cdp: precios_habitacion["CDP"] = cdp
                                if qpl: precios_habitacion["QPL"] = qpl
                                
                                if precios_habitacion:
                                    habitacion_text = " | ".join([f"{hab}: ${p:.2f}" for hab, p in precios_habitacion.items()])
                                    st.caption(f"🏷️ Precios por noche: {habitacion_text}")
                                
                                if tiene_ninos_gratis and ninos > 0:
                                    st.markdown(f'<span class="promocion-badge">🎁 ¡Niños gratis!</span>', unsafe_allow_html=True)
                                
                                st.markdown(f"""
                                <div class="desglose-box">
                                    <div class="fila">
                                        <span class="label">💰 Precio por persona (por noche)</span>
                                        <span class="valor">{precio_mostrado}</span>
                                    </div>
                                    <div class="fila">
                                        <span class="label">👥 Personas totales</span>
                                        <span class="valor">{total_personas} <span style="color:rgba(255,255,255,0.3);font-size:11px;">({adultos} adultos + {ninos} niños)</span></span>
                                    </div>
                                    <div class="fila">
                                        <span class="label">🌙 Noches de estancia</span>
                                        <span class="valor">{noches}</span>
                                    </div>
                                    <div class="fila" style="border-bottom:1px solid rgba(255,255,255,0.06);">
                                        <span class="label">🍽️ Régimen</span>
                                        <span class="valor">{regimen}</span>
                                    </div>
                                    <div class="fila" style="color:rgba(255,255,255,0.5);font-size:12px;">
                                        <span class="label">Subtotal (por noche)</span>
                                        <span class="valor">{subtotal_texto}</span>
                                    </div>
                                    <div class="fila total">
                                        <span class="label">💰 Total del viaje</span>
                                        <span class="valor">{total_texto}</span>
                                    </div>
                                    <div class="formula">Precio por persona × {total_personas} personas × {noches} noches</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.divider()
                        
                        st.markdown("---")
                        st.markdown("### 📊 Resumen de la cotización")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📍 Hospedaje", destino_final.title())
                        with col2:
                            st.metric("🌙 Noches", noches)
                        with col3:
                            st.metric("👤 Adultos", adultos)
                        with col4:
                            st.metric("🧒 Niños", ninos)
                        
                        st.info("💡 Revisa el PDF original para confirmar tarifas exactas.")
                else:
                    st.warning(f"😕 No encontré información para '{destino_final}'")
                    st.info("💡 Prueba con: 'hotel', 'precio', 'promoción' o el nombre de otro destino")
                    
            except Exception as e:
                st.error(f"❌ Error al buscar: {e}")
                st.info("💡 Asegúrate de haber ejecutado el extractor primero (python extractor.py)")

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class="footer-2026">
    Información extraída del PDF de BT Travel · Destino y Eventos Lotus 360
    <br>
    © 2026 · Carabobo, Venezuela
</div>
""", unsafe_allow_html=True)