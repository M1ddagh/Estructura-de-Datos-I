"""
models/model.py
---------------
Estructuras de datos de la aplicación: listas doblemente enlazadas.

Cada nodo mantiene referencias bidireccionales (anterior y siguiente) y cada
lista conserva punteros a la cabeza y a la cola, lo que permite insertar al
final en O(1) y recorrer la estructura en ambos sentidos.
"""

from datetime import datetime

# ── CONSTANTES ────────────────────────────────────────────────────────────────

PRIORIDADES_VALIDAS = ("alta", "media", "baja")
ESTADO_PENDIENTE = "pendiente"
ESTADO_COMPLETADA = "completada"


# ── NODO DE TAREA ─────────────────────────────────────────────────────────────

class NodoTarea:
    """
    Nodo de la lista doblemente enlazada de tareas.

    Atributos
    ----------
    titulo : str
        Nombre corto de la tarea.
    descripcion : str
        Detalle ampliado de la tarea.
    prioridad : str
        Nivel de urgencia: 'alta', 'media' o 'baja'.
    fecha_creacion : datetime
        Momento exacto en que se creó el nodo. Puede restaurarse
        desde la persistencia.
    estado : str
        'pendiente' o 'completada'.
    anterior : NodoTarea | None
        Puntero al nodo previo de la lista.
    siguiente : NodoTarea | None
        Puntero al siguiente nodo de la lista.
    """

    def __init__(
        self,
        titulo: str,
        descripcion: str = "",
        prioridad: str = "media",
        estado: str = ESTADO_PENDIENTE,
        fecha_creacion: datetime | None = None,
    ) -> None:
        self.titulo: str = titulo
        self.descripcion: str = descripcion
        self.prioridad: str = prioridad
        self.fecha_creacion: datetime = fecha_creacion or datetime.now()
        self.estado: str = estado
        self.anterior: "NodoTarea | None" = None
        self.siguiente: "NodoTarea | None" = None

    def to_dict(self) -> dict:
        """Devuelve los datos del nodo como diccionario serializable."""
        return {
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "prioridad": self.prioridad,
            "fecha_creacion": self.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
            "estado": self.estado,
        }


# ── LISTA DOBLEMENTE ENLAZADA DE TAREAS ───────────────────────────────────────

class ListaTareas:
    """
    Lista doblemente enlazada que gestiona los nodos de tarea
    pertenecientes a una carpeta.

    Mantiene punteros a la cabeza y a la cola
    py el recorrido puede hacerse en ambos sentidos.
    """

    def __init__(self) -> None:
        self._cabeza: "NodoTarea | None" = None
        self._cola: "NodoTarea | None" = None
        self._total: int = 0

    # ── propiedades ───────────────────────────────────────────

    @property
    def cabeza(self) -> "NodoTarea | None":
        return self._cabeza

    @property
    def cola(self) -> "NodoTarea | None":
        return self._cola

    @property
    def total(self) -> int:
        return self._total

    @property
    def total_completadas(self) -> int:
        count = 0
        actual = self._cabeza
        while actual is not None:
            if actual.estado == ESTADO_COMPLETADA:
                count += 1
            actual = actual.siguiente
        return count

    def esta_vacia(self) -> bool:
        return self._cabeza is None

    # ── inserción ─────────────────────────────────────────────

    def agregar_nodo(self, nodo: NodoTarea) -> NodoTarea:
        """
        Inserta un nodo ya construido al final de la lista.
        Se utiliza al crear tareas nuevas.

        Retorna
        -------
        NodoTarea
            El mismo nodo insertado.
        """
        nodo.anterior = self._cola
        nodo.siguiente = None

        if self._cola is None:
            self._cabeza = nodo
        else:
            self._cola.siguiente = nodo

        self._cola = nodo
        self._total += 1
        return nodo

    def agregar(
        self,
        titulo: str,
        descripcion: str = "",
        prioridad: str = "media",
    ) -> NodoTarea:
        """
        Crea e inserta un nuevo NodoTarea al final de la lista.
        Parámetros
        ----------
        titulo : str
        descripcion : str, optional
        prioridad : str, optional  'alta' | 'media' | 'baja'
        Retorna
        -------
        NodoTarea
            El nodo recién creado.
        """
        return self.agregar_nodo(NodoTarea(titulo, descripcion, prioridad))

    # ── búsqueda ──────────────────────────────────────────────

    def buscar(self, titulo: str) -> "NodoTarea | None":
        """
        Recorre la lista buscando por título exacto.

        Complejidad: O(n)
        """
        actual = self._cabeza
        while actual is not None:
            if actual.titulo == titulo:
                return actual
            actual = actual.siguiente
        return None

    # ── actualización ─────────────────────────────────────────

    def marcar_completada(self, titulo: str) -> bool:
        nodo = self.buscar(titulo)
        if nodo is None:
            return False
        nodo.estado = ESTADO_COMPLETADA
        return True

    def marcar_pendiente(self, titulo: str) -> bool:
        nodo = self.buscar(titulo)
        if nodo is None:
            return False
        nodo.estado = ESTADO_PENDIENTE
        return True

    def actualizar(
        self,
        titulo: str,
        nueva_descripcion: str | None = None,
        nueva_prioridad: str | None = None,
    ) -> bool:
        """
        Edita descripción y/o prioridad de una tarea existente.

        Retorna True si el nodo fue encontrado y modificado.
        """
        nodo = self.buscar(titulo)
        if nodo is None:
            return False
        if nueva_descripcion is not None:
            nodo.descripcion = nueva_descripcion
        if nueva_prioridad is not None:
            nodo.prioridad = nueva_prioridad
        return True

    # ── eliminación ───────────────────────────────────────────

    def eliminar(self, titulo: str) -> bool:
        """
        Localiza el nodo por título y lo desconecta de sus dos vecinos.

        Complejidad: O(n) por la búsqueda; el reenlace es O(1).
        """
        nodo = self.buscar(titulo)
        if nodo is None:
            return False

        # Enlazar el vecino anterior con el siguiente (o mover la cabeza)
        if nodo.anterior is None:
            self._cabeza = nodo.siguiente
        else:
            nodo.anterior.siguiente = nodo.siguiente

        # Enlazar el vecino siguiente con el anterior (o mover la cola)
        if nodo.siguiente is None:
            self._cola = nodo.anterior
        else:
            nodo.siguiente.anterior = nodo.anterior

        # Aislar el nodo eliminado para liberar sus referencias
        nodo.anterior = None
        nodo.siguiente = None
        self._total -= 1
        return True

    # ── recorrido ─────────────────────────────────────────────

    def obtener_todas(self) -> list[dict]:
        """Recorre la lista completa y devuelve una lista de dicts."""
        tareas = []
        actual = self._cabeza
        while actual is not None:
            tareas.append(actual.to_dict())
            actual = actual.siguiente
        return tareas

    def obtener_todas_inverso(self) -> list[dict]:
        """
        Recorre la lista desde la cola hacia la cabeza usando los
        punteros 'anterior'.

        Demuestra la bidireccionalidad de la estructura.
        Complejidad: O(n)
        """
        tareas = []
        actual = self._cola
        while actual is not None:
            tareas.append(actual.to_dict())
            actual = actual.anterior
        return tareas

    def filtrar_por_estado(self, estado: str) -> list[dict]:
        """Devuelve solo las tareas que coincidan con el estado dado."""
        return [t for t in self.obtener_todas() if t["estado"] == estado]

    def filtrar_por_prioridad(self, prioridad: str) -> list[dict]:
        """Devuelve solo las tareas con la prioridad indicada."""
        return [t for t in self.obtener_todas() if t["prioridad"] == prioridad]


# ── NODO DE CARPETA ───────────────────────────────────────────────────────────

class NodoCarpeta:
    """
    Nodo de la lista doblemente enlazada de carpetas.
    Cada carpeta contiene su propia ListaTareas independiente.
    Atributos
    ----------
    nombre : str
        Identificador único de la carpeta.
    tareas : ListaTareas
        Lista doblemente enlazada de tareas dentro de esta carpeta.
    anterior : NodoCarpeta | None
        Puntero al nodo previo de carpetas.
    siguiente : NodoCarpeta | None
        Puntero al siguiente nodo de carpetas.
    """

    def __init__(self, nombre: str) -> None:
        self.nombre: str = nombre
        self.tareas: ListaTareas = ListaTareas()
        self.anterior: "NodoCarpeta | None" = None
        self.siguiente: "NodoCarpeta | None" = None

# ── LISTA DOBLEMENTE ENLAZADA DE CARPETAS ─────────────────────────────────────

class ListaCarpetas:
    """
    Lista doblemente enlazada que gestiona las carpetas.
    Cada carpeta es un NodoCarpeta con su propia ListaTareas.

    Al igual que ListaTareas, conserva punteros a la cabeza y a la cola,
    por lo que la inserción al final es O(1) y el recorrido es reversible.
    """

    def __init__(self) -> None:
        self._cabeza: "NodoCarpeta | None" = None
        self._cola: "NodoCarpeta | None" = None
        self._total: int = 0

    # ── propiedades ───────────────────────────────────────────

    @property
    def cabeza(self) -> "NodoCarpeta | None":
        return self._cabeza

    @property
    def cola(self) -> "NodoCarpeta | None":
        return self._cola

    @property
    def total(self) -> int:
        return self._total

    def esta_vacia(self) -> bool:
        return self._cabeza is None

    # ── inserción ─────────────────────────────────────────────

    def agregar_nodo(self, nodo: NodoCarpeta) -> NodoCarpeta:
        """
        Inserta una carpeta ya construida al final de la lista.

        """
        nodo.anterior = self._cola
        nodo.siguiente = None

        if self._cola is None:
            self._cabeza = nodo
        else:
            self._cola.siguiente = nodo

        self._cola = nodo
        self._total += 1
        return nodo

    def agregar_carpeta(self, nombre: str) -> NodoCarpeta:
        """
        Crea e inserta una nueva carpeta al final de la lista.
        """
        return self.agregar_nodo(NodoCarpeta(nombre))

    # ── búsqueda ──────────────────────────────────────────────

    def buscar_carpeta(self, nombre: str) -> "NodoCarpeta | None":
        """Recorre la lista buscando la carpeta por nombre exacto."""
        actual = self._cabeza
        while actual is not None:
            if actual.nombre == nombre:
                return actual
            actual = actual.siguiente
        return None

    # ── eliminación ───────────────────────────────────────────

    def eliminar_carpeta(self, nombre: str) -> bool:
        """
        Elimina la carpeta y todas sus tareas internas, reenlazando
        los punteros anterior y siguiente de sus vecinos.

        Complejidad: O(m) por la búsqueda.
        """
        nodo = self.buscar_carpeta(nombre)
        if nodo is None:
            return False

        if nodo.anterior is None:
            self._cabeza = nodo.siguiente
        else:
            nodo.anterior.siguiente = nodo.siguiente

        if nodo.siguiente is None:
            self._cola = nodo.anterior
        else:
            nodo.siguiente.anterior = nodo.anterior

        nodo.anterior = None
        nodo.siguiente = None
        self._total -= 1
        return True

    # ── recorrido ─────────────────────────────────────────────

    def obtener_nombres(self) -> list[str]:
        """Devuelve la lista de nombres de todas las carpetas."""
        nombres = []
        actual = self._cabeza
        while actual is not None:
            nombres.append(actual.nombre)
            actual = actual.siguiente
        return nombres

    def obtener_nombres_inverso(self) -> list[str]:
        """Devuelve los nombres desde la última carpeta hasta la primera."""
        nombres = []
        actual = self._cola
        while actual is not None:
            nombres.append(actual.nombre)
            actual = actual.anterior
        return nombres

    def obtener_resumen(self) -> list[dict]:
        """
        Devuelve un resumen de cada carpeta con sus estadísticas.
        """
        resumen = []
        actual = self._cabeza
        while actual is not None:
            resumen.append({
                "nombre": actual.nombre,
                "total": actual.tareas.total,
                "completadas": actual.tareas.total_completadas,
                "pendientes": actual.tareas.total - actual.tareas.total_completadas,
            })
            actual = actual.siguiente
        return resumen