"""Control reutilizable de paso a paso: Inicio, Anterior, Siguiente, Mostrar todo."""

from tkinter import ttk


class ControlPasos(ttk.Frame):
    """Barra de botones. Avisa con al_cambiar(indice) cada vez que cambia el paso.

    self.todo es True cuando se pidió «Mostrar todo» (o al cargar los pasos).
    """

    def __init__(self, padre, al_cambiar):
        super().__init__(padre)
        self.al_cambiar = al_cambiar
        self.total = 0
        self.indice = -1
        self.todo = True
        for texto, orden in (("|< Inicio", self.inicio), ("< Anterior", self.anterior),
                             ("Siguiente >", self.siguiente), ("Mostrar todo >|", self.mostrar_todo)):
            ttk.Button(self, text=texto, command=orden).pack(side="left", padx=2)
        self.rotulo = ttk.Label(self, text="Sin pasos")
        self.rotulo.pack(side="left", padx=10)

    def cargar(self, total):
        """Recibe la cantidad de pasos y muestra todos."""
        self.total = total
        self.mostrar_todo()

    def _ir(self, indice, todo):
        if self.total == 0:
            return
        self.indice = max(0, min(self.total - 1, indice))
        self.todo = todo
        self.rotulo.configure(text=f"Paso {self.indice + 1} de {self.total}")
        self.al_cambiar(self.indice)

    def inicio(self):
        self._ir(0, False)

    def anterior(self):
        self._ir(self.indice - 1, False)

    def siguiente(self):
        self._ir(self.indice + 1, False)

    def mostrar_todo(self):
        self._ir(self.total - 1, True)
