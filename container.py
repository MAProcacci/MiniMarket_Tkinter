from tkinter import *
import tkinter as tk
from tkinter import messagebox
from libreria import *
from ventas import Ventas
from inventario import Inventario
from clientes import Clientes
from pedidos import Pedidos
from proveedor import Proveedores
from configuracion import Configuracion
import sys
import os


class Container(tk.Frame):
    """
    Clase que representa la ventana principal del programa
    """
    def __init__(self, padre, controlador):
        """
        Constructor de la clase Container
        """
        super().__init__(padre)
        self.controlador = controlador
        self.pack()
        self.place(x=0, y=0, width=1100, height=650)
        self.widgets()
        self.frames = {}
        #self.buttons = []
        for F in (Ventas, Inventario, Clientes, Pedidos, Proveedores, Configuracion):
            frame = F(self)
            self.frames[F] = frame
            frame.pack()
            frame.config(bg=COLOR_FONDO, highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
            frame.place(x=0, y=40, width=1100, height=610)
        self.show_frame(Ventas)

    def show_frame(self, container):
        """
        Muestra el frame correspondiente a la pestaña activa
        """
        frame = self.frames[container]
        frame.tkraise()
        self.highlight_button(container)  # Resaltar el botón de la pestaña activa

    def highlight_button(self, container):
        """
        Resalta el botón de la pestaña activa
        """
        # Restablecer el color de todos los botones
        for button in self.buttons:
            button.config(bg=COLOR_BOTON)

        # Cambiar el color del botón de la pestaña activa
        if container == Ventas:
            self.btn_ventas.config(bg=COLOR_BOTON_ACTIVO)
        elif container == Inventario:
            self.btn_inventario.config(bg=COLOR_BOTON_ACTIVO)
        elif container == Clientes:
            self.btn_clientes.config(bg=COLOR_BOTON_ACTIVO)
        elif container == Pedidos:
            self.btn_pedidos.config(bg=COLOR_BOTON_ACTIVO)
        elif container == Proveedores:
            self.btn_proveedores.config(bg=COLOR_BOTON_ACTIVO)
        elif container == Configuracion:
            self.btn_configuracion.config(bg=COLOR_BOTON_ACTIVO)

    def ventas(self):
        self.show_frame(Ventas)

    def inventario(self):
        self.show_frame(Inventario)

    def clientes(self):
        self.show_frame(Clientes)

    def pedidos(self):
        self.show_frame(Pedidos)

    def proveedores(self):
        self.show_frame(Proveedores)

    def configuracion(self):
        self.show_frame(Configuracion)

    def widgets(self):
        """
        Crea los widgets de la ventana
        """
        frame2 = tk.Frame(self)
        frame2.place(x=0, y=0, width=1100, height=40)

        self.btn_ventas = tk.Button(frame2, 
                                    text="Ventas",
                                    bg=COLOR_BOTON,
                                    fg="white", 
                                    font=("Arial", 16, "bold"),
                                    cursor="hand2",
                                    command=self.ventas)
        self.btn_ventas.place(x=0, y=0, width=184, height=40)

        self.btn_inventario = tk.Button(frame2, 
                                    text="Inventario", 
                                    bg=COLOR_BOTON,
                                    fg="white", 
                                    font=("Arial", 16, "bold"), 
                                    cursor="hand2",
                                    command=self.inventario)
        self.btn_inventario.place(x=184, y=0, width=184, height=40)

        self.btn_clientes = tk.Button(frame2, 
                                    text="Clientes", 
                                    bg=COLOR_BOTON,
                                    fg="white", 
                                    font=("Arial", 16, "bold"), 
                                    cursor="hand2",
                                    command=self.clientes)
        self.btn_clientes.place(x=368, y=0, width=184, height=40)

        self.btn_pedidos = tk.Button(frame2, 
                                    text="Pedidos", 
                                    bg=COLOR_BOTON,
                                    fg="white", 
                                    font=("Arial", 16, "bold"), 
                                    cursor="hand2",
                                    command=self.pedidos)
        self.btn_pedidos.place(x=552, y=0, width=184, height=40)

        self.btn_proveedores = tk.Button(frame2, 
                                        text="Proveedores", 
                                        bg=COLOR_BOTON,
                                        fg="white", 
                                        font=("Arial", 16, "bold"), 
                                        cursor="hand2",
                                        command=self.proveedores)
        self.btn_proveedores.place(x=736, y=0, width=184, height=40)

        self.btn_configuracion = tk.Button(frame2, 
                                    text="Config/Report", 
                                    bg=COLOR_BOTON,
                                    fg="white", 
                                    font=("Arial", 16, "bold"), 
                                    cursor="hand2",
                                    command=self.configuracion)   
        self.btn_configuracion.place(x=920, y=0, width=184, height=40)

        self.buttons = [
            self.btn_ventas,
            self.btn_inventario,
            self.btn_clientes,
            self.btn_pedidos,
            self.btn_proveedores,
            self.btn_configuracion
        ]