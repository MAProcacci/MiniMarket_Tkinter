from re import I
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, PhotoImage
import threading
from PIL import Image, ImageTk
from libreria import *
from sqlqueries import QueriesSQLite
import sys
import os


class Inventario(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.conn = QueriesSQLite.create_connection(DB_NAME)
        self.cargar_datos_margen()
        self.widgets()
        self.articulos_combobox()
        self._cargar_articulos()
        self.timer_articulos = None        

        self.img_folder = "Fotos"
        if not os.path.exists(self.img_folder):
            os.makedirs(self.img_folder)

    def load_image(self):
        """Carga una imagen desde un archivo y la muestra en un Label."""
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            image = image.resize((200, 200), Image.LANCZOS)
            image_name = os.path.basename(file_path)
            image_save_path = os.path.join(self.img_folder, image_name)
            image.save(image_save_path)
            
            self.image_tk = ImageTk.PhotoImage(image)

            self.product_image = self.image_tk
            self.image_path = image_save_path

            img_label = tk.Label(self.frameimg, image=self.image_tk)
            img_label.place(x=0, y=0, width=200, height=200)

    def widgets(self):
        """Definicion y configuracion de los widgets. Entorno Grafico."""
        # Definicion y configuracion del Primer LabelFrame (Canvas). Lado Derecho
        canvas_articulos = tk.LabelFrame(self, 
                                        text="Articulos", 
                                        font=("Arial", 14, "bold"), 
                                        bg=COLOR_FONDO)
        canvas_articulos.place(x=300, y=10, width=780, height=580)

        self.canvas = tk.Canvas(canvas_articulos, bg=COLOR_FONDO)
        self.scrollbar = tk.Scrollbar(canvas_articulos, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_FONDO)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Definicion y configuracion del Segundo LabelFrame. Lado Izquierdo 1
        lblframe_buscar = tk.LabelFrame(self, 
                                        text="Buscar", 
                                        font=("Arial", 14, "bold"), 
                                        bg=COLOR_FONDO)
        lblframe_buscar.place(x=10, y=10, width=280, height=80)

        self.comboboxbuscar = ttk.Combobox(lblframe_buscar,
                                        font=("Arial", 12),
                                        cursor="hand2")
        self.comboboxbuscar.place(x=5, y=5, width=260, height=40)
        self.comboboxbuscar.bind("<<ComboboxSelected>>", self.on_combobox_select)
        self.comboboxbuscar.bind("<KeyRelease>", self.filtrar_articulos)

        # Definicion y configuracion del Tercer LabelFrame. Lado Izquierdo 2
        lblframe_seleccion = tk.LabelFrame(self, 
                                        text="Seleccion", 
                                        font=("Arial", 14, "bold"), 
                                        bg=COLOR_FONDO)
        lblframe_seleccion.place(x=10, y=95, width=280, height=190)

        self.label1 = tk.Label(lblframe_seleccion, 
                            text="Articulo: ",
                            font=("Arial", 12),
                            bg=COLOR_FONDO,
                            fg="white",
                            wraplength=300,
                            justify="left")
        self.label1.place(x=5, y=5)

        self.label2 = tk.Label(lblframe_seleccion, 
                            text="Precio: ",
                            font=("Arial", 12),
                            bg=COLOR_FONDO,
                            fg="white",
                            wraplength=300,
                            justify="left")
        self.label2.place(x=5, y=35) #y=40

        self.label3 = tk.Label(lblframe_seleccion, 
                            text="Costo: ",
                            font=("Arial", 12),
                            bg=COLOR_FONDO,
                            fg="white",
                            wraplength=300,
                            justify="left")
        self.label3.place(x=5, y=65) #y=70

        self.label4 = tk.Label(lblframe_seleccion, 
                            text="Stock: ",
                            font=("Arial", 12),
                            bg=COLOR_FONDO,
                            fg="white",
                            wraplength=300,
                            justify="left")
        self.label4.place(x=5, y=95) #y=100

        self.label5_texto = tk.Label(lblframe_seleccion, 
                            text="Estado: ",
                            font=("Arial", 12),
                            bg=COLOR_FONDO,
                            fg="white",
                            wraplength=300,
                            justify="left")
        self.label5_texto.place(x=5, y=125)

        self.label5_valor = tk.Label(lblframe_seleccion, 
                            text="",
                            font=("Arial", 12, "bold"),
                            bg=COLOR_FONDO,
                            fg="white",
                            wraplength=300,
                            justify="left")
        self.label5_valor.place(x=70, y=125)

        # Definicion y configuracion del Cuarto LabelFrame. Lado Izquierdo 3
        lblframe_botones = tk.LabelFrame(self, 
                                        text="Opciones", 
                                        font=("Arial", 14, "bold"), 
                                        bg=COLOR_FONDO)
        lblframe_botones.place(x=10, y=285, width=280, height=300)

        # Cargar iconos de los botones
        self.icono_agregar = ImageTk.PhotoImage(Image.open("Imagenes/icono_agregar_item2.png").resize((30, 30)))
        self.icono_modificar = ImageTk.PhotoImage(Image.open("Imagenes/icono_editar_item2.png").resize((30, 30)))
        self.icono_eliminar = ImageTk.PhotoImage(Image.open("Imagenes/icono_eliminar_item2.png").resize((30, 30)))
        self.icono_refrescar = ImageTk.PhotoImage(Image.open("Imagenes/icono_refrescar2.png").resize((30, 30)))

        btn1 = tk.Button(lblframe_botones, 
                    text="  Agregar",
                    image=self.icono_agregar,
                    compound="left",
                    font=("Arial", 14, "bold"),
                    bg=COLOR_BOTON,
                    fg="white",
                    cursor="hand2",
                    command=self.agregar_articulo)
        btn1.place(x=20, y=20, width=180, height=40)

        btn2 = tk.Button(lblframe_botones, 
                    text="  Editar",
                    image=self.icono_modificar,
                    compound="left",
                    font=("Arial", 14, "bold"),
                    bg=COLOR_BOTON,
                    fg="white",
                    cursor="hand2",
                    command=self.modificar_articulo)
        btn2.place(x=20, y=80, width=180, height=40)

        btn3 = tk.Button(lblframe_botones, 
                    text="  Eliminar",
                    image=self.icono_eliminar,
                    compound="left",
                    font=("Arial", 14, "bold"),
                    bg=COLOR_BOTON,
                    fg="white",
                    cursor="hand2",
                    command=self.eliminar_articulo)
        btn3.place(x=20, y=140, width=180, height=40)

        btn4 = tk.Button(lblframe_botones, 
                    text="  Refrescar",
                    image=self.icono_refrescar,
                    compound="left",
                    font=("Arial", 14, "bold"),
                    bg=COLOR_BOTON,
                    fg="white",
                    cursor="hand2",
                    command=self._cargar_articulos)
        btn4.place(x=20, y=200, width=180, height=40)

    def articulos_combobox(self):
        """Actualiza el combobox de articulos."""
        query = "SELECT articulo FROM articulos"
        result = QueriesSQLite.execute_read_query(self.conn, query)
        self.articulos = [row[0] for row in result]
        self.comboboxbuscar['values'] = self.articulos

    def agregar_articulo(self):
        """Muestra la ventana de agregar articulo."""
        top = tk.Toplevel(self)
        top.title("Agregar Articulo")
        top.geometry("700x400+200+50")
        top.config(bg=COLOR_FONDO, highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
        top.resizable(False, False)

        # Este bloque hace que la ventana se mantenga en la vista por encima de la ventana principal
        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

        # Seccion para ingresar los datos del articulo
        tk.Label(top, 
                text="Articulo: ", 
                font=("Arial", 12, "bold"), 
                bg=COLOR_FONDO).place(x=20, y=20, width=80, height=25)
        entry_articulo = tk.Entry(top, font=("Arial", 12, "bold"))
        entry_articulo.place(x=120, y=20, width=250, height=30)

        tk.Label(top, 
                text="Precio: ", 
                font=("Arial", 12, "bold"), 
                bg=COLOR_FONDO).place(x=20, y=60, width=80, height=25)
        entry_precio = tk.Entry(top, font=("Arial", 12, "bold"))
        entry_precio.place(x=120, y=60, width=250, height=30)

        tk.Label(top, 
                text="Costo: ", 
                font=("Arial", 12, "bold"), 
                bg=COLOR_FONDO).place(x=20, y=100, width=80, height=25)
        entry_costo = tk.Entry(top, font=("Arial", 12, "bold"))
        entry_costo.place(x=120, y=100, width=250, height=30)

        tk.Label(top, 
                text="Stock: ", 
                font=("Arial", 12, "bold"), 
                bg=COLOR_FONDO).place(x=20, y=140, width=80, height=25)
        entry_stock = tk.Entry(top, font=("Arial", 12, "bold"))
        entry_stock.place(x=120, y=140, width=250, height=30)

        tk.Label(top, 
                text="Estado: ", 
                font=("Arial", 12, "bold"), 
                bg=COLOR_FONDO).place(x=20, y=180, width=80, height=25)
        #entry_estado = tk.Entry(top, font=("Arial", 12, "bold"))
        # Cambia la creación de entry_estado a un Combobox
        entry_estado = ttk.Combobox(top, 
                                    font=("Arial", 12, "bold"), 
                                    values=['Activo', 'Inactivo'], 
                                    state='readonly',
                                    cursor="hand2")
        entry_estado.current(0)  # Establece 'Activo' como valor predeterminado
        entry_estado.place(x=120, y=180, width=250, height=30)

        # Frame para la imagen y el boton de cargar imagen
        self.frameimg = tk.Frame(top, 
                                bg="white", 
                                highlightbackground="gray", 
                                highlightcolor="gray", 
                                highlightthickness=1)
        self.frameimg.place(x=440, y=30, width=200, height=200)

        btn_image = tk.Button(top, 
                            text="Cargar Imagen", 
                            font=("Arial", 12, "bold"), 
                            bg=COLOR_BOTON, 
                            fg="white", 
                            cursor="hand2",
                            command=self.load_image)
        btn_image.place(x=470, y=260, width=150, height=40)

        def guardar():
            articulo = entry_articulo.get()
            precio = entry_precio.get()
            costo = entry_costo.get()
            stock = entry_stock.get()
            estado = entry_estado.get()

            if not articulo or not precio or not costo or not stock or not estado:
                messagebox.showwarning("Agregar Articulo - Advertencia", "Por favor, complete todos los campos")
                return            

            try:
                precio = float(precio)
                costo = float(costo)
                stock = int(stock)

                if precio < 0 or costo < 0 or stock < 0:
                    messagebox.showwarning("Agregar Articulo - Advertencia", "Por favor, ingrese números positivos para precio, costo y stock")
                    return
            except ValueError:
                messagebox.showwarning("Agregar Articulo - Advertencia", "Por favor, ingrese valores numéricos para precio, costo y stock")
                return

            # Selecciona la imagen si existe, sino selecciona la imagen por defecto
            if hasattr(self, "image_path"):
                image_path = self.image_path
            else:
                image_path = (r"Imagenes\default_image.jpg")

            try:
                query = "INSERT INTO articulos (articulo, precio, costo, stock, estado, image_path) VALUES (?, ?, ?, ?, ?, ?)"
                data = (articulo, precio, costo, stock, estado, image_path)
                QueriesSQLite.execute_query(self.conn, query, data)
                messagebox.showinfo("Agregar Articulo - Exitoso", "Articulo agregado exitosamente")
                top.destroy()
                self.cargar_articulo()
                self.articulos_combobox()
            except Exception as e:
                messagebox.showerror("Agregar Articulo - Error", f"Error: Sin conexion a la base de datos. {e}")
                registrar_error(f"Agregar Articulo - Error: Sin conexion a la base de datos. {e}")

        btn_guardar = tk.Button(top, 
                            text="Guardar", 
                            font=("Arial", 12, "bold"), 
                            bg=COLOR_BOTON, 
                            fg="white", 
                            cursor="hand2",
                            command=guardar)
        btn_guardar.place(x=50, y=260, width=150, height=40)

        btn_cancelar = tk.Button(top, 
                                text="Cancelar", 
                                font=("Arial", 12, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white", 
                                cursor="hand2",
                                command=top.destroy)
        btn_cancelar.place(x=260, y=260, width=150, height=40)

    def cargar_articulo(self, filtro = None, categoria = None):
        """Carga los articulos en el canvas."""
        self.after(0, self._cargar_articulos, filtro, categoria)

    def _cargar_articulos(self, filtro = None, categoria = None):
        """Carga los articulos en el canvas.        
        :param filtro: Filtro a aplicar a los articulos
        :param categoria: Categoría a aplicar a los articulos
        :return: None
        """
        self.cargar_datos_margen()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        query = "SELECT articulo, precio, costo, image_path FROM articulos"
        data = []

        if filtro:
            query += " WHERE articulo LIKE ?"
            data.append(f"%{filtro}%")
        
        result = QueriesSQLite.execute_read_query(self.conn, query, data)
        self.row = 0
        self.column = 0

        for articulo, precio, costo, image_path in result:
            if self.uso_margen_ganancia.lower() == 'activo':
                precio = costo / self.margen_ganancia
            self.mostrar_articulo(articulo, precio, image_path)
            #self.row += 1
            #self.column += 1

    def mostrar_articulo(self, articulo, precio, image_path):
        """Muestra un articulo en el canvas.        
        :param articulo: Articulo a mostrar
        :param precio: Precio del articulo
        :param image_path: Ruta de la imagen del articulo
        :return: None
        """
        article_frame = tk.Frame(self.scrollable_frame, bg="white", relief="solid", borderwidth=1)
        article_frame.grid(row=self.row, column=self.column, padx=10, pady=10)

        if image_path and os.path.exists(image_path):
            image = Image.open(image_path)
            image = image.resize((150, 150), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            label_image = tk.Label(article_frame, image=photo)
            label_image.image = photo
            label_image.pack(expand=True, fill=tk.BOTH)

            label_nombre = tk.Label(article_frame, 
                                    text=articulo, 
                                    bg="white", 
                                    anchor="w", 
                                    wraplength=150, 
                                    font=("Arial", 10, "bold"))
            label_nombre.pack(side="top", fill=tk.X)

            label_precio = tk.Label(article_frame, 
                                    text=f"Precio: ${precio:.2f}", 
                                    bg="white", 
                                    anchor="w", 
                                    wraplength=150, 
                                    font=("Arial", 8, "bold"))
            label_precio.pack(side="bottom", fill=tk.X)
        else:
            label_image = tk.Label(article_frame, text="Imagen no disponible", font=("Arial", 10, "bold"))
            label_image.pack(side="top", fill=tk.X)

        self.column += 1
        if self.column > 3:
            self.column = 0
            self.row += 1

    def on_combobox_select(self, event):
        """Actualiza el label con los datos del articulo seleccionado.
        :param event: Evento que llama a la funcion
        :return: None
        """
        self.actualizar_label()

    def actualizar_label(self, event=None):
        """Actualiza el label con los datos del articulo seleccionado.
        :param event: Evento que llama a la funcion
        :return: None
        """
        articulo_seleccionado = self.comboboxbuscar.get()

        try:
            query = "SELECT articulo, precio, costo, stock, estado FROM articulos WHERE articulo = ?"
            data = (articulo_seleccionado,)
            result = QueriesSQLite.execute_read_query(self.conn, query, data)
            if result is not None:
                articulo, precio, costo, stock, estado = result[0]
                if self.uso_margen_ganancia.lower() == 'activo':
                    precio = costo / self.margen_ganancia
                self.label1.config(text=f"Articulo: {articulo}")
                self.label2.config(text=f"Precio: ${precio:.2f}")
                self.label3.config(text=f"Costo: ${costo:.2f}")
                self.label4.config(text=f"Stock: {stock}")
                self.label5_valor.config(text=estado)
            
                if estado == "Activo":
                    self.label5_valor.config(fg="green", bg="white")
                elif estado == "Inactivo":
                    self.label5_valor.config(fg="red", bg="white")
                else:
                    self.label5_valor.config(fg="white", bg=COLOR_FONDO)
            else:
                self.label1.config(text="Articulo: no encontrado")
                self.label2.config(text="Precio: N/A")
                self.label3.config(text="Costo: N/A")
                self.label4.config(text="Stock: N/A")
                self.label5_valor.config(text="N/A", fg="white")

        except Exception as e:
            messagebox.showerror("Actualizar_Label - Error", f"Error al obtener los datos de los articulos: {e}")
            registrar_error(f"Actualizar_Label - Error al obtener los datos de los articulos: {e}")

    def filtrar_articulos(self, event):
        """Filtrar los articulos en base a lo que se escribe en el combobox.
        :param event: Evento que llama a la funcion
        :return: None
        """
        if self.timer_articulos:
            self.timer_articulos.cancel()
            self.timer_articulos = None
        self.timer_articulos = threading.Timer(0.5, self._filtrar_articulos)
        self.timer_articulos.start()

    def _filtrar_articulos(self):
        """Filtrar los articulos en base a lo que se escribe en el combobox.
        :return: None
        """
        typed = self.comboboxbuscar.get()

        if typed == "":
            data = self.articulos
        else:
            data = [item for item in self.articulos if typed.lower() in item.lower()]

        if data:
            self.comboboxbuscar['values'] = data
            self.comboboxbuscar.event_generate("<Down>")
        else:
            self.comboboxbuscar['values'] = ["No se encontraron resultados"]
            self.comboboxbuscar.event_generate("<Down>")

        self.cargar_articulo(filtro=typed)

    def modificar_articulo(self):
        """Muestra una ventana para modificar un articulo.
        :return: None
        """
        selected_articulo = self.comboboxbuscar.get()
        if not selected_articulo:
            messagebox.showwarning("Modificar Articulo - Advertencia", "Por favor, seleccione un articulo a modificar")
            return
        
        query = "SELECT articulo, precio, costo, stock, estado, image_path FROM articulos WHERE articulo = ?"
        data = (selected_articulo,)
        result = QueriesSQLite.execute_read_query(self.conn, query, data)
        if not result:
            messagebox.showwarning("Modificar Articulo - Advertencia", "El articulo seleccionado no existe")
            return

        top = tk.Toplevel(self)
        top.title("Modificar Articulo")
        top.geometry("700x400+200+50")
        top.config(bg=COLOR_FONDO, highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
        top.resizable(False, False)

        # Este bloque hace que la ventana se mantenga en la vista por encima de la ventana principal
        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()
        
        (articulo, precio, costo, stock, estado, image_path) = result[0]

        tk.Label(top, 
                text="Articulo: ", 
                font=("Arial", 12, "bold"), 
                bg=COLOR_FONDO).place(x=20, y=20, width=80, height=25)
        entry_articulo = tk.Entry(top, font=("Arial", 12, "bold"))        
        entry_articulo.place(x=120, y=20, width=250, height=30)
        entry_articulo.insert(0, articulo)

        tk.Label(top, 
                text="Precio: ", 
                font=("Arial", 12, "bold"),
                bg=COLOR_FONDO).place(x=20, y=60, width=80, height=25)
        entry_precio = tk.Entry(top, font=("Arial", 12, "bold"))
        entry_precio.place(x=120, y=60, width=250, height=30)
        entry_precio.insert(0, precio)

        tk.Label(top, 
                text="Costo: ", 
                font=("Arial", 12, "bold"),
                bg=COLOR_FONDO).place(x=20, y=100, width=80, height=25) 
        entry_costo = tk.Entry(top, font=("Arial", 12, "bold"))
        entry_costo.place(x=120, y=100, width=250, height=30)
        entry_costo.insert(0, costo)

        tk.Label(top, 
                text="Stock: ", 
                font=("Arial", 12, "bold"),
                bg=COLOR_FONDO).place(x=20, y=140, width=80, height=25)
        entry_stock = tk.Entry(top, font=("Arial", 12, "bold"))
        entry_stock.place(x=120, y=140, width=250, height=30)
        entry_stock.insert(0, stock)

        tk.Label(top, 
                text="Estado: ", 
                font=("Arial", 12, "bold"),
                bg=COLOR_FONDO).place(x=20, y=180, width=80, height=25)
        #entry_estado = tk.Entry(top, font=("Arial", 12, "bold"))
        # Cambia la creación de entry_estado a un Combobox
        entry_estado = ttk.Combobox(top, 
                                    font=("Arial", 12, "bold"), 
                                    values=['Activo', 'Inactivo'], 
                                    cursor="hand2")
        #entry_estado.current(0)  # Establece 'Activo' como valor predeterminado
        entry_estado.place(x=120, y=180, width=250, height=30)
        entry_estado.insert(0, estado)
        entry_estado.config(state="readonly")

        self.frameimg = tk.Frame(top, 
                                bg="white", 
                                highlightbackground="gray", 
                                highlightcolor="gray", 
                                highlightthickness=1)
        self.frameimg.place(x=440, y=30, width=200, height=200)

        if image_path and os.path.exists(image_path):
            image = Image.open(image_path)
            image = image.resize((200, 200), Image.LANCZOS)
            self.image_product = ImageTk.PhotoImage(image)
            self.image_path = image_path
            img_label = tk.Label(self.frameimg, image=self.image_product)
            img_label.pack(expand=True, fill=tk.BOTH)

        btn_imagen = tk.Button(top,
                               text="Cargar Imagen",
                               font=("Arial", 12, "bold"),
                               cursor="hand2",
                               command=self.load_image)
        btn_imagen.place(x=470, y=260, width=150, height=40)

        # Función para guardar los cambios
        def guardar_cambios():
            nuevo_articulo = entry_articulo.get()
            precio = float(entry_precio.get())
            costo = float(entry_costo.get())
            stock = int(entry_stock.get())
            estado = entry_estado.get()

            if not nuevo_articulo or not precio or not costo or not stock or not estado:
                messagebox.showwarning("Modificar Articulo - Advertencia", "Por favor, complete todos los campos.")
                return

            try:
                precio = float(precio)
                costo = float(costo)
                stock = int(stock)

                if precio < 0 or costo < 0 or stock < 0:
                    messagebox.showwarning("Modificar Articulo - Advertencia", "Por favor, ingrese números positivos para precio, costo y stock")
                    return
            except ValueError:
                messagebox.showwarning("Modificar Articulo - Advertencia", "Por favor, ingrese números validos para precio, costo y stock.")
                return

            if hasattr(self, "image_path"):
                image_path = self.image_path
            else:
                image_path = (r"Imagenes\default_image.jpg")

            query = "UPDATE articulos SET articulo = ?, precio = ?, costo = ?, stock = ?, estado = ?, image_path = ? WHERE articulo = ?"
            data = (nuevo_articulo, precio, costo, stock, estado, image_path, selected_articulo)
            QueriesSQLite.execute_query(self.conn, query, data)
            
            self.articulos_combobox()
            self.actualizar_label()
            self.after(0, lambda: self.cargar_articulo(filtro=nuevo_articulo))
            top.destroy()
            messagebox.showinfo("Modificar Articulo - Exito", "Articulo modificado exitosamente.")

        btn_guardar = tk.Button(top, 
                            text="Guardar", 
                            font=("Arial", 12, "bold"), 
                            bg=COLOR_BOTON, 
                            fg="white", 
                            cursor="hand2",
                            command=guardar_cambios)
        btn_guardar.place(x=50, y=260, width=150, height=40)

        btn_cancelar = tk.Button(top, 
                                text="Cancelar", 
                                font=("Arial", 12, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2",
                                command=top.destroy)
        btn_cancelar.place(x=260, y=260, width=150, height=40)

    def eliminar_articulo(self):        
        """
        Función para eliminar un articulo
        """        
        selected_articulo = self.comboboxbuscar.get()
        
        if not selected_articulo:
            messagebox.showwarning("Eliminar Articulo - Advertencia", "Por favor, seleccione un articulo para eliminar")
            return
        
        # Verificar si el articulo existe
        query = "SELECT articulo, image_path FROM articulos WHERE articulo = ?"
        data = (selected_articulo,)
        result = QueriesSQLite.execute_read_query(self.conn, query, data)
        
        if not result:
            messagebox.showwarning("Eliminar Articulo - Advertencia", "El articulo seleccionado no existe")
            return
        
        # Crear ventana de confirmación personalizada
        confirm_window = tk.Toplevel(self)
        confirm_window.title("Confirmar Eliminacion")
        confirm_window.geometry("400x250+500+300")
        confirm_window.config(bg=COLOR_FONDO, highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
        confirm_window.resizable(False, False)
        
        # Hacer la ventana modal
        confirm_window.transient(self)
        confirm_window.grab_set()
        
        # Mensaje de confirmación
        tk.Label(confirm_window, 
                text="¿Esta seguro que desea eliminar\nel siguiente articulo?",
                justify="center",
                font=("Arial", 14, "bold"),
                bg=COLOR_FONDO,
                wraplength=350).pack(pady=20)
                
        tk.Label(confirm_window, 
                text=selected_articulo,
                font=("Arial", 14, "bold"),
                fg="red",
                bg="white").pack(pady=10)
                
        tk.Label(confirm_window,
                text="Esta accion no se puede deshacer",
                font=("Arial", 10, "bold"),
                fg="red",
                bg="white").pack(pady=5)        
        
        def confirmar_eliminacion():
            confirm_window.destroy()
            try:
                # Obtener la ruta de la imagen antes de eliminar
                image_path = result[0][1]
                
                # Eliminar el artículo de la base de datos
                query = "DELETE FROM articulos WHERE articulo = ?"
                QueriesSQLite.execute_query(self.conn, query, data)
                
                # Eliminar la imagen asociada si existe y no es la imagen por defecto
                if image_path and os.path.exists(image_path) and "default_image" not in image_path:
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        messagebox.showerror("Eliminar Articulo - Error", 
                                            f"Error al eliminar la imagen del articulo: {e}")
                        registrar_error(f"Eliminar Articulo - Error al eliminar la imagen del articulo: {e}")
                
                # Actualizar la interfaz
                self.comboboxbuscar.set('')  # Limpiar el combobox
                self.articulos_combobox()    # Actualizar lista de artículos
                self.cargar_articulo()       # Recargar la vista de artículos
                
                # Limpiar las etiquetas de información
                self.label1.config(text="Articulo: ")
                self.label2.config(text="Precio: ")
                self.label3.config(text="Costo: ")
                self.label4.config(text="Stock: ")
                self.label5_valor.config(text="", fg="white", bg=COLOR_FONDO)
                
                messagebox.showinfo("Eliminar Articulo - Exito", 
                                  f"El articulo '{selected_articulo}' ha sido eliminado exitosamente")
                
            except Exception as e:
                messagebox.showerror("Eliminar Articulo - Error", f"Error al eliminar el articulo: {e}")
                registrar_error(f"Eliminar Articulo - Error al eliminar articulo: {e}")
        
        # Botones de confirmación
        tk.Button(confirm_window,
                 text="Si, Eliminar",
                 font=("Arial", 12, "bold"),
                 bg="red",
                 fg="white",
                 width=15,
                 cursor="hand2",
                 command=confirmar_eliminacion).place(x=20, y=180, width=150, height=40)
                 
        tk.Button(confirm_window,
                 text="Cancelar",
                 font=("Arial", 12, "bold"),
                 bg=COLOR_BOTON,
                 fg="white",
                 width=15,
                 cursor="hand2",
                 command=confirm_window.destroy).place(x=220, y=180, width=150, height=40)

    def cargar_datos_margen(self):
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT * FROM margen_ganancia"
            result1 = QueriesSQLite.execute_read_query(conn, query)
            
            if result1 is None:
                messagebox.showwarning("Cargar_Datos_Margen - Advertencia", "No hay datos del margen de ganancia")
                return
            
            self.margen_ganancia = (100 - result1[0][0]) / 100
            
            try:
                conn = QueriesSQLite.create_connection(DB_NAME)
                query = "SELECT * FROM configuracion"
                result2 = QueriesSQLite.execute_read_query(conn, query)
                if result2 is None:
                    messagebox.showwarning("Cargar_Datos_Margen - Advertencia", "No hay datos de 'uso_margen_ganancia'")
                    return
                self.uso_margen_ganancia = result2[0][7]                

            except Exception as e:
                messagebox.showerror("Cargar_Datos_Margen - Error", f"Error al cargar los datos de 'uso_margen_ganancia': {e}")
                registrar_error(f"Cargar_Datos_Margen - Error al cargar los datos de 'uso_margen_ganancia': {e}")

        except Exception as e:
            messagebox.showerror("Cargar_Datos_Margen - Error", f"Error al cargar los datos del margen de ganancia: {e}")
            registrar_error(f"Cargar_Datos_Margen - Error al cargar los datos del margen de ganancia: {e}")