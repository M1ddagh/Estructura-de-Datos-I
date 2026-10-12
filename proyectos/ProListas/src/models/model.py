"""
models/model.py
---------------
"""

from datetime import datetime


# ── CONSTANTES ────────────────────────────────────────────────────────────────

PRIORIDADES_VALIDAS = ("alta", "media", "baja")
ESTADO_PENDIENTE = "pendiente"
ESTADO_COMPLETADA = "completada"


# ── NODO DE TAREA ─────────────────────────────────────────────────────────────

class NodoTarea:
    """
    Nodo de la lista enlazada de tareas.

    Atributos
    ----------
    titulo : str
        Nombre corto de la tarea.
    descripcion : str
        Detalle ampliado de la tarea.
    prioridad : str
        Nivel de urgencia: 'alta', 'media' o 'baja'.
    fecha_creacion : datetime
        Momento exacto en que se creó el nodo.
    estado : str
        'pendiente' o 'completada'.
    siguiente : NodoTarea | None
        Puntero al siguiente nodo de la lista.
    """

    def __init__(
        self,
        titulo: str,
        descripcion: str = "",
        prioridad: str = "media",
    ) -> None:
        self.titulo: str = titulo
        self.descripcion: str = descripcion
        self.prioridad: str = prioridad
        self.fecha_creacion: datetime = datetime.now()
        self.estado: str = ESTADO_PENDIENTE
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


# ── LISTA ENLAZADA DE TAREAS ──────────────────────────────────────────────────

class ListaTareas:
    """
    Lista enlazada simple que gestiona los nodos de tarea
    pertenecientes a una carpeta.
    """

    def __init__(self) -> None:
        self._cabeza: "NodoTarea | None" = None
        self._total: int = 0

    # ── propiedades ───────────────────────────────────────────

    @property
    def cabeza(self) -> "NodoTarea | None":
        return self._cabeza

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

    def agregar(
        self,
        titulo: str,
        descripcion: str = "",
        prioridad: str = "media",
    ) -> NodoTarea:
        """
        Inserta un nuevo NodoTarea al final de la lista.

        Complejidad: O(n)

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
        nuevo = NodoTarea(titulo, descripcion, prioridad)

        if self._cabeza is None:
            self._cabeza = nuevo
        else:
            actual = self._cabeza
            while actual.siguiente is not None:
                actual = actual.siguiente
            actual.siguiente = nuevo

        self._total += 1
        return nuevo

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
        Reenlaza los punteros para excluir el nodo buscado.

        Complejidad: O(n)
        """
        if self._cabeza is None:
            return False

        # Caso: el nodo a eliminar es la cabeza
        if self._cabeza.titulo == titulo:
            self._cabeza = self._cabeza.siguiente
            self._total -= 1
            return True

        anterior = self._cabeza
        actual = self._cabeza.siguiente
        while actual is not None:
            if actual.titulo == titulo:
                anterior.siguiente = actual.siguiente
                self._total -= 1
                return True
            anterior = actual
            actual = actual.siguiente

        return False

    # ── recorrido ─────────────────────────────────────────────

    def obtener_todas(self) -> list[dict]:
        """Recorre la lista completa y devuelve una lista de dicts."""
        tareas = []
        actual = self._cabeza
        while actual is not None:
            tareas.append(actual.to_dict())
            actual = actual.siguiente
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
    Nodo de la lista enlazada de carpetas.

    Cada carpeta contiene su propia ListaTareas independiente.

    Atributos
    ----------
    nombre : str
        Identificador único de la carpeta.
    tareas : ListaTareas
        Lista enlazada de tareas dentro de esta carpeta.
    siguiente : NodoCarpeta | None
        Puntero al siguiente nodo de carpetas.
    """

    def __init__(self, nombre: str) -> None:
        self.nombre: str = nombre
        self.tareas: ListaTareas = ListaTareas()
        self.siguiente: "NodoCarpeta | None" = None


# ── LISTA ENLAZADA DE CARPETAS ────────────────────────────────────────────────

class ListaCarpetas:
    """
    Lista enlazada simple que gestiona las carpetas.
    Cada carpeta es un NodoCarpeta con su propia ListaTareas.
    """

    def __init__(self) -> None:
        self._cabeza: "NodoCarpeta | None" = None
        self._total: int = 0

    # ── propiedades ───────────────────────────────────────────

    @property
    def total(self) -> int:
        return self._total

    def esta_vacia(self) -> bool:
        return self._cabeza is None

    # ── inserción ─────────────────────────────────────────────

    def agregar_carpeta(self, nombre: str) -> NodoCarpeta:
        """
        Crea e inserta una nueva carpeta al final de la lista.

        Complejidad: O(n)
        """
        nuevo = NodoCarpeta(nombre)

        if self._cabeza is None:
            self._cabeza = nuevo
        else:
            actual = self._cabeza
            while actual.siguiente is not None:
                actual = actual.siguiente
            actual.siguiente = nuevo

        self._total += 1
        return nuevo

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
        """Elimina la carpeta y todas sus tareas internas."""
        if self._cabeza is None:
            return False

        if self._cabeza.nombre == nombre:
            self._cabeza = self._cabeza.siguiente
            self._total -= 1
            return True

        anterior = self._cabeza
        actual = self._cabeza.siguiente
        while actual is not None:
            if actual.nombre == nombre:
                anterior.siguiente = actual.siguiente
                self._total -= 1
                return True
            anterior = actual
            actual = actual.siguiente

        return False

    # ── recorrido ─────────────────────────────────────────────

    def obtener_nombres(self) -> list[str]:
        """Devuelve la lista de nombres de todas las carpetas."""
        nombres = []
        actual = self._cabeza
        while actual is not None:
            nombres.append(actual.nombre)
            actual = actual.siguiente
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