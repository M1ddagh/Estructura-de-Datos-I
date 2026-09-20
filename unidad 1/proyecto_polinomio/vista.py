from tkinter import Frame, Label, Entry, Button, END


class VistaPolinomio:
    """Configura la interfaz grafica con Tkinter."""

    def __init__(self, root):
        self.root = root
        self.root.title("Evaluador de Polinomios")
        self.root.resizable(False, False)

        marco = Frame(root, padx=20, pady=20)
        marco.pack()

        Label(marco, text="EVALUADOR DE POLINOMIOS",
              font=("Arial", 14, "bold")).pack(pady=(0, 15))

        # --- polinomio ---
        Label(marco, text="Ingrese el polinomio:").pack(anchor="w")
        self.entry_poli = Entry(marco, width=40, font=("Arial", 11))
        self.entry_poli.pack(pady=(0, 5))

        self.btn_convertir = Button(marco, text="Convertir", width=15)
        self.btn_convertir.pack(pady=(0, 10))

        Label(marco, text="Polinomio convertido:").pack(anchor="w")
        self.lbl_convertido = Label(marco, text="", font=("Arial", 11),
                                    relief="sunken", width=40, anchor="w")
        self.lbl_convertido.pack(pady=(0, 10))

        # --- valor de x ---
        Label(marco, text="Ingrese el valor de x:").pack(anchor="w")
        self.entry_x = Entry(marco, width=20, font=("Arial", 11))
        self.entry_x.pack(pady=(0, 5))

        self.btn_calcular = Button(marco, text="Calcular", width=15)
        self.btn_calcular.pack(pady=(0, 10))

        # --- resultado ---
        Label(marco, text="Resultado:").pack(anchor="w")
        self.lbl_resultado = Label(marco, text="", font=("Arial", 11),
                                   relief="sunken", width=40, anchor="w")
        self.lbl_resultado.pack(pady=(0, 5))

    # --- metodos que el controlador usa ---

    def get_polinomio_text(self):
        return self.entry_poli.get()

    def set_polinomio_convertido(self, texto):
        self.lbl_convertido.config(text=texto)

    def get_x_text(self):
        return self.entry_x.get()

    def set_resultado(self, texto):
        self.lbl_resultado.config(text=texto)

    def show_error(self, texto):
        self.lbl_resultado.config(text=f"Error: {texto}")
