import tkinter as tk
import customtkinter as ctk

ctk.set_appearance_mode("System") # Modo del tema Sistema (System(default), Light, Dark)
ctk.set_default_color_theme("blue") # Tema por defecto (blue(default), dark-blue, green)

def boton():
    print("Botón clickeado")

def boton2():
    print("Botón 2 clickeado")

if __name__ == "__main__":
    app = ctk.CTk() # Creamos la ventana principal en CTkinter
    app.geometry("1100x650+340+170") # Tamaño y posición
    app.title("Ventana principal") # Titulo
    
    # Creamos y colocamos el botón en CTkinter
    boton = ctk.CTkButton(app, text="Ctk Botón", command=boton)
    boton.pack(padx=20, pady=20)
    
    # fg_color es el color del botón
    boton2 = ctk.CTkButton(app, text="Ctk Botón 2", fg_color="green", command=boton2)
    # relx y rely son la posición relativa al centro de la ventana, valores entre 0 y 1.
    boton2.place(relx=0.5, rely=0.5, anchor="center")
    
    app.mainloop()