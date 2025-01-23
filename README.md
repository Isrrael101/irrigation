# Sistema de Riego Automatizado ESP32

Sistema IoT para monitoreo y control de riego usando ESP32, sensores DHT11 y humedad de suelo.

## Hardware

- ESP32 Dev Board
- DHT11/DHT22
- Sensor humedad suelo (resistivo/capacitivo) 
- Relé
- Bomba agua 12V
- Fuente alimentación

## Conexiones

| Componente | Pin ESP32 |
|------------|-----------|
| DHT11      | GPIO 4    |
| Suelo      | GPIO 32   |
| Bomba      | GPIO 5    |

## Software

- MicroPython
- esptool
- rshell
- Navegador moderno

## Instalación

\```bash
# Flashear MicroPython
esptool.py --port COM6 erase_flash
esptool.py --chip esp32 --port COM6 write_flash -z 0x1000 esp32-20230426-v1.20.0.bin

# Subir archivos
rshell -p COM6 -b 115200
cp main.py /pyboard/
cp data/index.html /pyboard/
cp data/styles.css /pyboard/
cp data/script.js /pyboard/
\```

## Estructura

\```
irrigation/
├── main.py             # Código principal
├── README.md
└── data/
   ├── index.html     # Interfaz web
   ├── styles.css     # Estilos
   └── script.js      # JavaScript
\```

## Configuración

\```python
# WiFi
wifi.connect('TU_SSID', 'TU_PASSWORD')

# Calibración sensor capacitivo
SUELO_SECO = 4095
SUELO_MOJADO = 1500

# Calibración sensor resistivo  
SUELO_SECO = 3200
SUELO_MOJADO = 1500
\```

## Uso

1. Encender ESP32
2. Ver IP en monitor serial
3. Acceder: `http://<IP_ESP32>`

## Características

### Dashboard
- Métricas tiempo real
- Gráficas históricas
- Control manual bomba
- Alertas humedad baja
- Responsive design

### Automatización
- Activa bomba < 30% humedad
- Desactiva bomba > 70% humedad 
- Actualización cada 2s
- Histórico 20 mediciones

## Autor

- Email: isrraelfcaq@hotmail.com
- GitHub: @Isrrael101
