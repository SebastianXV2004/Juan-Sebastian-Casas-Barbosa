import machine
import network
import socket
import utime

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

# Configura los pines GPIO para los motores
pwm1_adelante = machine.PWM(machine.Pin(18))
pwm1_atras = machine.PWM(machine.Pin(19))
pwm2_adelante = machine.PWM(machine.Pin(21))
pwm2_atras = machine.PWM(machine.Pin(20))

pwm1_adelante.freq(500)
pwm1_atras.freq(500)
pwm2_adelante.freq(500)
pwm2_atras.freq(500)

pwm1_adelante.duty_u16(0)
pwm1_atras.duty_u16(0)
pwm2_adelante.duty_u16(0)
pwm2_atras.duty_u16(0)

# Configuración del pin GP16 como entrada
pwm_pin = machine.Pin(16, machine.Pin.IN)

# Función para medir el ciclo de trabajo del PWM externo
def medir_ciclo_de_trabajo():
    tiempo_inicio = utime.ticks_us()
    while pwm_pin.value() == 0:
        pass
    tiempo_inicio = utime.ticks_us()
    while pwm_pin.value() == 1:
        pass
    tiempo_fin = utime.ticks_us()
    duracion_pwm = utime.ticks_diff(tiempo_fin, tiempo_inicio)
    periodo_pwm = 1 / (duracion_pwm * 1e-6)
    ciclo_de_trabajo = duracion_pwm / (duracion_pwm + periodo_pwm)
    return duracion_pwm

def mapeo_valor(numero):
    if numero >= 0 and numero <= 300:
        return 1 + (numero / 300) * 79
    elif numero > 300 and numero <= 2500:
        return 80 + ((numero - 300) / (2500 - 300)) * 20
    else:
        return None  # Para valores fuera de los rangos especificados

# Función para generar la página HTML
def generate_html(valor_error):
    html_body = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Control de Velocidad de los Motores</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .container {
                width: 100%;
                margin: auto;
                text-align: center;
            }
            .slider-container {
                width: 40%;
                margin: auto;
                display: inline-block;
                vertical-align: top;
            }
            .slider {
                width: 40px;
                height: 200px;
                margin: 10px;
                -webkit-appearance: slider-vertical;
            }
            .btn-stop {
                width: 80px;
                height: 80px;
                margin: 20px;
                border-radius: 50%;
                background-color: red;
                border: none;
                cursor: pointer;
            }
            .btn-max {
                width: 80px;
                height: 80px;
                margin: 20px;
                border-radius: 50%;
                background-color: #4CAF50;
                border: none;
                cursor: pointer;
            }
            .btn-direction {
                width: 80px;
                height: 80px;
                margin: 20px;
                border-radius: 50%;
                background-color: #2196F3;
                border: none;
                cursor: pointer;
            }
            .left {
                float: left;
            }
            .right {
                float: right;
            }
            .bottom {
                clear: both;
                margin-top: 20px;
            }
        </style>
        <script>
            function sendSpeed(motor) {
                var speed = document.getElementById("speed_" + motor).value;
                var xhr = new XMLHttpRequest();
                xhr.open("POST", "/", true);
                xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
                xhr.send("motor=" + motor + "&speed=" + speed);
            }
            function stopMotor(motor) {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", "/", true);
                xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
                xhr.send("motor=" + motor + "&action=stop");
            }
            function maxSpeed() {
                document.getElementById("speed_1").value = 100;
                document.getElementById("speed_2").value = 100;
                sendSpeed(1);
                sendSpeed(2);
            }
            function leftMaxRightMin() {
                document.getElementById("speed_1").value = 10;
                document.getElementById("speed_2").value = 75;
                sendSpeed(1);
                sendSpeed(2);
            }
            function rightMaxLeftMin() {
                document.getElementById("speed_1").value = 75;
                document.getElementById("speed_2").value = 10;
                sendSpeed(1);
                sendSpeed(2);
            }
            function minSpeed() {
                document.getElementById("speed_1").value = 0;
                document.getElementById("speed_2").value = 0;
                sendSpeed(1);
                sendSpeed(2);
            }
            function updateError() {
                var xhr = new XMLHttpRequest();
                xhr.onreadystatechange = function() {
                    if (xhr.readyState == 4 && xhr.status == 200) {
                        document.getElementById("error").innerText = "Error: " + xhr.responseText;
                    }
                };
                xhr.open("GET", "/error", true);
                xhr.send();
            }
            setInterval(updateError, 1000);  // Actualizar el error cada segundo
        </script>
    </head>
    <body>
        <div class="container">
            <div class="slider-container left">
                <input type="range" id="speed_1" class="slider" name="speed_1" min="0" max="100" onchange="sendSpeed(1)">
            </div>
            <div class="slider-container right">
                <input type="range" id="speed_2" class="slider" name="speed_2" min="0" max="100" onchange="sendSpeed(2)">
            </div>
            <button class="btn-stop" onclick="stopMotor(1)"></button>
            <button class="btn-stop" onclick="stopMotor(2)"></button>
            <button class="btn-max" onclick="maxSpeed()">&#9650;</button>
        </div>
        <div class="container bottom">
            <button class="btn-direction" onclick="leftMaxRightMin()">&#8592;</button>
            <button class="btn-direction" onclick="rightMaxLeftMin()">&#8594;</button>
            <button class="btn-max" onclick="minSpeed()">&#9660;</button>
        </div>
        <div class="container">
            <p id="error">Error: ''' + str(valor_error) + '''</p>
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
        # Calcular el valor de error
        duty_cycle = mapeo_valor(medir_ciclo_de_trabajo())
        valor_error = 100 - (duty_cycle * 100 / 85)
        
        if request.startswith("GET /error"):
            response = 'HTTP/1.1 200 OK\n\n' + str(valor_error)
        else:
            html_body = generate_html(valor_error)  # Generar la página HTML con el valor de error
            response = 'HTTP/1.1 200 OK\n\n' + html_body
        client_socket.send(response)
    elif request_method == 'POST':
        content = request.split('\r\n')[-1]
        if 'speed' in content:
            motor, speed = content.split('&')
            motor = int(motor.split('=')[-1])
            speed = int(speed.split('=')[-1])
            if motor == 1:
                if speed == 50:
                    pwm1_adelante.duty_u16(0)
                    pwm1_atras.duty_u16(0)
                elif speed > 50:
                    pwm1_adelante.duty_u16(int((speed - 50) / 50 * 65535))
                    pwm1_atras.duty_u16(0)
                else:
                    pwm1_adelante.duty_u16(0)
                    pwm1_atras.duty_u16(int((50 - speed) / 50 * 65535))
            elif motor == 2:
                if speed == 50:
                    pwm2_adelante.duty_u16(0)
                    pwm2_atras.duty_u16(0)
                elif speed > 50:
                    pwm2_adelante.duty_u16(int((speed - 50) / 50 * 65535))
                    pwm2_atras.duty_u16(0)
                else:
                    pwm2_adelante.duty_u16(0)
                    pwm2_atras.duty_u16(int((50 - speed) / 50 * 65535))
        elif 'action=stop' in content:
            motor = int(content.split('&')[0].split('=')[-1])
            if motor == 1:
                pwm1_adelante.duty_u16(0)
                pwm1_atras.duty_u16(0)
            elif motor == 2:
                pwm2_adelante.duty_u16(0)
                pwm2_atras.duty_u16(0)
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
