from faker import Faker
import csv
import random
from datetime import datetime

# Inicializar Faker
fake = Faker()

# Función para generar una transacción comercial simulada
def generar_compra():
    return {
        "id_transaccion": fake.uuid4(),  # ID único de la transacción
        "fecha_emision": datetime.now().strftime("%Y-%m-%d"),  # Fecha actual
        "nombre": fake.name(),  # Nombre del cliente
        "correo": fake.email(),  # Correo electrónico
        "telefono": fake.phone_number(),  # Teléfono
        "direccion": fake.address().replace("\n", ", "),  # Dirección física
        "ciudad": fake.city(),  # Ciudad
        "cantidad": random.randint(1, 10),  # Cantidad de productos comprados
        "monto": round(random.uniform(100, 1000), 2),  # Monto total en colones
        "pago": random.choice(["completo", "fraccionado"]),  # Modalidad de pago
        "estado_pago": random.choice(["exitoso", "fallido"]),  # Estado del pago
        "ip": fake.ipv4(),  # IP de compra
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
        "observaciones": random.choice(["cliente frecuente", "promoción aplicada", ""])  # Observaciones
    }

# Función principal
def main():
    # Definir el archivo CSV donde se guardarán los datos
    archivo_csv = "data/compras.csv"
    
    # Escribir los datos en el archivo CSV
    with open(archivo_csv, "w", newline="", encoding="utf-8") as file:
        # Definir los encabezados del CSV
        writer = csv.DictWriter(file, fieldnames=generar_compra().keys())
        writer.writeheader()  # Escribir encabezados
        
        # Generar 10 transacciones simuladas
        for _ in range(10):
            writer.writerow(generar_compra())

    print(f"Datos generados exitosamente en {archivo_csv}")

if __name__ == "__main__":
    main()