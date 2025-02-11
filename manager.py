from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import customtkinter as ctk
from customtkinter import *

import sys
import os
from libreria import *
from sqlqueries import QueriesSQLite

from login import Login, Registro
from container import Container


class Manager(ctk.CTk): # Ventana principal del sistema hecha con CTkinter
    """
    Clase que representa la ventana principal del sistema
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor de la clase Manager
        """
        super().__init__(*args, **kwargs)

        # Establecer el modo de apariencia y el tema al modo predeterminado del sistema
        ctk.set_appearance_mode("System")  # Modo del tema Sistema (System(default), Light, Dark)
        ctk.set_default_color_theme("blue")  # Tema del sistema (blue(default), dark-blue, green)

        self.cargar_nombre_empresa()
        self.title(self.empresa_nombre)
        self.geometry("1100x650+340+170")
        self.resizable(False, False)

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.config(bg=COLOR_FONDO)        

        self.frames = {}
        for F in (Login, Registro, Container):
            frame = F(container, self)
            self.frames[F] = frame

        self.show_frame(Login)

        self.style = ttk.Style()
        self.style.theme_use("clam")

    def show_frame(self, container):
        """
        Muestra el frame correspondiente a la pestaña activa
        """
        frame = self.frames[container]
        frame.tkraise()

    def cargar_nombre_empresa(self):
        """Carga el nombre de la empresa desde la base de datos."""
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            query = "SELECT * FROM configuracion"
            data = QueriesSQLite.execute_read_query(conn, query)
            conn.close()
            self.empresa_nombre = data[0][2]            
        except Exception as e:
            messagebox.showerror("Cargar_Nombre_Empresa - Error", f"Error al cargar el nombre de la empresa: {e}")
            registrar_error(f"Cargar_Nombre_Empresa - Error al cargar el nombre de la empresa: {e}")
            return

def main():
    app = Manager()
    app.mainloop()

if __name__ == "__main__":
    main()