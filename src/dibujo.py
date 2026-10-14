"""Dibujo de autómatas en un Canvas de Tkinter.

Convención de clase: estados como óvalos, flechas con el símbolo,
flecha de entrada al estado inicial y doble óvalo en los finales.
Las funciones de posición no usan Tkinter (se pueden probar solas).
"""

import math
from collections import deque

ALTO = 22                      # radio vertical de los óvalos
FUENTE = ("Arial", 10)
COLOR_NORMAL = "black"
COLOR_RESALTE = "#d62828"
RELLENO_RESALTE = "#ffe066"


def radio_horizontal(nombre):
    """Ancho del óvalo según el largo del nombre del estado."""
    return max(26, 4 * len(nombre) + 14)


def agrupar_aristas(automata):
    """{(origen, destino): [símbolos]}: una flecha por par de estados."""
    orden = {e: i for i, e in enumerate(automata["estados"])}
    grupos = {}
    for (origen, simbolo), destinos in automata["transiciones"].items():
        for destino in destinos:
            grupos.setdefault((origen, destino), []).append(simbolo)
    claves = sorted(grupos, key=lambda k: (orden.get(k[0], 0), orden.get(k[1], 0)))
    return {k: sorted(set(grupos[k])) for k in claves}


def calcular_niveles(automata):
    """Distancia de cada estado al inicial (los inalcanzables van al final)."""
    vecinos = {}
    for (origen, _), destinos in automata["transiciones"].items():
        vecinos.setdefault(origen, []).extend(destinos)
    nivel = {automata["inicial"]: 0}
    cola = deque([automata["inicial"]])
    while cola:
        actual = cola.popleft()
        for destino in vecinos.get(actual, []):
            if destino not in nivel:
                nivel[destino] = nivel[actual] + 1
                cola.append(destino)
    ultimo = max(nivel.values())
    for estado in automata["estados"]:
        if estado not in nivel:
            nivel[estado] = ultimo + 1
    return nivel


def calcular_layout(automata, ancho, alto):
    """Posición (x, y) de cada estado: una columna por nivel."""
    nivel = calcular_niveles(automata)
    columnas = {}
    for estado in automata["estados"]:
        columnas.setdefault(nivel[estado], []).append(estado)
    claves = sorted(columnas)
    izquierda = 100
    ancho_max = max(radio_horizontal(e) for e in automata["estados"])
    paso_x = 0
    if len(claves) > 1:
        disponible = (ancho - izquierda - 70) / (len(claves) - 1)
        paso_x = max(2 * ancho_max + 70, min(230, disponible))
    posiciones = {}
    for indice, clave in enumerate(claves):
        estados = columnas[clave]
        x = izquierda + indice * paso_x if len(claves) > 1 else ancho / 2
        paso_y = max(90, (alto - 80) / len(estados))
        y0 = max(80, alto / 2 - paso_y * (len(estados) - 1) / 2)
        for i, estado in enumerate(estados):
            posiciones[estado] = (x, y0 + i * paso_y)
    return posiciones


# ---------- Dibujo en el Canvas ----------

def _borde(centro, rx, ry, hacia):
    """Punto del borde del óvalo en la dirección de 'hacia'."""
    dx, dy = hacia[0] - centro[0], hacia[1] - centro[1]
    t = 1 / math.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
    return centro[0] + dx * t, centro[1] + dy * t


def _distancia_a_segmento(p, a, b):
    ax, ay = a
    bx, by = b
    largo2 = (bx - ax) ** 2 + (by - ay) ** 2
    t = max(0, min(1, ((p[0] - ax) * (bx - ax) + (p[1] - ay) * (by - ay)) / largo2))
    return math.hypot(p[0] - (ax + t * (bx - ax)), p[1] - (ay + t * (by - ay)))


def _tapa_otro_estado(posiciones, origen, destino):
    """True si la flecha recta pasaría por encima de otro estado."""
    for estado, centro in posiciones.items():
        if estado in (origen, destino):
            continue
        if _distancia_a_segmento(centro, posiciones[origen],
                                 posiciones[destino]) < ALTO + 12:
            return True
    return False


def _bucle(canvas, centro, nombre, texto, color, grosor):
    x, y = centro
    arriba = y - ALTO
    puntos = [x - 14, arriba + 2, x - 28, arriba - 36,
              x + 28, arriba - 36, x + 14, arriba + 2]
    canvas.create_line(*puntos, smooth=True, arrow="last", fill=color, width=grosor)
    canvas.create_text(x, arriba - 46, text=texto, fill=color, font=FUENTE)


def _flecha(canvas, posiciones, origen, destino, texto, curva, color, grosor):
    (x1, y1), (x2, y2) = posiciones[origen], posiciones[destino]
    r1 = (radio_horizontal(origen), ALTO)
    r2 = (radio_horizontal(destino), ALTO)
    largo = math.hypot(x2 - x1, y2 - y1)
    nx, ny = -(y2 - y1) / largo, (x2 - x1) / largo      # perpendicular
    if curva:
        ctrl = ((x1 + x2) / 2 + nx * 45, (y1 + y2) / 2 + ny * 45)
        ini = _borde((x1, y1), *r1, ctrl)
        fin = _borde((x2, y2), *r2, ctrl)
        canvas.create_line(*ini, *ctrl, *fin, smooth=True, arrow="last",
                           fill=color, width=grosor)
        medio = (0.25 * ini[0] + 0.5 * ctrl[0] + 0.25 * fin[0],
                 0.25 * ini[1] + 0.5 * ctrl[1] + 0.25 * fin[1])
        etiqueta = (medio[0] + nx * 10, medio[1] + ny * 10)
    else:
        ini = _borde((x1, y1), *r1, (x2, y2))
        fin = _borde((x2, y2), *r2, (x1, y1))
        canvas.create_line(*ini, *fin, arrow="last", fill=color, width=grosor)
        if ny > 0:                                        # etiqueta hacia arriba
            nx, ny = -nx, -ny
        etiqueta = ((ini[0] + fin[0]) / 2 + nx * 12, (ini[1] + fin[1]) / 2 + ny * 12)
    canvas.create_text(*etiqueta, text=texto, fill=color, font=FUENTE)


def _estado(canvas, centro, nombre, es_final, resaltado):
    x, y = centro
    rx = radio_horizontal(nombre)
    relleno = RELLENO_RESALTE if resaltado else "white"
    canvas.create_oval(x - rx, y - ALTO, x + rx, y + ALTO,
                       fill=relleno, outline=COLOR_NORMAL, width=2)
    if es_final:                                          # doble óvalo
        canvas.create_oval(x - rx + 5, y - ALTO + 5, x + rx - 5, y + ALTO - 5,
                           outline=COLOR_NORMAL, width=2)
    canvas.create_text(x, y, text=nombre, font=FUENTE)


def dibujar_automata(canvas, automata, resaltar_estados=(), resaltar_arista=None):
    """Dibuja el autómata completo.

    resaltar_estados: estados con relleno amarillo.
    resaltar_arista: (origen, símbolo, destino) que se dibuja en rojo.
    """
    canvas.delete("all")
    if not automata or not automata["estados"]:
        canvas.create_text(20, 20, anchor="nw", text="(sin autómata)", fill="gray")
        return
    ancho = max(canvas.winfo_width(), 360)
    alto = max(canvas.winfo_height(), 240)
    posiciones = calcular_layout(automata, ancho, alto)
    aristas = agrupar_aristas(automata)

    for (origen, destino), simbolos in aristas.items():
        resaltada = (resaltar_arista is not None
                     and (origen, destino) == (resaltar_arista[0], resaltar_arista[2])
                     and resaltar_arista[1] in simbolos)
        color = COLOR_RESALTE if resaltada else COLOR_NORMAL
        grosor = 3 if resaltada else 1.5
        texto = ",".join(simbolos)
        if origen == destino:
            _bucle(canvas, posiciones[origen], origen, texto, color, grosor)
        else:
            curva = ((destino, origen) in aristas
                     or _tapa_otro_estado(posiciones, origen, destino))
            _flecha(canvas, posiciones, origen, destino, texto, curva, color, grosor)

    for estado in automata["estados"]:
        _estado(canvas, posiciones[estado], estado,
                estado in automata["finales"], estado in resaltar_estados)

    x, y = posiciones[automata["inicial"]]                # flecha de entrada
    rx = radio_horizontal(automata["inicial"])
    canvas.create_line(x - rx - 45, y, x - rx, y, arrow="last", width=2)

    caja = canvas.bbox("all")
    canvas.configure(scrollregion=(min(0, caja[0] - 10), min(0, caja[1] - 10),
                                   max(ancho, caja[2] + 10), max(alto, caja[3] + 10)))
