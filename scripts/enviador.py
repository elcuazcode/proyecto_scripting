import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import csv
import subprocess
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración del servidor SMTP desde variables de entorno
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

# Rutas de archivos - usar variables de entorno
PENDIENTES_ENVIO = os.getenv("PENDIENTES_ENVIO", "data/pendientes_envio.csv")
LOG_ENVIOS = os.getenv("LOG_ENVIOS", "logs/log_envios.csv")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")

def enviar_correo(destinatario, archivo_pdf):
    try:
        # Crear el mensaje
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = destinatario
        msg['Subject'] = "Tu factura adjunta"

        # Agregar cuerpo del mensaje
        body = "Adjunto encontrarás tu factura. Gracias por tu compra."
        msg.attach(MIMEText(body, 'plain'))

        # Adjuntar el archivo PDF
        with open(archivo_pdf, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(archivo_pdf)}')
            msg.attach(part)

        # Conectar al servidor SMTP y enviar el correo
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo a {destinatario}: {e}")
        return False

def validar_correo(correo):
    # Expresión regular para validar correos electrónicos
    regex = r"[^@]+@[^@]+\.[^@]+"
    return re.match(regex, correo)

def generar_reporte():
    """Ejecuta el script de generación de reporte"""
    try:
        result = subprocess.run(["bash", "scripts/generar_reporte.sh"], 
                              capture_output=True, text=True, check=True)
        print("Reporte diario generado exitosamente")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al generar reporte: {e}")
        print(f"Salida del error: {e.stderr}")
        return False

def enviar_reporte(correo_admin, archivo_reporte):
    """Envía el reporte al administrador"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = correo_admin
        msg['Subject'] = "Reporte Diario de Facturación"

        # Agregar cuerpo del mensaje
        body = "Adjunto el reporte diario de facturación con el resumen de envíos y ventas."
        msg.attach(MIMEText(body, 'plain'))

        # Adjuntar el archivo de reporte
        with open(archivo_reporte, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(archivo_reporte)}')
            msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print(f"Reporte enviado exitosamente a {correo_admin}")
        return True
    except Exception as e:
        print(f"Error al enviar reporte a {correo_admin}: {e}")
        return False

def main():
    print("Iniciando proceso de envío de facturas...")
    
    # Verificar que el archivo de pendientes existe
    if not os.path.exists(PENDIENTES_ENVIO):
        print(f"Error: El archivo {PENDIENTES_ENVIO} no existe")
        return

    # Leer el archivo pendientes_envio.csv
    with open(PENDIENTES_ENVIO, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if not rows:
        print("No hay facturas pendientes para enviar")
        return

    # Crear directorio de logs si no existe
    os.makedirs("logs", exist_ok=True)

    # Procesar cada fila
    with open(PENDIENTES_ENVIO, "w", newline="", encoding="utf-8") as file_out, \
         open(LOG_ENVIOS, "a", newline="", encoding="utf-8") as log_file:
        writer = csv.writer(file_out)
        log_writer = csv.writer(log_file)

        for row in rows:
            if len(row) != 2:
                continue  # Ignorar filas mal formadas

            pdf, correo = row
            archivo_pdf = f"output/{pdf}"

            # Verificar que el archivo PDF existe
            if not os.path.exists(archivo_pdf):
                print(f"Archivo PDF no encontrado: {archivo_pdf}")
                log_writer.writerow([pdf, correo, "fallido"])
                writer.writerow(row)  # Conservar en pendientes_envio.csv
                continue

            # Validar el correo
            if not validar_correo(correo):
                print(f"Correo inválido: {correo}")
                log_writer.writerow([pdf, correo, "fallido"])
                writer.writerow(row)  # Conservar en pendientes_envio.csv
                continue

            # Intentar enviar el correo
            if enviar_correo(correo, archivo_pdf):
                print(f"Correo enviado exitosamente a {correo}")
                log_writer.writerow([pdf, correo, "exitoso"])
            else:
                print(f"Fallo al enviar correo a {correo}")
                log_writer.writerow([pdf, correo, "fallido"])
                writer.writerow(row)  # Conservar en pendientes_envio.csv

    print("Proceso de envío de correos completado.")
    
    # Generar y enviar reporte automáticamente después del envío
    print("\nGenerando reporte diario...")
    if generar_reporte():
        reporte_path = os.path.join(REPORTS_DIR, "resumen_diario.txt")
        if os.path.exists(reporte_path):
            print("Enviando reporte al administrador...")
            enviar_reporte(ADMIN_EMAIL, reporte_path)
        else:
            print("Error: No se pudo encontrar el archivo de reporte generado")
    else:
        print("Error: No se pudo generar el reporte")

if __name__ == "__main__":
    main()
