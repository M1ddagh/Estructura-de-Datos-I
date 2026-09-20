def es_par(numero):
    """Determina si un número es par."""
    return numero % 2 == 0


def main():
    numero = int(input("Ingrese un número entero: "))

    if es_par(numero):
        print(f"{numero} es un número par.")
    else:
        print(f"{numero} es un número impar.")


if __name__ == "__main__":
    main()
