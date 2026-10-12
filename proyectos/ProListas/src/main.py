"""
main.py
-------
Punto de entrada de la aplicación To-Do List v2.
Ejecutar desde la carpeta src/:  python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from views.view import TodoApp


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()