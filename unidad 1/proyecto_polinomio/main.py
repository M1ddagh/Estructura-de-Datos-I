from tkinter import Tk
from vista import VistaPolinomio
from controlador import Controlador


def main():
    root = Tk()
    vista = VistaPolinomio(root)
    Controlador(vista)
    root.mainloop()


if __name__ == "__main__":
    main()
