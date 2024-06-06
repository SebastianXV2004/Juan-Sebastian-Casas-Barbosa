import time
import digitalio
import busio
import board

from adafruit_ov7670 import OV7670, OV7670_SIZE_DIV16, OV7670_COLOR_YUV

# Configurar el bus UART.

uart = busio.UART(board.GP16, board.GP17, baudrate=9600)

#Definimos la conexion I2C de la camara.

cam_bus = busio.I2C(board.GP21, board.GP20)

#Definimos las conexiones fisicas de la camara.

cam = OV7670(
    cam_bus,
    data_pins=[
        board.GP0,
        board.GP1,
        board.GP2,
        board.GP3,
        board.GP4,
        board.GP5,
        board.GP6,
        board.GP7,
    ],
    clock=board.GP8,
    vsync=board.GP13,
    href=board.GP12,
    mclk=board.GP9,
    shutdown=board.GP15,
    reset=board.GP14,
)

#Definimos algunas caracteristicas propias de la camara.

cam.size = OV7670_SIZE_DIV16
cam.colorspace = OV7670_COLOR_YUV
cam.flip_y = True
buf = bytearray(2 * cam.width * cam.height)
chars = b"#" * 128 + b"-" * 128 #Definimos una lectura de solo oscuro y claro.
width = cam.width
row = bytearray(2 * width)

error_anterior = 0.1#Inicializamos la variable que nos ayudara a comparar algunas carteristicas del analisis de la camara sobre la linea.

while True:
    
    cam.capture(buf) #LLamamos al listado de datos de la camara.
    error_suma = 0  #Suma de errores para calcular el promedio al final.
    cantidad_filas = cam.height  # Número total de filas con base a la camara.
    filas_interes = range(20, 21)  # Filas de interés para elavluar.
    
    #Realizamos ahora un barrido de los elemntos desntro de las finlas de interes.
    
    for j in filas_interes:
        
        error_filaN,error_filaP = 0,0  # Error para la fila actual entre positivos y negativos.
        row_index = width * j * 2
        
        #Definimos un rango de evaluo dentro de las filas asi como un salto para reducir los tiempos de analisis.
        
        for i in range(26, 54, 2):
            
            #LLamos la indormacion.
            pixel_value = buf[row_index + i]
            char_index = pixel_value * (len(chars) - 1) // 255
            char_value = chars[char_index]
            row[i] = row[i + 1] = char_value
            
            #Ahora bien los datos del rango se dividen en dos de manera en la cual comparamos con el centro para visualizar datos positivos y negativos.
            #Los datos negativos representan la informacion a la derecha del centro de la camara.
            #Los datos positivos representan la informacion a la derecha del centro de la camara.
            
            if 26<=i<=38:
                if char_value == 35:  # Si el carácter es '#'.
                    error_filaN += 1 #Añadimos uno a los datos de error en la fila de negativos.
            else:
                if char_value == 35:  # Si el carácter es '#'.
                    error_filaP += 1 #Añadimos uno a los datos de error en la fila de positivos.
                    
        #print("N",error_filaN,"P",error_filaP)#Visualizamos la distribuicion de los errores en camara actual.
                    
        #Ahora condiconamos nuestros datos a rangos de entre -100 a 100.
                    
        if error_filaP==error_filaN:#Se tiene que definir rangos simetricos para poder complir esta condicion.
            
            #existen dos condiciones para las cuales sean similares los datos.
            
            if error_filaP==0:#Ya condicionamos a que son iguales de manera en la cual decimos entonces que si son 0 indica que esta fuera de la linea.
                
                #Haciendo uso del valor anterior comparamos para decifrar si nos salimos de la linea a derecha o izquierda.
                
                if error_anterior>0:
                    #Si el valor anterior es mayor a 0 indica que nos salimos a derecha de la linea por ende marcamos 100 en error promedio.
                    error_promedio=100
                else:
                    #Si el valor anterior es menor a 0 indica que nos salimos a izquierda de la linea por ende marcamos -100 en error promedio.
                    error_promedio=-100
            
            else:#Dado que no es 0 entonces nos indica que son simetricos por ejemplo 7:7 asi que en dado caso decimos que el error promedio es 0 osea no esta fuera de la linea.
                error_promedio = 0
        
        else:#Por lo contrario indica que tenemos asimetria entre lso valores positivos y negativos.
            
            error_suma = error_filaP+error_filaN#Realizamos una suma de ambos datos.
            
            #Definimos entonces unas condiciones para determinar de que manera debemos analizar el dato del error promedio.
            if error_filaP>error_filaN:#Si se cumple la condicion indica que la camara esta algo a la derecha del centro de la linea
                
                
                error_promedio = int(abs((error_suma / 14)-1)*100)#Hallamos el porcentaje de error con respecto al maximo de sumatoria que podemos obtener "14"
                #Cabe resaltar que dada la condicion entonces hallamos el valor absoluto de ese promedio para abarcar un rango de entre 0 a 100.
            else:#Si se cumple la condicion indica que la camara esta algo a la izquierda del centro de la linea

                error_promedio = int(((error_suma / 14)-1)*100)#Hallamos el porcentaje de error con respecto al maximo de sumatoria que podemos obtener "14"
                #Cabe resaltar que dada la condicion entonces no hallamos el valor absoluto de ese promedio para abarcar un rango de entre -100 a 0.

                
        error_anterior = error_promedio#Registramos el valor actual en una variable que luego usaremos apra comparar como un valor anterior.
        
    uart.write(str(error_promedio).encode() + b"\r\n")#Enviamos la informacion mediante la uart.