from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import customtkinter as ctk
from customtkinter import *

from PIL import Image, ImageTk
from container import Container
from sqlqueries import QueriesSQLite
from libreria import *


class Login(tk.Frame):
    """
    Clase que representa la ventana de login
    """
    def __init__(self, padre, controlador):
        """
        Constructor de la clase Login
        """
        super().__init__(padre)
        self.pack()
        self.place(x=0, y=0, width=1100, height=650)
        self.controlador = controlador
        self.widgets()

    def validacion(self, user, passw):
        """
        Función para validar que el usuario y la contraseña no sean vacios
        """
        return len(user) > 0 and len(passw) > 0

    def toggle_password_visibility(self):
        """
        Función para mostrar u ocultar la contraseña
        """
        if self.password.cget('show') == '*':
            self.password.config(show='')
            self.toggle_btn.config(image=self.eye_closed_icon)
        else:
            self.password.config(show='*')
            self.toggle_btn.config(image=self.eye_open_icon)

    def login(self):
        """
        Función para iniciar sesión
        """
        user = self.username.get()
        passw = self.password.get()        

        if self.validacion(user, passw):
            query = "SELECT * FROM usuarios WHERE username = ? AND password = ?"
            data = (user, passw)
            try:
                connection = QueriesSQLite.create_connection(DB_NAME)
                result = QueriesSQLite.execute_read_query(connection, query, data)           
            
                if result:
                    self.control1()
                else:
                    self.username.delete(0, END)
                    self.password.delete(0, END)
                    messagebox.showwarning("Login - Error", "Error: Usuario y/o contraseña incorrectos")
            except Exception as e:
                messagebox.showerror("Login - Error", f"Error: Sin conexion a la base de datos. {e}")
                registrar_error(f"Login - Error: Sin conexion a la base de datos. {e}")
        else:
            messagebox.showwarning("Login - Error", "Error: Favor llene todas los campos.")            

    def control1(self):
        """
        Función para mostrar la ventana principal
        """
        self.controlador.show_frame(Container)

    def control2(self):
        """
        Función para mostrar la ventana de registro
        """
        self.controlador.show_frame(Registro)

    def widgets(self):
        """
        Función para crear los widgets de la ventana de login
        """
        fondo = tk.Frame(self, bg=COLOR_FONDO)
        fondo.pack()
        fondo.place(x=0, y=0, width=1100, height=650)

        self.bg_image = Image.open("Imagenes/BG_Img_SuperMarket.jpg")
        self.bg_image = self.bg_image.resize((1100, 650))
        self.bg_image = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = ttk.Label(fondo, image=self.bg_image)
        self.bg_label.place(x=0, y=0, width=1100, height=650)

        frame1 = tk.Frame(self, 
                        bg=COLOR_FONDO, 
                        highlightbackground="gray", 
                        highlightcolor="gray", 
                        highlightthickness=1)
        frame1.place(x=350, y=70, width=400, height=560)

        self.logo_image = Image.open("Imagenes/Logo_SuperMarket1.jpg")
        self.logo_image = self.logo_image.resize((200, 200))
        self.logo_image = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(frame1, image=self.logo_image, background=COLOR_FONDO)
        self.logo_label.place(x=100, y=20)

        user_label = tk.Label(frame1, text="Nombre de Usuario", bg=COLOR_FONDO, font=("Arial", 16, "bold"))
        user_label.place(x=80, y=255)
        self.username = ttk.Entry(frame1, font=("Arial", 16))
        self.username.place(x=80, y=290, width=240, height=40)

        pass_label = tk.Label(frame1, text="Contraseña", bg=COLOR_FONDO, font=("Arial", 16, "bold"))
        pass_label.place(x=80, y=345)
        self.password = ttk.Entry(frame1, font=("Arial", 16), show="*")
        self.password.place(x=80, y=380, width=240, height=40)

        # Cargar las imágenes del ícono del ojo
        self.eye_open_icon = ImageTk.PhotoImage(Image.open("Imagenes/Icono_ojo.png").resize((20, 20)))  # Ajusta el tamaño según sea necesario
        self.eye_closed_icon = ImageTk.PhotoImage(Image.open("Imagenes/Icono_ojo_cerrado.png").resize((20, 20)))  # Asegúrate de tener una imagen para el ojo cerrado

        # Cargar iconos de los botones
        self.iniciar_sesion = ImageTk.PhotoImage(Image.open("Imagenes/icono_login.png").resize((30, 30)))
        self.regitrar_usuario = ImageTk.PhotoImage(Image.open("Imagenes/icono_registrar_usuario4.png").resize((30, 30)))

        # Botón para mostrar/ocultar contraseña
        self.toggle_btn = tk.Button(frame1,
                                    image=self.eye_open_icon,  # Ícono inicial (ojo abierto)
                                    command=self.toggle_password_visibility,
                                    bg=COLOR_BOTON,
                                    fg="green",
                                    font=("Arial", 12, "bold"),
                                    border=0,
                                    borderwidth=2,
                                    cursor="hand2")
        self.toggle_btn.place(x=330, y=380, width=50, height=30)

        btn_login = tk.Button(frame1, 
                                text="  Iniciar Sesión",
                                image=self.iniciar_sesion,
                                compound="left",
                                command=self.login,
                                bg=COLOR_BOTON,
                                fg="white",
                                font=("Arial", 16, "bold"),
                                border=0,
                                borderwidth=2,
                                cursor="hand2")
        btn_login.place(x=80, y=440, width=240, height=40)

        # Ejemplo de uso del botón CTkButton
        #btn_login = CTkButton(frame1,
        #                        text="  Iniciar Sesión",
        #                        image=self.iniciar_sesion,
        #                        compound="left",
        #                        command=self.login,
        #                        bg_color=COLOR_FONDO,
        #                        fg_color=COLOR_BOTON,
        #                        text_color="white",
        #                        font=("Arial", 16, "bold"),
        #                        corner_radius=30,
        #                        border_spacing=0,
        #                        border_width=2,
        #                        width=240, 
        #                        height=40,
        #                        cursor="hand2")
        #btn_login.place(x=80, y=440)

        btn_registro = tk.Button(frame1, 
                                text="  Registrarse",
                                image=self.regitrar_usuario,
                                compound="left",
                                command=self.control2,
                                bg=COLOR_BOTON,
                                fg="white",
                                font=("Arial", 16, "bold"),
                                border=0,
                                borderwidth=2,
                                cursor="hand2")
        btn_registro.place(x=80, y=500, width=240, height=40)


class Registro(tk.Frame):
    """
    Clase que representa la ventana de registro
    """
    def __init__(self, padre, controlador):
        """
        Constructor de la clase Registro
        """
        super().__init__(padre)
        self.pack()
        self.place(x=0, y=0, width=1100, height=650)
        self.controlador = controlador
        self.widgets()

    def validacion(self, user, passw):
        """
        Función para validar que el usuario y la contraseña no sean vacios
        """
        return len(user) > 0 and len(passw) > 0

    def toggle_password_visibility(self):
        """
        Función para mostrar u ocultar la contraseña
        """
        if self.password.cget('show') == '*':
            self.password.config(show='')
            self.toggle_btn.config(image=self.eye_open_icon)
        else:
            self.password.config(show='*')
            self.toggle_btn.config(image=self.eye_closed_icon)

    def registro(self):
        """
        Función para registrar un nuevo usuario
        """
        user = self.username.get()
        passw = self.password.get()
        key = self.key.get()
        if self.validacion(user, passw):
            if len(passw) < 6:
                messagebox.showwarning("Registro - Error", "Error: La contraseña debe tener al menos 6 caracteres.")
                self.username.delete(0, END)
                self.password.delete(0, END)
                self.key.delete(0, END)
            else:
                if key == "1234":
                    query = "INSERT INTO usuarios (username, password) VALUES (?, ?)"
                    data = (user, passw)
                    try:
                        connection = QueriesSQLite.create_connection(DB_NAME)
                        QueriesSQLite.execute_query(connection, query, data)
                        messagebox.showinfo("Registro - Exitoso", "Usuario registrado exitosamente.")
                    except Exception as e:
                        messagebox.showerror("Registro - Error", f"Error: Sin conexion a la base de datos. {e}")
                        registrar_error(f"Registro - Error: Sin conexion a la base de datos. {e}")
                    self.control1()
                else:
                    messagebox.showwarning("Registro - Error", "Error: Clave de registro incorrecta.")
                    self.username.delete(0, END)
                    self.password.delete(0, END)
                    self.key.delete(0, END)
        else:
            messagebox.showwarning("Registro - Error", "Error: Favor llene todas los campos.")

    def control1(self):
        """
        Función para mostrar la ventana principal
        """
        self.controlador.show_frame(Container)

    def control2(self):
        """
        Función para mostrar la ventana de registro
        """
        self.controlador.show_frame(Login)

    def widgets(self):
        """
        Función para crear los widgets de la ventana de Registro
        """
        fondo = tk.Frame(self, bg=COLOR_FONDO)
        fondo.pack()
        fondo.place(x=0, y=0, width=1100, height=650)

        self.bg_image = Image.open("Imagenes/BG_Img_SuperMarket.jpg")
        self.bg_image = self.bg_image.resize((1100, 650))
        self.bg_image = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = ttk.Label(fondo, image=self.bg_image)
        self.bg_label.place(x=0, y=0, width=1100, height=650)

        frame1 = tk.Frame(self, 
                        bg=COLOR_FONDO, 
                        highlightbackground="gray", 
                        highlightcolor="gray", 
                        highlightthickness=1)
        frame1.place(x=350, y=10, width=400, height=630)

        self.logo_image = Image.open("Imagenes/Logo_SuperMarket1.jpg")
        self.logo_image = self.logo_image.resize((200, 200))
        self.logo_image = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(frame1, image=self.logo_image, background=COLOR_FONDO)
        self.logo_label.place(x=100, y=20)

        user_label = tk.Label(frame1, text="Nombre de Usuario", bg=COLOR_FONDO, font=("Arial", 16, "bold"))
        user_label.place(x=80, y=255)
        self.username = ttk.Entry(frame1, font=("Arial", 16))
        self.username.place(x=80, y=290, width=240, height=40)

        pass_label = tk.Label(frame1, text="Contraseña", bg=COLOR_FONDO, font=("Arial", 16, "bold"))
        pass_label.place(x=80, y=345)
        self.password = ttk.Entry(frame1, font=("Arial", 16), show="*")
        self.password.place(x=80, y=380, width=240, height=40)

        # Cargar las imágenes del ícono del ojo
        self.eye_open_icon = ImageTk.PhotoImage(Image.open("Imagenes/Icono_ojo.png").resize((20, 20)))  # Ajusta el tamaño según sea necesario
        self.eye_closed_icon = ImageTk.PhotoImage(Image.open("Imagenes/Icono_ojo_cerrado.png").resize((20, 20)))  # Asegúrate de tener una imagen para el ojo cerrado

        self.regitrar_usuario = ImageTk.PhotoImage(Image.open("Imagenes/icono_registrar_usuario4.png").resize((30, 30)))
        self.regresar = ImageTk.PhotoImage(Image.open("Imagenes/icono_volver3.png").resize((30, 30)))

        # Botón para mostrar/ocultar contraseña
        self.toggle_btn = tk.Button(frame1, 
                                    image=self.eye_closed_icon,  # Icono inicial: ojo cerrado
                                    command=self.toggle_password_visibility,
                                    bg=COLOR_BOTON,
                                    fg="green",
                                    font=("Arial", 12, "bold"),
                                    border=0,
                                    borderwidth=2,
                                    cursor="hand2")
        self.toggle_btn.place(x=330, y=380, width=50, height=30)

        key_label = tk.Label(frame1, text="Codigo de Registro", bg=COLOR_FONDO, font=("Arial", 16, "bold"))
        key_label.place(x=80, y=435)
        self.key = ttk.Entry(frame1, font=("Arial", 16), show="*")
        self.key.place(x=80, y=470, width=240, height=40)

        btn_registro = tk.Button(frame1, 
                                text="  Registrarse",
                                image=self.regitrar_usuario,
                                compound="left",
                                command=self.registro,
                                bg=COLOR_BOTON,
                                fg="white",
                                font=("Arial", 16, "bold"),
                                border=0,
                                borderwidth=2,
                                cursor="hand2")
        btn_registro.place(x=80, y=525, width=240, height=40)

        btn_regresar = tk.Button(frame1, 
                                text="  Regresar",
                                image=self.regresar,
                                compound="left",
                                command=self.control2,
                                bg=COLOR_BOTON,
                                fg="white",
                                font=("Arial", 16, "bold"),
                                border=0,
                                borderwidth=2,
                                cursor="hand2")
        btn_regresar.place(x=80, y=575, width=240, height=40)
        