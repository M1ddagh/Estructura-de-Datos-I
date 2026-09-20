class Polinomio:
    """ADT Polinomio: almacena los coeficientes en una lista.
    indice i  -> coeficiente de x^i"""

    def __init__(self, coeficientes):
        self.coeficientes = coeficientes

    def evaluar(self, x):
        """Calcula P(x) recorriendo la lista una sola vez.
        Complejidad temporal: O(n), n = grado del polinomio."""
        # calcula el valor del polinomio cuando conocemos a X
        resultado = 0
        for i in range(len(self.coeficientes)):
            resultado += self.coeficientes[i] * (x ** i)
        return resultado

    def __str__(self):
        terminos = []
        for i in range(len(self.coeficientes) - 1, -1, -1):
            c = self.coeficientes[i]
            if c == 0:
                continue
            if i == 0:
                terminos.append(f"{c}")
            elif i == 1:
                terminos.append("x" if c == 1 else ("-x" if c == -1 else f"{c}x"))
            else:
                terminos.append(f"x^{i}" if c == 1 else (f"-x^{i}" if c == -1 else f"{c}x^{i}"))
        if not terminos:
            return "0"
        resultado = terminos[0]
        for t in terminos[1:]:
            resultado += f" - {t[1:]}" if t.startswith("-") else f" + {t}"
        return resultado


def convertir_a_coeficientes(texto):
    """Convierte un texto como '3x^4 - 2x^2 + 5x - 1' a [-1, 5, -2, 0, 3]."""
    texto = texto.strip().replace(" ", "")
    if not texto:
        raise ValueError("El polinomio no puede estar vacio.")

    texto = texto.replace("-", "+-")
    terminos = [t for t in texto.split("+") if t]
    if not terminos:
        raise ValueError("No se encontraron terminos.")

    # Paso 1: encontrar el exponente maximo
    max_exp = 0
    for termino in terminos:
        if "x" not in termino:
            continue
        if "^" in termino:
            exp = int(termino.split("^")[1])
            if exp > max_exp:
                max_exp = exp
        else:
            max_exp = max(max_exp, 1)

    # Paso 2: construir la lista de coeficientes
    coeficientes = [0] * (max_exp + 1)
    for termino in terminos:
        if "x" not in termino:
            coeficientes[0] = int(termino)
        else:
            parte = termino.split("x")
            if parte[0] == "" or parte[0] == "+":
                coef = 1
            elif parte[0] == "-":
                coef = -1
            else:
                coef = int(parte[0])

            if parte[1] == "":
                exp = 1
            elif parte[1].startswith("^"):
                exp = int(parte[1][1:])
            else:
                raise ValueError(f"Formato invalido: {termino}")

            coeficientes[exp] = coef

    return coeficientes
