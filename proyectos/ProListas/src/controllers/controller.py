"""
controllers/controller.py
--------------------------
Intermediario entre la Vista y el Modelo.
Valida entradas, delega al Modelo y devuelve
tuplas (éxito: bool, mensaje: str).
"""

from models.model import ListaCarpetas, PRIORIDADES_VALIDAS


# ── CONSTANTES DE VALIDACIÓN ──────────────────────────────────────────────────

MAX_LEN_TITULO = 80
MAX_LEN_DESC = 300
MAX_LEN_CARPETA = 40


# ── CONTROLADOR PRINCIPAL ─────────────────────────────────────────────────────

class TareasController:
    """
    Gestiona carpetas y las tareas dentro de cada una.

    Todas las operaciones retornan una tupla:
        (True,  mensaje_de_exito)
        (False, mensaje_de_error)
    """

    def __init__(self) -> None:
        self._lista_carpetas: ListaCarpetas = ListaCarpetas()
        # Carpeta por defecto para tareas sin asignar
        self._lista_carpetas.agregar_carpeta("General")

    # ══════════════════════════════════════════════════════════
    # CARPETAS
    # ══════════════════════════════════════════════════════════

    def agregar_carpeta(self, nombre: str) -> tuple[bool, str]:
        """Crea una nueva carpeta si el nombre es válido y único."""
        nombre = nombre.strip()

        if not nombre:
            return False, "El nombre de la carpeta no puede estar vacío."

        if len(nombre) > MAX_LEN_CARPETA:
            return False, f"Nombre demasiado largo (máx. {MAX_LEN_CARPETA} caracteres)."

        if self._lista_carpetas.buscar_carpeta(nombre) is not None:
            return False, f'Ya existe una carpeta llamada "{nombre}".'

        self._lista_carpetas.agregar_carpeta(nombre)
        return True, f'Carpeta "{nombre}" creada.'

    def eliminar_carpeta(self, nombre: str) -> tuple[bool, str]:
        """
        Elimina la carpeta y todas sus tareas.
        No permite eliminar la carpeta 'General'.
        """
        if nombre == "General":
            return False, "La carpeta General no puede eliminarse."

        ok = self._lista_carpetas.eliminar_carpeta(nombre)
        if ok:
            return True, f'Carpeta "{nombre}" eliminada.'
        return False, f'No se encontró la carpeta "{nombre}".'

    def obtener_carpetas(self) -> list[str]:
        """Devuelve los nombres de todas las carpetas."""
        return self._lista_carpetas.obtener_nombres()

    def resumen_carpetas(self) -> list[dict]:
        """Devuelve estadísticas de cada carpeta."""
        return self._lista_carpetas.obtener_resumen()

    # ══════════════════════════════════════════════════════════
    # TAREAS
    # ══════════════════════════════════════════════════════════

    def agregar_tarea(
        self,
        titulo: str,
        carpeta: str = "General",
        descripcion: str = "",
        prioridad: str = "media",
    ) -> tuple[bool, str]:
        """
        Agrega una tarea a la carpeta indicada.

        Parámetros
        ----------
        titulo : str
        carpeta : str, optional
        descripcion : str, optional
        prioridad : str, optional  'alta' | 'media' | 'baja'
        """
        titulo = titulo.strip()
        descripcion = descripcion.strip()
        prioridad = prioridad.strip().lower()

        # ── validaciones ──────────────────────────────────────
        if not titulo:
            return False, "El título no puede estar vacío."

        if len(titulo) > MAX_LEN_TITULO:
            return False, f"Título demasiado largo (máx. {MAX_LEN_TITULO} caracteres)."

        if len(descripcion) > MAX_LEN_DESC:
            return False, f"Descripción demasiado larga (máx. {MAX_LEN_DESC} caracteres)."

        if prioridad not in PRIORIDADES_VALIDAS:
            return False, f"Prioridad inválida. Usa: {', '.join(PRIORIDADES_VALIDAS)}."

        nodo_carpeta = self._lista_carpetas.buscar_carpeta(carpeta)
        if nodo_carpeta is None:
            return False, f'La carpeta "{carpeta}" no existe.'

        if nodo_carpeta.tareas.buscar(titulo) is not None:
            return False, f'Ya existe una tarea llamada "{titulo}" en esta carpeta.'

        nodo_carpeta.tareas.agregar(titulo, descripcion, prioridad)
        return True, f'Tarea "{titulo}" agregada en "{carpeta}".'

    def editar_tarea(
        self,
        titulo: str,
        carpeta: str,
        nueva_descripcion: str | None = None,
        nueva_prioridad: str | None = None,
    ) -> tuple[bool, str]:
        """Modifica la descripción y/o prioridad de una tarea existente."""
        if nueva_prioridad is not None:
            nueva_prioridad = nueva_prioridad.strip().lower()
            if nueva_prioridad not in PRIORIDADES_VALIDAS:
                return False, f"Prioridad inválida. Usa: {', '.join(PRIORIDADES_VALIDAS)}."

        nodo_carpeta = self._lista_carpetas.buscar_carpeta(carpeta)
        if nodo_carpeta is None:
            return False, f'La carpeta "{carpeta}" no existe.'

        ok = nodo_carpeta.tareas.actualizar(titulo, nueva_descripcion, nueva_prioridad)
        if ok:
            return True, f'Tarea "{titulo}" actualizada.'
        return False, f'No se encontró la tarea "{titulo}" en "{carpeta}".'

    def marcar_completada(self, titulo: str, carpeta: str) -> tuple[bool, str]:
        nodo_carpeta = self._lista_carpetas.buscar_carpeta(carpeta)
        if nodo_carpeta is None:
            return False, f'La carpeta "{carpeta}" no existe.'
        ok = nodo_carpeta.tareas.marcar_completada(titulo)
        if ok:
            return True, f'"{titulo}" marcada como completada.'
        return False, f'No se encontró la tarea "{titulo}".'

    def marcar_pendiente(self, titulo: str, carpeta: str) -> tuple[bool, str]:
        nodo_carpeta = self._lista_carpetas.buscar_carpeta(carpeta)
        if nodo_carpeta is None:
            return False, f'La carpeta "{carpeta}" no existe.'
        ok = nodo_carpeta.tareas.marcar_pendiente(titulo)
        if ok:
            return True, f'"{titulo}" marcada como pendiente.'
        return False, f'No se encontró la tarea "{titulo}".'

    def eliminar_tarea(self, titulo: str, carpeta: str) -> tuple[bool, str]:
        nodo_carpeta = self._lista_carpetas.buscar_carpeta(carpeta)
        if nodo_carpeta is None:
            return False, f'La carpeta "{carpeta}" no existe.'
        ok = nodo_carpeta.tareas.eliminar(titulo)
        if ok:
            return True, f'Tarea "{titulo}" eliminada.'
        return False, f'No se encontró la tarea "{titulo}" en "{carpeta}".'

    # ══════════════════════════════════════════════════════════
    # CONSULTAS
    # ══════════════════════════════════════════════════════════

    def obtener_tareas(
        self,
        carpeta: str,
        filtro_estado: str = "todas",
        filtro_prioridad: str = "todas",
    ) -> list[dict]:
        """
        Devuelve las tareas de una carpeta con filtros opcionales.

        Parámetros
        ----------
        carpeta : str
        filtro_estado : str  'todas' | 'pendiente' | 'completada'
        filtro_prioridad : str  'todas' | 'alta' | 'media' | 'baja'
        """
        nodo_carpeta = self._lista_carpetas.buscar_carpeta(carpeta)
        if nodo_carpeta is None:
            return []

        tareas = nodo_carpeta.tareas.obtener_todas()

        if filtro_estado != "todas":
            tareas = [t for t in tareas if t["estado"] == filtro_estado]

        if filtro_prioridad != "todas":
            tareas = [t for t in tareas if t["prioridad"] == filtro_prioridad]

        return tareas

    def estadisticas_carpeta(self, carpeta: str) -> dict:
        """Estadísticas numéricas de una carpeta concreta."""
        nodo_carpeta = self._lista_carpetas.buscar_carpeta(carpeta)
        if nodo_carpeta is None:
            return {"total": 0, "completadas": 0, "pendientes": 0}

        total = nodo_carpeta.tareas.total
        completadas = nodo_carpeta.tareas.total_completadas
        return {
            "total": total,
            "completadas": completadas,
            "pendientes": total - completadas,
        }