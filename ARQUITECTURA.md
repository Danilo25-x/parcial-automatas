# Arquitectura

## Árbol de carpetas
```
parcial-automatas/
├── app.py                 # punto de entrada: abre la ventana
├── SPEC.md  ARQUITECTURA.md  README.md
├── src/
│   ├── modelo.py          # modelo de datos y utilidades (aceptar cadenas, alcanzables)
│   ├── afnd_afd.py        # Módulo 1: método de subconjuntos
│   ├── af_er.py           # Módulo 2: sistema de ecuaciones y reglas
│   ├── verificador.py     # compara AFND, AFD y ER
│   ├── lector.py          # convierte el texto del editor en un autómata
│   ├── pasos.py           # AFD parcial para el paso a paso del Módulo 1
│   ├── dibujo.py          # distribución y dibujo de grafos en Canvas
│   ├── paso_a_paso.py     # control Anterior / Siguiente reutilizable
│   └── interfaz.py        # ventana con pestañas
└── tests/                 # pruebas con unittest
```

## Reglas de diseño
- La **lógica** (`modelo`, `afnd_afd`, `af_er`, `verificador`, `lector`, `pasos`) no importa Tkinter.
- La **interfaz** (`dibujo`, `paso_a_paso`, `interfaz`) solo muestra lo que devuelve la lógica.
- Solo librería estándar. Nombres de funciones en español.

## Funciones principales
| Función | Qué hace |
|---|---|
| `crear_automata(...)` | arma el diccionario del autómata |
| `acepta_cadena(automata, cadena)` | simula AFND o AFD |
| `convertir_afnd_a_afd(afnd)` | devuelve `(tabla, pasos, afd)` |
| `afd_a_er(automata)` | devuelve `(pasos, er)` |
| `acepta_er(er, cadena)` | prueba una cadena contra la ER |
| `verificar_equivalencia(afnd, afd, er, n)` | cadenas donde difieren |
| `leer_afnd(...)` | texto del editor → autómata (con errores claros) |
| `afd_parcial(afd, pasos, k)` | AFD construido hasta el paso *k* |
| `calcular_layout(...)`, `dibujar_automata(...)` | posiciones y dibujo en Canvas |

## Flujo AFND → AFD → ER
1. `leer_afnd` convierte el texto del editor en `afnd`.
2. `convertir_afnd_a_afd(afnd)` devuelve `tabla`, `pasos` y `afd`.
3. `afd_a_er(afd)` devuelve los pasos con regla y la `er`.
4. `verificar_equivalencia(afnd, afd, er, n)` compara los tres.
