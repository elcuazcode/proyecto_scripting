#!/bin/bash

# Rutas de archivos
LOG_ENVIOS="logs/log_envios.csv"
REPORTE_DIARIO="reports/resumen_diario.txt"

# Crear la carpeta reports si no existe
mkdir -p "$(dirname "$REPORTE_DIARIO")"

# Verificar que el archivo de log existe
if [ ! -f "$LOG_ENVIOS" ]; then
    echo "Error: El archivo $LOG_ENVIOS no existe"
    exit 1
fi

# Procesar el archivo log_envios.csv con awk
awk -F',' 'BEGIN {
    total = 0
    exitosos = 0
    fallidos = 0
    total_vendido = 0
}
{
    if (NR > 1) {  # Ignorar la primera línea (encabezado)
        total++
        if ($3 == "exitoso") {
            exitosos++
        } else {
            fallidos++
        }
    }
}
END {
    print "Reporte Diario de Facturación" > "'"$REPORTE_DIARIO"'"
    print "-----------------------------------" >> "'"$REPORTE_DIARIO"'"
    print "Total de correos procesados: " total >> "'"$REPORTE_DIARIO"'"
    print "Correos exitosos: " exitosos >> "'"$REPORTE_DIARIO"'"
    print "Correos fallidos: " fallidos >> "'"$REPORTE_DIARIO"'"
    print "-----------------------------------" >> "'"$REPORTE_DIARIO"'"
}' "$LOG_ENVIOS"

echo "Reporte diario generado en $REPORTE_DIARIO"