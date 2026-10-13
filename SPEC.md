# SPEC · Simulador gráfico de autómatas

Teoría de la Computación · Parcial 2.º corte. App de escritorio en **Python + Tkinter**
(solo librería estándar, sin internet, sin servidores). Se ejecuta con `python app.py`.

## 1. Objetivo
Convertir un AFND en AFD, obtener la expresión regular (ER) de un autómata y comprobar
que AFND, AFD y ER reconocen el mismo lenguaje.

## 2. Modelo de datos
Un autómata es un diccionario:

| Clave | Contenido |
|---|---|
| `estados` | lista de nombres (`["q0","q1"]`) |
| `alfabeto` | lista de símbolos de **un carácter** (`["a","b"]`) |
| `inicial` | nombre del estado inicial |
| `finales` | lista de estados finales |
| `transiciones` | `{(estado, símbolo): [estados destino]}` |

Los símbolos no pueden ser `+ * ( ) λ ∅ ε`. La transición ε se escribe con el símbolo `ε`.

## 3. Requisitos funcionales
1. **Editor de AFND:** estados, alfabeto, inicial, finales y transiciones (una por línea: `origen,símbolo,destino`). Botones para cargar los ejemplos del Anexo A.
2. **Módulo 1 (AFND→AFD):** método de subconjuntos. Muestra la tabla de conversión, el estado pozo ∅ cuando aparece y marca como finales los conjuntos que contienen un final del AFND.
3. **Dibujo:** óvalos, flechas con símbolos, flecha de entrada al inicial, doble óvalo en finales, bucles. Dibuja el AFND y el AFD.
4. **Paso a paso (Módulo 1):** cada paso dice qué conjunto se procesa, con qué símbolo y a qué conjunto llega; el AFD se dibuja a medida que avanza.
5. **Módulo 2 (AF→ER):** sistema de ecuaciones (una por estado) con las reglas: transición simple, varias transiciones, bucle, bucle más salida, estado final. Cada paso muestra el nombre de la regla.
6. **Flujo completo:** el Módulo 2 recibe el AFD del Módulo 1 (AFND → AFD → ER) o el autómata del editor.
7. **Verificador:** genera todas las cadenas hasta longitud *n* (mínimo 6) y compara AFND, AFD y ER; muestra las cadenas en que difieren.
8. **Bonus:** transiciones ε con clausura-ε en el estado inicial y en cada conjunto.

## 4. Entradas y salidas
- **Entrada:** campos de texto del editor (estados, alfabeto, inicial, finales, transiciones) y el valor *n*.
- **Salida:** tabla de conversión, AFD, lista de pasos, ER final y resultado del verificador.
- **Errores de entrada:** mensaje claro (estado inexistente, símbolo fuera del alfabeto, línea mal escrita).

## 5. Casos límite
| Caso | Comportamiento esperado |
|---|---|
| Estado pozo | Aparece `∅` en el AFD solo si algún conjunto llega al vacío; `∅ –a,b→ ∅`. |
| Estados inalcanzables | No aparecen en el AFD; el Módulo 2 los descarta con un paso explicado. |
| Alfabeto de un símbolo | Funciona; puede no haber pozo. |
| AFND sin transiciones | El AFD tiene `{q0}` y `∅`. |
| Inicial también final | La ER incluye λ (ej. `a*`). |
| Sin estados finales | Lenguaje vacío: ER = `∅`. |
| Estados que no llegan a final | Se descartan en el Módulo 2 (valen ∅). |

## 6. Criterios de aceptación (comprobables a mano)
- [ ] Caso 1 del Anexo A produce `{q0}`, `{q0,q1}`, `{q2}`, `∅` con las transiciones y finales esperados.
- [ ] Caso 2 del Anexo A produce `x(xy*y)*` (o una equivalente confirmada por el verificador).
- [ ] Cada paso del Módulo 2 muestra el nombre de la regla aplicada.
- [ ] El verificador con *n* = 6 no muestra diferencias en los dos casos.
- [ ] Con una ER incorrecta, el verificador muestra al menos una cadena distinta.
- [ ] La app abre con `python app.py` sin conexión a internet.
