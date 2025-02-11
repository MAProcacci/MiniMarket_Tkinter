from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from sqlqueries import QueriesSQLite
from libreria import *


class Clientes(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.widgets()
        self.cargar_registros()

    def widgets(self):
        # Definicion y configuracion del LabelFrame. Lado Izquierdo
        self.labelframe = tk.LabelFrame(self, text="Clientes", font=("Arial", 20, "bold"), bg=COLOR_FONDO)
        self.labelframe.place(x=20, y=20, width=250, height=560)

        lbl_nombre = tk.Label(self.labelframe, text="Nombre: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        lbl_nombre.place(x=10, y=20)
        self.entry_nombre = ttk.Entry(self.labelframe, font=("Arial", 14))
        self.entry_nombre.place(x=10, y=50, width=220, height=40)

        lbl_nro_id = tk.Label(self.labelframe, text="Nro. de ID: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        lbl_nro_id.place(x=10, y=100)
        self.entry_nro_id = ttk.Entry(self.labelframe, font=("Arial", 14))
        self.entry_nro_id.place(x=10, y=130, width=220, height=40)

        lbl_direccion = tk.Label(self.labelframe, text="Dirección: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        lbl_direccion.place(x=10, y=180)
        self.entry_direccion = ttk.Entry(self.labelframe, font=("Arial", 14))
        self.entry_direccion.place(x=10, y=210, width=220, height=40)

        lbl_telefono = tk.Label(self.labelframe, text="Teléfono: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        lbl_telefono.place(x=10, y=260)
        self.entry_telefono = ttk.Entry(self.labelframe, font=("Arial", 14))
        self.entry_telefono.place(x=10, y=290, width=220, height=40)

        lbl_correo = tk.Label(self.labelframe, text="Correo: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        lbl_correo.place(x=10, y=340)
        self.entry_correo = ttk.Entry(self.labelframe, font=("Arial", 14))
        self.entry_correo.place(x=10, y=370, width=220, height=40)

        # Cargar iconos de los botones
        self.icono_agregar = ImageTk.PhotoImage(Image.open("Imagenes/icono_registrar_usuario4.png").resize((30, 30)))
        self.icono_modificar = ImageTk.PhotoImage(Image.open("Imagenes/icono_editar_item2.png").resize((30, 30)))

        btn_agregar = tk.Button(self.labelframe, 
                                text="  Agregar", 
                                image=self.icono_agregar,
                                compound="left",
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.agregar_cliente)
        btn_agregar.place(x=10, y=420, width=220, height=40)
        
        btn_modificar = tk.Button(self.labelframe, 
                                text="  Modificar", 
                                image=self.icono_modificar,
                                compound="left",
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=self.modificar_cliente)
        btn_modificar.place(x=10, y=470, width=220, height=40)

        # Definicion y configuracion del TreeView (Lista de Clientes). Lado Derecho
        treeFrame = tk.Frame(self, bg="white")
        treeFrame.place(x=280, y=20, width=800, height=560)

        scrol_y = ttk.Scrollbar(treeFrame, orient="vertical")
        scrol_y.pack(side=RIGHT, fill="y")
        scrol_x = ttk.Scrollbar(treeFrame, orient="horizontal")
        scrol_x.pack(side=BOTTOM, fill="x")
        
        self.tree = ttk.Treeview(treeFrame, 
                                columns=("ID", "Nombre", "Nro. ID", "Direccion", "Telefono", "Correo"),
                                show="headings",
                                yscrollcommand=scrol_y.set, 
                                xscrollcommand=scrol_x.set,
                                cursor="hand2",
                                height=40)
        self.tree.pack(fill="both", expand=True)
        
        scrol_y.config(command=self.tree.yview)
        scrol_x.config(command=self.tree.xview)
        
        self.tree.heading("ID", text="ID", command=lambda: sort_column(self.tree, "ID"))
        self.tree.heading("Nombre", text="Nombre", command=lambda: sort_column(self.tree, "Nombre"))
        self.tree.heading("Nro. ID", text="Nro. ID")
        self.tree.heading("Direccion", text="Direccion")
        self.tree.heading("Telefono", text="Telefono")
        self.tree.heading("Correo", text="Correo")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nombre", width=150, anchor="center")
        self.tree.column("Nro. ID", width=120, anchor="center")
        self.tree.column("Direccion", width=200, anchor="center")
        self.tree.column("Telefono", width=120, anchor="center")
        self.tree.column("Correo", width=200, anchor="center")

    def validar_campos(self):
        if not self.entry_nombre.get() or not self.entry_nro_id.get() or not self.entry_direccion.get() or not self.entry_telefono.get() or not self.entry_correo.get():
            messagebox.showerror("validar_campos - Error", "Todos los campos son obligatorios")
            return False
        return True
    
    def agregar_cliente(self):
        if not self.validar_campos():
            return
        
        nombre = self.entry_nombre.get()
        nro_id = self.entry_nro_id.get()
        direccion = self.entry_direccion.get()
        telefono = self.entry_telefono.get()
        correo = self.entry_correo.get()

        # Validar el correo electrónico
        if not validar_correo(correo):
            messagebox.showerror("Agregar Cliente - Error", "El correo electrónico no tiene un formato válido.")
            return

        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "INSERT INTO clientes (nombre, nro_id, direccion, telefono, correo) VALUES (?, ?, ?, ?, ?)"
            data = (nombre, nro_id, direccion, telefono, correo)
            QueriesSQLite.execute_query(conn, query, data)
            conn.close()
            messagebox.showinfo("Agregar Cliente - Informacion", "Cliente agregado correctamente")
            self.limpiar_treeview()
            self.limpiar_campos()
            self.cargar_registros()
        except Exception as e:
            messagebox.showerror("Agregar Cliente - Error", f"Error al agregar el cliente: {str(e)}")
            registrar_error(f"Agregar Cliente - Error al agregar el cliente: {str(e)}")
            conn.close()

    def cargar_registros(self):
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT * FROM clientes"
            result = QueriesSQLite.execute_read_query(conn, query)
            for row in result:
                self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Cargar_Registros - Error", f"Error al cargar los registros: {str(e)}")
            registrar_error(f"Cargar_Registros - Error al cargar los registros: {str(e)}")
            conn.close()

    def limpiar_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def limpiar_campos(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_nro_id.delete(0, tk.END)
        self.entry_direccion.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_correo.delete(0, tk.END)

    def modificar_cliente(self):
        if not self.tree.selection():
            messagebox.showwarning("Modificar_Cliente - Advertencia", "Por favor, seleccione un cliente para modificar")
            return
        
        # Obtener los datos del cliente seleccionado
        selected_item = self.tree.selection()[0]
        item_values = self.tree.item(selected_item)["values"]
        id = item_values[0]
        nombre_actual = item_values[1]
        nro_id_actual = item_values[2]
        direccion_actual = item_values[3]
        telefono_actual = item_values[4]
        correo_actual = item_values[5]

        # Crear ventana emergente de modificar cliente
        top_modificar = tk.Toplevel()
        top_modificar.title("Modificar Cliente")
        top_modificar.geometry("400x350+400+50")
        top_modificar.config(bg=COLOR_FONDO, highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
        top_modificar.resizable(False, False)
        top_modificar.transient(self.master)  # Ubicar la ventana modal sobre la principal
        top_modificar.grab_set()
        top_modificar.focus_set()
        top_modificar.lift()

        # Crear los campos de entrada para los nuevos datos y asignamos los valores actuales
        label_nombre_nuevo = tk.Label(top_modificar, text="Nombre: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_nombre_nuevo.grid(row=0, column=0, padx=10, pady=5)
        entry_nombre_nuevo = tk.Entry(top_modificar, font=("Arial", 14))
        entry_nombre_nuevo.grid(row=0, column=1, padx=10, pady=5)
        entry_nombre_nuevo.insert(0, nombre_actual)

        label_nro_id_nuevo = tk.Label(top_modificar, text="Nro. de ID: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_nro_id_nuevo.grid(row=1, column=0, padx=10, pady=5)
        entry_nro_id_nuevo = tk.Entry(top_modificar, font=("Arial", 14))
        entry_nro_id_nuevo.grid(row=1, column=1, padx=10, pady=5)
        entry_nro_id_nuevo.insert(0, nro_id_actual)

        label_direccion_nuevo = tk.Label(top_modificar, text="Direccion: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_direccion_nuevo.grid(row=2, column=0, padx=10, pady=5)
        entry_direccion_nuevo = tk.Entry(top_modificar, font=("Arial", 14))
        entry_direccion_nuevo.grid(row=2, column=1, padx=10, pady=5)
        entry_direccion_nuevo.insert(0, direccion_actual)

        label_telefono_nuevo = tk.Label(top_modificar, text="Telefono: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_telefono_nuevo.grid(row=3, column=0, padx=10, pady=5)
        entry_telefono_nuevo = tk.Entry(top_modificar, font=("Arial", 14))
        entry_telefono_nuevo.grid(row=3, column=1, padx=10, pady=5)
        entry_telefono_nuevo.insert(0, telefono_actual)

        label_correo_nuevo = tk.Label(top_modificar, text="Correo: ", font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        label_correo_nuevo.grid(row=4, column=0, padx=10, pady=5)
        entry_correo_nuevo = tk.Entry(top_modificar, font=("Arial", 14))
        entry_correo_nuevo.grid(row=4, column=1, padx=10, pady=5)
        entry_correo_nuevo.insert(0, correo_actual)        

        def guardar_modificaciones():
            # Validar que todos los campos esten completos
            if not entry_nombre_nuevo.get() or not entry_nro_id_nuevo.get() or not entry_direccion_nuevo.get() or not entry_telefono_nuevo.get() or not entry_correo_nuevo.get():
                messagebox.showerror("Guardar_Modificaciones - Error", "Todos los campos son obligatorios")
                return
            # Obtener los datos modificados
            nuevo_nombre = entry_nombre_nuevo.get()
            nuevo_nro_id = entry_nro_id_nuevo.get()
            nueva_direccion = entry_direccion_nuevo.get()
            nuevo_telefono = entry_telefono_nuevo.get()
            nuevo_correo = entry_correo_nuevo.get()

            try:
                conn = QueriesSQLite.create_connection(DB_NAME)
                query = "UPDATE clientes SET nombre = ?, nro_id = ?, direccion = ?, telefono = ?, correo = ? WHERE id = ?"
                data = (nuevo_nombre, nuevo_nro_id, nueva_direccion, nuevo_telefono, nuevo_correo, id)
                QueriesSQLite.execute_query(conn, query, data)
                conn.close()
                messagebox.showinfo("Guardar_Modificaciones - Informacion", "Cliente modificado correctamente")
                top_modificar.destroy()
                self.limpiar_treeview()
                self.cargar_registros()
            except Exception as e:
                messagebox.showerror("Guardar_Modificaciones - Error", f"Error al modificar el cliente: {str(e)}")
                registrar_error(f"Guardar_Modificaciones - Error al modificar el cliente: {str(e)}")
                conn.close()

        # Agregar una linea entre los campos y el boton de guardar
        tk.Label(top_modificar, text="", bg=COLOR_FONDO).grid(row=5, column=0, columnspan=2)

        # Botones de la ventana Modificar Cliente
        btn_guardar = tk.Button(top_modificar, 
                                text="Guardar Cambios", 
                                font=("Arial", 14, "bold"),
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=guardar_modificaciones)
        btn_guardar.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        btn_cancelar = tk.Button(top_modificar, 
                                text="Cancelar", 
                                font=("Arial", 14, "bold"), 
                                bg=COLOR_BOTON, 
                                fg="white",
                                cursor="hand2", 
                                command=top_modificar.destroy)
        btn_cancelar.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
        
