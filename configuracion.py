from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox, filedialog
from PIL import Image, ImageTk

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from libreria import *
import proveedor
from sqlqueries import QueriesSQLite
import datetime
from datetime import datetime
import sys
import os


class Configuracion(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.widgets()
        self.img_folder = "Imagenes"

    class ChoiceDialog(simpledialog.Dialog):
        def __init__(self, parent, title, options):
            self.options = options
            self.choice = None
            super().__init__(parent, title)

        def body(self, master):
            self.choice = tk.StringVar(value=self.options[1])  # Valor por defecto

            for option in self.options:
                rb = tk.Radiobutton(master, text=option, variable=self.choice, value=option)
                rb.pack(anchor=tk.W)

            return master

        def apply(self):
            self.result = self.choice.get()

    def ask_choice(self, parent, title, options):
        dialog = self.ChoiceDialog(parent, title, options)
        return dialog.result
    
    def widgets(self):
        """Configura los widgets de la interfaz.
        Crear la ventana principal y los widgets relacionados con la venta y visualizacion del modulo.
        """
        # Definicion y configuracion del LabelFrame. Lado Izquierdo
        self.labelframe = tk.LabelFrame(self, text="Configuracion", font=("Arial", 20, "bold"), bg=COLOR_FONDO)
        self.labelframe.place(x=20, y=20, width=250, height=560)

        btn_impuesto = tk.Button(self.labelframe, 
                                text="Impuesto/IVA/Tax", 
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.asignar_impuesto)
        btn_impuesto.place(x=10, y=20, width=220, height=40)

        btn_margen = tk.Button(self.labelframe, 
                                text="Margen de Ganancia", 
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.asignar_margen)
        btn_margen.place(x=10, y=70, width=220, height=40)

        btn_datos_empresa = tk.Button(self.labelframe, 
                                text="Datos de la Empresa", 
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.datos_empresa)
        btn_datos_empresa.place(x=10, y=120, width=220, height=40)

        btn_uso_margen_ganancia = tk.Button(self.labelframe, 
                                text="Uso del Margen de Ganancia", 
                                font=("Arial", 11, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.uso_margen_ganancia)
        btn_uso_margen_ganancia.place(x=10, y=170, width=220, height=40)

        btn_80_20_ventas = tk.Button(self.labelframe, 
                                text="80/20 V-Cliente", 
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.r80_20_vcliente)
        btn_80_20_ventas.place(x=10, y=220, width=220, height=40)

        btn_80_20_compras = tk.Button(self.labelframe, 
                                text="80/20 V-Producto", 
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.r80_20_vproducto)
        btn_80_20_compras.place(x=10, y=270, width=220, height=40)

        btn_80_20_clientes = tk.Button(self.labelframe, 
                                text="80/20 C-Proveedore", 
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.r80_20_cproveedor)
        btn_80_20_clientes.place(x=10, y=320, width=220, height=40)

        btn_80_20_proveedores = tk.Button(self.labelframe, 
                                text="80/20 C-Producto", 
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.r80_20_cproducto)    
        btn_80_20_proveedores.place(x=10, y=370, width=220, height=40)

        btn_80_20_productos = tk.Button(self.labelframe, 
                                text="Inventario", 
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.inventario)
        btn_80_20_productos.place(x=10, y=420, width=220, height=40)

        btn_edo_ganancias_perdidas = tk.Button(self.labelframe, 
                                text="Edo. Ganancias/Perdidas", 
                                font=("Arial", 12, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.edo_ganancias_perdidas)
        btn_edo_ganancias_perdidas.place(x=10, y=470, width=220, height=40)

        # Definicion y configuracion del LabelFrame. Lado Derecho
        treFrame = tk.Frame(self, bg=COLOR_BG_LISTAS)
        treFrame.place(x=280, y=20, width=800, height=560)

        scrol_y = ttk.Scrollbar(treFrame, orient="vertical")
        scrol_y.pack(side="right", fill="y")        

        scrol_x = ttk.Scrollbar(treFrame, orient="horizontal")
        scrol_x.pack(side="bottom", fill="x")

        # Definicion de las columnas
        self.columna_1 = "Cliente/Producto/Proveedor"
        self.columna_2 = "Total Ventas/Compras"

        # Definicion del Treeview
        self.tre = ttk.Treeview(treFrame, 
                        columns=(self.columna_1, self.columna_2), 
                        show="headings",
                        yscrollcommand=scrol_y.set, 
                        xscrollcommand=scrol_x.set, 
                        selectmode="browse",
                        height=40)
        
        self.tre.pack(expand=True, fill=tk.BOTH)

        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)

        # Definicion de los encabezados
        self.encabezado_1 = "Nombre de Cliente/Producto/Proveedor"
        self.encabezado_2 = "Total Ventas/Compras"

        # Configuracion de los Encabezados
        self.tre.heading(self.columna_1, text=self.encabezado_1)
        self.tre.heading(self.columna_2, text=self.encabezado_2)

        self.tre.column(self.columna_1, width=250, anchor=CENTER)
        self.tre.column(self.columna_2, width=150, anchor=CENTER)

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
        
    def asignar_impuesto(self):
        """Asigna el impuesto al modulo de ventas."""
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT * FROM impuesto"
            result = QueriesSQLite.execute_read_query(conn, query)
            self.impuesto = result[0][0]
            conn.close()
        except Exception as e:
            messagebox.showerror("Asignar_Impuesto - Error", f"Error al obtener el impuesto: {str(e)}")
            registrar_error(f"Asignar_Impuesto - Error al obtener el impuesto: {str(e)}")
            conn.close()
        while True:
            new_impuesto = simpledialog.askfloat("Asignar_Impuesto", "Ingrese el nuevo % de impuesto:", 
                                                initialvalue=self.impuesto)
            if new_impuesto is not None and new_impuesto > 0:
                try:
                    conn = QueriesSQLite.create_connection(DB_NAME)
                    data = (new_impuesto,)
                    query = f"UPDATE impuesto SET impuesto= ?"
                    QueriesSQLite.execute_query(conn, query, data)
                    conn.close()
                    messagebox.showinfo("Asignar_Impuesto - Informacion", "Impuesto actualizado correctamente")
                    #self.impuesto = new_impuesto
                    break
                except Exception as e:
                    messagebox.showerror("Asignar_Impuesto - Error", f"Error al actualizar el impuesto: {str(e)}")
                    registrar_error(f"Asignar_Impuesto - Error al actualizar el impuesto: {str(e)}")
                    conn.close()
            else:
                messagebox.showwarning("Asignar_Impuesto - Advertencia", "Por favor, ingrese un impuesto valido")
                return

    def asignar_margen(self):
        """Asigna el margen de ganancia al modulo de ventas."""
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT * FROM margen_ganancia"
            result = QueriesSQLite.execute_read_query(conn, query)
            self.margen = result[0][0]
            conn.close()
        except Exception as e:
            messagebox.showerror("Asignar_Margen - Error", f"Error al obtener el margen: {str(e)}")
            registrar_error(f"Asignar_Margen - Error al obtener el margen: {str(e)}")
            conn.close()
        while True:
            new_margen = simpledialog.askfloat("Asignar_Margen", "Ingrese el nuevo % de margen de ganancia:",
                                            initialvalue=self.margen)
            if new_margen is not None and new_margen > 0:
                try:
                    conn = QueriesSQLite.create_connection(DB_NAME)
                    data = (new_margen,)
                    query = f"UPDATE margen_ganancia SET margen_ganancia= ?"
                    QueriesSQLite.execute_query(conn, query, data)
                    conn.close()
                    messagebox.showinfo("Asignar_Margen - Informacion", "Margen actualizado correctamente")
                    #self.margen = new_margen
                    break
                except Exception as e:
                    messagebox.showerror("Asignar_Margen - Error", f"Error al actualizar el margen: {str(e)}")
                    registrar_error(f"Asignar_Margen - Error al actualizar el margen: {str(e)}")
                    conn.close()
            else:
                messagebox.showwarning("Asignar_Margen - Advertencia", "Por favor, ingrese un margen valido")
                return

    def datos_empresa(self):
        # Obtener los datos de la empresa seleccionada
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT * FROM configuracion"
            result = QueriesSQLite.execute_read_query(conn, query)
            if result:
                id = result[0][0]
                logo = result[0][1]
                nombre_actual = result[0][2]
                direccion_actual = result[0][3]
                telefono_actual = result[0][4]
                correo_actual = result[0][5]
                web_actual = result[0][6]
            else:
                id = ""
                logo = ""
                nombre_actual = ""
                direccion_actual = ""
                telefono_actual = ""
                correo_actual = ""
                web_actual = ""
            conn.close()
        except Exception as e:
            messagebox.showerror("Datos_Empresa - Error", f"Error al obtener los datos de la empresa: {str(e)}")
            registrar_error(f"Datos_Empresa - Error al obtener los datos de la empresa: {str(e)}")
            conn.close()        

        # Crear ventana emergente de modificar empresa
        top_modificar = tk.Toplevel()
        top_modificar.title("Datos de la Empresa")
        top_modificar.geometry("750x400+200+50")
        top_modificar.config(bg=COLOR_FONDO, highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
        top_modificar.resizable(False, False)
        top_modificar.transient(self.master)  # Ubicar la ventana modal sobre la principal
        top_modificar.grab_set()
        top_modificar.focus_set()
        top_modificar.lift()

        # Crear los campos de entrada para los nuevos datos y asignamos los valores actuales
        label_nombre_nuevo = tk.Label(top_modificar, text="Nombre: ", font=("Arial", 12, "bold"), bg=COLOR_FONDO)
        label_nombre_nuevo.place(x=20, y=20, width=80, height=25)
        entry_nombre_nuevo = tk.Entry(top_modificar, font=("Arial", 12))
        entry_nombre_nuevo.place(x=150, y=20, width=300, height=25)
        entry_nombre_nuevo.insert(0, nombre_actual)

        label_direccion_nuevo = tk.Label(top_modificar, text="Direccion: ", font=("Arial", 12, "bold"), bg=COLOR_FONDO)
        label_direccion_nuevo.place(x=20, y=60, width=80, height=25)
        entry_direccion_nuevo = tk.Entry(top_modificar, font=("Arial", 12))
        entry_direccion_nuevo.place(x=150, y=60, width=300, height=25)
        entry_direccion_nuevo.insert(0, direccion_actual)

        label_telefono_nuevo = tk.Label(top_modificar, text="Telefono: ", font=("Arial", 12, "bold"), bg=COLOR_FONDO)
        label_telefono_nuevo.place(x=20, y=100, width=80, height=25)
        entry_telefono_nuevo = tk.Entry(top_modificar, font=("Arial", 12))
        entry_telefono_nuevo.place(x=150, y=100, width=300, height=25)
        entry_telefono_nuevo.insert(0, telefono_actual)

        label_correo_nuevo = tk.Label(top_modificar, text="Correo: ", font=("Arial", 12, "bold"), bg=COLOR_FONDO)
        label_correo_nuevo.place(x=20, y=140, width=80, height=25)
        entry_correo_nuevo = tk.Entry(top_modificar, font=("Arial", 12))
        entry_correo_nuevo.place(x=150, y=140, width=300, height=25)
        entry_correo_nuevo.insert(0, correo_actual)

        label_web_nuevo = tk.Label(top_modificar, text="Web: ", font=("Arial", 12, "bold"), bg=COLOR_FONDO)
        label_web_nuevo.place(x=20, y=180, width=80, height=25)
        entry_web_nuevo = tk.Entry(top_modificar, font=("Arial", 12))
        entry_web_nuevo.place(x=150, y=180, width=300, height=25)
        entry_web_nuevo.insert(0, web_actual)

        # Frame para la imagen y el boton de cargar imagen
        self.frameimg = tk.Frame(top_modificar, 
                                bg="white", 
                                highlightbackground="gray", 
                                highlightcolor="gray", 
                                highlightthickness=1)
        self.frameimg.place(x=490, y=30, width=200, height=200)

        btn_image = tk.Button(top_modificar, 
                            text="Cargar Imagen", 
                            font=("Arial", 12, "bold"), 
                            bg=COLOR_BOTON, 
                            fg="white", 
                            cursor="hand2",
                            command=self.load_image)
        btn_image.place(x=520, y=260, width=150, height=40)

        def guardar_datos_empresa():
            """Guarda las modificaciones realizadas en la base de datos."""
            # Validar que todos los campos esten completos
            if not entry_nombre_nuevo.get() or not entry_direccion_nuevo.get() or not entry_telefono_nuevo.get() or not entry_correo_nuevo.get():
                messagebox.showerror("Guardar_Datos_Empresa - Error", "Todos los campos son obligatorios")
                return
            # Obtener los datos modificados
            nuevo_nombre = entry_nombre_nuevo.get()
            nueva_direccion = entry_direccion_nuevo.get()
            nuevo_telefono = entry_telefono_nuevo.get()
            nuevo_correo = entry_correo_nuevo.get()
            nueva_web = entry_web_nuevo.get()

            # Selecciona la imagen si existe, sino selecciona la imagen por defecto
            if hasattr(self, "image_path"):
                image_path = self.image_path
            else:
                image_path = (r"Imagenes\default_image.jpg")

            nuevo_logo = image_path

            try:
                conn = QueriesSQLite.create_connection(DB_NAME)
                query = "UPDATE configuracion SET nombre_empresa = ?, direccion_empresa = ?, telefono_empresa = ?, correo_empresa = ?, web_empresa = ?, logo_empresa = ? WHERE id = ?"
                data = (nuevo_nombre, nueva_direccion, nuevo_telefono, nuevo_correo, nueva_web, nuevo_logo, id)
                QueriesSQLite.execute_query(conn, query, data)
                conn.close()
                messagebox.showinfo("Guardar_Datos_Empresa - Informacion", "Datos de la empresa actualizados correctamente")
                top_modificar.destroy()                
            except Exception as e:
                messagebox.showerror("Guardar_Datos_Empresa - Error", f"Error al actualizar los datos de la empresa: {str(e)}")
                registrar_error(f"Guardar_Datos_Empresa - Error al actualizar los datos de la empresa: {str(e)}")
                conn.close()

        # Agregar una linea entre los campos y el boton de guardar
        tk.Label(top_modificar, text="", bg=COLOR_FONDO).grid(row=5, column=0, columnspan=2)

        # Botones de la ventana Modificar Cliente
        btn_guardar = tk.Button(top_modificar, 
                                text="Guardar Cambios", 
                                font=("Arial", 12, "bold"),
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=guardar_datos_empresa)
        btn_guardar.place(x=100, y=260, width=150, height=40)

        btn_cancelar = tk.Button(top_modificar, 
                                text="Cancelar", 
                                font=("Arial", 12, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=top_modificar.destroy)
        btn_cancelar.place(x=310, y=260, width=150, height=40)

        def cargar_logo_exixtente():
            file_path = logo
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
        
        cargar_logo_exixtente()

    def uso_margen_ganancia(self):
        choice = self.ask_choice(self, "Elige el status del uso del margen de ganancia", options=["Activo", "Inactivo"])
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "UPDATE configuracion SET uso_margen_ganancia = ? WHERE id = 1"
            data = (choice,)
            QueriesSQLite.execute_query(conn, query, data)
            conn.close()            
            messagebox.showinfo("Uso_Margen_Ganancia - Informacion", "Uso del margen de ganancia actualizado correctamente")
        except Exception as e:
            messagebox.showerror("Uso_Margen_Ganancia - Error", f"Error al actualizar el uso del margen de ganancia: {str(e)}")
            registrar_error(f"Uso_Margen_Ganancia - Error al actualizar el uso del margen de ganancia: {str(e)}")
            conn.close()

    def r80_20_vcliente(self):
        """Muestra un listado de ventas acumuladas por cliente."""
        try:
            # Conectar a la base de datos
            conn = QueriesSQLite.create_connection(DB_NAME)
            
            # Consulta SQL para obtener el acumulado de ventas por cliente
            query = """
            SELECT cliente, SUM(total) as total_ventas
            FROM ventas
            GROUP BY cliente
            ORDER BY total_ventas DESC
            """
            
            # Ejecutar la consulta
            result = QueriesSQLite.execute_read_query(conn, query)
            
            # Cerrar la conexión
            conn.close()
            
            # Limpiar el Treeview antes de insertar nuevos datos
            for item in self.tre.get_children():
                self.tre.delete(item)
            
            # Insertar los datos en el Treeview
            for row in result:
                cliente, total_ventas = row
                self.tre.insert("", "end", values=(cliente, f"{total_ventas:.2f}"))            
        
        except Exception as e:
            messagebox.showerror("r80_20_vcliente - Error", f"Error al obtener el acumulado de ventas por cliente: {e}")
            registrar_error(f"r80_20_vcliente - Error al obtener el acumulado de ventas por cliente: {e}")

    def r80_20_vproducto(self):
        """Muestra un listado de ventas acumuladas por producto."""
        try:
            # Conectar a la base de datos
            conn = QueriesSQLite.create_connection(DB_NAME)
            
            # Consulta SQL para obtener el acumulado de ventas por producto
            query = """
            SELECT articulo, SUM(cantidad) as total_ventas
            FROM ventas
            GROUP BY articulo
            ORDER BY total_ventas DESC
            """
            
            # Ejecutar la consulta
            result = QueriesSQLite.execute_read_query(conn, query)
            
            # Cerrar la conexión
            conn.close()
            
            # Limpiar el Treeview antes de insertar nuevos datos
            for item in self.tre.get_children():
                self.tre.delete(item)
            
            # Insertar los datos en el Treeview
            for row in result:
                producto, total_ventas = row
                self.tre.insert("", "end", values=(producto, f"{total_ventas}"))            
        
        except Exception as e:
            messagebox.showerror("r80_20_vproducto - Error", f"Error al obtener el acumulado de ventas por producto: {e}")
            registrar_error(f"r80_20_vproducto - Error al obtener el acumulado de ventas por producto: {e}")

    def r80_20_cproveedor(self):
        """Muestra un listado de compras acumuladas por proveedor."""
        try:
            # Conectar a la base de datos
            conn = QueriesSQLite.create_connection(DB_NAME)
            
            # Consulta SQL para obtener el acumulado de compras por proveedor
            query = """
            SELECT proveedor, SUM(total) as total_compras
            FROM pedidos
            GROUP BY proveedor
            ORDER BY total_compras DESC
            """
            
            # Ejecutar la consulta
            result = QueriesSQLite.execute_read_query(conn, query)
            
            # Cerrar la conexión
            conn.close()
            
            # Limpiar el Treeview antes de insertar nuevos datos
            for item in self.tre.get_children():
                self.tre.delete(item)
            
            # Insertar los datos en el Treeview
            for row in result:
                proveedor, total_compras = row
                self.tre.insert("", "end", values=(proveedor, f"{total_compras:.2f}"))            
        
        except Exception as e:
            messagebox.showerror("r80_20_cproveedor - Error", f"Error al obtener el acumulado de compras por proveedor: {e}")
            registrar_error(f"r80_20_cproveedor - Error al obtener el acumulado de compras por proveedor: {e}")

    def r80_20_cproducto(self):
        """Muestra un listado de pedidos acumuladas por producto."""
        try:
            # Conectar a la base de datos
            conn = QueriesSQLite.create_connection(DB_NAME)
            
            # Consulta SQL para obtener el acumulado de pedidos por producto
            query = """
            SELECT articulo, SUM(cantidad) as total_pedidos
            FROM pedidos
            GROUP BY articulo
            ORDER BY total_pedidos DESC
            """
            
            # Ejecutar la consulta
            result = QueriesSQLite.execute_read_query(conn, query)
            
            # Cerrar la conexión
            conn.close()
            
            # Limpiar el Treeview antes de insertar nuevos datos
            for item in self.tre.get_children():
                self.tre.delete(item)
            
            # Insertar los datos en el Treeview
            for row in result:
                producto, total_pedidos = row
                self.tre.insert("", "end", values=(producto, f"{total_pedidos}"))            
        
        except Exception as e:
            messagebox.showerror("r80_20_cproducto - Error", f"Error al obtener el acumulado de pedidos por producto: {e}")
            registrar_error(f"r80_20_cproducto - Error al obtener el acumulado de pedidos por producto: {e}")

    def inventario(self):
        """Muestra un listado de artículos y sus respectivos precios, costos y stock."""

        # Cargar datos del uso del margen de ganancia
        self.cargar_datos_margen()

        # Crear ventana de inventario
        ventana_inventario = tk.Toplevel()
        ventana_inventario.title("Inventario")
        ventana_inventario.geometry("1100x650+120+20")
        ventana_inventario.config(bg=COLOR_FONDO, highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
        ventana_inventario.resizable(False, False)
        ventana_inventario.transient(self.master)
        ventana_inventario.grab_set()
        ventana_inventario.focus_set()
        ventana_inventario.lift()

        label_inventario = tk.Label(ventana_inventario,
                                    text="Inventario",
                                    font=("Arial", 26, "bold"),
                                    bg=COLOR_FONDO)
        label_inventario.place(x=450, y=20)

        btn_frame = tk.Frame(ventana_inventario, bg=COLOR_FONDO)
        btn_frame.place(x=20, y=60, width=1060, height=60)

        # Checkbutton para filtrar productos con stock <= 5
        self.filtrar_stock = tk.BooleanVar(value=False)  # Variable para rastrear el estado del Checkbutton
        check_stock = tk.Checkbutton(btn_frame,
                                        text="Solo con Stock <= 5",
                                        font=("Arial", 12, "bold"),
                                        variable=self.filtrar_stock,
                                        command=self.actualizar_inventario,
                                        bg=COLOR_FONDO,
                                        fg="black")
        check_stock.pack(side="right", padx=10)

        # Checkbutton para filtrar productos inactivos
        self.filtrar_inactivos = tk.BooleanVar(value=False)  # Variable para rastrear el estado del Checkbutton
        check_inactivos = tk.Checkbutton(btn_frame,
                                        text="Solo Productos Inactivos",
                                        font=("Arial", 12, "bold"),
                                        variable=self.filtrar_inactivos,
                                        command=self.actualizar_inventario,
                                        bg=COLOR_FONDO,
                                        fg="black")
        check_inactivos.pack(side="right", padx=10)

        btn_inventario_pdf = tk.Button(btn_frame,
                                    text="Generar PDF",
                                    font=("Arial", 14, "bold"),
                                    bg=COLOR_BOTON,
                                    fg="white",
                                    cursor="hand2",
                                    command=self.inventario_pdf)
        btn_inventario_pdf.pack(side="left", padx=10)

        tree_frame = tk.Frame(ventana_inventario, bg="white")
        tree_frame.place(x=20, y=130, width=1060, height=500)

        scrol_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scrol_y.pack(side="right", fill="y")

        scrol_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        scrol_x.pack(side="bottom", fill="x")

        # Crear un estilo para el Treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 8))  # Configurar la fuente del Treeview

        # Definición del Treeview
        self.tree = ttk.Treeview(tree_frame,
                                columns=("nombre", "precio", "costo", "stock", "estado"),
                                show="headings",
                                yscrollcommand=scrol_y.set,
                                xscrollcommand=scrol_x.set,
                                selectmode="browse",
                                height=40)

        self.tree.pack(expand=True, fill=tk.BOTH)

        scrol_y.config(command=self.tree.yview)
        scrol_x.config(command=self.tree.xview)

        # Configuración de los Encabezados
        self.tree.heading("nombre", text="Nombre Artículo")
        self.tree.heading("precio", text="Precio")
        self.tree.heading("costo", text="Costo")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("estado", text="Estado")

        self.tree.column("nombre", width=250, anchor=CENTER)
        self.tree.column("precio", width=150, anchor=CENTER)
        self.tree.column("costo", width=150, anchor=CENTER)
        self.tree.column("stock", width=150, anchor=CENTER)
        self.tree.column("estado", width=150, anchor=CENTER)

        # Cargar los datos iniciales del inventario
        self.actualizar_inventario()

    def actualizar_inventario(self):
        """Actualiza el Treeview con los productos filtrados según el estado seleccionado."""
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)

            # Filtrar productos según el estado seleccionado en el Checkbutton
            if self.filtrar_inactivos.get():
                query = "SELECT articulo, precio, costo, stock, estado FROM articulos WHERE estado = 'Inactivo' ORDER BY articulo ASC"
                if self.filtrar_stock.get():
                    query = "SELECT articulo, precio, costo, stock, estado FROM articulos WHERE estado = 'Inactivo' AND stock <= 5 ORDER BY articulo ASC"
            else:
                query = "SELECT articulo, precio, costo, stock, estado FROM articulos WHERE estado = 'Activo' ORDER BY articulo ASC"
                if self.filtrar_stock.get():
                    query = "SELECT articulo, precio, costo, stock, estado FROM articulos WHERE estado = 'Activo' AND stock <= 5 ORDER BY articulo ASC"

            result = QueriesSQLite.execute_read_query(conn, query)

            # Limpiar el Treeview antes de insertar nuevos datos
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insertar los datos en el Treeview
            for row in result:
                articulo, precio, costo, stock, estado = row

                # Calcular el precio basado en el uso del margen de ganancia (si está activo)
                if self.uso_margen_ganancia.lower() == 'activo':
                    precio = costo / self.margen_ganancia

                self.tree.insert("", "end", values=(articulo, f"{precio:.2f}", f"{costo:.2f}", f"{stock}", estado))

        except Exception as e:
            messagebox.showerror("Inventario - Error", f"Error al obtener el inventario: {e}")
            registrar_error(f"Inventario - Error al obtener el inventario: {e}")

        finally:
            conn.close()

    def inventario_pdf(self):
        """Genera un PDF con el inventario de productos, manejando múltiples páginas."""

        # cargar los datos del margen de ganancia
        self.cargar_datos_margen()

        try:
            # Conectar a la base de datos y obtener los datos del inventario
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT articulo, precio, costo, stock FROM articulos ORDER BY articulo ASC"
            result = QueriesSQLite.execute_read_query(conn, query)
            conn.close()

            # Crear el archivo PDF
            pdf_filename = "inventario.pdf"
            c = canvas.Canvas(pdf_filename, pagesize=letter)

            # Configuración de márgenes y posiciones
            margin_left = 50
            margin_top = 750
            line_height = 20
            image_size = 100
            rows_per_page = 20  # Número de filas por página

            # Cargar los datos de la empresa
            self.cargar_datos_empresa()

            # Dibujar el logo de la empresa (si existe)
            if hasattr(self, 'empresa_logo') and os.path.exists(self.empresa_logo):
                c.drawImage(self.empresa_logo, margin_left, margin_top - image_size, width=image_size, height=image_size)

            # Título del reporte
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(colors.darkblue)
            c.drawCentredString(300, margin_top, "INVENTARIO DE PRODUCTOS ACTIVOS")

            # Información de la empresa
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 12)
            c.drawString(margin_left + image_size + 10, margin_top - 20, f"{self.empresa_nombre}")
            c.drawString(margin_left + image_size + 10, margin_top - 40, f"Dirección: {self.empresa_direccion}")
            c.drawString(margin_left + image_size + 10, margin_top - 60, f"Teléfono: {self.empresa_telefono}")
            c.drawString(margin_left + image_size + 10, margin_top - 80, f"Email: {self.empresa_email}")
            c.drawString(margin_left + image_size + 10, margin_top - 100, f"Web: {self.empresa_web}")

            # Línea separadora
            c.setLineWidth(0.5)
            c.setStrokeColor(colors.gray)
            c.line(margin_left, margin_top - 110, 550, margin_top - 110)

            # Crear la tabla con los datos del inventario
            data = [["Producto", "Precio", "Costo", "Stock"]]  # Encabezados de la tabla
            for row in result:
                articulo, precio, costo, stock = row

                # Calcular el precio basado en el uso del margen de ganancia (si esta activo)
                if self.uso_margen_ganancia.lower() == 'activo':
                    precio = costo / self.margen_ganancia
                    
                data.append([articulo, f"${precio:.2f}", f"${costo:.2f}", str(stock)])

            # Definir el ancho de las columnas
            col_widths = [200, 100, 100, 100]  # Ancho de cada columna en puntos (1 punto = 1/72 de pulgada)

            # Estilo de la tabla
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),  # Fondo azul para los encabezados
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto blanco para los encabezados
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinear todo al centro
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente en negrita para los encabezados
                ('FONTSIZE', (0, 0), (-1, 0), 12),  # Tamaño de fuente para los encabezados
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Espaciado inferior para los encabezados
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fondo beige para las filas de datos
                ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Líneas de la tabla
            ])

            # Dividir los datos en páginas
            total_rows = len(data)
            start_row = 0
            page_number = 1

            while start_row < total_rows:
                # Crear una nueva página
                if start_row > 0:
                    c.showPage()  # Crear una nueva página
                    margin_top = 750  # Reiniciar la posición vertical para la nueva página

                    # Dibujar el título y la información de la empresa en cada página
                    c.setFont("Helvetica-Bold", 18)
                    c.setFillColor(colors.darkblue)
                    c.drawCentredString(300, margin_top, "INVENTARIO DE PRODUCTOS")

                    c.setFillColor(colors.black)
                    c.setFont("Helvetica", 12)
                    c.drawString(margin_left + image_size + 10, margin_top - 20, f"{self.empresa_nombre}")
                    c.drawString(margin_left + image_size + 10, margin_top - 40, f"Dirección: {self.empresa_direccion}")
                    c.drawString(margin_left + image_size + 10, margin_top - 60, f"Teléfono: {self.empresa_telefono}")
                    c.drawString(margin_left + image_size + 10, margin_top - 80, f"Email: {self.empresa_email}")
                    c.drawString(margin_left + image_size + 10, margin_top - 100, f"Web: {self.empresa_web}")

                    # Línea separadora
                    c.setLineWidth(0.5)
                    c.setStrokeColor(colors.gray)
                    c.line(margin_left, margin_top - 110, 550, margin_top - 110)

                # Obtener los datos para la página actual
                end_row = min(start_row + rows_per_page, total_rows)
                page_data = data[start_row:end_row]

                # Crear la tabla para la página actual
                table = Table(page_data, colWidths=col_widths)
                table.setStyle(style)

                # Posicionar la tabla en el PDF
                table.wrapOn(c, 400, 200)
                table.drawOn(c, margin_left, margin_top - 250)

                # Agregar el número de página
                c.setFont("Helvetica", 10)
                c.drawString(500, 50, f"Página {page_number}")

                # Actualizar el contador de filas y páginas
                start_row = end_row
                page_number += 1

            # Guardar el PDF
            c.save()

            # Mostrar mensaje de éxito
            messagebox.showinfo("Inventario PDF", f"El archivo PDF '{pdf_filename}' ha sido generado correctamente.")

            # Abrir el PDF automáticamente
            os.startfile(os.path.abspath(pdf_filename))

        except Exception as e:
            messagebox.showerror("Inventario PDF - Error", f"Error al generar el PDF: {e}")
            registrar_error(f"Inventario PDF - Error al generar el PDF: {e}")

    def cargar_datos_empresa(self):
        """Carga los datos de la empresa desde la base de datos."""
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT * FROM configuracion"
            data = QueriesSQLite.execute_read_query(conn, query)
            conn.close()
            self.empresa_logo = data[0][1]
            self.empresa_nombre = data[0][2]
            self.empresa_direccion = data[0][3]
            self.empresa_telefono = data[0][4]
            self.empresa_email = data[0][5]
            self.empresa_web = data[0][6]
        except Exception as e:
            messagebox.showerror("Cargar_Datos_Empresa - Error", f"Error al cargar los datos de la empresa: {e}")
            registrar_error(f"Cargar_Datos_Empresa - Error al cargar los datos de la empresa: {e}")
            return

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

    def edo_ganancias_perdidas(self):
        """Muestra una ventana con la lista de ventas realizadas."""
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT * FROM ventas"
            ventas = QueriesSQLite.execute_read_query(conn, query)

            if ventas is None:
                messagebox.showwarning("Ver_Ventas - Advertencia", "No hay ventas realizadas")
                return

            query = "SELECT * FROM pedidos"
            pedidos = QueriesSQLite.execute_read_query(conn, query)
            
            if pedidos is None:
                messagebox.showwarning("Ver_Ventas - Advertencia", "No hay pedidos realizados")
                return

            query = "SELECT * FROM articulos"
            inventarios = QueriesSQLite.execute_read_query(conn, query)
            
            if inventarios is None:
                messagebox.showwarning("Ver_Ventas - Advertencia", "No hay productos realizados")
                return

            # Crear ventana de ventas realizadas
            ventana_edo_ganancias = tk.Toplevel()
            ventana_edo_ganancias.title("Estado de Ganancias y Perdidas")
            ventana_edo_ganancias.geometry("1100x650+120+20")
            ventana_edo_ganancias.config(bg=COLOR_FONDO, highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
            ventana_edo_ganancias.resizable(False, False)
            ventana_edo_ganancias.transient(self.master)
            ventana_edo_ganancias.grab_set()
            ventana_edo_ganancias.focus_set()
            ventana_edo_ganancias.lift()

            # Definir entry_fch_inicial y entry_fch_final como atributos de la clase
            self.entry_fch_inicial = tk.StringVar()
            self.entry_fch_final = tk.StringVar()

            # Función para filtrar las ventas y pedidos por fecha y producto
            def filtrar_datos():
                fch_inicial_str = self.entry_fch_inicial.get()
                fch_final_str = self.entry_fch_final.get()
                producto = entry_producto.get()

                # Validar las fechas
                if not validar_fechas(fch_inicial_str, fch_final_str):
                    return # Salir si las fechas no son válidas

                # Convertir las fechas de cadena a objetos datetime
                fch_inicial = datetime.strptime(fch_inicial_str, "%m-%d-%Y") if fch_inicial_str else None
                fch_final = datetime.strptime(fch_final_str, "%m-%d-%Y") if fch_final_str else None

                # Filtrar ventas por fecha y producto
                ventas_filtradas = [
                    venta for venta in ventas
                    if (not fch_inicial or datetime.strptime(venta[6], "%Y-%m-%d") >= fch_inicial) and
                    (not fch_final or datetime.strptime(venta[6], "%Y-%m-%d") <= fch_final) and
                    (not producto or producto.lower() in venta[2].lower())
                ]

                # Filtrar pedidos por fecha y producto
                pedidos_filtrados = [
                    pedido for pedido in pedidos
                    if (not fch_inicial or datetime.strptime(pedido[6], "%Y-%m-%d") >= fch_inicial) and
                    (not fch_final or datetime.strptime(pedido[6], "%Y-%m-%d") <= fch_final) and
                    (not producto or producto.lower() in pedido[2].lower())
                ]

                # Filtrar inventarios por fecha y producto
                inventarios_filtrados = [
                    inventario for inventario in inventarios
                    if (not producto or producto.lower() in inventario[1].lower())
                ]

                # Calcular totales
                total_ventas = sum(venta[5] for venta in ventas_filtradas)
                total_compras = sum(pedido[5] for pedido in pedidos_filtrados)
                total_inventario = sum((inventario[3] * inventario[4]) for inventario in inventarios_filtrados)

                # Calcular el balance
                total_balance = (total_inventario + total_ventas) - total_compras

                # Limpiar el Treeview antes de insertar nuevos datos
                for item in tree.get_children():
                    tree.delete(item)

                # Insertar los resultados en el Treeview                
                tree.insert("", "end", values=("Total Ventas", f"{total_ventas:.2f}"))
                tree.insert("", "end", values=("Total Inventario", f"{total_inventario:.2f}"))
                tree.insert("", "end", values=("Total Compras", f"{total_compras:.2f}"))
                tree.insert("", "end", values=("Total Balance", f"{total_balance:.2f}"))

            label_edo_ganancias = tk.Label(ventana_edo_ganancias, 
                                            text="Estado de Ganancias y Perdidas", 
                                            font=("Arial", 26, "bold"), 
                                            bg=COLOR_FONDO)
            label_edo_ganancias.place(x=300, y=20)

            # Crear el Frame para los filtros
            filtro_frame2 = tk.Frame(ventana_edo_ganancias, bg=COLOR_FONDO)
            filtro_frame2.place(x=20, y=60, width=1060, height=60)

            # Botón para seleccionar fecha inicial
            btn_fch_inicial = tk.Button(filtro_frame2, text="Fecha Inicial", font=("Arial", 12, "bold"), 
                                    bg=COLOR_BOTON, fg="white", cursor="hand2",
                                    command=lambda: self.entry_fch_inicial.set(datetime.strptime(seleccionar_fecha(ventana_edo_ganancias, "Seleccionar Fecha Inicial"), "%Y-%m-%d").strftime("%m-%d-%Y")))
            btn_fch_inicial.place(x=10, y=10, width=120, height=40)

            # Muestra la fecha inicial seleccionada en el Label
            fecha_inicial_view = tk.Label(filtro_frame2, 
                                        textvariable=self.entry_fch_inicial, 
                                        font=("Arial", 12, "bold"), 
                                        bg="white", 
                                        fg="black")
            fecha_inicial_view.place(x=140, y=10, width=120, height=40)            

            # Botón para seleccionar fecha final
            btn_fch_final = tk.Button(filtro_frame2, text="Fecha Final", font=("Arial", 12, "bold"), 
                                    bg=COLOR_BOTON, fg="white", cursor="hand2",
                                    command=lambda: self.entry_fch_final.set(datetime.strptime(seleccionar_fecha(ventana_edo_ganancias, "Seleccionar Fecha Final"), "%Y-%m-%d").strftime("%m-%d-%Y")))
            btn_fch_final.place(x=280, y=10, width=120, height=40)

            # Muestra la fecha final seleccionada en el Label
            fecha_final_view = tk.Label(filtro_frame2, 
                                        textvariable=self.entry_fch_final, 
                                        font=("Arial", 12, "bold"), 
                                        bg="white", 
                                        fg="black")
            fecha_final_view.place(x=410, y=10, width=120, height=40)

            label_producto = tk.Label(filtro_frame2, text="Producto: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
            label_producto.place(x=545, y=15)
            entry_producto = tk.Entry(filtro_frame2, font=("Arial", 14, "bold"), cursor="hand2")
            entry_producto.place(x=645, y=10, width=200, height=40)

            # Cargar el icono de filtrar
            self.icono_filtrar = ImageTk.PhotoImage(Image.open("Imagenes/icono_filtro.png").resize((30, 30)))
            
            boton_filtrar = tk.Button(filtro_frame2, 
                                    text="  Filtrar", 
                                    image=self.icono_filtrar,
                                    compound="left",
                                    font=("Arial", 14, "bold"),
                                    bg=COLOR_BOTON,
                                    fg="white", 
                                    cursor="hand2", 
                                    command=filtrar_datos)
            boton_filtrar.place(x=865, y=10, width=130, height=40)

            def limpiar_filtro():
                self.entry_fch_inicial.set("")  # Limpiar la fecha inicial
                self.entry_fch_final.set("")  # Limpiar la fecha final
                entry_producto.delete(0, "end")  # Limpiar el campo de entrada de producto
                tree.delete(*tree.get_children())  # Limpiar el Treeview

            # Cargar el icono de limpiar
            self.icono_limpiar = ImageTk.PhotoImage(Image.open("Imagenes/icono_limpiar2.png").resize((30, 30)))

            boton_limpiar = tk.Button(filtro_frame2, 
                                    image=self.icono_limpiar,
                                    compound="center",
                                    bg=COLOR_BOTON,
                                    fg="white", 
                                    cursor="hand2", 
                                    command=limpiar_filtro)
            boton_limpiar.place(x=1005, y=10, width=50, height=40)

            # Crear el Frame para el Treeview
            tree_frame2 = tk.Frame(ventana_edo_ganancias, bg="white")
            tree_frame2.place(x=20, y=120, width=1060, height=510)

            scrol_y = ttk.Scrollbar(tree_frame2, orient="vertical")
            scrol_y.pack(side="right", fill="y")

            scrol_x = ttk.Scrollbar(tree_frame2, orient="horizontal")
            scrol_x.pack(side="bottom", fill="x")

            # Definir las columnas del Treeview para mostrar los resultados
            tree = ttk.Treeview(tree_frame2, columns=("Concepto", "Total"), show="headings", yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set)
            tree.pack(expand=True, fill=tk.BOTH)

            scrol_y.config(command=tree.yview)
            scrol_x.config(command=tree.xview)

            # Configurar los encabezados
            tree.heading("Concepto", text="Concepto")
            tree.heading("Total", text="Total")

            # Configurar el ancho de las columnas
            tree.column("Concepto", width=500, anchor="center")
            tree.column("Total", width=500, anchor="center")

        except Exception as e:
            messagebox.showerror("Ver_Ventas_Realizadas - Error", f"Error al obtener las ventas y/o pedidos realizadas: {e}")
            registrar_error(f"Ver_Ventas_Realizadas - Error al obtener las ventas y/o pedidos realizadas: {e}")
            return        
    