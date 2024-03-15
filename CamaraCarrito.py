#https://docs.circuitpython.org/projects/ov7670/en/latest/examples.html
# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""Capture an image from the camera and display it as ASCII art.

The camera is placed in YUV mode, so the top 8 bits of each color
value can be treated as "greyscale".

It's important that you use a terminal program that can interpret
"ANSI" escape sequences.  The demo uses them to "paint" each frame
on top of the prevous one, rather than scrolling.

Remember to take the lens cap off, or un-comment the line setting
the test pattern!
"""

import sys
import time
import pwmio
import digitalio
import busio
import board

PWM = pwmio.PWMOut(board.GP16, frequency=5000, duty_cycle=0)

from adafruit_ov7670 import (  # pylint: disable=unused-import
    OV7670,
    OV7670_SIZE_DIV16,
    OV7670_COLOR_YUV,
    OV7670_TEST_PATTERN_COLOR_BAR_FADE,
)

# Ensure the camera is shut down, so that it releases the SDA/SCL lines,
# then create the configuration I2C bus

#with digitalio.DigitalInOut(board.D39) as shutdown:
#    shutdown.switch_to_output(True)
#    time.sleep(0.001)
cam_bus = busio.I2C(board.GP21, board.GP20)

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
cam.size = OV7670_SIZE_DIV16
cam.colorspace = OV7670_COLOR_YUV
cam.flip_y = True

#print(cam.width, cam.height)

buf = bytearray(2 * cam.width * cam.height)
# print('##################################')
# print(buf)
cam.capture(buf)
# print('##################################')
# print(len(buf))
# print('##################################')
# print(len(list(buf)))


chars = b"###-------"

width = cam.width
row = bytearray(2 * width)
lista_camera = []
lista_errores = []
lista_prom_errores = []
posiciones_35 = []
distancia = 0
error_porcentaje = 0
prom_error_fila = 0
error_total = 0

while True:
    cam.capture(buf)
    lista_prom_errores = []
    for j in range(cam.height):
        lista_errores = []
        for i in range(cam.width):
            row[i * 2] = row[i * 2 + 1] = chars[
                buf[2 * (width * j + i)] * (len(chars) - 1) // 255]
            if 10 <= j <= 20:
                lista_camera = list(row)
                posiciones_35 = [i for i, x in enumerate(lista_camera) if x == 35]  # Obtiene todas las posiciones de '35' en la lista
                if len(posiciones_35)==0:
                    posicion_promedio_35 = 0
                    error_porcentaje = (abs(40 - posicion_promedio_35) / 40) * 100
                else:
                    posicion_promedio_35 = sum(posiciones_35) / len(posiciones_35)  # Calcula el promedio de las posiciones de '35'
                    distancia = abs(40 - posicion_promedio_35)  # Calcula la distancia entre la posición 40 y el promedio de las posiciones de '35'
                    error_porcentaje = (abs(40 - posicion_promedio_35) / 40) * 100
                lista_errores.append(error_porcentaje)
                #print(error_porcentaje)
                #print(lista_errores)
            #print(lista_errores)
        #print(lista_errores)
        if len(lista_errores) != 0:
            prom_error_fila = sum(lista_errores) / len(lista_errores)
            lista_prom_errores.append(prom_error_fila)
        #print(row)
        #print(posiciones_35)
        #print(lista_camera)
        #print(lista_errores)
        #print("El porcentaje de error es:", error_porcentaje, "%")
        #print("La distancia entre la posición 40 y el promedio de todas las posiciones de '35' es:", distancia)
        #print(len(lista_camera))
    #print(lista_prom_errores)
    error_total = sum(lista_prom_errores) / len(lista_prom_errores)
    print(error_total, "%")
    PWM.duty_cycle = int(65535/error_total)
    print(PWM)
    #print(list(row))
    print()
    time.sleep(1.2)