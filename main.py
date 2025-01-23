from machine import Pin, ADC
import dht
import network
import socket
import json
import time

# Configuración
dht_sensor = dht.DHT11(Pin(4))
soil_sensor = ADC(Pin(32))
soil_sensor.atten(ADC.ATTN_11DB)
soil_sensor.width(ADC.WIDTH_12BIT)
bomba = Pin(2, Pin.OUT)

# ELIGE TU SENSOR (comenta el que no uses)
# Capacitivo
# VALOR_AIRE = 4095
# VALOR_AGUA = 1500

# Resistivo
VALOR_AIRE = 80
VALOR_AGUA = 2000

historico = {
   'temperatura': [],
   'humedad_aire': [],
   'humedad_suelo': [],
   'tiempo': []
}
MAX_HISTORICO = 20

def conectar_wifi():
   wifi = network.WLAN(network.STA_IF)
   wifi.active(True)
   print("Conectando a WiFi...")
   wifi.connect('FABRICA', 'Carol2023@')
   
   intentos = 0
   while not wifi.isconnected() and intentos < 10:
       print("Intentando conectar...")
       time.sleep(1)
       intentos += 1
   
   if wifi.isconnected():
       ip = wifi.ifconfig()[0]
       print("¡Conectado!")
       print("IP:", ip)
       return wifi
   print("No se pudo conectar")
   return None

def leer_sensores():
   try:
       dht_sensor.measure()
       temp = dht_sensor.temperature()
       hum = dht_sensor.humidity()
       
       suma = 0
       for _ in range(10):
           suma += soil_sensor.read()
           time.sleep_ms(10)
       valor_crudo = suma / 10
       print("Valor crudo:", valor_crudo)
       
       # ELIGE TU FÓRMULA (comenta la que no uses)
       # Capacitivo: H = ((Va-Vm)/(Va-Vw))×100%
       #soil_percent = ((VALOR_AIRE - valor_crudo) * 100) / (VALOR_AIRE - VALOR_AGUA)
       
       # Resistivo: H = ((Vm-Va)/(Vw-Va))×100%
       soil_percent = ((valor_crudo - VALOR_AIRE) * 100) / (VALOR_AGUA - VALOR_AIRE)
       
       soil_percent = max(0, min(100, soil_percent))
       return temp, hum, soil_percent
   except:
       return 0, 0, 0

def actualizar_historico(temp, hum_aire, hum_suelo):
   tiempo_actual = time.localtime()
   hora = "{:02d}:{:02d}:{:02d}".format(tiempo_actual[3], tiempo_actual[4], tiempo_actual[5])
   
   historico['temperatura'].append(temp)
   historico['humedad_aire'].append(hum_aire)
   historico['humedad_suelo'].append(hum_suelo)
   historico['tiempo'].append(hora)
   
   if len(historico['temperatura']) > MAX_HISTORICO:
       for key in historico:
           historico[key] = historico[key][-MAX_HISTORICO:]

def read_file(filename):
   try:
       with open(filename, 'r', encoding='utf-8') as file:
           return file.read()
   except:
       print(f"Error leyendo archivo: {filename}")
       return ""

def handle_request(client):
   try:
       request = client.recv(1024).decode()
       request_line = request.split('\n')[0]
       method = request_line.split()[0]
       path = request_line.split()[1]
       
       if path == '/':
           response = read_file('index.html')
           client.send('HTTP/1.1 200 OK\n')
           client.send('Content-Type: text/html; charset=utf-8\n')
           client.send('Connection: close\n\n')
           client.sendall(response.encode('utf-8'))
       
       elif path == '/styles.css':
           response = read_file('styles.css')
           client.send('HTTP/1.1 200 OK\n')
           client.send('Content-Type: text/css\n')
           client.send('Connection: close\n\n')
           client.sendall(response.encode('utf-8'))
       
       elif path == '/script.js':
           response = read_file('script.js')
           client.send('HTTP/1.1 200 OK\n')
           client.send('Content-Type: text/javascript\n')
           client.send('Connection: close\n\n')
           client.sendall(response.encode('utf-8'))
       
       elif path == '/datos':
           try:
               temp, hum_aire, hum_suelo = leer_sensores()
               actualizar_historico(temp, hum_aire, hum_suelo)
               
               data = {
                   'temperatura': temp,
                   'humedad_aire': hum_aire,
                   'humedad_suelo': hum_suelo,
                   'bomba': bomba.value(),
                   'historico': historico
               }
               response = json.dumps(data)
               client.send('HTTP/1.1 200 OK\n')
               client.send('Content-Type: application/json\n')
               client.send('Connection: close\n\n')
               client.sendall(response.encode('utf-8'))
           except Exception as e:
               print("Error en /datos:", e)
               client.send('HTTP/1.1 500 Internal Server Error\n\n')
       
       elif path.startswith('/bomba'):
        if method == 'POST':
            estado = '1' in request
            bomba.value(1 if estado else 0)
            client.send('HTTP/1.1 200 OK\n')
            client.send('Content-Type: text/plain\n')  # Agregado Content-Type
            client.send('Connection: close\n\n')
            client.sendall(('OK:' + str(estado)).encode('utf-8'))  # Agregado feedback
            print('Bomba:', 'ON' if estado else 'OFF')  # Debug
   except Exception as e:
       print("Error manejando petición:", e)
   finally:
       client.close()

def main():
   wifi = conectar_wifi()
   if not wifi:
       raise Exception("Error de conexión WiFi")
   
   server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   server.bind(('', 80))
   server.listen(5)
   
   print("Servidor web iniciado")
   print("Accede a http://" + wifi.ifconfig()[0])
   
   last_measure = 0
   measure_interval = 2000
   
   while True:
       try:
           current_time = time.ticks_ms()
           
           if time.ticks_diff(current_time, last_measure) >= measure_interval:
               temp, hum_aire, hum_suelo = leer_sensores()
               print(f"T: {temp}°C, H_aire: {hum_aire}%, H_suelo: {hum_suelo}%")
               
               if hum_suelo < 30 and not bomba.value():
                   bomba.value(1)
                   print("Bomba ON - suelo seco")
               elif hum_suelo > 70 and bomba.value():
                   bomba.value(0)
                   print("Bomba OFF - suelo húmedo")
                   
               last_measure = current_time
           
           server.settimeout(0.1)
           try:
               client, addr = server.accept()
               handle_request(client)
           except OSError:
               pass
               
       except Exception as e:
           print("Error en loop principal:", e)

if __name__ == '__main__':
   try:
       main()
   except Exception as e:
       print("Error crítico:", e)