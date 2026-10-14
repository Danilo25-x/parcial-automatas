# Simulador gráfico de autómatas

Parcial 2.º corte · Teoría de la Computación.
Aplicación de escritorio (Python + Tkinter, solo librería estándar, sin internet ni servidor) que:

1. **Convierte un AFND en AFD** con el método de subconjuntos (tabla, estado pozo ∅, dibujo y paso a paso).
2. **Obtiene la expresión regular** de un autómata con el sistema de ecuaciones, mostrando el nombre de cada regla.
3. **Verifica la equivalencia** de AFND, AFD y ER probando todas las cadenas hasta una longitud *n* (mínimo 6).
4. **Bonus:** soporta transiciones ε con clausura-ε.

## Cómo ejecutarla

Requiere Python 3.8 o superior con Tkinter (viene con la instalación estándar de Python en Windows y macOS; en Linux: `sudo apt install python3-tk`).

```bash
python app.py
```

No usa internet, ni CDN, ni APIs, ni librerías externas.

## Cómo usarla

1. **Pestaña «1 · AFND → AFD».** Escriba el autómata o elija un ejemplo y pulse *Cargar ejemplo*. Pulse *Convertir a AFD*.
   - Las transiciones se escriben una por línea: `origen,símbolo,destino` (ej. `q0,a,q1`).
   - Para una transición vacía use `ε` o `eps`.
   - Con *|< Inicio*, *< Anterior*, *Siguiente >* y *Mostrar todo >|* recorre la conversión: el AFD se dibuja a medida que avanza y se resalta el conjunto y la flecha del paso actual.
2. **Pestaña «2 · AF → Expresión regular».** Elija si resuelve el AFD del Módulo 1 o el AFND del editor y pulse *Obtener ER*. Cada paso muestra la regla aplicada y el sistema de ecuaciones.
3. **Pestaña «3 · Verificador».** Elija *n* (mínimo 6), use *Usar la ER del Módulo 2* o escriba otra ER y pulse *Verificar*. Si no coinciden, se listan las cadenas en que difieren.

Notación de la ER: unión `+`, estrella `*`, concatenación sin símbolo, `λ` cadena vacía, `∅` lenguaje vacío.

## Estructura del proyecto

```
app.py                 punto de entrada
SPEC.md                especificación (Fase 0)
ARQUITECTURA.md        plan y modelo de datos (Fase 1)
capturas/              pantallazos de la aplicación
src/
  modelo.py            modelo del autómata, aceptar cadenas, clausura-ε
  afnd_afd.py          Módulo 1: método de subconjuntos
  af_er.py             Módulo 2: sistema de ecuaciones y reglas
  verificador.py       compara AFND, AFD y ER
  lector.py            texto del editor -> autómata (con errores claros)
  ejemplos.py          casos del Anexo A y ejemplo con ε
  pasos.py             AFD parcial para el paso a paso
  dibujo.py            posiciones y dibujo de grafos en Canvas
  paso_a_paso.py       control Anterior / Siguiente
  interfaz.py          ventana con pestañas
tests/                 pruebas con unittest
```

La lógica (`modelo`, `afnd_afd`, `af_er`, `verificador`, `lector`, `pasos`) no usa Tkinter; la interfaz solo muestra lo que ella calcula.

## Pruebas

```bash
python -m unittest -v
```

Incluyen los dos casos del Anexo A, casos límite (estado pozo, estados inalcanzables, alfabeto de un símbolo, inicial también final, sin finales, sin transiciones), el verificador, el lector, las posiciones del dibujo, el paso a paso y el bonus ε (con autómatas aleatorios).

## Limitaciones conocidas

- Los símbolos del alfabeto son de un solo carácter y no pueden ser `+ * ( ) λ ∅ ε`.
- Si la ER supera 20 000 caracteres (ocurre con AFD de unos 13 estados o más), la aplicación avisa en vez de intentar mostrarla.
- El verificador rechaza combinaciones de alfabeto y *n* con más de 300 000 cadenas.

## Integrantes

-Harold Danilo Tuquerres
-Jhoan Santiago Camayo 
