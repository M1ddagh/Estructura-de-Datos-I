# 📋 To-Do List con Lista Doblemente Enlazada

> **Proyecto de Estructuras de Datos I** — Implementación del patrón de arquitectura **MVC (Modelo - Vista - Controlador)** con interfaz gráfica moderna en **Python (Tkinter)**.

---

## 📖 1. Descripción General

Esta aplicación es un gestor de tareas (*To-Do List*) organizado por carpetas o categorías. A diferencia de las aplicaciones convencionales que utilizan listas nativas de Python o arreglos dinámicos en memoria, este proyecto utiliza **Listas Doblemente Enlazadas personalizadas** como estructura de datos principal para el almacenamiento y gestión de la información.

El sistema organiza los datos en dos niveles enlazados:
1. **Lista Doblemente Enlazada de Carpetas:** Estructura de primer nivel que agrupa las categorías de trabajo.
2. **Lista Doblemente Enlazada de Tareas:** Cada carpeta contiene su propia lista doble independiente de tareas con prioridad, estado y descripción.

Además, las carpetas y tareas se **persisten automáticamente en un archivo JSON**, por lo que la información se conserva entre ejecuciones de la aplicación.

---

## 🗂️ 2. Estructura del Proyecto

```text
ProListas/
│
├── data/                       # Datos persistidos (se generan en ejecución)
│   └── tareas.json             # Carpetas y tareas guardadas automáticamente
├── env/                        # Entorno virtual de Python (venv)
├── src/                        # Código fuente de la aplicación
│   ├── models/
│   │   ├── model.py            # Nodos y listas doblemente enlazadas
│   │   └── storage.py          # Persistencia JSON (cargar / guardar)
│   ├── controllers/
│   │   └── controller.py       # Validaciones y puente entre Vista y Modelo
│   ├── views/
│   │   └── view.py             # Interfaz gráfica de usuario (Tkinter)
│   └── main.py                 # Punto de entrada de la aplicación
│
├── .gitignore                  # Archivos ignorados por Git
├── MODELO.md                   # Documentación técnica (model.py y storage.py)
├── README.md                   # Documentación general del proyecto
└── requirements.txt            # Sin dependencias externas (solo biblioteca estándar)
```

---

## ⚙️ 3. Entorno Virtual (`venv`) y Ejecución

El proyecto está preparado para ejecutarse dentro de un entorno virtual de Python (`venv`), lo cual aísla los paquetes e intérprete del sistema operativo.

### 3.1. Requisitos Previos
* **Python 3.10 o superior** instalado en el sistema.
* **Tkinter** (incluido por defecto en las instalaciones oficiales de Python en Windows y macOS).

---

### 3.2. Paso a Paso: Crear, Activar y Ejecutar

#### 🔹 Opción A: Usar el entorno virtual existente (`env`)
Si ya tienes la carpeta `env` en la raíz del proyecto, solo debes activarla:

* **En Windows (PowerShell):**
  ```powershell
  .\env\Scripts\Activate.ps1
  ```
  *(Si PowerShell bloquea la ejecución de scripts, ejecuta previamente: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

* **En Windows (Símbolo del sistema / CMD):**
  ```cmd
  .\env\Scripts\activate.bat
  ```

* **En Linux / macOS:**
  ```bash
  source env/bin/activate
  ```

---

#### 🔹 Opción B: Crear un entorno virtual desde cero
Si necesitas recrear el entorno virtual desde cero:

1. **Crear el entorno virtual:**
   ```bash
   python -m venv env
   ```
   *(Esto creará la carpeta `env` en el directorio actual).*

2. **Activar el entorno:**
   * **Windows (PowerShell):** `.\env\Scripts\Activate.ps1`
   * **Windows (CMD):** `.\env\Scripts\activate.bat`
   * **Linux/macOS:** `source env/bin/activate`

3. **(Opcional) Dependencias externas:**
   El proyecto no requiere paquetes de `pip`: usa únicamente la biblioteca estándar
   (`tkinter`, `json`, `pathlib`, `shutil`, `datetime`). El archivo
   `requirements.txt` solo deja constancia de ello, por lo que puedes omitir
   `pip install`.

---

### 3.3. Ejecutar la Aplicación

Con el entorno virtual activado, puedes ejecutar la aplicación directamente desde la raíz del proyecto:

```bash
python src/main.py
```

O accediendo a la carpeta `src`:

```bash
cd src
python main.py
```

> 💾 En el primer arranque se crea automáticamente `data/tareas.json` con la carpeta `General`. Cada cambio posterior se guarda al instante en ese archivo.

---

### 3.4. Desactivar el Entorno Virtual
Cuando termines de trabajar en el proyecto, puedes salir del entorno virtual ejecutando:

```bash
deactivate
```

---

## 🧠 4. Estructura de Datos: Lista Doblemente Enlazada

El proyecto implementa listas **doblemente enlazadas** no circulares. Cada nodo mantiene dos referencias (`anterior` y `siguiente`) y cada lista conserva punteros a la **cabeza** y a la **cola**.

```
None <- [Cabeza: Tarea A] <-> [Tarea B] <-> [Tarea C: Cola] -> None
```

* **NodoTarea / NodoCarpeta:** Cada nodo guarda sus datos y referencias al nodo previo (`anterior`) y al siguiente (`siguiente`). En la cabeza `anterior is None`; en la cola `siguiente is None`.
* **Inserción al final ($O(1)$):** Gracias al puntero `_cola` no se recorre la lista: se enlaza `cola.siguiente = nuevo` y `nuevo.anterior = cola`.
* **Recorrido bidireccional ($O(n)$):** Puede hacerse desde la cabeza con `siguiente` o desde la cola con `anterior` (`obtener_todas_inverso()` y `obtener_nombres_inverso()`).
* **Búsqueda secuencial ($O(n)$):** Recorrido paso a paso comparando el identificador (nombre o título).
* **Eliminación ($O(n)$):** Se localiza el nodo y se reconectan ambos vecinos (`nodo.anterior.siguiente = nodo.siguiente` y `nodo.siguiente.anterior = nodo.anterior`), actualizando `_cabeza` y `_cola` cuando corresponde.

> 💡 **Para una explicación profunda y detallada del código del modelo, consulta [MODELO.md](MODELO.md).**

---

## 🏛️ 5. Patrón de Diseño MVC

* **Modelo (`src/models/model.py`):**
  Implementa las clases de las estructuras de datos (`NodoTarea`, `ListaTareas`, `NodoCarpeta`, `ListaCarpetas`) como listas doblemente enlazadas. Es independiente de la GUI y de la lógica de validación externa.
* **Persistencia (`src/models/storage.py`):**
  Convierte las listas enlazadas a/desde JSON (`serializar`, `deserializar`, `cargar`, `guardar`). No conoce Tkinter ni las reglas de negocio.
* **Controlador (`src/controllers/controller.py`):**
  Aplica reglas de negocio (longitud máxima de texto, unicidad de nombres, prioridades permitidas), transmite datos entre la vista y las listas enlazadas devolviendo tuplas `(éxito: bool, mensaje: str)` y guarda automáticamente tras cada cambio.
* **Vista (`src/views/view.py`):**
  Interfaz gráfica basada en Tkinter con diseño en modo oscuro, paneles divididos, tarjetas estilizadas y feedback visual en tiempo real. Si el archivo de datos no puede leerse, muestra una advertencia al iniciar.

---

## 💾 6. Persistencia en JSON

Cada operación que modifica el estado (crear/eliminar carpeta, crear/editar/eliminar tarea, cambiar estado) llama a `storage.guardar()`.

* **Archivo:** `data/tareas.json`, creado automáticamente en el primer arranque.
* **Guardado atómico:** se escribe un archivo temporal y se reemplaza el original con `os.replace`, evitando archivos a medio escribir.
* **Restauración completa:** se conservan el orden de carpetas y tareas, la descripción, la prioridad, el estado y la fecha de creación.
* **Tolerancia a errores:** si el JSON está corrupto, se crea una copia `tareas.json.bak`, se arranca con la carpeta `General` y la Vista muestra un aviso.
* **Ruta configurable:** `TareasController(ruta_datos="mi_archivo.json")`, útil para pruebas o para guardar los datos en otra ubicación.

Ejemplo del formato:

```json
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
```

> `data/` está incluido en `.gitignore` porque contiene datos locales del usuario.

---

## ✨ 7. Funcionalidades Principales

* 📁 **Gestión de Carpetas:** Creación y eliminación de carpetas temáticas (con carpeta `General` protegida por defecto).
* 📝 **Gestión de Tareas:** Alta, edición, marcado de estado (`pendiente` / `completada`) y eliminación.
* 🚦 **Prioridades:** Clasificación por niveles (`alta`, `media`, `baja`) con diferenciación cromática.
* 🔍 **Filtros en Vivo:** Filtrado simultáneo por estado (todas / pendientes / completadas) y por prioridad.
* 📊 **Estadísticas Dinámicas:** Contadores en tiempo real de tareas totales, completadas y pendientes.
* 💾 **Persistencia automática:** Las tareas y carpetas se conservan entre ejecuciones sin intervención del usuario.
