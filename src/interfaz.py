"""Ventana principal con tres pestañas (solo muestra lo que calcula la lógica)."""

import tkinter as tk
from tkinter import ttk, messagebox

from .afnd_afd import convertir_afnd_a_afd
from .af_er import afd_a_er, ERDemasiadoGrande
from .dibujo import dibujar_automata
from .ejemplos import EJEMPLOS
from .lector import leer_afnd, automata_a_textos
from .paso_a_paso import ControlPasos
from .pasos import vista_paso
from .verificador import verificar_equivalencia, contar_cadenas

FUENTE_TEXTO = ("Consolas", 10)
LIMITE_CADENAS = 300000


class PanelGrafo(ttk.LabelFrame):
    """Un Canvas con barras de desplazamiento que redibuja al cambiar de tamaño."""

    def __init__(self, padre, titulo):
        super().__init__(padre, text=titulo)
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0,
                                width=380, height=260)
        barra_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        barra_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=barra_x.set, yscrollcommand=barra_y.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.datos = None
        self.canvas.bind("<Configure>", lambda e: self.redibujar())

    def mostrar(self, automata, resaltar_estados=(), resaltar_arista=None):
        self.datos = (automata, tuple(resaltar_estados), resaltar_arista)
        self.redibujar()

    def redibujar(self):
        if self.datos is None:
            self.canvas.delete("all")
        else:
            dibujar_automata(self.canvas, *self.datos)


def calcular_er(automata):
    """Devuelve (pasos, er) o None si la ER es demasiado grande (avisa al usuario)."""
    try:
        return afd_a_er(automata)
    except ERDemasiadoGrande as error:
        messagebox.showwarning("ER demasiado grande", str(error))
        return None


def crear_texto(padre, alto=8):
    """Text de solo lectura con barra de desplazamiento. Devuelve (marco, text)."""
    marco = ttk.Frame(padre)
    texto = tk.Text(marco, height=alto, wrap="word", font=FUENTE_TEXTO, state="disabled")
    barra = ttk.Scrollbar(marco, command=texto.yview)
    texto.configure(yscrollcommand=barra.set)
    texto.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    texto.tag_configure("regla", foreground="#1d4ed8", font=("Consolas", 10, "bold"))
    texto.tag_configure("titulo", font=("Consolas", 10, "bold"))
    return marco, texto


def escribir(texto, contenido, etiqueta=None, borrar=False):
    texto.configure(state="normal")
    if borrar:
        texto.delete("1.0", "end")
    texto.insert("end", contenido, etiqueta)
    texto.configure(state="disabled")
    texto.see("end")


# ---------- Pestaña 1: editor + conversión AFND → AFD ----------

class PestanaConversion(ttk.Frame):
    def __init__(self, notebook, app):
        super().__init__(notebook)
        self.app = app
        self._armar_editor()
        self._armar_resultados()
        self.cargar_ejemplo()

    def _armar_editor(self):
        marco = ttk.LabelFrame(self, text="Autómata de entrada (AFND)")
        marco.pack(fill="x", padx=8, pady=(6, 2))
        self.campos = {}
        for fila, (clave, rotulo) in enumerate([
                ("estados", "Estados (separados por coma)"),
                ("alfabeto", "Alfabeto"),
                ("inicial", "Estado inicial"),
                ("finales", "Estados finales")]):
            ttk.Label(marco, text=rotulo).grid(row=fila, column=0, sticky="w", padx=4, pady=2)
            entrada = ttk.Entry(marco, width=26)
            entrada.grid(row=fila, column=1, padx=4, pady=2)
            self.campos[clave] = entrada
        ttk.Label(marco, text="Transiciones: origen,símbolo,destino").grid(
            row=0, column=2, sticky="w", padx=10)
        self.transiciones = tk.Text(marco, width=32, height=5, font=FUENTE_TEXTO)
        self.transiciones.grid(row=1, column=2, rowspan=3, padx=10, pady=2)
        ttk.Label(marco, text="Una por línea. ε (o eps) = transición vacía",
                  foreground="gray").grid(row=4, column=2, sticky="w", padx=10)

        botones = ttk.Frame(marco)
        botones.grid(row=0, column=3, rowspan=4, padx=10)
        self.combo = ttk.Combobox(botones, values=list(EJEMPLOS), state="readonly", width=22)
        self.combo.current(0)
        self.combo.pack(pady=2)
        ttk.Button(botones, text="Cargar ejemplo", command=self.cargar_ejemplo).pack(fill="x", pady=2)
        ttk.Button(botones, text="Convertir a AFD", command=self.convertir).pack(fill="x", pady=2)

    def _armar_resultados(self):
        paneles = ttk.PanedWindow(self, orient="horizontal")
        paneles.pack(fill="both", expand=True, padx=8, pady=2)
        self.panel_afnd = PanelGrafo(paneles, "AFND de partida")
        self.panel_afd = PanelGrafo(paneles, "AFD resultante")
        paneles.add(self.panel_afnd, weight=1)
        paneles.add(self.panel_afd, weight=1)

        abajo = ttk.PanedWindow(self, orient="horizontal")
        abajo.pack(fill="x", padx=8, pady=(2, 6))
        marco_tabla = ttk.LabelFrame(abajo, text="Tabla de conversión  (→ inicial, * final)")
        self.tabla = ttk.Treeview(marco_tabla, show="headings", height=6)
        self.tabla.pack(fill="both", expand=True)
        marco_pasos = ttk.LabelFrame(abajo, text="Paso a paso")
        self.control = ControlPasos(marco_pasos, self.mostrar_paso)
        self.control.pack(fill="x", pady=2)
        self.zona_pasos, self.texto_pasos = crear_texto(marco_pasos, alto=6)
        self.zona_pasos.pack(fill="both", expand=True)
        abajo.add(marco_tabla, weight=1)
        abajo.add(marco_pasos, weight=1)

    # --- acciones ---

    def cargar_ejemplo(self):
        automata = EJEMPLOS[self.combo.get()]()
        estados, alfabeto, inicial, finales, trans = automata_a_textos(automata)
        for clave, valor in zip(("estados", "alfabeto", "inicial", "finales"),
                                (estados, alfabeto, inicial, finales)):
            self.campos[clave].delete(0, "end")
            self.campos[clave].insert(0, valor)
        self.transiciones.delete("1.0", "end")
        self.transiciones.insert("1.0", trans)

    def leer_editor(self):
        """Devuelve el AFND escrito en el editor, o None si hay error."""
        try:
            return leer_afnd(self.campos["estados"].get(), self.campos["alfabeto"].get(),
                             self.campos["inicial"].get(), self.campos["finales"].get(),
                             self.transiciones.get("1.0", "end"))
        except ValueError as error:
            messagebox.showerror("Error en el autómata", str(error))
            return None

    def convertir(self):
        """Convierte el AFND del editor. Devuelve True si salió bien."""
        afnd = self.leer_editor()
        if afnd is None:
            return False
        tabla, pasos, afd = convertir_afnd_a_afd(afnd)
        self.app.afnd, self.app.afd = afnd, afd
        self.app.tabla, self.app.pasos_conversion = tabla, pasos
        self.panel_afnd.mostrar(afnd)
        self._llenar_tabla(tabla, afnd["alfabeto"], afd)
        self.control.cargar(len(pasos))      # muestra todo y avisa a mostrar_paso
        return True

    def mostrar_paso(self, k):
        """Dibuja el AFD hasta el paso k y resalta el conjunto y la flecha actuales."""
        pasos = self.app.pasos_conversion
        parcial, resaltados, flecha = vista_paso(self.app.afd, pasos, k)
        self.panel_afd.mostrar(parcial, resaltados, flecha)
        escribir(self.texto_pasos, "", borrar=True)
        for numero, paso in enumerate(pasos[:k + 1], start=1):
            etiqueta = "regla" if numero == k + 1 else None
            escribir(self.texto_pasos, f"{numero}. {paso['descripcion']}\n", etiqueta)
        self.tabla.selection_set(pasos[k]["conjunto"])

    def _llenar_tabla(self, tabla, alfabeto, afd):
        columnas = ["estado"] + list(alfabeto)
        self.tabla.configure(columns=columnas)
        self.tabla.heading("estado", text="Estado del AFD")
        self.tabla.column("estado", width=140, anchor="w")
        for simbolo in alfabeto:
            self.tabla.heading(simbolo, text=simbolo)
            self.tabla.column(simbolo, width=110, anchor="center")
        self.tabla.delete(*self.tabla.get_children())
        for fila in tabla:
            marca = ("→ " if fila["conjunto"] == afd["inicial"] else "") + \
                    ("* " if fila["final"] else "")
            valores = [marca + fila["conjunto"]] + [fila["destinos"][s] for s in alfabeto]
            self.tabla.insert("", "end", iid=fila["conjunto"], values=valores)


# ---------- Pestaña 2: autómata → expresión regular ----------

class PestanaER(ttk.Frame):
    FUENTES = ("AFD obtenido en el Módulo 1", "AFND del editor")

    def __init__(self, notebook, app):
        super().__init__(notebook)
        self.app = app
        barra = ttk.Frame(self)
        barra.pack(fill="x", padx=8, pady=6)
        ttk.Label(barra, text="Autómata a resolver:").pack(side="left")
        self.combo = ttk.Combobox(barra, values=self.FUENTES, state="readonly", width=30)
        self.combo.current(0)
        self.combo.pack(side="left", padx=6)
        ttk.Button(barra, text="Obtener ER", command=self.obtener_er).pack(side="left", padx=6)
        ttk.Label(barra, text="ER final:").pack(side="left", padx=(20, 4))
        self.var_er = tk.StringVar()
        ttk.Entry(barra, textvariable=self.var_er, width=36, state="readonly",
                  font=("Consolas", 12, "bold")).pack(side="left")

        paneles = ttk.PanedWindow(self, orient="horizontal")
        paneles.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.panel = PanelGrafo(paneles, "Autómata")
        marco = ttk.LabelFrame(paneles, text="Sistema de ecuaciones y reglas aplicadas")
        self.control = ControlPasos(marco, self.mostrar_paso)
        self.control.pack(fill="x", pady=2)
        self.zona, self.texto = crear_texto(marco, alto=20)
        self.zona.pack(fill="both", expand=True)
        paneles.add(self.panel, weight=1)
        paneles.add(marco, weight=2)

    def obtener_er(self):
        if self.combo.current() == 0:
            if not self.app.pestana_conversion.convertir():
                return
            automata = self.app.afd
        else:
            automata = self.app.pestana_conversion.leer_editor()
            if automata is None:
                return
        resultado = calcular_er(automata)
        if resultado is None:
            return
        pasos, er = resultado
        self.app.pasos_er, self.app.er = pasos, er
        self.var_er.set(er)
        self.panel.mostrar(automata)
        self.control.cargar(len(pasos))

    def mostrar_paso(self, k):
        """Con «Mostrar todo» escribe todos los pasos; si no, solo el paso k."""
        pasos = self.app.pasos_er
        escribir(self.texto, "", borrar=True)
        numeros = range(len(pasos)) if self.control.todo else [k]
        for i in numeros:
            paso = pasos[i]
            escribir(self.texto, f"Paso {i + 1} · Regla: {paso['regla']}\n", "regla")
            escribir(self.texto, f"   {paso['descripcion']}\n")
            for ecuacion in paso["ecuaciones"]:
                escribir(self.texto, f"      {ecuacion}\n")
            escribir(self.texto, "\n")
        self.texto.see("1.0" if not self.control.todo else "end")


# ---------- Pestaña 3: verificador ----------

class PestanaVerificador(ttk.Frame):
    def __init__(self, notebook, app):
        super().__init__(notebook)
        self.app = app
        barra = ttk.Frame(self)
        barra.pack(fill="x", padx=8, pady=8)
        ttk.Label(barra, text="Longitud máxima n (mínimo 6):").pack(side="left")
        self.n = tk.IntVar(value=6)
        ttk.Spinbox(barra, from_=6, to=14, textvariable=self.n, width=4).pack(side="left", padx=6)
        ttk.Label(barra, text="ER a verificar:").pack(side="left", padx=(16, 4))
        self.var_er = tk.StringVar()
        ttk.Entry(barra, textvariable=self.var_er, width=34,
                  font=("Consolas", 11)).pack(side="left")
        ttk.Button(barra, text="Usar la ER del Módulo 2", command=self.usar_er_calculada).pack(
            side="left", padx=6)
        ttk.Button(barra, text="Verificar", command=self.verificar).pack(side="left", padx=6)

        self.resultado = ttk.Label(self, text="", font=("Arial", 12, "bold"))
        self.resultado.pack(anchor="w", padx=10, pady=4)
        self.tabla = ttk.Treeview(self, columns=("cadena", "afnd", "afd", "er"),
                                  show="headings", height=16)
        for clave, titulo, ancho in (("cadena", "Cadena", 260), ("afnd", "AFND", 100),
                                     ("afd", "AFD", 100), ("er", "ER", 100)):
            self.tabla.heading(clave, text=titulo)
            self.tabla.column(clave, width=ancho, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def usar_er_calculada(self):
        if not self.app.pestana_conversion.convertir():
            return
        resultado = calcular_er(self.app.afd)
        if resultado is None:
            return
        self.app.er = resultado[1]
        self.var_er.set(self.app.er)

    def verificar(self):
        if not self.app.pestana_conversion.convertir():
            return
        if not self.var_er.get().strip():
            self.usar_er_calculada()
            if not self.var_er.get().strip():
                return
        try:
            n = int(self.n.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Valor no válido", "n debe ser un número entero.")
            return
        if n < 6:
            messagebox.showerror("Valor no válido", "n debe ser al menos 6.")
            return
        if contar_cadenas(self.app.afnd["alfabeto"], n) > LIMITE_CADENAS:
            messagebox.showerror("Demasiadas cadenas",
                                 "Con ese alfabeto y n hay demasiadas cadenas. Baje n.")
            return
        try:
            res = verificar_equivalencia(self.app.afnd, self.app.afd,
                                         self.var_er.get().strip(), n)
        except Exception as error:      # ER mal escrita (paréntesis, etc.)
            messagebox.showerror("ER no válida", f"No se pudo evaluar la ER: {error}")
            return
        self.tabla.delete(*self.tabla.get_children())
        if res["equivalentes"]:
            self.resultado.configure(
                text=f"✔ Equivalentes: {res['total']} cadenas probadas, 0 diferencias.",
                foreground="#15803d")
        else:
            cantidad = len(res["diferencias"])
            palabra = "diferencia" if cantidad == 1 else "diferencias"
            self.resultado.configure(
                text=f"✘ NO equivalentes: {cantidad} {palabra} en {res['total']} cadenas.",
                foreground="#b91c1c")
        for cadena, a, b, c in res["diferencias"]:
            si_no = lambda v: "acepta" if v else "rechaza"
            self.tabla.insert("", "end", values=(cadena or "(cadena vacía)",
                                                 si_no(a), si_no(b), si_no(c)))


# ---------- Ventana ----------

class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de autómatas · AFND → AFD → ER")
        self.geometry("1180x780")
        # datos compartidos entre pestañas
        self.afnd = self.afd = self.tabla = self.pasos_conversion = None
        self.pasos_er = self.er = None
        cuaderno = ttk.Notebook(self)
        cuaderno.pack(fill="both", expand=True)
        self.pestana_conversion = PestanaConversion(cuaderno, self)
        self.pestana_er = PestanaER(cuaderno, self)
        self.pestana_verificador = PestanaVerificador(cuaderno, self)
        cuaderno.add(self.pestana_conversion, text="1 · AFND → AFD")
        cuaderno.add(self.pestana_er, text="2 · AF → Expresión regular")
        cuaderno.add(self.pestana_verificador, text="3 · Verificador")
