"""
models/storage.py
-----------------
Persistencia en disco de las listas de carpetas y tareas.

El formato utilizado es JSON legible, con el siguiente esquema:

    {
      "version": 1,
      "carpetas": [
        {
          "nombre": "General",
          "tareas": [
            {
              "titulo": "Comprar pan",
              "descripcion": "",
              "prioridad": "media",
              "estado": "pendiente",
              "fecha_creacion": "2026-10-17T10:30:00"
            }
          ]
        }
      ]
    }

El módulo no conoce Tkinter ni reglas de negocio: solo convierte entre
la estructura en memoria (listas doblemente enlazadas) y el archivo JSON.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from models.model import (
    ESTADO_COMPLETADA,
    ESTADO_PENDIENTE,
    PRIORIDADES_VALIDAS,
    ListaCarpetas,
    NodoCarpeta,
    NodoTarea,
)


# ── RUTAS Y CONSTANTES ────────────────────────────────────────────────────────

# ProListas/src/models/storage.py -> parents[2] == raíz del proyecto
RUTA_DATOS_PREDETERMINADA = Path(__file__).resolve().parents[2] / "data" / "tareas.json"

VERSION_ESQUEMA = 1
FORMATO_FECHA_LEGADO = "%d/%m/%Y %H:%M"


# ── SERIALIZACIÓN ─────────────────────────────────────────────────────────────

def serializar(lista_carpetas: ListaCarpetas) -> dict:
    """
    Convierte la estructura enlazada completa a un diccionario JSON.

    Complejidad: O(m * n), donde m son las carpetas y n sus tareas.
    """
    carpetas = []
    actual = lista_carpetas.cabeza

    while actual is not None:
        tareas = []
        tarea = actual.tareas.cabeza

        while tarea is not None:
            tareas.append({
                "titulo": tarea.titulo,
                "descripcion": tarea.descripcion,
                "prioridad": tarea.prioridad,
                "estado": tarea.estado,
                "fecha_creacion": tarea.fecha_creacion.isoformat(),
            })
            tarea = tarea.siguiente

        carpetas.append({
            "nombre": actual.nombre,
            "tareas": tareas,
        })
        actual = actual.siguiente

    return {
        "version": VERSION_ESQUEMA,
        "carpetas": carpetas,
    }


def _parsear_fecha(valor: object) -> datetime:
    """Acepta ISO 8601 y el formato antiguo dd/mm/aaaa hh:mm."""
    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            try:
                return datetime.strptime(valor, FORMATO_FECHA_LEGADO)
            except ValueError:
                pass
    return datetime.now()


def _crear_tarea(datos: dict) -> NodoTarea | None:
    """Construye un NodoTarea validando los campos leídos del archivo."""
    titulo = str(datos.get("titulo", "")).strip()
    if not titulo:
        return None

    prioridad = str(datos.get("prioridad", "media")).strip().lower()
    if prioridad not in PRIORIDADES_VALIDAS:
        prioridad = "media"

    estado = str(datos.get("estado", ESTADO_PENDIENTE)).strip().lower()
    if estado not in (ESTADO_PENDIENTE, ESTADO_COMPLETADA):
        estado = ESTADO_PENDIENTE

    return NodoTarea(
        titulo=titulo,
        descripcion=str(datos.get("descripcion", "")),
        prioridad=prioridad,
        estado=estado,
        fecha_creacion=_parsear_fecha(datos.get("fecha_creacion")),
    )


def deserializar(datos: dict) -> ListaCarpetas:
    """
    Reconstruye las listas doblemente enlazadas desde un diccionario.

    Ignora carpetas o tareas con datos inválidos o duplicados para que
    un archivo editado a mano no rompa la aplicación.
    """
    lista_carpetas = ListaCarpetas()
    if not isinstance(datos, dict):
        return lista_carpetas

    carpetas = datos.get("carpetas", [])
    if not isinstance(carpetas, list):
        return lista_carpetas

    for datos_carpeta in carpetas:
        if not isinstance(datos_carpeta, dict):
            continue

        nombre = str(datos_carpeta.get("nombre", "")).strip()
        if not nombre or lista_carpetas.buscar_carpeta(nombre) is not None:
            continue

        nodo_carpeta = NodoCarpeta(nombre)

        tareas = datos_carpeta.get("tareas", [])
        if isinstance(tareas, list):
            for datos_tarea in tareas:
                if not isinstance(datos_tarea, dict):
                    continue
                nodo_tarea = _crear_tarea(datos_tarea)
                if nodo_tarea is None:
                    continue
                # Evita títulos repetidos dentro de la misma carpeta
                if nodo_carpeta.tareas.buscar(nodo_tarea.titulo) is not None:
                    continue
                nodo_carpeta.tareas.agregar_nodo(nodo_tarea)

        lista_carpetas.agregar_nodo(nodo_carpeta)

    return lista_carpetas


# ── LECTURA Y ESCRITURA EN DISCO ──────────────────────────────────────────────

def _resolver_ruta(ruta: str | Path | None) -> Path:
    return Path(ruta) if ruta is not None else RUTA_DATOS_PREDETERMINADA


def cargar(ruta: str | Path | None = None) -> tuple[ListaCarpetas, str | None]:
    """
    Lee el archivo JSON y devuelve (lista, .

    * Si el archivo no existe, retorna una lista vacía 
      (primer arranque de la aplicación).
    * Si el archivo está corrupto, crea una copia de respaldo .bak y
      retorna una lista vacía junto con un mensaje para la Vista.
    """
    destino = _resolver_ruta(ruta)

    if not destino.exists():
        return ListaCarpetas(), None

    try:
        with destino.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (OSError, json.JSONDecodeError) as error:
        respaldo = _crear_respaldo(destino)
        mensaje = f"No se pudo leer {destino.name}: {error}."
        if respaldo is not None:
            mensaje += f" Se creó un respaldo en {respaldo.name}."
        return ListaCarpetas(), mensaje

    if not isinstance(datos, dict):
        return ListaCarpetas(), f"El archivo {destino.name} tiene un formato inesperado."

    return deserializar(datos), None


def _crear_respaldo(destino: Path) -> Path | None:
    """Copia el archivo dañado a <nombre>.bak para no perder los datos."""
    respaldo = destino.with_name(destino.name + ".bak")
    try:
        shutil.copy2(destino, respaldo)
    except OSError:
        return None
    return respaldo


def guardar(
    lista_carpetas: ListaCarpetas,
    ruta: str | Path | None = None,
) -> tuple[bool, str]:
    """
    Guarda la estructura completa en JSON de forma atómica.

    Se escribe primero un archivo temporal y luego se reemplaza el
    original con os.replace, de modo que una interrupción no deje el
    archivo de datos a medio escribir.

    Retorna (éxito, mensaje).
    """
    destino = _resolver_ruta(ruta)
    temporal = destino.with_name(destino.name + ".tmp")

    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(
                serializar(lista_carpetas),
                archivo,
                ensure_ascii=False,
                indent=2,
            )
            archivo.write("\n")
        os.replace(temporal, destino)
    except (OSError, TypeError, ValueError, AttributeError) as error:
        try:
            temporal.unlink(missing_ok=True)
        except OSError:
            pass
        return False, f"No se pudieron guardar los datos: {error}"

    return True, f"Datos guardados en {destino}."
