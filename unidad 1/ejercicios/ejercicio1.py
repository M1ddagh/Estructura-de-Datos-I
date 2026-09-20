from abc import ABC, abstractmethod


class ADT(ABC):
    """Interfaz ADT mínima."""

    @abstractmethod
    def agregar(self, dato):
        """Agrega un dato a la estructura."""
        pass

    @abstractmethod
    def obtener(self, indice):
        """Obtiene un dato mediante su índice."""
        pass

    @abstractmethod
    def tamanio(self):
        """Retorna el tamaño de la estructura."""
        pass


class ArrayEstatico(ADT):
    """Implementación de un arreglo estático."""

    def __init__(self, capacidad):
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor que cero.")

        self._datos = [None] * capacidad
        self._capacidad = capacidad
        self._tamanio = 0

    def agregar(self, dato):
        """Agrega un dato si existe espacio disponible."""
        if self._tamanio >= self._capacidad:
            raise OverflowError("El array está lleno.")

        self._datos[self._tamanio] = dato
        self._tamanio += 1

    def obtener(self, indice):
        """Obtiene un elemento validando los límites."""
        if indice < 0 or indice >= self._tamanio:
            raise IndexError("Índice fuera de rango.")

        return self._datos[indice]

    def tamanio(self):
        """Retorna la cantidad de elementos almacenados."""
        return self._tamanio


def main():
    """Prueba el funcionamiento del ArrayEstatico."""
    arreglo = ArrayEstatico(3)

    arreglo.agregar("Juan")
    arreglo.agregar("Pedro")
    arreglo.agregar("Maria")

    print("Elementos almacenados:")

    for indice in range(arreglo.tamanio()):
        print(f"Índice {indice}: {arreglo.obtener(indice)}")

    print(f"\nTamaño: {arreglo.tamanio()}")

    # Prueba de validación de límites.
    try:
        print(arreglo.obtener(5))
    except IndexError as error:
        print(f"\nError: {error}")

    # Prueba de capacidad máxima.
    try:
        arreglo.agregar("Carlos")
    except OverflowError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
