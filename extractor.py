import pdfplumber
import sqlite3
import os
import re
import json

# ======================================================
# CONFIGURACIÓN
# ======================================================

RUTA_PDF = "BT_Travel.pdf"
POPPLER_PATH = r".\poppler-26.02.0\Library\bin"

# Hoteles de Margarita más populares
HOTELES_MARGARITA = [
    "Hotel Costa Caribe",
    "LD Palm Beach",
    "Hesperia Playa el Agua",
    "Margarita Village",
    "Hotel Sunsol",
    "Hotel Hesperia Isla de Margarita"
]

# ======================================================
# FUNCIONES DE EXTRACCIÓN
# ======================================================

def extraer_tablas_y_datos():
    """Extrae tablas de precios, hoteles y promociones del PDF."""
    print("📄 Procesando PDF...")
    fragmentos = []
    
    try:
        with pdfplumber.open(RUTA_PDF) as pdf:
            for pagina_num, pagina in enumerate(pdf.pages, start=1):
                texto = pagina.extract_text()
                tablas = pagina.extract_tables()
                
                if not texto:
                    continue
                
                # Buscar hoteles en el texto
                hoteles_encontrados = []
                for hotel in HOTELES_MARGARITA:
                    variantes = [
                        hotel,
                        hotel.upper(),
                        hotel.lower(),
                        hotel.replace("Hotel ", "").strip(),
                        hotel.replace("Hotel ", "").strip().upper(),
                    ]
                    for variante in variantes:
                        if variante in texto or variante.lower() in texto.lower():
                            if hotel not in hoteles_encontrados:
                                hoteles_encontrados.append(hotel)
                            break
                
                if not hoteles_encontrados:
                    continue
                
                # Procesar tablas
                for tabla in tablas:
                    if not tabla:
                        continue
                    
                    texto_tabla = "\n".join([" | ".join([str(c) if c else "" for c in fila]) for fila in tabla])
                    
                    info_extraida = analizar_tabla(tabla, hoteles_encontrados, texto_tabla)
                    if info_extraida and info_extraida.get("precios_habitacion"):
                        fragmentos.append({
                            "pagina": pagina_num,
                            "hoteles": hoteles_encontrados,
                            "texto_tabla": texto_tabla,
                            "info_extraida": info_extraida
                        })
                        print(f"   📄 Página {pagina_num}: Encontrados datos para {', '.join(hoteles_encontrados)}")
    
    except Exception as e:
        print(f"⚠️ Error al procesar PDF: {e}")
    
    print(f"✅ Extraídos {len(fragmentos)} fragmentos")
    return fragmentos

def analizar_tabla(tabla, hoteles, texto_tabla):
    """Analiza una tabla para extraer precios, promociones y fechas."""
    info = {
        "hoteles": hoteles,
        "regimen": None,
        "vigencia": None,
        "precios_habitacion": {},
        "precios_extras": {},
        "promociones": [],
        "condiciones_fecha": []
    }
    
    texto_completo = " ".join([" ".join([str(c) if c else "" for c in fila]) for fila in tabla])
    
    # ============================================================
    # 1. DETECTAR RÉGIMEN
    # ============================================================
    if "TODO INCLUIDO" in texto_completo.upper():
        info["regimen"] = "TODO INCLUIDO"
    elif "SOLO DESAYUNO" in texto_completo.upper():
        info["regimen"] = "SOLO DESAYUNO"
    elif "MEDIA PENSIÓN" in texto_completo.upper():
        info["regimen"] = "MEDIA PENSIÓN"
    elif "PENSIÓN COMPLETA" in texto_completo.upper():
        info["regimen"] = "PENSIÓN COMPLETA"
    
    # ============================================================
    # 2. DETECTAR VIGENCIA
    # ============================================================
    fechas = re.findall(r'(\d{2}/\d{2}/\d{4})', texto_completo)
    if len(fechas) >= 2:
        info["vigencia"] = {"inicio": fechas[0], "fin": fechas[1]}
    elif len(fechas) == 1:
        info["vigencia"] = {"inicio": fechas[0], "fin": fechas[0]}
    
    # ============================================================
    # 3. DETECTAR PRECIOS POR HABITACIÓN
    # ============================================================
    
    for fila in tabla:
        texto_fila = " ".join([str(c) if c else "" for c in fila])
        
        patrones = {
            "SGL": r'SGL\s*[:]?\s*\$?\s*(\d+[\.,]?\d*)',
            "DBL": r'DBL\s*[:]?\s*\$?\s*(\d+[\.,]?\d*)',
            "TPL": r'TPL\s*[:]?\s*\$?\s*(\d+[\.,]?\d*)',
            "CDP": r'CDP\s*[:]?\s*\$?\s*(\d+[\.,]?\d*)',
            "QPL": r'QPL\s*[:]?\s*\$?\s*(\d+[\.,]?\d*)',
        }
        
        for hab, patron in patrones.items():
            coincidencias = re.findall(patron, texto_fila, re.IGNORECASE)
            if coincidencias:
                try:
                    valor_str = coincidencias[0].replace(',', '.').strip()
                    valor = float(valor_str)
                    if valor > 0 and valor < 1000:
                        info["precios_habitacion"][hab] = valor
                        print(f"      Precio encontrado: {hab} = ${valor:.2f}")
                except:
                    pass
        
        # Fallback: buscar números sueltos
        if not info["precios_habitacion"]:
            numeros = re.findall(r'\$?\s*(\d+[\.,]\d{2})', texto_fila)
            if numeros:
                tipos = ["SGL", "DBL", "TPL", "CDP", "QPL"]
                for i, num in enumerate(numeros[:5]):
                    try:
                        valor = float(num.replace(',', '.'))
                        if valor > 0 and valor < 1000:
                            info["precios_habitacion"][tipos[i]] = valor
                    except:
                        pass
    
    # ============================================================
    # 4. DETECTAR PRECIOS PARA NIÑOS
    # ============================================================
    
    patrones_ninos = {
        "CHD": r'CHD\s*[:]?\s*\$?\s*(\d+[\.,]?\d*)',
        "INF": r'INF\s*[:]?\s*\$?\s*(\d+[\.,]?\d*)',
        "CHD_4_10": r'CHD\s*4-10\s*[:]?\s*\$?\s*(\d+[\.,]?\d*)',
        "CHD_5_10": r'CHD\s*5-10\s*[:]?\s*\$?\s*(\d+[\.,]?\d*)',
    }
    
    for key, patron in patrones_ninos.items():
        coincidencias = re.findall(patron, texto_completo, re.IGNORECASE)
        if coincidencias:
            try:
                valor = float(coincidencias[0].replace(',', '.'))
                if valor >= 0 and valor < 200:
                    info["precios_extras"][key] = valor
            except:
                pass
    
    # ============================================================
    # 5. DETECTAR PROMOCIONES
    # ============================================================
    
    if re.search(r'CHD\s*FREE|NIÑOS?\s*GRATIS|FREE\s*CHD|GRATIS.*CHD|1ER.*2DO.*CHD.*FREE', texto_completo, re.IGNORECASE):
        info["promociones"].append("Niños gratis")
    
    chd_free = re.findall(r'CHD\s*(?:FREE|GRATIS)\s*(?:\(?\s*(\d+)\s*-\s*(\d+)\s*\)?)?', texto_completo, re.IGNORECASE)
    for edades in chd_free:
        if edades[0] and edades[1]:
            info["promociones"].append(f"Niños gratis {edades[0]}-{edades[1]} años")
        elif edades[0]:
            info["promociones"].append(f"Niños gratis hasta {edades[0]} años")
    
    # ============================================================
    # 6. DETECTAR CONDICIONES DE FECHA
    # ============================================================
    
    if "TEMPORADA ALTA" in texto_completo.upper():
        info["condiciones_fecha"].append("TEMPORADA ALTA")
    if "TEMPORADA BAJA" in texto_completo.upper():
        info["condiciones_fecha"].append("TEMPORADA BAJA")
    if "FIN DE SEMANA" in texto_completo.upper():
        info["condiciones_fecha"].append("FIN DE SEMANA")
    
    return info

def guardar_en_bd(fragmentos):
    """Guarda los fragmentos extraídos en la base de datos SQLite, evitando duplicados."""
    print("🗄️ Guardando en base de datos...")
    conn = sqlite3.connect("pdf_busqueda.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hoteles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarifas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER,
            pagina INTEGER,
            regimen TEXT,
            vigencia_inicio TEXT,
            vigencia_fin TEXT,
            sgl REAL,
            dbl REAL,
            tpl REAL,
            cdp REAL,
            qpl REAL,
            chd REAL,
            inf REAL,
            promociones TEXT,
            condiciones TEXT,
            FOREIGN KEY (hotel_id) REFERENCES hoteles (id)
        )
    ''')
    
    # Eliminar tarifas existentes para evitar duplicados
    for frag in fragmentos:
        for hotel in frag["hoteles"]:
            cursor.execute("INSERT OR IGNORE INTO hoteles (nombre) VALUES (?)", (hotel,))
            cursor.execute("SELECT id FROM hoteles WHERE nombre = ?", (hotel,))
            hotel_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM tarifas WHERE hotel_id = ? AND pagina = ?", (hotel_id, frag["pagina"]))
    
    # Insertar nuevos datos
    for frag in fragmentos:
        for hotel in frag["hoteles"]:
            cursor.execute("SELECT id FROM hoteles WHERE nombre = ?", (hotel,))
            hotel_id = cursor.fetchone()[0]
            
            info = frag["info_extraida"]
            precios_hab = info.get("precios_habitacion", {})
            
            if not precios_hab:
                print(f"   ⏭️ Saltando {hotel} (sin precios)")
                continue
            
            vigencia = info.get("vigencia")
            if vigencia is None:
                vigencia_inicio = None
                vigencia_fin = None
            else:
                vigencia_inicio = vigencia.get("inicio")
                vigencia_fin = vigencia.get("fin")
            
            precios_ext = info.get("precios_extras", {})
            
            print(f"   💰 {hotel}: {precios_hab}")
            
            cursor.execute('''
                INSERT INTO tarifas (
                    hotel_id, pagina, regimen, vigencia_inicio, vigencia_fin,
                    sgl, dbl, tpl, cdp, qpl, chd, inf, promociones, condiciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                hotel_id,
                frag["pagina"],
                info.get("regimen"),
                vigencia_inicio,
                vigencia_fin,
                precios_hab.get("SGL"),
                precios_hab.get("DBL"),
                precios_hab.get("TPL"),
                precios_hab.get("CDP"),
                precios_hab.get("QPL"),
                precios_ext.get("CHD"),
                precios_ext.get("INF"),
                json.dumps(info.get("promociones", [])),
                json.dumps(info.get("condiciones_fecha", []))
            ))
    
    conn.commit()
    conn.close()
    print("✅ Base de datos actualizada exitosamente")

# ======================================================
# EJECUCIÓN PRINCIPAL
# ======================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 EXTRACTOR PDF - BT TRAVEL")
    print("   Optimizado para hoteles de Margarita")
    print("=" * 60)
    
    if not os.path.exists(RUTA_PDF):
        print(f"❌ ERROR: No encuentro el PDF en: {RUTA_PDF}")
        print(f"   Carpeta actual: {os.getcwd()}")
    else:
        fragmentos = extraer_tablas_y_datos()
        if fragmentos:
            guardar_en_bd(fragmentos)
            print("🎉 ¡Proceso completado!")
        else:
            print("❌ No se encontraron datos de hoteles en el PDF.")