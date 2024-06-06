from Matrix import Matrix
import array
import random
from machine import Pin, UART, PWM, I2C
import utime
import time
import ssd1306

#Definimos algunos pines para LEDs que utilizaremos al aplicar el entrenamiento.

Red = Pin(18, Pin.OUT)
Green = Pin(19, Pin.OUT)

#Definimos el pin que nos ayuda a cambiar de modo de entrenamiento a aplicacion de la red neuronal.

gp0_pin = Pin(0, Pin.IN)

#Definimos la uart por donde estaremos recibiendo los datos transmitidos por el microcontrolador que maneja la camara.

uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

received_text = ""#Inicializamos estado vacio para la informacion recibida para la uart en un primer momento.

#Definimos los pines a trabajar para cada uno de los motores.

motor_derecho_pwm = PWM(machine.Pin(16))
motor_izquierdo_pwm = PWM(machine.Pin(17))

#Definimos las caracteristicas de los motores.

motor_derecho_pwm.freq(500)
motor_izquierdo_pwm.freq(500)

motor_derecho_pwm.duty_u16(0)  
motor_izquierdo_pwm.duty_u16(0)

#Definimos caracteristicas para la pantalla OLED.

i2c = I2C(1, scl=Pin(27), sda=Pin(26))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Función para dibujar el tacómetro en la pantalla OLED

def draw_tachometer(Velocidad_Izquierdo, Velocidad_Derecho,Valor_Error):
    
    oled.fill(0)#Apagamos todos los pixeles de la pantalla.
    Max_Valor_Barra=65555#Definimos el valormaximo alcanzable de la barra.
    
    #Dibujar la barra para el motor izquierdo.
    
    Barra_Izquierda = int((Velocidad_Izquierdo / Max_Valor_Barra) * 40)
    if Barra_Izquierda < 0:
        Barra_Izquierda = 0
    elif Barra_Izquierda > 40:
        Barra_Izquierda = 40
    oled.rect(5, 10, 10, 40, 1)
    oled.fill_rect(6, 50 - Barra_Izquierda, 8, Barra_Izquierda, 1)
    
    #Dibujar la barra para el motor derecho.
    
    Barra_Derecha = int((Velocidad_Derecho / Max_Valor_Barra) * 40)
    if Barra_Derecha < 0:
        Barra_Derecha = 0
    elif Barra_Derecha > 40:
        Barra_Derecha = 40
    oled.rect(110, 10, 10, 40, 1)
    oled.fill_rect(111, 50 - Barra_Derecha, 8, Barra_Derecha, 1)
    
    # Mostrar el valor del RPM para el motor izquierdo.
    
    oled.text("RPM Izq:", 35, 3)
    oled.text(str(Velocidad_Izquierdo), 50, 12)
    
    # Mostrar el valor del RPM para el motor derecho.
    
    oled.text("RPM Der:", 35, 21)
    oled.text(str(Velocidad_Derecho), 50, 30)
    
    # Mostrar el valor del error.
    
    oled.text("Valor Error", 19, 39)
    oled.text(str(Valor_Error), 50, 48)
    
    oled.show()#Mostramos la infromacion de la pantalla.

#Definimos la clase Perceptron que se encargará de la red neuronal.
    
class Perceptron:
    
    #Definimos las caractereisticas de la matriz de pesos con esta definicion.
    
    def __init__(self, ENTRADAS, SALIDAS=None):
        
        #Realizamos una condicion que nos diga si existe informacion en la matriz de pesos o si no generar una aleatoria.
        
        if isinstance(ENTRADAS,str):
            
            self.weights = Matrix.load_file(ENTRADAS)
            
        else:
            
            self.weights = Matrix(ENTRADAS+1, SALIDAS+1,  [random.random() for _ in range((ENTRADAS+1) * (SALIDAS+1))])
            
    #Definimos la manera en la que trabajaremos las predicciones de las variables de salida con la siguiente definicion.
            
    def predict(self, inputs):
        
        tail=False
        
        if inputs.n==self.weights.m-1:
            
            result = Matrix.untail(Matrix.tail(inputs) * self.weights)
            
        else:
            
            result = inputs * self.weights
            
        return result
    
    #Definimos la forma en la cual traajamos el entrenamiento de la red con base en datos introduciodos a esta definicion.
    
    def train(self, inputs, labels, learning_rate=0.01, epochs=1):
        
        if inputs.n==self.weights.m-1:
            
            inputs=Matrix.tail(inputs)
            
        if labels.n==self.weights.n-1:
            
            labels=Matrix.tail(labels)
            
        for epoch in range(epochs):
            
            predictions = self.predict(inputs)
            
            error = labels - predictions
            
            self.weights=self.weights.add_tail(  inputs.T() * error * learning_rate)

    #Definimos la manera en la cual aseguraremos que se guarde la matriz de pesos.
            
    def save_file(self, name):
        
        self.weights.save_file(name)

v_i,v_d,v_i_Porcentual,v_d_Porcentual,Contador_Entrenamiento=0,0,0,0,0  #Inicializamso algunas de las carcteristicas del proceso de entrenamiento.

while True:
    
    try:

        datos_recibidos = uart.read(1)  # Leer un byte de datos
        
        if datos_recibidos:
            
            char = datos_recibidos.decode('utf-8', 'replace')
            
            if char == '\r':  # Si se recibe retorno de camara
                
                try:
                    
                    valor = int(received_text.strip())  #Transformamos el valor recibido a un numero entero.
                    
                except ValueError:
                    
                    print("El texto recibido no es un número entero válido:", received_text)
                    valor = None  #Valor invalido.
                    received_text = ""  # Reiniciar la variable para el próximo texto.
                    continue  # Saltar el resto del ciclo y esperar más datos.

                if __name__ == "__main__":
                    
                    #Definimos la matriz de pesos como el contenido del archivo carro.txt.
                    
                    perceptron = Perceptron("carro.txt")
                    
                    # Leer el estado del pin gp0 encargado de evaluar si esta entrenando o aplicando la red.
                    
                    if gp0_pin.value() == 1:
                        
                        train = False#Definimos entrada de la red.
                        
                    else:
                        train = True#Definimos entrada  del entrenamiento.
                    
                    #Definimos la manera en la que realizamso el control del entrenamiento.

                    def train_control():
                        
                        global Contador_Entrenamiento,train #Definimos algunas variables como cambiantes en esta definicion.
                    
                        LINE_MATRIX = Matrix(1,1,[valor])#Definimos el contenido de la siguiente matriz con el valor leído de la uart
                        
                        #Evaluamos la condicion del valor registrado en train
                        
                        if train==True:#De ser cierto hablamos de nuestro metodo para entrenamiento automatico.
                            
                            multiplier=655.55/3#Variable que regula la velocidad de los motores.
                            
                            v_d_Porcentual=int(min(100,(100+LINE_MATRIX[0,0])))#Proceso encargado de la velocidad porcentual del motor derecho.
                            v_i_Porcentual=int(min(100,(100-LINE_MATRIX[0,0])))#Proceso encargado de la velocidad porcentual del motor izquierdo.
                            
                            v_d=int(v_d_Porcentual*multiplier)#Regulacion de la velocidad a valores de entre 65555 y 0 para motor derecho.
                            v_i=int(v_i_Porcentual*multiplier)#Regulacion de la velocidad a valores de entre 65555 y 0 para motor izquierdo.
                            
                            motors_vel= Matrix(1,2,[v_i,v_d])#Generamos una matriz que almacena los valores de velocidad de ambos motores.
                            
                            perceptron.train(LINE_MATRIX, motors_vel)#llamamos a entrenamiento para que actue con las variables suministradas.
                            
                            Contador_Entrenamiento +=1#Generamos un contador acomulativo.
                            
                            #Definimos unas condiciones en las cuales registraremos adecuadamente el guardado de la matriz de pesos cada 100 lecturas de la uart.
                            
                            if Contador_Entrenamiento==100:
                                
                                #perceptron.save_file("carro.txt")#Guardamos la informacion de pesos en carro.txt.
                                Green.value(1)#Encendemos el LED verde cada que guardamos la matriz de pesos.
                                Red.value(0)#Apagamos el LED rojo cada que guardamos la matriz de pesos.
                                Contador_Entrenamiento=0#Volvemos a inicializar el contador en 0.
                                
                            else:
                                
                                Green.value(0)#Mantenemos apagado el LED verde.
                                Red.value(1)#Mantenemos encendido el LED rojo.
                            
                        else:#De no cumplirse la condición inicial entonces hablamos de aplicar la red neuronal.
                            
                            prediction=perceptron.predict(LINE_MATRIX)#Definimos una matrix que contenga los valores de la predicción.
                            
                            #Definimos los valores de velocidad con las predicciones.
                            
                            v_i=prediction[0,0]#Velocidad izquierda.
                            v_d=prediction[0,1]#Velociadd derecha.
                            
                        #Saliendo de las condiciones aplicamos los mismos metodos de velodiades y dibujar el tacometro para ambas situaciones.
                            
                        motor_derecho_pwm.duty_u16(abs(int(v_d)))#Configurar velocidad motor derecho.
                        motor_izquierdo_pwm.duty_u16(abs(int(v_i)))#Configurar velocidad motor izquierdo.
                        draw_tachometer(v_i, v_d,valor)#Dibujamos la informacion en la pantalla OLED.
                                
                    train_control()#Hacemos un llamado a la definicion.
                
                received_text = ""  #Reiniciar la variable para el próximo texto.
            else:
                received_text += char

    except KeyboardInterrupt:
        break
