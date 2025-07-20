import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración del servidor SMTP desde variables de entorno
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Rutas de archivos
PENDIENTES_ENVIO = "data/pendientes_envio.csv"
LOG_ENVIOS = "logs/log_envios.csv"

def enviar_correo(destinatario, archivo_pdf):
    try:
        # Crear el mensaje
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = destinatario
        msg['Subject'] = "Tu factura adjunta"

        # Adjuntar el archivo PDF
        with open(archivo_pdf, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={archivo_pdf}')
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

def main():
    # Leer el archivo pendientes_envio.csv
    with open(PENDIENTES_ENVIO, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)

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

            # Validar el correo
            if not validar_correo(correo):
                print(f"Correo inválido: {correo}")
                log_writer.writerow([pdf, correo, "fallido"])
                writer.writerow(row)  # Conservar en pendientes_envio.csv
                continue

            # Intentar enviar el correo
            if enviar_correo(correo, archivo_pdf):
                print(f"Correo enviado a {correo}")
                log_writer.writerow([pdf, correo, "exitoso"])
            else:
                print(f"Fallo al enviar correo a {correo}")
                log_writer.writerow([pdf, correo, "fallido"])
                writer.writerow(row)  # Conservar en pendientes_envio.csv

    print("Proceso de envío de correos completado. Revise los logs.")


def enviar_reporte(correo_admin, archivo_reporte):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = correo_admin
        msg['Subject'] = "Reporte Diario de Facturación"

        with open(archivo_reporte, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={archivo_reporte}')
            msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print(f"Reporte enviado a {correo_admin}")
    except Exception as e:
        print(f"Error al enviar reporte: {e}")

# Llama a esta función al final del script


if __name__ == "__main__":
    main()
    # Enviar reporte solo si existe
    reporte_path = "reports/resumen_diario.txt"
    if os.path.exists(reporte_path):
        enviar_reporte("24002749@galileo.edu", reporte_path)