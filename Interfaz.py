import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

# Importamos los módulos de nuestras 3 fases
from Fase1 import AnalizadorLexico
from Fase2 import AnalizadorSintactico, AdaptadorLexicoPLY
from Fase3 import AnalizadorSemantico

class InterfazMiniLang:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Compilador MiniLang - Fases 1, 2 y 3 | hecho por: Ian & Bruno")
        self.raiz.geometry("1250x850") # Ajustamos el ancho para acomodar la tercera tabla
        self.raiz.minsize(1000, 680)
        self.archivo_actual = None

        # Tema general con colores armonizados
        self.colores = {
            "fondo": "#F8DDEB",
            "panel": "#FCEAF2",
            "panel2": "#FFF4F8",
            "borde": "#D8AFC2",
            "texto": "#5C4350",
            "editor": "#FFF9FC",
            "btn_cargar": "#F7C6D9",
            "btn_cargar_hover": "#EFB1CA",
            "btn_run": "#CDECCF",
            "btn_run_hover": "#B8E0BB",
            "err_lex": "#FFF0F3",
            "err_sin": "#F4F0FF",
            "err_sem": "#FFF5EB", 
            "scroll": "#EAB8CD",
            "scroll_hover": "#D99AB5",
            "scroll_trough": "#F7DCE8"
        }

        self.fuentes = {
            "titulo": ("Candara", 11, "bold"),
            "texto": ("Calibri", 10),
            "editor": ("Consolas", 11),
            "boton": ("Candara", 10, "bold"),
            "heading": ("Candara", 10, "bold")
        }

        self.raiz.configure(bg=self.colores["fondo"])
        self._configurar_estilos()

        principal = tk.Frame(self.raiz, bg=self.colores["fondo"])
        principal.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        barra = tk.Frame(principal, bg=self.colores["panel"], bd=2, relief=tk.GROOVE, padx=10, pady=8)
        barra.pack(fill=tk.X, pady=(0, 8))

        self.btn_cargar = self._crear_boton(
            barra, "Cargar Archivo (.mlng)", self.cargar_archivo,
            self.colores["btn_cargar"], self.colores["btn_cargar_hover"], self.colores["texto"]
        )
        self.btn_cargar.pack(side=tk.LEFT, padx=8)

        self.btn_analizar = self._crear_boton(
            barra, "Ejecutar Compilador", self.ejecutar_analisis,
            self.colores["btn_run"], self.colores["btn_run_hover"], "#35523C"
        )
        self.btn_analizar.pack(side=tk.LEFT, padx=8)

        panel_principal = tk.PanedWindow(
            principal, orient=tk.VERTICAL, bg=self.colores["fondo"],
            sashwidth=8, sashrelief=tk.RAISED, bd=0
        )
        panel_principal.pack(fill=tk.BOTH, expand=True)

        # Panel superior dividido en 3 secciones horizontales
        panel_superior = tk.PanedWindow(
            panel_principal, orient=tk.HORIZONTAL, bg=self.colores["fondo"],
            sashwidth=8, sashrelief=tk.RAISED, bd=0
        )

        # Sección 1: Editor de código
        frame_entrada = self._crear_labelframe(panel_superior, "Entrada (Código Fuente)", self.colores["panel"])
        self.txt_entrada = self._crear_texto_con_scroll(
            frame_entrada, bg=self.colores["editor"], fg="#3F2F37",
            fuente=self.fuentes["editor"], wrap=tk.NONE
        )
        panel_superior.add(frame_entrada, minsize=350)

        # Sección 2: Tabla de Tokens
        frame_tokens = self._crear_labelframe(panel_superior, "Salida Léxica (Tokens)", self.colores["panel"])
        self._crear_tabla_tokens(frame_tokens)
        panel_superior.add(frame_tokens, minsize=350)

        # Sección 3: Tabla de Símbolos Dinámica (¡NUEVA!)
        frame_simbolos = self._crear_labelframe(panel_superior, "Tabla de Símbolos (Fase 3)", self.colores["panel"])
        self._crear_tabla_simbolos(frame_simbolos)
        panel_superior.add(frame_simbolos, minsize=350)

        # Panel inferior para las consolas de errores
        panel_errores = tk.PanedWindow(
            panel_principal, orient=tk.HORIZONTAL, bg=self.colores["fondo"],
            sashwidth=8, sashrelief=tk.RAISED, bd=0
        )

        frame_lex = self._crear_labelframe(panel_errores, "Errores Léxicos (Fase 1)", self.colores["panel2"], "#C43D5A")
        self.txt_errores_lex = self._crear_texto_con_scroll(
            frame_lex, bg=self.colores["err_lex"], fg="#6B2E3D",
            fuente=self.fuentes["texto"], wrap=tk.WORD, height=8
        )
        panel_errores.add(frame_lex, minsize=200)

        frame_sin = self._crear_labelframe(panel_errores, "Errores Sintácticos (Fase 2)", self.colores["panel2"], "#4E63C7")
        self.txt_errores_sin = self._crear_texto_con_scroll(
            frame_sin, bg=self.colores["err_sin"], fg="#32408B",
            fuente=self.fuentes["texto"], wrap=tk.WORD, height=8
        )
        panel_errores.add(frame_sin, minsize=200)

        frame_sem = self._crear_labelframe(panel_errores, "Errores Semánticos (Fase 3)", self.colores["panel2"], "#A35C15")
        self.txt_errores_sem = self._crear_texto_con_scroll(
            frame_sem, bg=self.colores["err_sem"], fg="#8A4A1C",
            fuente=self.fuentes["texto"], wrap=tk.WORD, height=8
        )
        panel_errores.add(frame_sem, minsize=200)

        panel_principal.add(panel_superior, minsize=360)
        panel_principal.add(panel_errores, minsize=150)

    def _configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure(
            "Treeview",
            background="#FFF9FC",
            fieldbackground="#FFF9FC",
            foreground=self.colores["texto"],
            font=self.fuentes["texto"],
            rowheight=28,
            bordercolor=self.colores["borde"],
            relief="flat"
        )

        estilo.configure(
            "Treeview.Heading",
            background="#EFC9D9",
            foreground="#4E3943",
            font=self.fuentes["heading"],
            relief="raised"
        )

        estilo.map(
            "Treeview",
            background=[("selected", "#EAB8CD")],
            foreground=[("selected", "#2F1F27")]
        )

        estilo.configure(
            "Vertical.TScrollbar",
            background=self.colores["scroll"],
            troughcolor=self.colores["scroll_trough"],
            bordercolor=self.colores["borde"],
            arrowcolor=self.colores["texto"],
            lightcolor=self.colores["scroll"],
            darkcolor=self.colores["scroll"]
        )

        estilo.map(
            "Vertical.TScrollbar",
            background=[("active", self.colores["scroll_hover"])]
        )

    def _crear_boton(self, padre, texto, comando, color, color_hover, fg):
        boton = tk.Button(
            padre, text=texto, command=comando, bg=color, fg=fg,
            font=self.fuentes["boton"], activebackground=color_hover,
            activeforeground=fg, relief=tk.RAISED, bd=4, padx=14, pady=6,
            cursor="hand2", highlightthickness=0
        )
        boton.bind("<Enter>", lambda e: boton.config(bg=color_hover))
        boton.bind("<Leave>", lambda e: boton.config(bg=color))
        return boton

    def _crear_labelframe(self, padre, texto, bg, fg=None):
        return tk.LabelFrame(
            padre, text=texto, font=self.fuentes["titulo"], bg=bg,
            fg=fg or self.colores["texto"], bd=2, relief=tk.GROOVE, padx=6, pady=6
        )

    def _crear_texto_con_scroll(self, padre, bg, fg, fuente, wrap=tk.WORD, height=None):
        contenedor = tk.Frame(padre, bg=padre.cget("bg"))
        contenedor.pack(fill=tk.BOTH, expand=True)

        texto = tk.Text(
            contenedor, font=fuente, bg=bg, fg=fg, insertbackground=fg,
            relief=tk.SUNKEN, bd=2, wrap=wrap, undo=True if wrap == tk.NONE else False, height=height
        )

        scroll = ttk.Scrollbar(contenedor, orient=tk.VERTICAL, command=texto.yview, style="Vertical.TScrollbar")
        texto.configure(yscrollcommand=scroll.set)

        texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        return texto

    def _crear_tabla_tokens(self, padre):
        columnas = ("linea", "col", "tipo", "valor")
        self.tabla = ttk.Treeview(padre, columns=columnas, show="headings", selectmode="browse")

        for col, txt, width, anchor in (
            ("linea", "Lin", 55, tk.CENTER),
            ("col", "Col", 80, tk.CENTER),
            ("tipo", "Tipo", 140, tk.CENTER),
            ("valor", "Valor", 180, tk.W)
        ):
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=width, anchor=anchor)

        scroll = ttk.Scrollbar(padre, orient=tk.VERTICAL, command=self.tabla.yview, style="Vertical.TScrollbar")
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _crear_tabla_simbolos(self, padre):
        """ Construye el Treeview para renderizar la Tabla de Símbolos """
        columnas = ("nombre", "tipo", "valor", "linea")
        self.tabla_simbolos_gui = ttk.Treeview(padre, columns=columnas, show="headings", selectmode="browse")

        for col, txt, width, anchor in (
            ("nombre", "Nombre ID", 110, tk.W),
            ("tipo", "Tipo Dato", 90, tk.CENTER),
            ("valor", "Valor Actual", 110, tk.CENTER),
            ("linea", "Línea Decl.", 75, tk.CENTER)
        ):
            self.tabla_simbolos_gui.heading(col, text=txt)
            self.tabla_simbolos_gui.column(col, width=width, anchor=anchor)

        scroll = ttk.Scrollbar(padre, orient=tk.VERTICAL, command=self.tabla_simbolos_gui.yview, style="Vertical.TScrollbar")
        self.tabla_simbolos_gui.configure(yscrollcommand=scroll.set)
        self.tabla_simbolos_gui.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos MiniLang", "*.mlng *.ming *.txt"), ("Todos", "*.*")]
        )
        if not ruta:
            return

        self.archivo_actual = ruta
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            self.txt_entrada.delete("1.0", tk.END)
            self.txt_entrada.insert(tk.END, contenido)
            self.raiz.title(f"Compilador MiniLang (Fases 1, 2 y 3) - {os.path.basename(ruta)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")

    def ejecutar_analisis(self):
        # 1. Limpiar componentes visuales (Garantiza el dinamismo)
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        for item in self.tabla_simbolos_gui.get_children():
            self.tabla_simbolos_gui.delete(item)

        for caja in (self.txt_errores_lex, self.txt_errores_sin, self.txt_errores_sem):
            caja.config(state=tk.NORMAL)
            caja.delete("1.0", tk.END)

        codigo = self.txt_entrada.get("1.0", tk.END)

        # 2. FASE 1: Análisis Léxico
        escanner = AnalizadorLexico()
        tokens, err_lexicos = escanner.analizar(codigo)

        contenido_salida = []
        for t in tokens:
            self.tabla.insert("", tk.END, values=(t.linea, f"{t.col_inicio}-{t.col_fin}", t.tipo, t.valor))
            contenido_salida.append(str(t))

        if err_lexicos:
            self.txt_errores_lex.insert(tk.END, "\n".join(str(err) for err in err_lexicos))
        else:
            self.txt_errores_lex.insert(tk.END, "0 Errores Léxicos.")
        self.txt_errores_lex.config(state=tk.DISABLED)

        # 3. FASE 3: Instanciar la Memoria Limpia
        semantico = AnalizadorSemantico()

        # 4. FASE 2: Análisis Sintáctico (Nutre la memoria semántica)
        adaptador = AdaptadorLexicoPLY(tokens)
        parser = AnalizadorSintactico(semantico)
        err_sintacticos = parser.analizar_sintaxis(adaptador)

        if err_sintacticos:
            self.txt_errores_sin.insert(tk.END, "\n".join(str(err) for err in err_sintacticos))
        else:
            self.txt_errores_sin.insert(tk.END, "OK - El programa es sintácticamente correcto.\n0 Errores Sintácticos.")
        self.txt_errores_sin.config(state=tk.DISABLED)

        # 5. Renderizado Dinámico de la Tabla de Símbolos en la Interfaz
        for nombre, simbolo in semantico.tabla_simbolos.items():
            val = simbolo.valor if simbolo.valor is not None else "NULL"
            self.tabla_simbolos_gui.insert("", tk.END, values=(simbolo.nombre, simbolo.tipo_dato, val, simbolo.linea))

        # Imprimir Resultados Semánticos en Consola Inferior
        if semantico.errores_semanticos:
            self.txt_errores_sem.insert(tk.END, "\n".join(str(err) for err in semantico.errores_semanticos))
        else:
            self.txt_errores_sem.insert(tk.END, "OK - El programa es semánticamente correcto.\n0 Errores Semánticos.")
        self.txt_errores_sem.config(state=tk.DISABLED)

        # 6. Exportación física de reportes (.out)
        self.guardar_salida(contenido_salida)
        
        base_nombre = os.path.splitext(self.archivo_actual)[0] if self.archivo_actual else "salida"
        semantico.exportar_tabla(f"{base_nombre}_tabla_simbolos.out")


    def guardar_salida(self, lineas_tokens):
        nombre_salida = os.path.splitext(self.archivo_actual)[0] + ".out" if self.archivo_actual else "salida.out"
        try:
            with open(nombre_salida, "w", encoding="utf-8") as f:
                f.write("\n".join(lineas_tokens))
        except Exception as e:
            messagebox.showerror("Error de Guardado", f"No se pudo crear el archivo .out: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazMiniLang(root)
    root.mainloop()