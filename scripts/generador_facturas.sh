#!/bin/bash

# Cargar variables de entorno desde .env si existe
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Definir rutas de archivos usando variables de entorno con valores por defecto
INPUT_CSV="${COMPRAS_CSV:-data/compras.csv}"
TEMPLATE_TEX="${TEMPLATE_TEX:-templates/plantilla_factura.tex}"
OUTPUT_DIR="${OUTPUT_DIR:-output}"
LOG_FILE="${LOG_FILE:-logs/log_diario.log}"
PENDIENTES_ENVIO="${PENDIENTES_ENVIO:-data/pendientes_envio.csv}"

# Crear carpetas si no existen
mkdir -p "$OUTPUT_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Limpiar el archivo de pendientes de envío
> "$PENDIENTES_ENVIO"

# Función para parsear CSV correctamente respetando comillas
parse_csv_line() {
    local line="$1"
    # Usar awk con FPAT para manejar campos CSV con comillas correctamente
    echo "$line" | awk 'BEGIN{FPAT="([^,]+)|(\"[^\"]+\")"} {
        # Limpiar comillas dobles de todos los campos
        for(i=1; i<=NF; i++) {
            gsub(/^"/, "", $i)
            gsub(/"$/, "", $i)
        }
        print $1"|"$2"|"$3"|"$4"|"$5"|"$6"|"$7"|"$8"|"$9"|"$10"|"$11"|"$12"|"$13"|"$14
    }'
}

# Leer el archivo CSV línea por línea (ignorando el encabezado)
tail -n +2 "$INPUT_CSV" | while read -r line; do
    # Parsear la línea CSV correctamente
    parsed=$(parse_csv_line "$line")
    
    # Separar los campos usando el delimitador |
    IFS='|' read -r id fecha nombre correo telefono direccion ciudad cantidad monto pago estado ip timestamp observaciones <<< "$parsed"
    
    # Definir nombres de archivos
    OUTPUT_TEX="${OUTPUT_DIR}/factura_${id}.tex"
    OUTPUT_PDF="${OUTPUT_DIR}/factura_${id}.pdf"
    LOG_PDF="${OUTPUT_DIR}/factura_${id}.log"

    # Escapar caracteres especiales para sed
    direccion_escaped=$(echo "$direccion" | sed 's/[\/&]/\\&/g')
    observaciones_escaped=$(echo "$observaciones" | sed 's/[\/&]/\\&/g')

    # Reemplazar placeholders en la plantilla LaTeX
    sed -e "s/{id_transaccion}/${id}/g" \
        -e "s/{fecha_emision}/${fecha}/g" \
        -e "s/{nombre}/${nombre}/g" \
        -e "s/{correo}/${correo}/g" \
        -e "s/{telefono}/${telefono}/g" \
        -e "s/{direccion}/${direccion_escaped}/g" \
        -e "s/{ciudad}/${ciudad}/g" \
        -e "s/{cantidad}/${cantidad}/g" \
        -e "s/{monto}/${monto}/g" \
        -e "s/{pago}/${pago}/g" \
        -e "s/{estado_pago}/${estado}/g" \
        -e "s/{ip}/${ip}/g" \
        -e "s/{timestamp}/${timestamp}/g" \
        -e "s/{observaciones}/${observaciones_escaped}/g" \
        "$TEMPLATE_TEX" > "$OUTPUT_TEX"

    # Compilar el archivo .tex a PDF
    pdflatex -interaction=nonstopmode -output-directory="$OUTPUT_DIR" "$OUTPUT_TEX" > "$LOG_PDF" 2>&1

    # Verificar si hubo errores durante la compilación
    if grep -q "!" "$LOG_PDF"; then
        echo "Error al generar factura ${id}" >> "$LOG_FILE"
    else
        echo "Factura ${id} generada exitosamente" >> "$LOG_FILE"
        # Agregar la factura al archivo de pendientes de envío
        echo "factura_${id}.pdf,${correo}" >> "$PENDIENTES_ENVIO"
    fi
done

echo "Proceso de generación de facturas completado. Revise el log en $LOG_FILE"