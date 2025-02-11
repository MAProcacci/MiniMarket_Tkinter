from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog, filedialog
import threading
from PIL import Image, ImageTk
from libreria import *
from sqlqueries import QueriesSQLite
import sys
import os
import datetime
from datetime import datetime



class Pedidos(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.nro_factura = ""
        self.productos_seleccionados = [] 
        self.widgets()
        self.cargar_proveedores()
        self.cargar_productos()
        self.timer_proveedor = None
        self.timer_producto = None
    

    def cargar_proveedores(self):
        """Metodo para cargar los proveedores
        :return: lista de proveedores
        """
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT nombre FROM proveedores"
            result = QueriesSQLite.execute_read_query(conn, query)
            self.proveedores = [row[0] for row in result]
            self.entry_proveedor['values'] = self.proveedores            
            return result
        except Exception as e:
            messagebox.showerror("Cargar_Proveedores - Error", f"Error al cargar los proveedores: {e}")
            registrar_error(f"Cargar_Proveedores - Error al cargar los proveedores: {e}")
            return []

    def filtrar_proveedores(self, event):
        """Metodo para filtrar los proveedores
        :param event: evento que activa el filtro
        """
        if self.timer_proveedor:
            self.timer_proveedor.cancel()
        self.timer_proveedor = threading.Timer(0.5, self._filtrar_proveedores)
        self.timer_proveedor.start()

    def _filtrar_proveedores(self):
        """Metodo interno para filtrar los proveedores
        :return: None
        """
        self.cargar_proveedores()
        type_proveedor = self.entry_proveedor.get()

        if type_proveedor == "":
            data = self.proveedores
        else:
            data = [item for item in self.proveedores if type_proveedor.lower() in item.lower()]

        if data:
            self.entry_proveedor['values'] = data
            self.entry_proveedor.event_generate("<Down>")
        else:
            self.entry_proveedor['values'] = ["No se encontraron resultados"]
            self.entry_proveedor.event_generate("<Down>")
            self.entry_proveedor.delete(0, tk.END)

    def cargar_productos(self):
        """Metodo para cargar los productos
        :return: lista de productos
        """
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT articulo FROM articulos"
            result = QueriesSQLite.execute_read_query(conn, query)
            self.productos = [row[0] for row in result]
            self.entry_producto['values'] = self.productos
            return result
        except Exception as e:
            messagebox.showerror("Cargar_Productos - Error", f"Error al cargar los productos: {e}")
            registrar_error(f"Cargar_Productos - Error al cargar los productos: {e}")
            return []

    def filtrar_productos(self, event):
        """Metodo para filtrar los productos
        :param event: evento que activa el filtro
        """
        if self.timer_producto:
            self.timer_producto.cancel()
        self.timer_producto = threading.Timer(0.5, self._filtrar_productos)
        self.timer_producto.start()

    def _filtrar_productos(self):
        """Metodo para filtrar los productos
        :return: lista de productos filtrados
        """
        self.cargar_productos()
        type_producto = self.entry_producto.get()

        if type_producto == "":
            data = self.productos
        else:
            data = [item for item in self.productos if type_producto.lower() in item.lower()]

        if data:
            self.entry_producto['values'] = data
            self.entry_producto.event_generate("<Down>")
        else:
            self.entry_producto['values'] = ["No se encontraron resultados"]
            self.entry_producto.event_generate("<Down>")
            self.entry_producto.delete(0, tk.END)

    def agregar_articulo(self):
        """Metodo para agregar un articulo a la venta
        :return: None
        """
        self.nro_factura = self.entry_factura_valor.get()
        proveedor = self.entry_proveedor.get()
        producto = self.entry_producto.get()
        cantidad = self.entry_cantidad.get()

        if not proveedor or not producto:
            messagebox.showwarning("Agregar_Articulo - Advertencia", "Por favor, seleccione un proveedor y un producto")            

        if not cantidad.isdigit() or int(cantidad) <= 0:
            messagebox.showwarning("Agregar_Articulo - Advertencia", "Por favor, ingrese una cantidad válida")
            return

        cantidad = int(cantidad)

        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT precio, costo, stock FROM articulos WHERE articulo = ?"
            result = QueriesSQLite.execute_read_query(conn, query, (producto,))

            if result is None:
                messagebox.showwarning("Agregar_Articulo - Advertencia", "Producto no encontrado")
                return

            precio, costo, stock = result[0]

            try:
                nuevo_costo = float(self.entry_costo.get())
            except ValueError:
                messagebox.showwarning("Agregar_Articulo - Advertencia", "Por favor, ingrese un costo válido")
                return

            #if stock < cantidad:
            #    messagebox.showwarning("Agregar_Articulo - Advertencia", 
            #                        f"El stock es insuficiente, solo hay {stock} unidad(es) en stock")
            #    return

            total = nuevo_costo * cantidad

            self.tre.insert("", END, values=(self.nro_factura, 
                                            proveedor, 
                                            producto, 
                                            "{:.2f}".format(nuevo_costo), 
                                            cantidad, 
                                            "{:.2f}".format(total)))
            self.productos_seleccionados.append((self.nro_factura, proveedor, producto, nuevo_costo, cantidad, total, costo))
            self.limpiar_label()

        except Exception as e:
            messagebox.showerror("Agregar_Articulo - Error", f"Error al agregar el articulo: {e}")
            registrar_error(f"Agregar_Articulo - Error al agregar el articulo: {e}")

        self.calcular_precio_total()
        self.entry_stock_valor.config(text="")
        self.entry_costo.delete(0, END)

    def calcular_precio_total(self):
        """Metodo para calcular el precio total de la venta
        :return: None
        """
        total_pagar = sum(float(self.tre.item(item)["values"][-1]) for item in self.tre.get_children())
        self.label_precio_total_valor.config(text=f"{total_pagar:.2f}")

    def actualizar_stock(self, event=None):
        """Metodo para actualizar el stock del producto seleccionado
        :param event: evento que activa el actualizacion
        :return: None
        """
        producto_seleccionado = self.entry_producto.get()
        
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT stock, costo FROM articulos WHERE articulo = ?"
            result = QueriesSQLite.execute_read_query(conn, query, (producto_seleccionado,))

            # Muestra el stock actual del producto en el entry
            stock_actual = result[0][0]
            self.entry_stock_valor.config(text=f"{stock_actual}")

            # Muestra  el precio costo actual del producto en el entry
            self.costo_actual = result[0][1]
            self.entry_costo.insert(0, f"{self.costo_actual:.2f}")

            if result is None:
                messagebox.showwarning("Actualizar_Stock - Advertencia", "Producto no encontrado")
                return            
        except Exception as e:
            messagebox.showerror("Actualizar_Stock - Error", f"Error al obtener el stock del producto: {e}")
            registrar_error(f"Actualizar_Stock - Error al obtener el stock del producto: {e}")
            return

    def registrar_pedido(self):
        """Metodo para realizar el pago de la venta
        :return: None
        """
        if not self.tre.get_children():
            messagebox.showwarning("Registrar_Pedido - Advertencia", "No hay productos en la lista de pedidos")
            return

        proveedor = self.entry_proveedor.get()

        # Actualizar la base de datos
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            hora_actual = datetime.now().strftime("%H:%M:%S")

            for item in self.productos_seleccionados:
                factura, proveedor, producto, costo, cantidad, total, viejo_costo = item
                query = "INSERT INTO pedidos (factura, proveedor, articulo, costo, cantidad, total, fecha, hora, viejo_costo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                data = (factura, proveedor, producto, costo, cantidad, total, fecha_actual, hora_actual, viejo_costo)
                QueriesSQLite.execute_query(conn, query, data)

                query = "UPDATE articulos SET stock = stock + ? WHERE articulo = ?"
                data = (cantidad, producto)
                QueriesSQLite.execute_query(conn, query, data)                        

        except Exception as e:
            messagebox.showerror("Registrar_Pedido - Error", f"Error al registrar el pedido: {e}")
            registrar_error(f"Registrar_Pedido - Error al registrar el pedido: {e}")
            return

        self.limpiar_datos_pedidos()

    def limpiar_datos_pedidos(self):
        """Limpia los datos de la venta después de generar el PDF."""
        self.productos_seleccionados = []
        self.limpiar_campos()

    def limpiar_campos(self):
        """Limpia los campos de la venta."""
        for item in self.tre.get_children():
            self.tre.delete(item)

        self.label_precio_total_valor.config(text="0.00")
        self.entry_proveedor.set("")
        self.entry_stock_valor.config(text="")

        self.limpiar_label()

    def limpiar_label(self):
        """Limpia los labels del pedido."""
        self.entry_producto.set("")        
        self.entry_cantidad.delete(0, END)
        self.entry_stock_valor.config(text="")
        self.entry_costo.delete(0, END)

    def limpiar_lista_pedidos(self):
        """Limpia la lista de pedidos."""
        self.tre.delete(*self.tre.get_children())
        self.entry_cantidad.delete(0, END)        
        self.entry_costo.delete(0, END)
        self.entry_factura_valor.delete(0, END)
        self.entry_stock_valor.config(text="")
        self.productos_seleccionados.clear()
        self.calcular_precio_total()

    def eliminar_articulo(self):
        """Elimina un articulo de la venta."""
        selected_item = self.tre.selection()
        if not selected_item:
            messagebox.showwarning("Eliminar_Articulo - Advertencia", "Por favor, seleccione un articulo")
            return
        item_id = selected_item[0]
        valores_item = self.tre.item(item_id)["values"]
        factura, proveedor, articulo, costo, cantidad, total = valores_item
        
        self.tre.delete(selected_item)
        self.productos_seleccionados = [producto for producto in self.productos_seleccionados if producto[2] != articulo]
        self.calcular_precio_total()
        self.entry_stock_valor.config(text="")
        self.entry_costo.delete(0, END)

    def editar_articulo(self):
        """Edita un articulo de la venta."""
        selected_item = self.tre.selection()
        if not selected_item:
            messagebox.showwarning("Editar_Articulo - Advertencia", "Por favor, seleccione un articulo")
            return
        item_id = selected_item[0]
        valores_item = self.tre.item(item_id)["values"]
        if not valores_item:
            return
        
        current_producto = valores_item[2]
        current_cantidad = int(valores_item[4])
        current_costo = float(valores_item[3])
        viejo_costo = float(valores_item[-1])

        while True:
            new_cantidad = simpledialog.askinteger("Editar_Articulo", "Ingrese la nueva cantidad:", 
                                                initialvalue=current_cantidad)
            if new_cantidad is not None and new_cantidad > 0:
                break
            else:
                messagebox.showwarning("Editar_Articulo - Advertencia", "Por favor, ingrese una cantidad valida")
                return
        
        if new_cantidad is not None:
            try:
                total = current_costo * new_cantidad
                self.tre.item(item_id, values=(self.nro_factura, 
                                                self.entry_proveedor.get(), 
                                                current_producto, 
                                                "{:.2f}".format(current_costo), 
                                                new_cantidad, 
                                                "{:.2f}".format(total)))
                self.productos_seleccionados = [producto for producto in self.productos_seleccionados if producto[2] != current_producto]
                
                for idx, producto in enumerate(self.productos_seleccionados):
                    if producto[2] == current_producto:
                        self.productos_seleccionados[idx] = (self.nro_factura, 
                                                            self.entry_proveedor.get(), 
                                                            current_producto, 
                                                            current_costo, 
                                                            new_cantidad, 
                                                            total,
                                                            viejo_costo)
                        break
                self.calcular_precio_total()

            except Exception as e:
                messagebox.showerror("Editar_Articulo - Error", f"Error al editar el articulo: {e}")
                registrar_error(f"Editar_Articulo - Error al editar el articulo: {e}")
                return

    def ver_pedidos_realizados(self):
        """Muestra una ventana con la lista de pedidos realizados."""
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT * FROM pedidos"
            result = QueriesSQLite.execute_read_query(conn, query)

            if result is None:
                messagebox.showwarning("Ver_Pedidos_Realizados - Advertencia", "No hay pedidos realizados")
                return
            
            # Crear ventana de pedidos realizados
            ventana_pedidos = tk.Toplevel()
            ventana_pedidos.title("Pedidos Realizados")
            ventana_pedidos.geometry("1100x650+120+20")
            ventana_pedidos.config(bg=COLOR_FONDO, highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
            ventana_pedidos.resizable(False, False)
            ventana_pedidos.transient(self.master)
            ventana_pedidos.grab_set()
            ventana_pedidos.focus_set()
            ventana_pedidos.lift()

            # Función para filtrar las ventas por factura y/o cliente
            def filtrar_pedidos():
                #factura_a_buscar = entry_factura.get()
                proveedor_a_buscar = entry_proveedor.get()
                producto_a_buscar = entry_producto.get()

                for item in tree.get_children():
                    tree.delete(item)                

                # Este filtrado es para una coincidencia parcial en el producto y parcial en el cliente.
                pedidos_filtrados = [pedido for pedido in result 
                                    if (producto_a_buscar.lower() in pedido[2].lower() or not producto_a_buscar) and 
                                    (proveedor_a_buscar.lower() in pedido[1].lower() or not proveedor_a_buscar)]
                
                for pedido in pedidos_filtrados:
                    pedido = list(pedido)
                    pedido [3] = "{:.2f}".format(pedido[3])
                    pedido [5] = "{:.2f}".format(pedido[5])
                    pedido[6] = datetime.strptime(pedido[6], "%Y-%m-%d").strftime("%m-%d-%Y")
                    tree.insert("", "end", values=pedido)

            label_pedidos_realizados = tk.Label(ventana_pedidos, 
                                            text="Pedidos Realizados", 
                                            font=("Arial", 26, "bold"), 
                                            bg=COLOR_FONDO)
            label_pedidos_realizados.place(x=350, y=20)

            filtro_frame = tk.Frame(ventana_pedidos, bg=COLOR_FONDO)
            filtro_frame.place(x=20, y=60, width=1060, height=60)

            label_producto = tk.Label(filtro_frame, text="Producto: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
            label_producto.place(x=10, y=15)
            entry_producto = tk.Entry(filtro_frame, font=("Arial", 14, "bold"), cursor="hand2")
            entry_producto.place(x=120, y=10, width=200, height=40)        

            label_proveedor = tk.Label(filtro_frame, text="Proveedor: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
            label_proveedor.place(x=420, y=15)
            entry_proveedor = tk.Entry(filtro_frame, font=("Arial", 14, "bold"), cursor="hand2")
            entry_proveedor.place(x=540, y=10, width=200, height=40)

            # Cargar el icono de filtrar
            self.icono_filtrar = ImageTk.PhotoImage(Image.open("Imagenes/icono_filtro.png").resize((30, 30)))
            
            boton_filtrar = tk.Button(filtro_frame, 
                                    text="  Filtrar", 
                                    image=self.icono_filtrar,
                                    compound="left",
                                    font=("Arial", 14, "bold"),
                                    bg=COLOR_BOTON,
                                    fg="white",
                                    cursor="hand2", 
                                    command=filtrar_pedidos)
            boton_filtrar.place(x=840, y=10, width=200, height=40)

            tree_frame = tk.Frame(ventana_pedidos, bg="white")
            tree_frame.place(x=20, y=130, width=1060, height=500)

            scrol_y = ttk.Scrollbar(tree_frame, orient="vertical")
            scrol_y.pack(side="right", fill="y")        

            scrol_x = ttk.Scrollbar(tree_frame, orient="horizontal")
            scrol_x.pack(side="bottom", fill="x")

            # Crear un estilo para el Treeview
            style = ttk.Style()
            style.configure("Treeview", font=("Arial", 8))  # Configurar la fuente del Treeview

            tree = ttk.Treeview(tree_frame,
                                columns=("Factura", "Proveedor", "Producto", "Costo", "Cantidad", "Total", "Fecha", "Hora"),
                                show="headings", 
                                style="Treeview")
            tree.pack(fill="both", expand=True)

            scrol_y.config(command=tree.yview)
            scrol_x.config(command=tree.xview)

            tree.heading("Factura", text="Factura", command=lambda: sort_column(tree, "Factura"))
            tree.heading("Proveedor", text="Proveedor", command=lambda: sort_column(tree, "Proveedor"))
            tree.heading("Producto", text="Producto", command=lambda: sort_column(tree, "Producto"))
            tree.heading("Costo", text="Costo")
            tree.heading("Cantidad", text="Cantidad")
            tree.heading("Total", text="Total")
            tree.heading("Fecha", text="Fecha", command=lambda: sort_column(tree, "Fecha"))
            tree.heading("Hora", text="Hora", command=lambda: sort_column(tree, "Hora"))

            tree.column("Factura", width=60, anchor="center")
            tree.column("Proveedor", width=120, anchor="center")
            tree.column("Producto", width=120, anchor="center")
            tree.column("Costo", width=80, anchor="center")
            tree.column("Cantidad", width=80, anchor="center")
            tree.column("Total", width=80, anchor="center")
            tree.column("Fecha", width=80, anchor="center")
            tree.column("Hora", width=80, anchor="center")

            for pedido in result:
                pedido = list(pedido)
                pedido [3] = "{:.2f}".format(pedido[3])
                pedido [5] = "{:.2f}".format(pedido[5])
                pedido[6] = datetime.strptime(pedido[6], "%Y-%m-%d").strftime("%m-%d-%Y")
                tree.insert("", "end", values=pedido)

        except Exception as e:
            messagebox.showerror("Ver_Pedidos_Realizados - Error", f"Error al obtener los pedidos realizados: {e}")
            registrar_error(f"Ver_Pedidos_Realizados - Error al obtener los pedidos realizados: {e}")
            return

    def widgets(self):
        """Configura los widgets de la interfaz.
        Crear la ventana principal y los widgets relacionados con la venta y visualizacion del modulo.
        """
        labelframe = tk.LabelFrame(self, font=("Arial", 12, "bold"), bg=COLOR_FONDO)
        labelframe.place(x=25, y=30, width=1045, height=180)

        label_proveedor = tk.Label(labelframe, text="Proveedor: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_proveedor.place(x=10, y=11)
        self.entry_proveedor = ttk.Combobox(labelframe, font=("Arial", 14), cursor="hand2")
        self.entry_proveedor.place(x=120, y=8, width=260, height=40)
        self.entry_proveedor.bind("<KeyRelease>", self.filtrar_proveedores)

        label_producto  = tk.Label(labelframe, text="Producto: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_producto.place(x=10, y=70)
        self.entry_producto = ttk.Combobox(labelframe, font=("Arial", 14), cursor="hand2")
        self.entry_producto.place(x=120, y=66, width=260, height=40)
        self.entry_producto.bind("<KeyRelease>", self.filtrar_productos)

        label_cantidad = tk.Label(labelframe, text="Cantidad: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_cantidad.place(x=500, y=11)
        self.entry_cantidad = tk.Entry(labelframe, font=("Arial", 14), justify="center", cursor="hand2")
        self.entry_cantidad.place(x=610, y=8, width=100, height=40)

        self.label_stock = tk.Label(labelframe, text="Stock: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        self.label_stock.place(x=500, y=70)
        self.entry_stock_valor = tk.Label(labelframe, font=("Arial", 14), justify="center")
        self.entry_stock_valor.place(x=610, y=66, width=100, height=40)
        self.entry_producto.bind("<<ComboboxSelected>>", self.actualizar_stock)

        label_factura = tk.Label(labelframe, text="# Factura: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_factura.place(x=750, y=11)
        self.entry_factura_valor = tk.Entry(labelframe, 
                                            text=f"{self.nro_factura}", 
                                            font=("Arial", 14, "bold"), 
                                            justify="center", 
                                            cursor="hand2")
        self.entry_factura_valor.place(x=870, y=8, width=100, height=40)

        label_costo = tk.Label(labelframe, text="Costo: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_costo.place(x=750, y=70)
        self.entry_costo = tk.Entry(labelframe, font=("Arial", 14), justify="center", cursor="hand2")
        self.entry_costo.place(x=870, y=66, width=100, height=40)

        # Cargar iconos de los botones
        self.icono_agregar = ImageTk.PhotoImage(Image.open("Imagenes/icono_agregar_carrito.png").resize((35, 35)))
        self.icono_eliminar = ImageTk.PhotoImage(Image.open("Imagenes/icono_eliminar_carrito.png").resize((35, 35)))
        self.icono_editar = ImageTk.PhotoImage(Image.open("Imagenes/icono_carrito.png").resize((35, 35)))
        self.icono_limpiar = ImageTk.PhotoImage(Image.open("Imagenes/icono_limpiar_carrito2.png").resize((35, 35)))

        boton_agregar = tk.Button(labelframe, 
                                text="  Agregar", 
                                image=self.icono_agregar,
                                compound="left",
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white", 
                                cursor="hand2", 
                                command=self.agregar_articulo)
        boton_agregar.place(x=90, y=120, width=200, height=40)

        boton_eliminar = tk.Button(labelframe, 
                                text="  Eliminar", 
                                image=self.icono_eliminar,
                                compound="left",
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white", 
                                cursor="hand2", 
                                command=self.eliminar_articulo)
        boton_eliminar.place(x=310, y=120, width=200, height=40)

        boton_editar = tk.Button(labelframe, 
                                text="  Editar", 
                                image=self.icono_editar,
                                compound="left",
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white", 
                                cursor="hand2", 
                                command=self.editar_articulo)
        boton_editar.place(x=530, y=120, width=200, height=40)

        boton_limpiar = tk.Button(labelframe, 
                                text="  Limpiar", 
                                image=self.icono_limpiar,
                                compound="left",
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white", 
                                cursor="hand2", 
                                command=self.limpiar_lista_pedidos)
        boton_limpiar.place(x=750, y=120, width=200, height=40)

        # Crear el Frame para la tabla de pedidos (treeview)
        treFrame = tk.Frame(self, bg=COLOR_BG_LISTAS)
        treFrame.place(x=70, y=220, width=980, height=300)

        scrol_y = ttk.Scrollbar(treFrame, orient="vertical")
        scrol_y.pack(side="right", fill="y")        

        scrol_x = ttk.Scrollbar(treFrame, orient="horizontal")
        scrol_x.pack(side="bottom", fill="x")        

        # Crear la tabla de pedidos (treeview)
        self.tre = ttk.Treeview(treFrame, 
                                columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total"), 
                                show="headings",
                                yscrollcommand=scrol_y.set, 
                                xscrollcommand=scrol_x.set, 
                                selectmode="browse",
                                height=40)
        self.tre.pack(expand=True, fill=tk.BOTH)

        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)

        self.tre.heading("Factura", text="Factura")
        self.tre.heading("Cliente", text="Cliente")
        self.tre.heading("Producto", text="Producto")
        self.tre.heading("Precio", text="Precio")
        self.tre.heading("Cantidad", text="Cantidad")
        self.tre.heading("Total", text="Total")

        self.tre.column("Factura", width=70, anchor=CENTER)
        self.tre.column("Cliente", width=250, anchor=CENTER)
        self.tre.column("Producto", width=250, anchor=CENTER)
        self.tre.column("Precio", width=120, anchor=CENTER)
        self.tre.column("Cantidad", width=120, anchor=CENTER)
        self.tre.column("Total", width=150, anchor=CENTER)

        label_precio_total = tk.Label(self, 
                                    text="Precio Total: $", 
                                    font=("Arial", 18, "bold"), 
                                    bg=COLOR_FONDO)
        label_precio_total.place(x=660, y=550)
        self.label_precio_total_valor = tk.Label(self, 
                                                text=f"{0.00:.2f}", 
                                                font=("Arial", 18, "bold"),
                                                justify="right",
                                                fg="red")
        self.label_precio_total_valor.place(x=840, y=550, width=180, height=40)

        # Cargar iconos de los botones
        self.icono_ver_pedidos = ImageTk.PhotoImage(Image.open("Imagenes/icono_pedidos4.png").resize((35, 35)))

        boton_pagar = tk.Button(self, 
                                text="  Registrar Pedido", 
                                image=self.icono_ver_pedidos,
                                compound="left",
                                font=("Arial", 13, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white", 
                                cursor="hand2", 
                                command=self.registrar_pedido)
        boton_pagar.place(x=70, y=550, width=190, height=40)

        boton_ver_ventas = tk.Button(self, 
                                    text="  Ver Pedidos", 
                                    image=self.icono_ver_pedidos,
                                    compound="left",
                                    font=("Arial", 14, "bold"), 
                                    bg=COLOR_BOTON, 
                                    fg="white", 
                                    cursor="hand2", 
                                    command=self.ver_pedidos_realizados)
        boton_ver_ventas.place(x=290, y=550, width=280, height=40)

      
        