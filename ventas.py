from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog, filedialog
import threading
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from libreria import *
from libreria_tkinter import RoundedButton
from sqlqueries import QueriesSQLite

import sys
import os
import datetime
from datetime import datetime



class Ventas(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.nro_factura = self.obtener_Nro_factura_actual()
        self.productos_seleccionados = []
        self.widgets()
        self.cargar_clientes()
        self.cargar_productos()
        self.timer_cliente = None
        self.timer_producto = None

    def obtener_Nro_factura_actual(self):
        """Metodo para obtener el nro de factura actual
        :return: nro de factura actual
        """
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT MAX(factura) FROM ventas"
            result = QueriesSQLite.execute_read_query(conn, query)
            return result[0][0] + 1 if result[0][0] is not None else 1
        except Exception as e:
            messagebox.showerror("Obtener_Nro_Factura_Actual - Error", f"Error al obtener el número de factura: {e}")
            registrar_error(f"Obtener_Nro_Factura_Actual - Error al obtener el número de factura: {e}")
            return 1

    def cargar_clientes(self):
        """Metodo para cargar los clientes
        :return: lista de clientes
        """
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT nombre FROM clientes"
            result = QueriesSQLite.execute_read_query(conn, query)
            self.clientes = [row[0] for row in result]
            self.entry_cliente['values'] = self.clientes            
            return result
        except Exception as e:
            messagebox.showerror("Cargar_Clientes - Error", f"Error al cargar los clientes: {e}")
            registrar_error(f"Cargar_Clientes - Error al cargar los clientes: {e}")
            return []

    def filtrar_clientes(self, event):
        """Metodo para filtrar los clientes
        :param event: evento que activa el filtro
        """
        if self.timer_cliente:
            self.timer_cliente.cancel()
        self.timer_cliente = threading.Timer(0.5, self._filtrar_clientes)
        self.timer_cliente.start()

    def _filtrar_clientes(self):
        """Metodo interno para filtrar los clientes
        :return: None
        """
        self.cargar_clientes()
        type_cliente = self.entry_cliente.get()

        if type_cliente == "":
            data = self.clientes
        else:
            data = [item for item in self.clientes if type_cliente.lower() in item.lower()]

        if data:
            self.entry_cliente['values'] = data
            self.entry_cliente.event_generate("<Down>")
        else:
            self.entry_cliente['values'] = ["No se encontraron resultados"]
            self.entry_cliente.event_generate("<Down>")
            self.entry_cliente.delete(0, tk.END)        

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
        self.cargar_datos_margen()
        cliente = self.entry_cliente.get()
        producto = self.entry_producto.get()
        cantidad = self.entry_cantidad.get()

        if not cliente or not producto:
            messagebox.showwarning("Agregar_Articulo - Advertencia", "Por favor, seleccione un cliente y un producto")            

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

            # Validar si el uso del margen de ganancia esta activo
            if self.uso_margen_ganancia.lower() == 'activo':
                precio = costo / self.margen_ganancia

            if stock < cantidad:
                messagebox.showwarning("Agregar_Articulo - Advertencia", 
                                    f"El stock es insuficiente, solo hay {stock} unidad(es) en stock")
                return

            total = precio * cantidad

            self.tre.insert("", END, values=(self.nro_factura, 
                                            cliente, 
                                            producto, 
                                            "{:.2f}".format(precio), 
                                            cantidad, 
                                            "{:.2f}".format(total)))
            self.productos_seleccionados.append((self.nro_factura, cliente, producto, precio, cantidad, total, costo))
            self.limpiar_label()

        except Exception as e:
            messagebox.showerror("Agregar_Articulo - Error", f"Error al agregar el articulo: {e}")
            registrar_error(f"Agregar_Articulo - Error al agregar el articulo: {e}")

        self.calcular_precio_total()

    def calcular_precio_total(self):
        """Metodo para calcular el precio total de la venta
        :return: None
        """
        total_pagar = sum(float(self.tre.item(item)["values"][-1]) for item in self.tre.get_children())
        self.label_precio_total_valor.config(text=f"{total_pagar:.2f}")

    def actualizar_stock_precio(self, event=None):
        """Metodo para actualizar el stock y precio del producto seleccionado
        :param event: evento que activa el actualizacion
        :return: None
        """
        # Obtener el producto seleccionado
        producto_seleccionado = self.entry_producto.get()

        # Cargar los datos del margen de ganancia
        self.cargar_datos_margen()
        
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT stock, precio FROM articulos WHERE articulo = ?"
            result = QueriesSQLite.execute_read_query(conn, query, (producto_seleccionado,))

            # Obtener los datos actuales del producto
            stock_actual = result[0][0]
            precio_actual = result[0][1]

            # Insertar 1 en la cantidad por defecto
            self.entry_cantidad.insert(0, "1")

            # Actualizar los valores en los labels
            self.entry_stock_valor.config(text=f"{stock_actual}")
            self.entry_precio_valor.config(text=f"{precio_actual}")

            # Validar si el uso del margen de ganancia esta activo
            if self.uso_margen_ganancia.lower() == 'activo':
                precio_actual = precio_actual / self.margen_ganancia
                self.entry_precio_valor.config(text=f"{precio_actual}")

            if result is None:
                messagebox.showwarning("Actualizar_Stock_Precio - Advertencia", "Producto no encontrado")
                return            

        except Exception as e:
            messagebox.showerror("Actualizar_Stock_Precio - Error", f"Error al obtener el stock y/o precio del producto: {e}")
            registrar_error(f"Actualizar_Stock_Precio - Error al obtener el stock y/o precio del producto: {e}")
            return    

    def realizar_pago(self):
        """Metodo para realizar el pago de la venta
        :return: None
        """
        # Cargar detos de Impuesto.
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT impuesto FROM impuesto"
            result = QueriesSQLite.execute_read_query(conn, query)
            valor_impuesto = result[0][0] / 100
        except Exception as e:
            messagebox.showerror("Realizar_Pago - Error", f"Error al obtener el valor del impuesto: {e}")
            registrar_error(f"Realizar_Pago - Error al obtener el valor del impuesto: {e}")
            return        

        if not self.tre.get_children():
            messagebox.showwarning("Realizar_Pago - Advertencia", "No hay productos en la venta")
            return

        # Calcular total de la venta
        total_venta = sum(float(item[5]) for item in self.productos_seleccionados)
        
        # Calcular impuestos y total
        total_impuesto = total_venta * valor_impuesto
        gran_total = total_venta + total_impuesto

        # Formatear los valores a formato moneda
        total_venta_forteado = "{:.2f}".format(total_venta)
        gran_total_forteado = "{:.2f}".format(gran_total)
        total_impuesto_forteado = "{:.2f}".format(total_impuesto)

        

        # Crear ventana de pago
        ventana_pago = tk.Toplevel()
        ventana_pago.title("Realizar Pago")
        ventana_pago.geometry("400x400+450+80")
        ventana_pago.config(bg=COLOR_FONDO, highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
        ventana_pago.resizable(False, False)
        ventana_pago.transient(self.master)
        ventana_pago.grab_set()
        ventana_pago.focus_set()
        ventana_pago.lift()

        label_titulo = tk.Label(ventana_pago, text="Realizar Pago", font=("Arial", 30, "bold"), bg=COLOR_FONDO)
        label_titulo.place(x=70, y=10)

        label_total = tk.Label(ventana_pago, text="Total a pagar: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_total.place(x=80, y=100)

        label_total_valor = tk.Label(ventana_pago, text=total_venta_forteado, font=("Arial", 14, "bold"), fg="green")
        label_total_valor.place(x=240, y=100, width=140)

        label_total = tk.Label(ventana_pago, text="Total Impuesto: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_total.place(x=80, y=140)

        label_total_valor = tk.Label(ventana_pago, text=total_impuesto_forteado, font=("Arial", 14, "bold"), fg="red")
        label_total_valor.place(x=240, y=140, width=140)

        label_total = tk.Label(ventana_pago, text="Gran Total: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_total.place(x=80, y=180)

        label_total_valor = tk.Label(ventana_pago, text=gran_total_forteado, font=("Arial", 14, "bold"), fg="blue")
        label_total_valor.place(x=240, y=180, width=140)

        label_monto = tk.Label(ventana_pago, text="Ingrese Monto Pagado: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_monto.place(x=80, y=220)

        entry_monto = tk.Entry(ventana_pago, 
                                        font=("Arial", 14, "bold"), 
                                        fg="blue", 
                                        cursor="hand2", 
                                        justify="center")
        entry_monto.place(x=80, y=260, width=260, height=40)

        boton_pagar = tk.Button(ventana_pago, 
                                text="Confirmar Pago", 
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white", 
                                cursor="hand2", 
                                command=lambda: self.procesar_pago(entry_monto.get(), ventana_pago, total_venta, total_impuesto))
        boton_pagar.place(x=80, y=320, width=240, height=40)

    def procesar_pago(self, cantidad_pagada, ventana_pago, total_venta, total_impuesto):
        """Metodo para procesar el pago de la venta
        :param cantidad_pagada: Monto pagado
        :param ventana_pago: Ventana de pago
        :param total_venta: Total de la venta
        :param total_impuesto: Total de impuestos
        :return: None
        """
        cantidad_pagada = float(cantidad_pagada)
        cliente = self.entry_cliente.get()
        gran_total = total_venta + total_impuesto

        if cantidad_pagada < gran_total:
            messagebox.showwarning("Realizar_Pago - Advertencia", "Monto pagado insuficiente")
            return

        cambio = cantidad_pagada - gran_total
        total_venta_forteado = "{:.2f}".format(gran_total)
        cantidad_pagada_forteado = "{:.2f}".format(cantidad_pagada)
        cambio_forteado = "{:.2f}".format(cambio)

        mensaje = f"Total a pagar: {total_venta_forteado}\nMonto pagado: {cantidad_pagada_forteado}\nCambio: {cambio_forteado}"
        messagebox.showinfo("Realizar_Pago - Pago Exitoso", mensaje)

        # Actualizar la base de datos
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            hora_actual = datetime.now().strftime("%H:%M:%S")

            for item in self.productos_seleccionados:
                factura, cliente, producto, precio, cantidad, total, costo = item
                query = "INSERT INTO ventas (factura, cliente, articulo, precio, cantidad, total, fecha, hora, costo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                data = (factura, cliente, producto, precio, cantidad, total, fecha_actual, hora_actual, costo)
                QueriesSQLite.execute_query(conn, query, data)

                query = "UPDATE articulos SET stock = stock - ? WHERE articulo = ?"
                data = (cantidad, producto)
                QueriesSQLite.execute_query(conn, query, data)

            # Ventana emergente para preguntar si desea imprimir Factura o Recibo
            ventana_imprimir = tk.Toplevel()
            ventana_imprimir.title("Imprimir Documento")
            ventana_imprimir.geometry("400x200+500+200")
            ventana_imprimir.config(bg=COLOR_BG_VENTANA_EMERGENTE, 
                                    highlightbackground="gray", 
                                    highlightcolor="gray", 
                                    highlightthickness=1)
            ventana_imprimir.resizable(False, False)
            ventana_imprimir.transient(self.master)
            ventana_imprimir.grab_set()
            ventana_imprimir.focus_set()
            ventana_imprimir.lift()

            label_pregunta = tk.Label(ventana_imprimir, 
                                    text="¿Deseas imprimir la Factura o Recibo?", 
                                    font=("Arial", 14, "bold"), 
                                    bg=COLOR_BG_VENTANA_EMERGENTE)
            label_pregunta.place(x=20, y=20)

            # Función para cerrar la ventana y generar la factura
            def imprimir_factura():
                self.generar_factura_pdf(total_venta, total_impuesto, cliente)
                ventana_imprimir.destroy()  # Cerrar la ventana emergente
                self.limpiar_datos_venta()  # Limpiar los datos después de generar el PDF

            # Función para cerrar la ventana y generar el recibo
            def imprimir_recibo():
                self.generar_recibo_pdf(total_venta, total_impuesto, cliente)
                ventana_imprimir.destroy()  # Cerrar la ventana emergente
                self.limpiar_datos_venta()  # Limpiar los datos después de generar el PDF

            boton_factura = tk.Button(ventana_imprimir, 
                                    text="Imprimir Factura", 
                                    font=("Arial", 12, "bold"), 
                                    bg=COLOR_BOTON, 
                                    fg="white", 
                                    cursor="hand2", 
                                    command=imprimir_factura)
            boton_factura.place(x=50, y=80, width=140, height=40)

            boton_recibo = tk.Button(ventana_imprimir, 
                                text="Imprimir Recibo", 
                                font=("Arial", 12, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white", 
                                cursor="hand2", 
                                command=imprimir_recibo)
            boton_recibo.place(x=210, y=80, width=140, height=40)            

        except Exception as e:
            messagebox.showerror("Realizar_Pago - Error", f"Error al registrar la venta: {e}")
            registrar_error(f"Realizar_Pago - Error al registrar la venta: {e}")
            return

        self.nro_factura += 1
        self.entry_factura_valor.config(text=str(self.nro_factura))

        ventana_pago.destroy()

    def limpiar_datos_venta(self):
        """Limpia los datos de la venta después de generar el PDF."""
        self.productos_seleccionados = []
        self.limpiar_campos()

    def limpiar_campos(self):
        """Limpia los campos de la venta."""
        for item in self.tre.get_children():
            self.tre.delete(item)

        self.label_precio_total_valor.config(text="0.00")
        self.entry_cliente.set("")
        self.entry_stock_valor.config(text="")
        self.entry_precio_valor.config(text="")

        self.limpiar_label()

    def limpiar_label(self):
        """Limpia los labels de la venta."""
        self.entry_producto.set("")        
        self.entry_cantidad.delete(0, END)

    def limpiar_lista_ventas(self):
        """Limpia la lista de ventas."""
        self.tre.delete(*self.tre.get_children())
        self.entry_producto.set("")
        self.entry_cantidad.delete(0, END)
        self.entry_stock_valor.config(text="")
        self.entry_precio_valor.config(text="")
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
        factura, cliente, articulo, precio, cantidad, total = valores_item
        
        self.tre.delete(selected_item)
        self.productos_seleccionados = [producto for producto in self.productos_seleccionados if producto[2] != articulo]
        self.calcular_precio_total()

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
        current_cantidad = valores_item[4]

        new_cantidad = simpledialog.askinteger("Editar_Articulo", "Ingrese la nueva cantidad:", 
                                                initialvalue=current_cantidad)
        
        if new_cantidad is not None:
            try:
                conn = QueriesSQLite.create_connection(DB_NAME)
                query = "SELECT precio, costo, stock FROM articulos WHERE articulo = ?"
                data = (current_producto,)
                result = QueriesSQLite.execute_read_query(conn, query, data)

                if result is None:
                    messagebox.showwarning("Editar_Articulo - Advertencia", "Producto no encontrado")
                    return
                
                precio, costo, stock = result[0]

                if new_cantidad > stock:
                    messagebox.showwarning("Editar_Articulo - Advertencia", f"Stock insuficiente, solo hay {stock} unidad(es) en stock")
                    return

                total = precio * new_cantidad
                self.tre.item(item_id, values=(self.nro_factura, 
                                                self.entry_cliente.get(), 
                                                current_producto, 
                                                "{:.2f}".format(precio), 
                                                new_cantidad, 
                                                "{:.2f}".format(total)))
                self.productos_seleccionados = [producto for producto in self.productos_seleccionados if producto[2] != current_producto]
                
                for idx, producto in enumerate(self.productos_seleccionados):
                    if producto[2] == current_producto:
                        self.productos_seleccionados[idx] = (self.nro_factura, 
                                                            self.entry_cliente.get(), 
                                                            current_producto, 
                                                            precio, 
                                                            new_cantidad, 
                                                            total,
                                                            costo)
                        break
                self.calcular_precio_total()

            except Exception as e:
                messagebox.showerror("Editar_Articulo - Error", f"Error al editar el articulo: {e}")
                registrar_error(f"Editar_Articulo - Error al editar el articulo: {e}")
                return

    def ver_ventas_realizadas(self):
        """Muestra una ventana con la lista de ventas realizadas."""
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT * FROM ventas"
            result = QueriesSQLite.execute_read_query(conn, query)

            if result is None:
                messagebox.showwarning("Ver_Ventas - Advertencia", "No hay ventas realizadas")
                return
            
            # Crear ventana de ventas realizadas
            ventana_ventas = tk.Toplevel()
            ventana_ventas.title("Ventas Realizadas")
            ventana_ventas.geometry("1100x650+120+20")
            ventana_ventas.config(bg=COLOR_FONDO, highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
            ventana_ventas.resizable(False, False)
            ventana_ventas.transient(self.master)
            ventana_ventas.grab_set()
            ventana_ventas.focus_set()
            ventana_ventas.lift()

            # Función para filtrar las ventas por factura y/o cliente
            def filtrar_ventas():
                factura_a_buscar = entry_factura.get()
                cliente_a_buscar = entry_cliente.get()
                producto_a_buscar = entry_producto.get()

                for item in tree.get_children():
                    tree.delete(item)

                # Este filtrado es para una coincidencia exacta en la factura y en el cliente.
                #ventas_filtradas = [venta for venta in result 
                #                    if (str(venta[0]) == factura_a_buscar or not factura_a_buscar) and 
                #                    (venta[1].lower() == cliente_a_buscar.lower() or not cliente_a_buscar)]

                # Este filtrado es para una coincidencia exacta en la factura y parcial en el cliente.
                ventas_filtradas = [venta for venta in result 
                                    if (str(venta[0]) == factura_a_buscar or not factura_a_buscar) and 
                                    (cliente_a_buscar.lower() in venta[1].lower() or not cliente_a_buscar) and 
                                    (producto_a_buscar.lower() in venta[2].lower() or not producto_a_buscar)]
                
                for venta in ventas_filtradas:
                    venta = list(venta)
                    venta [3] = "{:.2f}".format(venta[3])
                    venta [5] = "{:.2f}".format(venta[5])
                    venta[6] = datetime.strptime(venta[6], "%Y-%m-%d").strftime("%m-%d-%Y")
                    tree.insert("", "end", values=venta)

            label_ventas_realizadas = tk.Label(ventana_ventas, 
                                            text="Ventas Realizadas", 
                                            font=("Arial", 26, "bold"), 
                                            bg=COLOR_FONDO)
            label_ventas_realizadas.place(x=350, y=20)

            filtro_frame = tk.Frame(ventana_ventas, bg=COLOR_FONDO)
            filtro_frame.place(x=20, y=60, width=1060, height=60)

            label_factura = tk.Label(filtro_frame, text="Nro. deFactura: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
            label_factura.place(x=10, y=15)
            entry_factura = tk.Entry(filtro_frame, font=("Arial", 14, "bold"), cursor="hand2")
            entry_factura.place(x=160, y=10, width=100, height=40)        

            label_cliente = tk.Label(filtro_frame, text="Cliente: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
            label_cliente.place(x=280, y=15)
            entry_cliente = tk.Entry(filtro_frame, font=("Arial", 14, "bold"), cursor="hand2")
            entry_cliente.place(x=360, y=10, width=200, height=40)

            label_producto = tk.Label(filtro_frame, text="Producto: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
            label_producto.place(x=580, y=15)
            entry_producto = tk.Entry(filtro_frame, font=("Arial", 14, "bold"), cursor="hand2")
            entry_producto.place(x=680, y=10, width=200, height=40)

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
                                    command=filtrar_ventas)
            boton_filtrar.place(x=910, y=10, width=140, height=40)

            tree_frame = tk.Frame(ventana_ventas, bg="white")
            tree_frame.place(x=20, y=130, width=1060, height=500)

            scrol_y = ttk.Scrollbar(tree_frame, orient="vertical")
            scrol_y.pack(side="right", fill="y")        

            scrol_x = ttk.Scrollbar(tree_frame, orient="horizontal")
            scrol_x.pack(side="bottom", fill="x")

            # Crear un estilo para el Treeview
            style = ttk.Style()
            style.configure("Treeview", font=("Arial", 8))  # Configurar la fuente del Treeview

            tree = ttk.Treeview(tree_frame,
                                columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total", "Fecha", "Hora"),
                                show="headings", 
                                style="Treeview")
            tree.pack(fill="both", expand=True)

            scrol_y.config(command=tree.yview)
            scrol_x.config(command=tree.xview)

            tree.heading("Factura", text="Factura", command=lambda: sort_column(tree, "Factura"))
            tree.heading("Cliente", text="Cliente", command=lambda: sort_column(tree, "Cliente"))
            tree.heading("Producto", text="Producto", command=lambda: sort_column(tree, "Producto"))
            tree.heading("Precio", text="Precio")
            tree.heading("Cantidad", text="Cantidad")
            tree.heading("Total", text="Total")
            tree.heading("Fecha", text="Fecha", command=lambda: sort_column(tree, "Fecha"))
            tree.heading("Hora", text="Hora", command=lambda: sort_column(tree, "Hora"))

            tree.column("Factura", width=60, anchor="center")
            tree.column("Cliente", width=120, anchor="center")
            tree.column("Producto", width=120, anchor="center")
            tree.column("Precio", width=80, anchor="center")
            tree.column("Cantidad", width=80, anchor="center")
            tree.column("Total", width=80, anchor="center")
            tree.column("Fecha", width=80, anchor="center")
            tree.column("Hora", width=80, anchor="center")

            for venta in result:
                venta = list(venta)
                venta [3] = "{:.2f}".format(venta[3])
                venta [5] = "{:.2f}".format(venta[5])
                venta[6] = datetime.strptime(venta[6], "%Y-%m-%d").strftime("%m-%d-%Y")
                tree.insert("", "end", values=venta)

        except Exception as e:
            messagebox.showerror("Ver_Ventas_Realizadas - Error", f"Error al obtener las ventas realizadas: {e}")
            registrar_error(f"Ver_Ventas_Realizadas - Error al obtener las ventas realizadas: {e}")
            return

    def generar_factura_pdf(self, total_venta, total_impuesto, cliente):
        """Genera un PDF de la factura de la venta como factura en papel tipo Carta.
        :param total_venta: Total de la venta.
        :param cliente: Cliente de la venta.
        :return: None
        """
        try:
            try:
                # Nombre de la carpeta de logs (relativa al directorio de trabajo actual)
                facturas_folder = os.path.join(os.getcwd(), "facturas")
                # Crear la carpeta si no existe
                if not os.path.exists(facturas_folder):
                    os.makedirs(facturas_folder)

            except Exception as e:
                messagebox.showerror("Generar_Factura_PDF - Error", f"Error al crear la carpeta de facturas: {e}")
                registrar_error(f"Generar_Factura_PDF - Error al crear la carpeta de facturas: {e}")
                return

            factura_path = os.path.join(facturas_folder, f"Factura_{self.nro_factura}.pdf")

            c = canvas.Canvas(factura_path, pagesize=letter)

            # Cargar los datos de la empresa
            self.cargar_datos_empresa()

            empresa_nombre = self.empresa_nombre
            empresa_direccion = self.empresa_direccion
            empresa_telefono = self.empresa_telefono
            empresa_email = self.empresa_email
            empresa_web = self.empresa_web
            empresa_logo = self.empresa_logo

            # Configuración de márgenes y posiciones
            margin_left = 50
            margin_top = 750
            line_height = 20
            image_size = 100

            # Dibujar el logo de la empresa
            c.drawImage(empresa_logo, margin_left, margin_top - image_size, width=image_size, height=image_size)

            # Título de la factura
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(colors.darkblue)
            c.drawCentredString(300, margin_top, "FACTURA DE VENTA")

            # Añadir una línea en blanco adicional
            margin_top -= 30  # Ajusta este valor para aumentar o disminuir el espacio

            # Información de la empresa
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 12)
            c.drawString(margin_left + image_size + 10, margin_top - 20, f"{empresa_nombre}")
            c.drawString(margin_left + image_size + 10, margin_top - 40, f"Dirección: {empresa_direccion}")
            c.drawString(margin_left + image_size + 10, margin_top - 60, f"Teléfono: {empresa_telefono}")
            c.drawString(margin_left + image_size + 10, margin_top - 80, f"Email: {empresa_email}")
            c.drawString(margin_left + image_size + 10, margin_top - 100, f"Web: {empresa_web}")

            # Línea separadora
            c.setLineWidth(0.5)
            c.setStrokeColor(colors.gray)
            c.line(margin_left, margin_top - 110, 550, margin_top - 110)

            # Información de la factura
            c.setFont("Helvetica", 12)
            c.drawString(margin_left, margin_top - 130, f"Factura Nro: {self.nro_factura}")
            c.drawString(margin_left, margin_top - 150, f"Fecha: {datetime.now().strftime('%m-%d-%Y %H:%M:%S')}")

            # Línea separadora
            c.line(margin_left, margin_top - 160, 550, margin_top - 160)

            # Información del cliente
            c.drawString(margin_left, margin_top - 180, f"Cliente: {cliente}")
            c.drawString(margin_left, margin_top - 200, f"Descripción de Productos:")

            # Encabezados de la tabla de productos
            y_offset = margin_top - 220
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin_left, y_offset, "Producto")
            c.drawString(margin_left + 200, y_offset, "Cantidad")
            c.drawString(margin_left + 300, y_offset, "Precio")
            c.drawString(margin_left + 400, y_offset, "Total")

            # Línea separadora
            c.line(margin_left, y_offset - 10, 550, y_offset - 10)

            # Detalles de los productos
            y_offset -= 30
            c.setFont("Helvetica", 12)
            for item in self.productos_seleccionados:
                factura, cliente, producto, precio, cantidad, total, costo = item
                c.drawString(margin_left, y_offset, f"{producto}")
                c.drawString(margin_left + 200, y_offset, str(cantidad))
                c.drawString(margin_left + 300, y_offset, f"${precio:.2f}")
                c.drawString(margin_left + 400, y_offset, f"${total:.2f}")
                y_offset -= line_height

            # Línea separadora
            c.line(margin_left, y_offset, 550, y_offset)

            # Total a pagar
            y_offset -= 20
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.darkblue)
            c.drawString(margin_left, y_offset, f"Total Venta: ${total_venta:.2f}")
            y_offset -= 20
            c.drawString(margin_left, y_offset, f"Total Impuesto: ${total_impuesto:.2f}")
            y_offset -= 20
            c.drawString(margin_left, y_offset, f"Total a Pagar: ${(total_impuesto + total_venta):.2f}")
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 12)

            # Línea separadora
            y_offset -= 20
            c.line(margin_left, y_offset, 550, y_offset)

            # Mensaje de agradecimiento
            c.setFont("Helvetica-Bold", 16)
            c.drawString(margin_left, y_offset - 40, "Gracias por su compra, vuelva pronto!!!")

            # Términos y condiciones
            y_offset -= 100
            c.setFont("Helvetica", 8)
            c.drawString(margin_left, y_offset, "Términos y Condiciones:")
            c.setFont("Helvetica-Bold", 6)
            c.drawString(margin_left, y_offset - 20, "1. Conserve esta factura como comprobante de la compra y posible devolucion.")
            c.drawString(margin_left, y_offset - 40, "2. Todas las devoluciones deben ser solicitadas dentro de los 30 dias posteriores a la fecha de la compra.")
            c.drawString(margin_left, y_offset - 60, "3. Para cualquier consulta o asistencia, contáctenos por email o teléfono.")
            c.drawString(margin_left, y_offset - 80, f"4. Visite nuestro sitio web: {empresa_web} para mas informacion y promociones.")

            # Guardar el PDF
            c.save()

            messagebox.showinfo("Generar_Factura_PDF - Información", f"Factura generada con éxito en: {factura_path}")

            # Abrir el PDF automáticamente
            os.startfile(os.path.abspath(factura_path))

        except Exception as e:
            messagebox.showerror("Generar_Factura_PDF - Error", f"Error al generar la factura: {e}")
            registrar_error(f"Generar_Factura_PDF - Error al generar la factura: {e}")
            return

    def generar_recibo_pdf(self, total_venta, total_impuesto, cliente):
        """Genera un PDF de la factura de la venta como recibo en papel tamaño 3.150 pulgadas.
        :param total_venta: Total de la venta.
        :param cliente: Cliente de la venta.
        :return: None
        """
        try:
            try:
                # Nombre de la carpeta de recibos (relativa al directorio de trabajo actual)
                recibos_folder = os.path.join(os.getcwd(), "recibos")
                # Crear la carpeta si no existe
                if not os.path.exists(recibos_folder):
                    os.makedirs(recibos_folder)

            except Exception as e:
                messagebox.showerror("Generar_Recibo_PDF - Error", f"Error al crear la carpeta de recibos: {e}")
                registrar_error(f"Generar_Recibo_PDF - Error al crear la carpeta de recibos: {e}")
                return

            recibo_path = os.path.join(recibos_folder, f"Recibo_{self.nro_factura}.pdf")

            # Tamaño personalizado para el recibo (3.150 in de ancho x 11 in de alto)
            page_width = 3.150 * inch
            page_height = 11 * inch
            c = canvas.Canvas(recibo_path, pagesize=(page_width, page_height))

            # Cargar los datos de la empresa
            self.cargar_datos_empresa()
            
            # Datos de la empresa
            empresa_nombre = self.empresa_nombre
            empresa_direccion = self.empresa_direccion
            empresa_telefono = self.empresa_telefono
            empresa_email = self.empresa_email
            empresa_web = self.empresa_web
            empresa_logo = self.empresa_logo

            # Configuración de márgenes y posiciones
            margin_left = 0.2 * inch  # Margen izquierdo reducido
            margin_top = page_height - 0.5 * inch  # Comenzar cerca del borde superior
            line_height = 0.2 * inch  # Espaciado entre líneas reducido
            image_size = 2.5 * inch  # Tamaño del logo reducido

            # Dibujar el logo de la empresa (antes de los datos de la empresa)
            c.drawImage(empresa_logo, margin_left, margin_top - image_size, width=image_size, height=image_size)
            margin_top -= image_size + line_height  # Espacio después del logo

            # Título del recibo
            c.setFont("Helvetica-Bold", 10)  # Fuente más pequeña
            c.setFillColor(colors.black)
            c.drawCentredString(page_width / 2, margin_top, "RECIBO DE VENTA")
            margin_top -= line_height * 2  # Espacio después del título

            # Información de la empresa (después del logo)
            c.setFont("Helvetica", 7)  # Fuente más pequeña
            c.drawString(margin_left, margin_top, f"{empresa_nombre}")
            margin_top -= line_height
            c.drawString(margin_left, margin_top, f"Dirección: {empresa_direccion}")
            margin_top -= line_height
            c.drawString(margin_left, margin_top, f"Teléfono: {empresa_telefono}")
            margin_top -= line_height
            c.drawString(margin_left, margin_top, f"Email: {empresa_email}")
            margin_top -= line_height
            c.drawString(margin_left, margin_top, f"Web: {empresa_web}")
            margin_top -= line_height * 2  # Espacio adicional

            # Línea separadora
            c.setLineWidth(0.5)
            c.setStrokeColor(colors.gray)
            c.line(margin_left, margin_top, page_width - margin_left, margin_top)
            margin_top -= line_height * 2  # Espacio después de la línea

            # Información del recibo
            c.setFont("Helvetica", 8)
            c.drawString(margin_left, margin_top, f"Recibo Nro: {self.nro_factura}")
            margin_top -= line_height
            c.drawString(margin_left, margin_top, f"Fecha: {datetime.now().strftime('%m-%d-%Y %H:%M:%S')}")
            margin_top -= line_height
            c.drawString(margin_left, margin_top, f"Cliente: {cliente}")
            margin_top -= line_height * 2  # Espacio adicional

            # Encabezados de la tabla de productos
            c.setFont("Helvetica-Bold", 8)
            c.drawString(margin_left, margin_top, "Producto")
            c.drawString(margin_left + 1.5 * inch, margin_top, "Cant.")
            c.drawString(margin_left + 2.0 * inch, margin_top, "Precio")
            c.drawString(margin_left + 2.5 * inch, margin_top, "Total")
            margin_top -= line_height

            # Línea separadora
            c.line(margin_left, margin_top, page_width - margin_left, margin_top)
            margin_top -= line_height

            # Detalles de los productos
            c.setFont("Helvetica", 7)
            for item in self.productos_seleccionados:
                factura, cliente, producto, precio, cantidad, total, costo = item
                c.drawString(margin_left, margin_top, f"{producto}")
                c.drawString(margin_left + 1.5 * inch, margin_top, str(cantidad))
                c.drawString(margin_left + 2.0 * inch, margin_top, f"${precio:.2f}")
                c.drawString(margin_left + 2.5 * inch, margin_top, f"${total:.2f}")
                margin_top -= line_height

            # Línea separadora
            c.line(margin_left, margin_top, page_width - margin_left, margin_top)
            margin_top -= line_height * 2  # Espacio adicional

            # Total a pagar
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.black)
            c.drawString(margin_left, margin_top, f"Total Venta: ${total_venta:.2f}")
            margin_top -= line_height
            c.drawString(margin_left, margin_top, f"Total Impuesto: ${total_impuesto:.2f}")
            margin_top -= line_height
            c.drawString(margin_left, margin_top, f"Total a Pagar: ${(total_impuesto + total_venta):.2f}")
            margin_top -= line_height * 2  # Espacio adicional

            # Mensaje de agradecimiento
            c.setFont("Helvetica-Bold", 10)
            c.drawString(margin_left, margin_top, "Gracias por su compra, vuelva pronto!")
            margin_top -= line_height * 2  # Espacio adicional

            # Términos y condiciones (opcional, dependiendo del espacio)
            c.setFont("Helvetica", 6)
            c.drawString(margin_left, margin_top, "Términos y Condiciones:")
            margin_top -= line_height
            c.drawString(margin_left, margin_top, "1. Conserve este recibo como comprobante de la compra.")
            margin_top -= line_height
            c.drawString(margin_left, margin_top, "2. Para devoluciones, contáctenos dentro de los 30 días.")
            margin_top -= line_height
            c.drawString(margin_left, margin_top, f"3. Visite nuestro sitio web: {empresa_web}")

            # Guardar el PDF
            c.save()

            messagebox.showinfo("Generar_Recibo_PDF - Información", f"Recibo generado con éxito en: {recibo_path}")

            # Abrir el PDF automáticamente
            os.startfile(os.path.abspath(recibo_path))

        except Exception as e:
            messagebox.showerror("Generar_Recibo_PDF - Error", f"Error al generar el recibo: {e}")
            registrar_error(f"Generar_Recibo_PDF - Error al generar el recibo: {e}")
            return

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

    def widgets(self):
        """Configura los widgets de la interfaz.
        Crear la ventana principal y los widgets relacionados con la venta y visualizacion del modulo.
        """
        labelframe = tk.LabelFrame(self, font=("Arial", 12, "bold"), bg=COLOR_FONDO)
        labelframe.place(x=25, y=30, width=1045, height=180)

        label_cliente = tk.Label(labelframe, text="Cliente: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_cliente.place(x=10, y=11)
        self.entry_cliente = ttk.Combobox(labelframe, font=("Arial", 14), cursor="hand2")
        self.entry_cliente.place(x=120, y=8, width=260, height=40)
        self.entry_cliente.bind("<KeyRelease>", self.filtrar_clientes) # Actualizar lista de clientes al escribir en el entry

        label_producto  = tk.Label(labelframe, text="Producto: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_producto.place(x=10, y=70)
        self.entry_producto = ttk.Combobox(labelframe, font=("Arial", 14), cursor="hand2")
        self.entry_producto.place(x=120, y=66, width=260, height=40)
        self.entry_producto.bind("<KeyRelease>", self.filtrar_productos) # Actualizar lista de productos al escribir en el entry

        label_cantidad = tk.Label(labelframe, text="Cantidad: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_cantidad.place(x=500, y=11)
        self.entry_cantidad = tk.Entry(labelframe, font=("Arial", 14), justify="center", cursor="hand2")
        self.entry_cantidad.place(x=610, y=8, width=100, height=40)

        self.label_stock = tk.Label(labelframe, text="Stock: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        self.label_stock.place(x=500, y=70)
        self.entry_stock_valor = tk.Label(labelframe, font=("Arial", 14), justify="center")
        self.entry_stock_valor.place(x=610, y=66, width=100, height=40)
        self.entry_producto.bind("<<ComboboxSelected>>", self.actualizar_stock_precio) # Actualizar stock y precio al seleccionar un producto

        self.label_precio = tk.Label(labelframe, text="Precio/und: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        self.label_precio.place(x=750, y=70)
        self.entry_precio_valor = tk.Label(labelframe, font=("Arial", 14), justify="center")
        self.entry_precio_valor.place(x=870, y=66, width=100, height=40)        

        label_factura = tk.Label(labelframe, text="# Factura: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_factura.place(x=750, y=11)
        self.entry_factura_valor = tk.Label(labelframe, 
                                            text=f"{self.nro_factura}", 
                                            font=("Arial", 14, "bold"), 
                                            justify="center")
        self.entry_factura_valor.place(x=870, y=8, width=100, height=40)

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
                                command=self.limpiar_lista_ventas)
        boton_limpiar.place(x=750, y=120, width=200, height=40)

        # Crear el Frame para la tabla de ventas (treeview)
        treFrame = tk.Frame(self, bg=COLOR_BG_LISTAS)
        treFrame.place(x=70, y=220, width=980, height=300)

        scrol_y = ttk.Scrollbar(treFrame, orient="vertical")
        scrol_y.pack(side="right", fill="y")        

        scrol_x = ttk.Scrollbar(treFrame, orient="horizontal")
        scrol_x.pack(side="bottom", fill="x")        

        # Crear la tabla de ventas (treeview)
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
                                                text=f"{0:.2f}", 
                                                font=("Arial", 18, "bold"),
                                                justify="right",
                                                fg="red")
        self.label_precio_total_valor.place(x=840, y=550, width=180, height=40)

        # Cargar iconos de los botones
        self.icono_pagar = ImageTk.PhotoImage(Image.open("Imagenes/icono_pagar3.png").resize((35, 35)))
        self.icono_ver_ventas = ImageTk.PhotoImage(Image.open("Imagenes/icono_ventas.png").resize((35, 35)))

        boton_pagar = tk.Button(self, 
                                text="  Pagar", 
                                image=self.icono_pagar,
                                compound="left",
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white", 
                                cursor="hand2", 
                                command=self.realizar_pago)
        boton_pagar.place(x=70, y=550, width=180, height=40)

        boton_ver_ventas = tk.Button(self, 
                                    text="  Ver Ventas", 
                                    image=self.icono_ver_ventas,
                                    compound="left",
                                    font=("Arial", 14, "bold"), 
                                    bg=COLOR_BOTON, 
                                    fg="white", 
                                    cursor="hand2", 
                                    command=self.ver_ventas_realizadas)
        boton_ver_ventas.place(x=290, y=550, width=280, height=40)

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
    
    
        