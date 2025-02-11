import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk


COLOR_BOTON_ACTIVO = "#18232b"

# ********** Clase para crear botones redondeados en tkinter **********
class RoundedButton(tk.Canvas):
    """Clase que crea un botón redondeado con efecto visual.

    Args:
        parent (tk.Widget): El widget padre.
        width (int): Ancho del botón.
        height (int): Alto del botón.
        corner_radius (int): Radio del borde redondeado.
        font_size (int): Tamaño de la fuente.
        bg (str): Color de fondo del botón.
        text (str): Texto del botón.
        icon (PIL.Image.Image): Imagen del icono.
        command (callable): Función a ejecutar al hacer clic en el botón.
    """
    def __init__(self, parent, width, height, corner_radius, font_size, bg, text="", icon=None, command=None):
        tk.Canvas.__init__(self, parent, width=width, height=height, highlightthickness=0)
        self.command = command
        self.corner_radius = corner_radius
        self.bg = bg
        self.icon = icon
        self.pressed = False  # Estado para rastrear si el botón está presionado

        # Definir una fuente para el texto
        self.font = tkfont.Font(family="Helvetica", size=font_size)

        # Dibujar el botón redondeado
        self.rectangle = self.create_rounded_rectangle(0, 0, width, height, corner_radius, fill=bg, outline=bg)

        # Calcular la posición del ícono y el texto
        if icon:
            #self.icon_image = ImageTk.PhotoImage(icon)
            icon_width = icon.width()
            icon_height = icon.height()
        else:
            icon_width = 0
            icon_height = 0

        text_width = self.font.measure(text) if text else 0
        text_height = self.font.metrics("linespace") if text else 0

        total_width = icon_width + text_width + (20 if icon and text else 0)  # 20 píxeles de separación entre el ícono y el texto
        total_height = max(icon_height, text_height)

        self.x_center = width / 2
        self.y_center = height / 2

        self.icon_x = self.x_center - total_width / 2
        self.icon_y = self.y_center - icon_height / 2

        self.text_x = self.icon_x + icon_width + (20 if icon else 0)
        self.text_y = self.y_center - text_height / 2

        # Añadir el ícono si se proporciona
        if icon:
            self.icon_id = self.create_image(self.icon_x, self.icon_y, image=icon, anchor="nw")

        # Añadir el texto
        if text:
            self.text_id = self.create_text(self.text_x, self.text_y, text=text, fill="white", font=self.font, anchor="nw")

        # Manejar eventos del mouse
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def create_rounded_rectangle(self, x1, y1, x2, y2, r, **kwargs):
        """Crea un rectángulo redondeado en tkinter.

        Args:
            x1 (int): Coordenada x inicial.
            y1 (int): Coordenada y inicial.
            x2 (int): Coordenada x final.
            y2 (int): Coordenada y final.
            r (int): Radio del rectángulo redondeado.
            **kwargs: Otras opciones de configuración para el rectángulo.

        Returns:
            int: Id del rectángulo creado.
        """
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_click(self, event):
        """Maneja el evento de clic en el botón.

        Args:
            event (tkinter.Event): El evento de clic.
        """
        # Cambiar el color de fondo y mover ligeramente el texto/ícono para simular presión
        self.itemconfig(self.rectangle, fill=COLOR_BOTON_ACTIVO)  # Cambiar el color de fondo a un tono más oscuro
        if hasattr(self, 'text_id'):
            self.move(self.text_id, 2, 2)  # Mover el texto ligeramente hacia abajo y a la derecha
        if hasattr(self, 'icon_id'):
            self.move(self.icon_id, 2, 2)  # Mover el ícono ligeramente hacia abajo y a la derecha
        self.pressed = True

    def on_release(self, event):
        """Maneja el evento de liberación del botón.

        Args:
            event (tkinter.Event): El evento de liberación.
        """
        if self.pressed:
            # Restaurar el color de fondo y la posición original del texto/ícono
            self.itemconfig(self.rectangle, fill=self.bg)  # Restaurar el color de fondo original
            if hasattr(self, 'text_id'):
                self.move(self.text_id, -2, -2)  # Mover el texto de vuelta a su posición original
            if hasattr(self, 'icon_id'):
                self.move(self.icon_id, -2, -2)  # Mover el ícono de vuelta a su posición original
            self.pressed = False
            if self.command:
                self.command()  # Ejecutar la función asociada al botón

'''
Ejemplo de uso:

def on_button_click():
    """Función asociada al botón. Se ejecuta cuando se hace clic en el botón."""
    print("Botón clickeado")

# Crear la ventana principal
root = tk.Tk()
root.geometry("400x100")
root.title("Botón Redondeado con Efecto Visual")

# Cargar una imagen para el ícono
icon_image = Image.open("Imagenes/icono_clientes2.png").resize((24, 24))  # Ajusta el tamaño según sea necesario

# Crear un botón redondeado con ícono
rounded_button = RoundedButton(root, width=200, height=50, corner_radius=20, font_size=12, bg="blue", text="Haz clic", icon=icon_image, command=on_button_click)
rounded_button.pack(pady=20)

# Ejecutar la aplicación
root.mainloop()
'''





