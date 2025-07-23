# Sistema Automatizado de Facturación - Mercado IRSI

Sistema completo de facturación electrónica que genera datos simulados, crea facturas en PDF, envía correos electrónicos y genera reportes automáticos.

## Características

- Generación automática de datos de transacciones con Faker
- Creación de facturas PDF profesionales con LaTeX
- Envío automatizado de correos electrónicos
- Generación de reportes diarios
- Programación automática con cron
- Manejo seguro de credenciales con variables de entorno

## Instalación

### Prerrequisitos

- Python 3.7+
- LaTeX (pdflatex)
- Git

### Configuración

1. Clonar el repositorio:
```bash
git clone https://github.com/elcuazcode/proyecto_scripting.git
cd proyecto_scripting
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# venv\Scripts\activate     # En Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales reales
```

5. Dar permisos de ejecución a los scripts:
```bash
chmod +x scripts/*.sh
```

## Uso

### Generar datos de prueba
```bash
python scripts/generador_compras.py
```

### Generar facturas
```bash
./scripts/generador_facturas.sh
```

### Enviar facturas por correo
```bash
python scripts/enviador.py
```

### Generar reporte
```bash
./scripts/generar_reporte.sh
```

## Automatización con Cron

Agregar al crontab:
```bash
# Generar facturas a las 17:00 PM todos los días
00 17 * * * /ruta/completa/scripts/run_generador.sh >> /ruta/completa/logs/cron.log 2>&1

# Enviar facturas y reporte a las 18:00 PM todos los días
00 18 * * * /ruta/completa/scripts/run_enviador.sh >> /ruta/completa/logs/cron.log 2>&1
```

## Estructura del Proyecto

```
proyecto_scripting/
├── scripts/
│   ├── generador_compras.py
│   ├── generador_facturas.sh
│   ├── enviador.py
│   ├── generar_reporte.sh
│   ├── run_generador.sh
│   └── run_enviador.sh
├── templates/
│   └── plantilla_factura.tex
├── data/
├── logs/
├── output/
├── reports/
├── .env.example
├── requirements.txt
└── README.md
```

## Configuración de Correo

Para usar Gmail, necesitas:
1. Habilitar autenticación de dos factores
2. Generar una contraseña de aplicación
3. Usar esa contraseña en EMAIL_PASSWORD

## Licencia

Este proyecto es de uso educativo y demostrativo.