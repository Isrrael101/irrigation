import network
import socket
from machine import Pin
import time

# Configuración de la red WiFi
ssid = 'SIB ORURO 2024'
password = 'siboruro2024'

# Configurar el pin para la bomba
pump = Pin(2, Pin.OUT)  # Usando GPIO2, ajusta según tu conexión
pump.off()  # Inicialmente apagada

# Función para conectarse al WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a WiFi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Conexión WiFi exitosa')
    print('Dirección IP:', wlan.ifconfig()[0])
    return wlan

# Página HTML
def web_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Control de Bomba</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { text-align: center; font-family: Arial; }
            .button {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 16px 40px;
                text-decoration: none;
                font-size: 30px;
                margin: 2px;
                cursor: pointer;
                border-radius: 8px;
            }
            .button-off {
                background-color: #ff0000;
            }
        </style>
    </head>
    <body>
        <h1>Control de Bomba</h1>
        <p>Estado: %s</p>
        <a href="/?pump=on"><button class="button">ENCENDER</button></a>
        <a href="/?pump=off"><button class="button button-off">APAGAR</button></a>
    </body>
    </html>
    """ % ("APAGADA" if pump.value() else "ENCENDIDA")
    return html

# Conectar al WiFi
wlan = connect_wifi()

# Configurar servidor web
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

print('Servidor web iniciado')

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024).decode()
        
        # Procesar solicitud
        if "GET /?pump=on" in request:
            pump.off()
        elif "GET /?pump=off" in request:
            pump.on()
            
        # Enviar respuesta
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response.encode())
        conn.close()
        
    except Exception as e:
        conn.close()
        print('Error:', e)
