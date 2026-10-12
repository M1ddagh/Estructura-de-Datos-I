TO-DO LIST CON LISTA ENLAZADA
Proyecto de Estructuras de Datos
Implementacion MVC con Python y Tkinter
Nivel: Principiante  |  Materia: Estructuras de Datos
 
1. Descripcion General
Este proyecto implementa una aplicacion de gestion de tareas (To-Do List) usando una Lista Enlazada Simple como estructura de datos central. La aplicacion sigue el patron de diseño MVC (Modelo-Vista-Controlador) y cuenta con una interfaz grafica desarrollada en Tkinter.

📌  La estructura de datos PRINCIPAL es la Lista Enlazada, no arrays ni listas de Python. Cada tarea es un Nodo conectado al siguiente mediante punteros.

2. Estructura del Proyecto
Archivo	Responsabilidad
src/models/model.py	Nodo + Lista enlazada (logica de datos pura)
src/controllers/controller.py	Validaciones y puente Vista-Modelo
src/views/view.py	Interfaz grafica Tkinter (GUI)
src/main.py	Punto de entrada de la aplicacion

3. Estructura de Datos: Lista Enlazada Simple
3.1 El Nodo
Cada nodo representa una tarea y contiene tres campos:
•	descripcion (str) — texto de la tarea
•	estado (str) — 'pendiente' o 'completada'
•	siguiente (Nodo | None) — puntero al proximo nodo

class Nodo:
    def __init__(self, descripcion):
        self.descripcion = descripcion
        self.estado = 'pendiente'
        self.siguiente = None  # <-- PUNTERO

3.2 La Lista (ListaTareas)
La lista solo conoce su cabeza (primer nodo). Para llegar a cualquier otro nodo hay que recorrerla secuencialmente:

Operacion	Complejidad | Descripcion
agregar_tarea()	O(n) — recorre hasta el final para insertar
marcar_completada()	O(n) — busca por descripcion y cambia estado
eliminar_tarea()	O(n) — busca y reenlaza los nodos vecinos
obtener_todas()	O(n) — recorre toda la lista y devuelve lista
esta_vacia()	O(1) — comprueba si cabeza es None
total()	O(1) — contador interno

4. Patron de Diseno MVC
Modelo (model.py)
Contiene UNICAMENTE la logica de la lista enlazada. No sabe nada de la interfaz grafica ni de validaciones de negocio. Solo opera sobre nodos.
Controlador (controller.py)
Recibe las acciones del usuario desde la Vista, las valida (evitar duplicados, campos vacios, longitud maxima) y delega al Modelo. Devuelve tuplas (exito: bool, mensaje: str) para que la Vista muestre feedback.
Vista (view.py)
Construye la GUI con Tkinter. Llama exclusivamente al Controlador; nunca toca el Modelo directamente. Muestra tarjetas por tarea, filtros y estadisticas en tiempo real.

✅  Separacion de responsabilidades: si maniana cambias la GUI por una web, solo reescribes view.py. El modelo y el controlador no se tocan.

5. Funcionalidades Implementadas
•	Agregar tarea — inserta un nuevo Nodo al final de la lista
•	Marcar completada / pendiente — cambia el estado del nodo buscado
•	Eliminar tarea — reenlaza los punteros para sacar el nodo
•	Mostrar todas las tareas — recorre la lista completa
•	Filtrar por estado — todas / pendientes / completadas
•	Estadisticas en tiempo real — contador de completadas / total
•	Validaciones — duplicados, campo vacio, longitud maxima 120 chars

6. Instrucciones de Ejecucion
Requisitos
•	Python 3.10 o superior
•	Tkinter (incluido en la instalacion estandar de Python)
•	Sin dependencias externas

Ejecutar
cd env/Scripts
./activate
cd src
python main.py

⚠️  Asegurate de ejecutar desde la carpeta src/ para que las importaciones relativas funcionen correctamente.

