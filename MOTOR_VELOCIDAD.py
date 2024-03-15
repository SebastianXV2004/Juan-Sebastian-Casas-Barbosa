import machine
import network
import socket

# Configura la interfaz WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Casas_Barbosa", "joseb@rbos@53")

# Espera a que se establezca la conexión WiFi
print("Esperando conexión a la red WiFi...")
while not wlan.isconnected():
    pass

# Imprime la dirección IP
ip_address = wlan.ifconfig()[0]
print("Conectado a la red WiFi. Dirección IP:", ip_address)

# Configura el pin GPIO 0 como salida
motor1 = machine.Pin(19, machine.Pin.OUT)
pwm = machine.PWM(machine.Pin(18))
pwm.freq(500)
motor1.value(0)

def generate_html():
    html_body = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Control de Velocidad del Motor</title>
        <h1>Juan Sebastian Casas<p>
        Haider Santiago Calderon<p>
        Juan Camilo Rodriguez</h1>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            h1 {
                text-align: center;
            }
            .container {
                width: 50%;
                margin: auto;
                text-align: center;
            }
            .motor {
                width: 100px;
                height: 100px;
                background-color: #ccc;
                border-radius: 50%;
                margin: 20px auto;
                position: relative;
                transition: transform 0.3s ease-in-out; /* Agregamos una transición para que el giro sea suave */
            }
            .motor:before {
                content: "";
                position: absolute;
                top: 50%;
                left: 50%;
                width: 10px;
                height: 40px;
                background-color: black;
                transform: translate(-50%, -50%);
            }
            .speed-slider {
                width: 80%;
                margin-bottom: 20px;
            }
            .btn {
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
            }
        </style>
        <script>
            function sendSpeed() {
                var speed = document.getElementById("speed").value;
                var xhr = new XMLHttpRequest();
                xhr.open("POST", "/", true);
                xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
                xhr.send("speed=" + speed);
                document.getElementById("motor").style.transform = "rotate(" + (speed * 1.8 - 90) + "deg)"; /* Ajustamos la rotación del motor según el valor del slider */
            }
            function stopMotor() {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", "/", true);
                xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
                xhr.send("action=stop");
                document.getElementById("motor").style.transform = "rotate(-90deg)"; /* Detenemos el motor al girarlo a su posición inicial */
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Control de Velocidad del Motor</h1>
            <div class="motor" id="motor"></div>
            <input type="range" id="speed" class="speed-slider" name="speed" min="0" max="100" onchange="sendSpeed()">
            <br>
            <button class="btn" onclick="sendSpeed()">Establecer Velocidad</button>
            <br>
            <button class="btn" onclick="stopMotor()">Detener Motor</button>
        </div>
    </body>
    </html>
    '''
    return html_body

# Función para manejar las peticiones HTTP
def handle_request(client_socket):
    request = client_socket.recv(1024).decode()
    request_method = request.split(' ')[0]
    if request_method == 'GET':
        html_body = generate_html()  # Generar la página HTML
        response = 'HTTP/1.1 200 OK\n\n' + html_body
        client_socket.send(response)
    elif request_method == 'POST':
        content = request.split('\r\n')[-1]
        if 'speed' in content:
            speed = int(content.split('=')[-1])
            pwm.duty_u16(int(speed / 100 * 65535))  # Establece la velocidad del motor
        elif 'action=stop' in content:
            pwm.duty_u16(0)  # Detiene el motor estableciendo el PWM a 0
        response = 'HTTP/1.1 303 See Other\nLocation: /\n\n'
        client_socket.send(response)
    client_socket.close()

# Configura el servidor HTTP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reutilizar la dirección IP y el puerto
server_socket.bind(('0.0.0.0', 80))
server_socket.listen(5)

print("Servidor HTTP en ejecución. Esperando peticiones...")

# Espera y maneja las peticiones entrantes
while True:
    client_socket, addr = server_socket.accept()
    handle_request(client_socket)

