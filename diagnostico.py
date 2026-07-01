import sqlite3
import sys
import io

# Configurar encoding para evitar errores
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    conn = sqlite3.connect("pdf_busqueda.db")
    cursor = conn.cursor()
    
    # Ver cuántos fragmentos hay
    cursor.execute("SELECT COUNT(*) FROM contenido_pdf")
    total = cursor.fetchone()[0]
    print(f"📊 Total de fragmentos: {total}")
    
    # Ver los primeros 3 fragmentos
    cursor.execute("SELECT pagina, texto FROM contenido_pdf LIMIT 3")
    for pagina, texto in cursor.fetchall():
        print(f"\n--- Página {pagina} ---")
        # Mostrar solo los primeros 300 caracteres
        print(texto[:300] if texto else "(vacío)")
    
    # Ver qué palabras aparecen (para saber qué buscar)
    cursor.execute("SELECT texto FROM contenido_pdf WHERE texto LIKE '%Margarita%' LIMIT 5")
    resultados = cursor.fetchall()
    print(f"\n🔍 Resultados con 'Margarita': {len(resultados)}")
    for row in resultados:
        print(row[0][:200])
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")