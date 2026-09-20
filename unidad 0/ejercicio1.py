## Código 1: Cálculo del promedio

#Este programa permite ingresar tres notas y calcular su promedio.


def calcular_promedio(nota_1, nota_2, nota_3):
    """Calcula el promedio de tres notas."""
    return (nota_1 + nota_2 + nota_3) / 3


def main():
    nota_1 = float(input("Ingrese la primera nota: "))
    nota_2 = float(input("Ingrese la segunda nota: "))
    nota_3 = float(input("Ingrese la tercera nota: "))

    promedio = calcular_promedio(nota_1, nota_2, nota_3)

    print(f"El promedio es: {promedio:.2f}")


if __name__ == "__main__":
    main()
