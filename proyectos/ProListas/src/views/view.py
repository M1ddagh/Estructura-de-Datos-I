"""
views/view.py
-------------
Interfaz gráfica Tkinter para la To-Do List con carpetas.
La vista solo habla con el Controlador, nunca con el Modelo.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog

from controllers.controller import TareasController


# ── PALETA ────────────────────────────────────────────────────────────────────

BG_MAIN = "#0F0F13"
BG_CARD = "#1A1A24"
BG_INPUT = "#22222E"
ACCENT = "#7C6AF7"
ACCENT_HOVER = "#9B8FFB"
GREEN = "#4ADE80"
RED = "#F87171"
YELLOW = "#FBD147"
ORANGE = "#FB923C"
TEXT_MAIN = "#F0EEF8"
TEXT_MUTED = "#6B6883"
BORDER = "#2E2E3E"
BORDER_ACTIVE = "#4A4860"

# Colores por prioridad
PRIORIDAD_COLOR = {
    "alta": ("#7F1D1D", "#FCA5A5"),    # (fondo, texto)
    "media": ("#713F12", "#FCD34D"),
    "baja": ("#14532D", "#86EFAC"),
}


# ── VENTANA PRINCIPAL ─────────────────────────────────────────────────────────

class TodoApp(tk.Tk):
    """Ventana raíz de la aplicación."""

    def __init__(self) -> None:
        super().__init__()
        self._controller = TareasController()
        self._carpeta_activa: str = "General"
        self._filtro_estado: str = "todas"
        self._filtro_prioridad: str = "todas"
        self._build_window()
        self._build_ui()
        self._refresh_sidebar()
        self._refresh_list()

        # Si el archivo de datos no pudo leerse, avisar tras dibujar la ventana
        if self._controller.advertencia_inicial:
            self.after(200, self._mostrar_advertencia_inicial)

    def _mostrar_advertencia_inicial(self) -> None:
        messagebox.showwarning(
            "Persistencia",
            self._controller.advertencia_inicial,
            parent=self,
        )

    # ── configuración de ventana ──────────────────────────────

    def _build_window(self) -> None:
        self.title("To-Do List · Carpetas · Lista Doble")
        self.geometry("820x680")
        self.minsize(700, 500)
        self.configure(bg=BG_MAIN)
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 820) // 2
        y = (self.winfo_screenheight() - 680) // 2
        self.geometry(f"+{x}+{y}")

    # ── layout general ────────────────────────────────────────

    def _build_ui(self) -> None:
        # Panel izquierdo (carpetas) + panel derecho (tareas)
        self._pane = tk.PanedWindow(
            self,
            orient="horizontal",
            bg=BG_MAIN,
            sashwidth=4,
            sashrelief="flat",
        )
        self._pane.pack(fill="both", expand=True)

        self._build_sidebar()
        self._build_main_panel()

    # ══════════════════════════════════════════════════════════
    # SIDEBAR — CARPETAS
    # ══════════════════════════════════════════════════════════

    def _build_sidebar(self) -> None:
        self._sidebar = tk.Frame(self._pane, bg=BG_CARD, width=200)
        self._pane.add(self._sidebar, minsize=160)

        # Encabezado sidebar
        header = tk.Frame(self._sidebar, bg=BG_CARD)
        header.pack(fill="x", padx=12, pady=(16, 8))

        tk.Label(
            header,
            text="CARPETAS",
            bg=BG_CARD,
            fg=ACCENT,
            font=("Courier New", 10, "bold"),
        ).pack(side="left")

        btn_new = tk.Label(
            header,
            text="＋",
            bg=BG_CARD,
            fg=ACCENT,
            font=("Courier New", 14, "bold"),
            cursor="hand2",
        )
        btn_new.pack(side="right")
        btn_new.bind("<Button-1>", lambda _e: self._nueva_carpeta())

        tk.Frame(self._sidebar, bg=BORDER, height=1).pack(fill="x")

        # Contenedor scrollable de carpetas
        self._sidebar_list = tk.Frame(self._sidebar, bg=BG_CARD)
        self._sidebar_list.pack(fill="both", expand=True, pady=8)

        # Indicador de persistencia
        tk.Frame(self._sidebar, bg=BORDER, height=1).pack(fill="x")
        tk.Label(
            self._sidebar,
            text="💾 Guardado automático",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Courier New", 8),
            pady=6,
        ).pack(fill="x")

    def _refresh_sidebar(self) -> None:
        for widget in self._sidebar_list.winfo_children():
            widget.destroy()

        for nombre in self._controller.obtener_carpetas():
            stats = self._controller.estadisticas_carpeta(nombre)
            activa = nombre == self._carpeta_activa

            row = tk.Frame(
                self._sidebar_list,
                bg=ACCENT if activa else BG_CARD,
                cursor="hand2",
            )
            row.pack(fill="x", padx=8, pady=2)

            tk.Label(
                row,
                text=f"📁  {nombre}",
                bg=ACCENT if activa else BG_CARD,
                fg=TEXT_MAIN if activa else TEXT_MUTED,
                font=("Courier New", 10),
                anchor="w",
                padx=8,
                pady=6,
            ).pack(side="left", fill="x", expand=True)

            tk.Label(
                row,
                text=str(stats["total"]),
                bg=ACCENT if activa else BG_CARD,
                fg=TEXT_MAIN if activa else TEXT_MUTED,
                font=("Courier New", 9),
                padx=8,
            ).pack(side="right")

            row.bind("<Button-1>", lambda _e, n=nombre: self._seleccionar_carpeta(n))
            for child in row.winfo_children():
                child.bind(
                    "<Button-1>",
                    lambda _e, n=nombre: self._seleccionar_carpeta(n),
                )

            # Clic derecho → eliminar carpeta
            if nombre != "General":
                row.bind(
                    "<Button-3>",
                    lambda _e, n=nombre: self._confirmar_eliminar_carpeta(n),
                )

    # ══════════════════════════════════════════════════════════
    # PANEL DERECHO — TAREAS
    # ══════════════════════════════════════════════════════════

    def _build_main_panel(self) -> None:
        self._main = tk.Frame(self._pane, bg=BG_MAIN)
        self._pane.add(self._main, minsize=460)

        # Encabezado con nombre de carpeta y stats
        top = tk.Frame(self._main, bg=BG_MAIN)
        top.pack(fill="x", padx=20, pady=(18, 0))

        self._lbl_carpeta = tk.Label(
            top,
            text="",
            bg=BG_MAIN,
            fg=TEXT_MAIN,
            font=("Courier New", 14, "bold"),
            anchor="w",
        )
        self._lbl_carpeta.pack(side="left")

        self._lbl_stats = tk.Label(
            top,
            text="",
            bg=BG_MAIN,
            fg=TEXT_MUTED,
            font=("Courier New", 10),
            anchor="e",
        )
        self._lbl_stats.pack(side="right")

        tk.Frame(self._main, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)

        # Formulario de nueva tarea
        self._build_form()

        # Filtros
        self._build_filters()

        # Lista de tareas
        self._build_task_list()

    def _build_form(self) -> None:
        """Formulario extendido: título, descripción, prioridad."""
        form = tk.Frame(self._main, bg=BG_CARD, padx=14, pady=12)
        form.pack(fill="x", padx=20, pady=(0, 10))

        # Fila 1: título
        row1 = tk.Frame(form, bg=BG_CARD)
        row1.pack(fill="x", pady=(0, 8))

        self._entry_titulo = tk.Entry(
            row1,
            bg=BG_INPUT,
            fg=TEXT_MAIN,
            insertbackground=ACCENT,
            relief="flat",
            font=("Courier New", 11),
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self._entry_titulo.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self._entry_titulo.insert(0, "Título de la tarea…")
        self._entry_titulo.config(fg=TEXT_MUTED)
        self._entry_titulo.bind("<FocusIn>", self._clear_titulo)
        self._entry_titulo.bind("<FocusOut>", self._set_titulo)
        self._entry_titulo.bind("<Return>", lambda _e: self._agregar_tarea())

        # Selector de prioridad
        self._var_prioridad = tk.StringVar(value="media")
        for valor, etiqueta in [("alta", "🔴 Alta"), ("media", "🟡 Media"), ("baja", "🟢 Baja")]:
            rb = tk.Radiobutton(
                row1,
                text=etiqueta,
                variable=self._var_prioridad,
                value=valor,
                bg=BG_CARD,
                fg=TEXT_MUTED,
                selectcolor=BG_CARD,
                activebackground=BG_CARD,
                activeforeground=ACCENT,
                font=("Courier New", 10),
                cursor="hand2",
            )
            rb.pack(side="left", padx=(0, 6))

        # Fila 2: descripción
        row2 = tk.Frame(form, bg=BG_CARD)
        row2.pack(fill="x", pady=(0, 8))

        self._entry_desc = tk.Text(
            row2,
            bg=BG_INPUT,
            fg=TEXT_MUTED,
            insertbackground=ACCENT,
            relief="flat",
            font=("Courier New", 10),
            height=2,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            wrap="word",
        )
        self._entry_desc.pack(fill="x", ipady=4)
        self._entry_desc.insert("1.0", "Descripción opcional…")
        self._entry_desc.bind("<FocusIn>", self._clear_desc)
        self._entry_desc.bind("<FocusOut>", self._set_desc)

        # Fila 3: botón agregar
        row3 = tk.Frame(form, bg=BG_CARD)
        row3.pack(fill="x")

        tk.Button(
            row3,
            text="＋ Agregar tarea",
            bg=ACCENT,
            fg=TEXT_MAIN,
            activebackground=ACCENT_HOVER,
            activeforeground=TEXT_MAIN,
            relief="flat",
            font=("Courier New", 11, "bold"),
            cursor="hand2",
            bd=0,
            padx=18,
            pady=8,
            command=self._agregar_tarea,
        ).pack(side="right")

    def _build_filters(self) -> None:
        bar = tk.Frame(self._main, bg=BG_MAIN)
        bar.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(
            bar, text="Estado:", bg=BG_MAIN, fg=TEXT_MUTED,
            font=("Courier New", 10),
        ).pack(side="left", padx=(0, 4))

        self._var_filtro_estado = tk.StringVar(value="todas")
        for txt, val in [("Todas", "todas"), ("Pendientes", "pendiente"), ("Completadas", "completada")]:
            tk.Radiobutton(
                bar, text=txt, variable=self._var_filtro_estado, value=val,
                bg=BG_MAIN, fg=TEXT_MUTED, selectcolor=BG_MAIN,
                activebackground=BG_MAIN, activeforeground=ACCENT,
                font=("Courier New", 10), cursor="hand2",
                command=self._aplicar_filtros,
            ).pack(side="left", padx=(0, 8))

        tk.Label(
            bar, text="  Prioridad:", bg=BG_MAIN, fg=TEXT_MUTED,
            font=("Courier New", 10),
        ).pack(side="left", padx=(0, 4))

        self._var_filtro_prioridad = tk.StringVar(value="todas")
        for txt, val in [("Todas", "todas"), ("Alta", "alta"), ("Media", "media"), ("Baja", "baja")]:
            tk.Radiobutton(
                bar, text=txt, variable=self._var_filtro_prioridad, value=val,
                bg=BG_MAIN, fg=TEXT_MUTED, selectcolor=BG_MAIN,
                activebackground=BG_MAIN, activeforeground=ACCENT,
                font=("Courier New", 10), cursor="hand2",
                command=self._aplicar_filtros,
            ).pack(side="left", padx=(0, 6))

    def _build_task_list(self) -> None:
        container = tk.Frame(self._main, bg=BG_MAIN)
        container.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self._canvas = tk.Canvas(
            container, bg=BG_MAIN, bd=0, highlightthickness=0,
        )
        scrollbar = tk.Scrollbar(
            container, orient="vertical", command=self._canvas.yview,
        )
        self._canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._list_frame = tk.Frame(self._canvas, bg=BG_MAIN)
        self._canvas_win = self._canvas.create_window(
            (0, 0), window=self._list_frame, anchor="nw",
        )
        self._list_frame.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    # ── scroll ────────────────────────────────────────────────

    def _on_frame_configure(self, _event: tk.Event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfig(self._canvas_win, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── placeholders ─────────────────────────────────────────

    def _clear_titulo(self, _event: tk.Event) -> None:
        if self._entry_titulo.get() == "Título de la tarea…":
            self._entry_titulo.delete(0, "end")
            self._entry_titulo.config(fg=TEXT_MAIN)

    def _set_titulo(self, _event: tk.Event) -> None:
        if not self._entry_titulo.get():
            self._entry_titulo.insert(0, "Título de la tarea…")
            self._entry_titulo.config(fg=TEXT_MUTED)

    def _clear_desc(self, _event: tk.Event) -> None:
        if self._entry_desc.get("1.0", "end-1c") == "Descripción opcional…":
            self._entry_desc.delete("1.0", "end")
            self._entry_desc.config(fg=TEXT_MAIN)

    def _set_desc(self, _event: tk.Event) -> None:
        if not self._entry_desc.get("1.0", "end-1c").strip():
            self._entry_desc.delete("1.0", "end")
            self._entry_desc.insert("1.0", "Descripción opcional…")
            self._entry_desc.config(fg=TEXT_MUTED)

    # ══════════════════════════════════════════════════════════
    # ACCIONES
    # ══════════════════════════════════════════════════════════

    def _seleccionar_carpeta(self, nombre: str) -> None:
        self._carpeta_activa = nombre
        self._filtro_estado = "todas"
        self._filtro_prioridad = "todas"
        self._var_filtro_estado.set("todas")
        self._var_filtro_prioridad.set("todas")
        self._refresh_sidebar()
        self._refresh_list()

    def _nueva_carpeta(self) -> None:
        nombre = simpledialog.askstring(
            "Nueva carpeta",
            "Nombre de la carpeta:",
            parent=self,
        )
        if nombre is None:
            return
        ok, msg = self._controller.agregar_carpeta(nombre)
        if ok:
            self._refresh_sidebar()
        else:
            messagebox.showwarning("Atención", msg, parent=self)

    def _confirmar_eliminar_carpeta(self, nombre: str) -> None:
        confirmar = messagebox.askyesno(
            "Eliminar carpeta",
            f'¿Eliminar "{nombre}" y todas sus tareas?',
            parent=self,
        )
        if not confirmar:
            return
        ok, msg = self._controller.eliminar_carpeta(nombre)
        if ok:
            if self._carpeta_activa == nombre:
                self._carpeta_activa = "General"
            self._refresh_sidebar()
            self._refresh_list()
        else:
            messagebox.showerror("Error", msg, parent=self)

    def _agregar_tarea(self) -> None:
        titulo = self._entry_titulo.get().strip()
        if titulo == "Título de la tarea…":
            titulo = ""

        desc = self._entry_desc.get("1.0", "end-1c").strip()
        if desc == "Descripción opcional…":
            desc = ""

        prioridad = self._var_prioridad.get()

        ok, msg = self._controller.agregar_tarea(
            titulo=titulo,
            carpeta=self._carpeta_activa,
            descripcion=desc,
            prioridad=prioridad,
        )
        if ok:
            self._entry_titulo.delete(0, "end")
            self._set_titulo(None)
            self._entry_desc.delete("1.0", "end")
            self._set_desc(None)
            self._var_prioridad.set("media")
            self._refresh_sidebar()
            self._refresh_list()
        else:
            messagebox.showwarning("Atención", msg, parent=self)

    def _editar_tarea(self, titulo: str, descripcion: str, prioridad: str) -> None:
        """Abre un diálogo modal para editar la descripción y la prioridad."""
        dialogo = tk.Toplevel(self)
        dialogo.title("Editar tarea")
        dialogo.configure(bg=BG_CARD)
        dialogo.resizable(False, False)
        dialogo.transient(self)
        dialogo.grab_set()
        dialogo.bind("<Escape>", lambda _e: dialogo.destroy())

        tk.Label(
            dialogo,
            text=titulo,
            bg=BG_CARD,
            fg=TEXT_MAIN,
            font=("Courier New", 12, "bold"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 8))

        tk.Label(
            dialogo,
            text="Descripción",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Courier New", 9),
            anchor="w",
        ).pack(fill="x", padx=16)

        texto = tk.Text(
            dialogo,
            bg=BG_INPUT,
            fg=TEXT_MAIN,
            insertbackground=ACCENT,
            relief="flat",
            font=("Courier New", 10),
            height=4,
            width=46,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            wrap="word",
        )
        texto.pack(fill="x", padx=16, pady=(4, 10))
        texto.insert("1.0", descripcion)

        tk.Label(
            dialogo,
            text="Prioridad",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Courier New", 9),
            anchor="w",
        ).pack(fill="x", padx=16)

        var_prioridad = tk.StringVar(value=prioridad)
        fila_prioridad = tk.Frame(dialogo, bg=BG_CARD)
        fila_prioridad.pack(fill="x", padx=16, pady=(4, 14))

        for valor, etiqueta in [("alta", "🔴 Alta"), ("media", "🟡 Media"), ("baja", "🟢 Baja")]:
            tk.Radiobutton(
                fila_prioridad,
                text=etiqueta,
                variable=var_prioridad,
                value=valor,
                bg=BG_CARD,
                fg=TEXT_MUTED,
                selectcolor=BG_CARD,
                activebackground=BG_CARD,
                activeforeground=ACCENT,
                font=("Courier New", 10),
                cursor="hand2",
            ).pack(side="left", padx=(0, 10))

        botones = tk.Frame(dialogo, bg=BG_CARD)
        botones.pack(fill="x", padx=16, pady=(0, 14))

        def guardar() -> None:
            nueva_descripcion = texto.get("1.0", "end-1c").strip()
            ok, msg = self._controller.editar_tarea(
                titulo,
                self._carpeta_activa,
                nueva_descripcion=nueva_descripcion,
                nueva_prioridad=var_prioridad.get(),
            )
            if ok:
                dialogo.destroy()
                self._refresh_sidebar()
                self._refresh_list()
            else:
                messagebox.showwarning("Atención", msg, parent=dialogo)

        tk.Button(
            botones,
            text="Guardar",
            command=guardar,
            bg=ACCENT,
            fg=TEXT_MAIN,
            activebackground=ACCENT_HOVER,
            activeforeground=TEXT_MAIN,
            relief="flat",
            font=("Courier New", 10, "bold"),
            cursor="hand2",
            bd=0,
            padx=14,
            pady=6,
        ).pack(side="right")

        tk.Button(
            botones,
            text="Cancelar",
            command=dialogo.destroy,
            bg=BG_INPUT,
            fg=TEXT_MUTED,
            activebackground=BORDER_ACTIVE,
            activeforeground=TEXT_MAIN,
            relief="flat",
            font=("Courier New", 10),
            cursor="hand2",
            bd=0,
            padx=14,
            pady=6,
        ).pack(side="right", padx=(0, 8))

        texto.focus_set()
        dialogo.wait_window()

    def _toggle_estado(self, titulo: str, estado_actual: str) -> None:
        if estado_actual == "pendiente":
            self._controller.marcar_completada(titulo, self._carpeta_activa)
        else:
            self._controller.marcar_pendiente(titulo, self._carpeta_activa)
        self._refresh_sidebar()
        self._refresh_list()

    def _eliminar_tarea(self, titulo: str) -> None:
        ok, msg = self._controller.eliminar_tarea(titulo, self._carpeta_activa)
        if ok:
            self._refresh_sidebar()
            self._refresh_list()
        else:
            messagebox.showerror("Error", msg, parent=self)

    def _aplicar_filtros(self) -> None:
        self._filtro_estado = self._var_filtro_estado.get()
        self._filtro_prioridad = self._var_filtro_prioridad.get()
        self._refresh_list()

    # ══════════════════════════════════════════════════════════
    # RENDERIZADO
    # ══════════════════════════════════════════════════════════

    def _refresh_list(self) -> None:
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        tareas = self._controller.obtener_tareas(
            self._carpeta_activa,
            filtro_estado=self._filtro_estado,
            filtro_prioridad=self._filtro_prioridad,
        )

        self._lbl_carpeta.config(text=f"📁  {self._carpeta_activa}")
        stats = self._controller.estadisticas_carpeta(self._carpeta_activa)
        self._lbl_stats.config(
            text=f"{stats['completadas']}/{stats['total']} completadas"
        )

        if not tareas:
            tk.Label(
                self._list_frame,
                text="— sin tareas —",
                bg=BG_MAIN,
                fg=TEXT_MUTED,
                font=("Courier New", 11),
                pady=30,
            ).pack()
        else:
            for tarea in tareas:
                self._build_task_card(tarea)

    def _build_task_card(self, tarea: dict) -> None:
        titulo = tarea["titulo"]
        estado = tarea["estado"]
        prioridad = tarea["prioridad"]
        descripcion = tarea["descripcion"]
        fecha = tarea["fecha_creacion"]
        done = estado == "completada"

        fondo_pr, texto_pr = PRIORIDAD_COLOR[prioridad]

        # Tarjeta contenedor
        card = tk.Frame(
            self._list_frame,
            bg=BG_CARD,
            highlightthickness=1,
            highlightbackground=GREEN if done else BORDER,
            pady=10,
            padx=14,
            cursor="hand2",
        )
        card.pack(fill="x", pady=5)

        # Fila 1: checkbox + título + badge prioridad + botón eliminar
        row1 = tk.Frame(card, bg=BG_CARD)
        row1.pack(fill="x")

        # Checkbox visual
        check_char = "✔" if done else "○"
        lbl_check = tk.Label(
            row1,
            text=check_char,
            bg=BG_CARD,
            fg=GREEN if done else TEXT_MUTED,
            font=("Courier New", 14),
            cursor="hand2",
        )
        lbl_check.pack(side="left", padx=(0, 8))

        # Título
        lbl_titulo = tk.Label(
            row1,
            text=titulo,
            bg=BG_CARD,
            fg=TEXT_MUTED if done else TEXT_MAIN,
            font=("Courier New", 11, "overstrike" if done else "normal"),
            anchor="w",
        )
        lbl_titulo.pack(side="left", fill="x", expand=True)

        # Badge prioridad
        tk.Label(
            row1,
            text=prioridad.upper(),
            bg=fondo_pr,
            fg=texto_pr,
            font=("Courier New", 8, "bold"),
            padx=6,
            pady=2,
        ).pack(side="right", padx=(6, 4))

        # Botón eliminar
        btn_del = tk.Label(
            row1,
            text="✕",
            bg=BG_CARD,
            fg=RED,
            font=("Courier New", 13, "bold"),
            cursor="hand2",
        )
        btn_del.pack(side="right")

        # Botón editar
        btn_edit = tk.Label(
            row1,
            text="✎",
            bg=BG_CARD,
            fg=ACCENT,
            font=("Courier New", 13, "bold"),
            cursor="hand2",
        )
        btn_edit.pack(side="right", padx=(0, 4))

        # Fila 2: descripción (si existe)
        if descripcion:
            tk.Label(
                card,
                text=descripcion,
                bg=BG_CARD,
                fg=TEXT_MUTED,
                font=("Courier New", 9),
                anchor="w",
                wraplength=460,
                justify="left",
                pady=4,
            ).pack(fill="x", padx=(22, 0))

        # Fila 3: fecha de creación
        tk.Label(
            card,
            text=f"🕐  {fecha}",
            bg=BG_CARD,
            fg="#3D3B52",
            font=("Courier New", 8),
            anchor="w",
        ).pack(fill="x", padx=(22, 0), pady=(2, 0))

        # ── bindings ──────────────────────────────────────────
        for widget in (card, lbl_check, lbl_titulo):
            widget.bind(
                "<Button-1>",
                lambda _e, t=titulo, s=estado: self._toggle_estado(t, s),
            )
        btn_del.bind(
            "<Button-1>",
            lambda _e, t=titulo: self._eliminar_tarea(t),
        )
        btn_edit.bind(
            "<Button-1>",
            lambda _e, t=titulo, d=descripcion, p=prioridad: self._editar_tarea(t, d, p),
        )

        def on_enter(_e: tk.Event) -> None:
            card.config(highlightbackground=ACCENT_HOVER)

        def on_leave(_e: tk.Event) -> None:
            card.config(highlightbackground=GREEN if done else BORDER)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)