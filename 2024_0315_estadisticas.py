# -*- coding: utf-8 -*-
"""2024_0315_Estadisticas.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18SnpRz8MFcdkbT6zJ-BhtmhseDqDqO34
"""

from math import sqrt

v = [10, 7, 9, 11, 19]

def promedio(v):
    k = len(v)
    sumatoria = 0
    for i in range(k):
        sumatoria += v[i]
    prom = sumatoria / k
    return prom


def desv_est(v):
    k = len(v)
    prom = promedio(v)
    sumatoria = 0
    for i in range(k):
        sumatoria += (v[i] - prom) ** 2
    desv_est = sqrt (sumatoria / k)
    return desv_est


def varianza(v):
    k = len(v)
    prom = promedio(v)
    sumatoria = 0
    for i in range(k):
        sumatoria += (v[i] - prom) ** 2
    var = sumatoria / k
    return var


print("Promedio:", promedio(v))
print("Desviacion estandar:", desv_est(v))
print("Varianza:", varianza(v))