from modelo import Polinomio, convertir_a_coeficientes


class Controlador:
    """Conecta la Vista con el Modelo."""

    def __init__(self, vista):
        self.vista = vista
        self.polinomio = None
        self.vista.btn_convertir.config(command=self.convertir)
        self.vista.btn_calcular.config(command=self.calcular)

    def convertir(self):
        texto = self.vista.get_polinomio_text()
        try:
            coef = convertir_a_coeficientes(texto)
            self.polinomio = Polinomio(coef)
            self.vista.set_polinomio_convertido(str(self.polinomio))
        except Exception as e:
            self.vista.show_error(str(e))
            self.polinomio = None

    def calcular(self):
        if self.polinomio is None:
            self.vista.show_error("Primero convierta un polinomio.")
            return
        texto_x = self.vista.get_x_text()
        try:
            x = float(texto_x)
        except ValueError:
            self.vista.show_error("Ingrese un numero valido para x.")
            return
        resultado = self.polinomio.evaluar(x)
        if x == int(x):
            x = int(x)
        self.vista.set_resultado(f"P({x}) = {resultado}")
