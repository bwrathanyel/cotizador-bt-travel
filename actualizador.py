import imaplib
import email
from email.header import decode_header
import os
import subprocess
from datetime import datetime

# ======================================================
# CONFIGURACIÓN - CAMBIA ESTOS DATOS
# ======================================================

# 📧 Datos de tu correo (el que recibe los PDFs de BT Travel)
# AHORA USA VARIABLES DE ENTORNO PARA SEGURIDAD
CORREO = os.environ.get("CORREO_PDF", "tu_correo@empresa.com")
CONTRASENA = os.environ.get("CONTRASENA_PDF", "tu_contraseña")
SERVIDOR_IMAP = os.environ.get("SERVIDOR_IMAP", "imap.gmail.com")

# 📂 Carpeta donde está el proyecto
CARPETA_PROYECTO = os.getcwd()  # Usa la carpeta actual

# 📄 Nombre del PDF
NOMBRE_PDF = "BT_Travel.pdf"

# ======================================================
# NO TOCAR DEBAJO DE ESTA LÍNEA
# ======================================================

def conectar_correo():
    """Conecta al correo usando IMAP"""
    try:
        mail = imaplib.IMAP4_SSL(SERVIDOR_IMAP)
        mail.login(CORREO, CONTRASENA)
        mail.select("INBOX")
        return mail
    except Exception as e:
        print(f"❌ Error al conectar al correo: {e}")
        return None

def buscar_ultimo_pdf(mail):
    """Busca el correo más reciente con PDF adjunto de BT Travel"""
    try:
        # Buscar correos con asunto que contenga "BT Travel"
        status, mensajes = mail.search(None, 'SUBJECT "BT Travel"')
        if not mensajes[0]:
            print("📭 No hay correos nuevos de BT Travel")
            return None
        
        ids = mensajes[0].split()
        ultimo_id = ids[-1]
        
        status, data = mail.fetch(ultimo_id, "(RFC822)")
        if status != "OK":
            return None
        
        msg = email.message_from_bytes(data[0][1])
        
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                if filename and filename.lower().endswith('.pdf'):
                    pdf_data = part.get_payload(decode=True)
                    ruta_pdf = os.path.join(CARPETA_PROYECTO, NOMBRE_PDF)
                    
                    with open(ruta_pdf, "wb") as f:
                        f.write(pdf_data)
                    
                    print(f"✅ PDF descargado: {filename}")
                    return True
        
        print("📭 No se encontró PDF adjunto")
        return None
        
    except Exception as e:
        print(f"❌ Error al buscar correo: {e}")
        return None

def ejecutar_extractor():
    """Ejecuta extractor.py para actualizar la base de datos"""
    try:
        resultado = subprocess.run(
            ["python", "extractor.py"],
            capture_output=True,
            text=True
        )
        print(resultado.stdout)
        if resultado.stderr:
            print(f"⚠️ Errores: {resultado.stderr}")
        return True
    except Exception as e:
        print(f"❌ Error al ejecutar extractor: {e}")
        return False

def main():
    print(f"🔄 Iniciando actualizador automático - {datetime.now()}")
    print(f"📧 Revisando correo: {CORREO}")
    
    mail = conectar_correo()
    if not mail:
        print("❌ No se pudo conectar al correo. Revisa tus datos.")
        return
    
    if buscar_ultimo_pdf(mail):
        print("📄 Procesando nuevo PDF...")
        if ejecutar_extractor():
            print("✅ Base de datos actualizada con éxito")
        else:
            print("❌ Error al actualizar la base de datos")
    else:
        print("⏳ No hay novedades")
    
    mail.close()
    mail.logout()
    print("✅ Ciclo completado")

if __name__ == "__main__":
    main()