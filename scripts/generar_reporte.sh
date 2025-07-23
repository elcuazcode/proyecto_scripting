#!/bin/bash

# Cargar variables de entorno desde .env si existe
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Rutas de archivos usando variables de entorno
LOG_ENVIOS="${LOG_ENVIOS:-logs/log_envios.csv}"
COMPRAS_CSV="${COMPRAS_CSV:-data/compras.csv}"
REPORTE_DIARIO="${REPORTE_DIARIO:-reports/resumen_diario.txt}"

# Crear la carpeta reports si no existe
mkdir -p "$(dirname "$REPORTE_DIARIO")"

# Verificar que los archivos existen
if [ ! -f "$LOG_ENVIOS" ]; then
    echo "Error: El archivo $LOG_ENVIOS no existe"
    exit 1
fi

if [ ! -f "$COMPRAS_CSV" ]; then
    echo "Error: El archivo $COMPRAS_CSV no existe"
    exit 1
fi

# Procesar los archivos con awk
awk -F, '
# Bloque para procesar el primer archivo: compras.csv
FNR==NR {
    if (FNR > 1) { # Ignorar el encabezado
        # Limpiar espacios y caracteres especiales del ID
        gsub(/^[ \t\r\n]+|[ \t\r\n]+$/, "", $1)
        compras[$1, "monto"] = $9
        compras[$1, "pago"] = $10
        compras[$1, "estado_pago"] = $11
    }
    next
}

# Bloque para procesar el segundo archivo: log_envios.csv
{
    total_correos++
    
    # Limpiar el estado del envío para quitar espacios o saltos de línea
    estado_envio = $3
    gsub(/^[ \t\r\n]+|[ \t\r\n]+$/, "", estado_envio)

    if (estado_envio == "exitoso") {
        exitosos++
        
        # Extraer ID de transacción del nombre del archivo PDF
        nombre_archivo = $1
        gsub(/^[ \t\r\n]+|[ \t\r\n]+$/, "", nombre_archivo)
        id_transaccion = nombre_archivo
        gsub(/factura_|\.pdf/, "", id_transaccion)
        
        # Verificar si el pago fue exitoso para sumar al total vendido
        if (compras[id_transaccion, "estado_pago"] == "exitoso") {
            total_vendido += compras[id_transaccion, "monto"]
            
            # Verificar si el tipo de pago fue completo
            if (compras[id_transaccion, "pago"] == "completo") {
                pagos_completos++
            }
        }
    } else {
        fallidos++
    }
}

END {
    fecha_hora = strftime("%Y-%m-%d %H:%M:%S")
    
    # Inicializar variables si están vacías
    if (total_correos == "") total_correos = 0
    if (exitosos == "") exitosos = 0
    if (fallidos == "") fallidos = 0
    if (total_vendido == "") total_vendido = 0
    if (pagos_completos == "") pagos_completos = 0
    
    # Generar el archivo de reporte
    print "Reporte Diario de Facturación" > "'"$REPORTE_DIARIO"'"
    print "Generado: " fecha_hora >> "'"$REPORTE_DIARIO"'"
    print "-----------------------------------" >> "'"$REPORTE_DIARIO"'"
    print "Total de correos procesados: " total_correos >> "'"$REPORTE_DIARIO"'"
    print "Correos exitosos: " exitosos >> "'"$REPORTE_DIARIO"'"
    print "Correos fallidos: " fallidos >> "'"$REPORTE_DIARIO"'"
    print "-----------------------------------" >> "'"$REPORTE_DIARIO"'"
    print "Total vendido: ₡" sprintf("%.2f", total_vendido) >> "'"$REPORTE_DIARIO"'"
    print "Pedidos pagados completamente: " pagos_completos >> "'"$REPORTE_DIARIO"'"
    print "-----------------------------------" >> "'"$REPORTE_DIARIO"'"
}' "$COMPRAS_CSV" "$LOG_ENVIOS"

echo "Reporte diario generado en $REPORTE_DIARIO"