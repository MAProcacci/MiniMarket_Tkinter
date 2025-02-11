import sqlite3
from contextlib import contextmanager
from sqlite3 import Error
from tkinter import messagebox
from libreria import *


class QueriesSQLite:
    @staticmethod
    def create_connection(path):
        """
        Metodo para crear una conexion a la base de datos

        :param path: Ruta de la base de datos
        :return: Conexion a la base de datos
        """
        connection = None
        try:
            connection = sqlite3.connect(path)            
        except Error as e:
            messagebox.showerror("Create_Connection - Error", f"El error '{e}' a ocurrido")            
            registrar_error(f"Create_Connection - Error al crear la conexion: {e}")

        return connection

    @contextmanager
    def get_db_connection(path):
        """
        Metodo para obtener una conexion a la base de datos

        :param path: Ruta de la base de datos
        :return: Conexion a la base de datos
        """
        connection = None
        try:
            connection = sqlite3.connect(path)
            yield connection
        except Error as e:
            messagebox.showerror("Get_DB_Connection - Error", f"El error '{e}' a ocurrido")
            registrar_error(f"Get_DB_Connection - Error al crear la conexion: {e}")
        finally:
            if connection:
                connection.close()
    """
    # Modo de uso en el codigo:
    with get_db_connection(DB_NAME) as connection:
        query = "SELECT * FROM articulos"
        result = QueriesSQLite.execute_read_query(connection, query)
    """

    @staticmethod
    def execute_query(connection, query, data_tuple):
        """
        Metodo para ejecutar una consulta SQL

        :param connection: Conexion a la base de datos
        :param query: Consulta SQL a ejecutar
        :param data_tuple: Parametros de la consulta
        :return: El ultimo ID insertado
        """
        cursor = connection.cursor()
        try:
            connection.execute("BEGIN TRANSACTION")
            cursor.execute(query, data_tuple)
            connection.commit()            
            return cursor.lastrowid            
        except Error as e:
            connection.rollback()
            messagebox.showerror("Execute_Query - Error", f"El error '{e}' a ocurrido")            
            registrar_error(f"Execute_Query - Error al ejecutar la consulta: {e}")
        finally:
            cursor.close()            

    @staticmethod
    def execute_read_query(connection, query, data_tuple=()):
        """
        Metodo para ejecutar una consulta SQL

        :param connection: Conexion a la base de datos
        :param query: Consulta SQL a ejecutar
        :param data_tuple: Parametros de la consulta
        :return: Resultado de la consulta
        """
        cursor = connection.cursor()
        result = None
        try:
            cursor.execute(query, data_tuple)
            result = cursor.fetchall()            
            return result
        except Error as e:
            messagebox.showerror("Execute_Read_Query - Error", f"El error '{e}' a ocurrido")
            registrar_error(f"Execute_Read_Query - Error al ejecutar la consulta: {e}")
        finally:
            cursor.close()

    def create_tables():
        connection = QueriesSQLite.create_connection(DB_NAME)

        tabla_clientes = """
        CREATE TABLE IF NOT EXISTS clientes(
         id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         nombre TEXT NOT NULL,
         nro_id TEXT NOT NULL,
         direccion TEXT,
         telefono TEXT,
         correo TEXT
        );
        """

        tabla_proveedores = """
        CREATE TABLE IF NOT EXISTS proveedores(
         id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         nombre TEXT NOT NULL,
         nro_id TEXT NOT NULL,
         direccion TEXT,
         telefono TEXT,
         correo TEXT
        );
        """

        tabla_ventas = """
        CREATE TABLE IF NOT EXISTS ventas(
         factura INTEGER NOT NULL,
         cliente TEXT NOT NULL,
         articulo TEXT NOT NULL,
         precio REAL NOT NULL,
         cantidad INTEGER NOT NULL,
         total REAL NOT NULL,
         fecha TEXT NOT NULL,
         hora TEXT NOT NULL,
         costo REAL NOT NULL
        );
        """

        tabla_pedidos = """
        CREATE TABLE IF NOT EXISTS pedidos(
         factura INTEGER NOT NULL,
         proveedor TEXT NOT NULL,
         articulo TEXT NOT NULL,
         costo REAL NOT NULL,
         cantidad INTEGER NOT NULL,
         total REAL NOT NULL,
         fecha TEXT NOT NULL,
         hora TEXT NOT NULL,
         viejo_costo REAL NOT NULL
        );
        """

        tabla_articulos = """
        CREATE TABLE IF NOT EXISTS articulos(
         id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         articulo TEXT NOT NULL,
         precio REAL NOT NULL,        
         costo REAL NOT NULL,
         stock INTEGER NOT NULL,
         estado TEXT NOT NULL,
         image_path TEXT
        );
        """

        tabla_usuarios = """
        CREATE TABLE IF NOT EXISTS usuarios(
         id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         username TEXT NOT NULL, 
         password TEXT NOT NULL         
        );
        """        

        tabla_margen_ganancia = """
        CREATE TABLE IF NOT EXISTS margen_ganancia(
         margen_ganancia REAL NOT NULL PRIMARY KEY
        );
        """

        tabla_impuesto = """
        CREATE TABLE IF NOT EXISTS impuesto(
         impuesto REAL NOT NULL PRIMARY KEY
        );
        """

        tabla_configuracion = """
        CREATE TABLE IF NOT EXISTS configuracion(
         id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         logo_empresa TEXT NOT NULL,
         nombre_empresa TEXT NOT NULL,
         direccion_empresa TEXT NOT NULL,
         telefono_empresa TEXT NOT NULL,
         correo_empresa TEXT NOT NULL,
         web_empresa TEXT NOT NULL,
         uso_margen_ganancia TEXT NOT NULL
        );
        """

        QueriesSQLite.execute_query(connection, tabla_usuarios, tuple()) 
        QueriesSQLite.execute_query(connection, tabla_margen_ganancia, tuple())
        QueriesSQLite.execute_query(connection, tabla_impuesto, tuple())
        QueriesSQLite.execute_query(connection, tabla_articulos, tuple())
        QueriesSQLite.execute_query(connection, tabla_ventas, tuple())
        QueriesSQLite.execute_query(connection, tabla_clientes, tuple())
        QueriesSQLite.execute_query(connection, tabla_proveedores, tuple())
        QueriesSQLite.execute_query(connection, tabla_pedidos, tuple())
        QueriesSQLite.execute_query(connection, tabla_configuracion, tuple())

    def eliminar_restriccion_unique():
        try:
            conn = QueriesSQLite.create_connection(DB_NAME)
            
            # Paso 1: Crear una nueva tabla sin la restricción UNIQUE
            crear_tabla_nueva = """
            CREATE TABLE ventas_nueva (
                factura INTEGER NOT NULL,
                cliente TEXT NOT NULL,
                articulo TEXT NOT NULL,
                precio REAL NOT NULL,
                cantidad INTEGER NOT NULL,
                total REAL NOT NULL,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                costo REAL NOT NULL
            );
            """
            QueriesSQLite.execute_query(conn, crear_tabla_nueva, tuple())

            # Paso 2: Copiar los datos de la tabla original a la nueva tabla
            copiar_datos = """
            INSERT INTO ventas_nueva (factura, cliente, articulo, precio, cantidad, total, fecha, hora, costo)
            SELECT factura, cliente, articulo, precio, cantidad, total, fecha, hora, costo
            FROM ventas;
            """
            QueriesSQLite.execute_query(conn, copiar_datos, tuple())

            # Paso 3: Eliminar la tabla original
            eliminar_tabla_original = "DROP TABLE ventas;"
            QueriesSQLite.execute_query(conn, eliminar_tabla_original, tuple())

            # Paso 4: Renombrar la nueva tabla con el nombre de la tabla original
            renombrar_tabla = "ALTER TABLE ventas_nueva RENAME TO ventas;"
            QueriesSQLite.execute_query(conn, renombrar_tabla, tuple())

            messagebox.showinfo("Éxito", "La restricción UNIQUE ha sido eliminada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar la restricción UNIQUE: {e}")
            registrar_error(f"Error al eliminar la restricción UNIQUE: {e}")
        finally:
            if conn:
                conn.close()

if __name__=="__main__":
    connection = QueriesSQLite.create_connection(DB_NAME)    

    """ Inicializar tablas de Impuestos """
    # Primero verificamos si la tabla está vacía
    verificar_vacia = """ SELECT COUNT(*) FROM impuesto; """
    cantidad = QueriesSQLite.execute_read_query(connection, verificar_vacia)[0][0]

    # Solo insertamos si la tabla está vacía (cantidad == 0)
    if cantidad == 0:
        crear_impuesto = """ INSERT INTO impuesto (impuesto) VALUES (?); """
        QueriesSQLite.execute_query(connection, crear_impuesto, (0.0,))

    """ Inicializar tabla de Margen de Ganancia """
    # Primero verificamos si la tabla está vacía
    verificar_vacia = """ SELECT COUNT(*) FROM margen_ganancia; """
    cantidad = QueriesSQLite.execute_read_query(connection, verificar_vacia)[0][0]

    # Solo insertamos si la tabla está vacía (cantidad == 0)
    if cantidad == 0:
        crear_margen_ganancia = """ INSERT INTO margen_ganancia (margen_ganancia) VALUES (?); """
        QueriesSQLite.execute_query(connection, crear_margen_ganancia, (0.0,))

    """ Inicializar tabla de Usuarios """
    # Verificar si la tabla está vacía
    query_verificar_tabla = "SELECT COUNT(*) FROM usuarios;"
    resultado = QueriesSQLite.execute_read_query(connection, query_verificar_tabla)

    # Si la tabla está vacía (COUNT(*) == 0), insertar el usuario admin
    if resultado and resultado[0][0] == 0:
        usuario_tuple = ('admin', 'admin')
        crear_usuario = """
        INSERT INTO
            usuarios (username, password)
        VALUES
            (?,?);
        """
        QueriesSQLite.execute_query(connection, crear_usuario, usuario_tuple)

    #borrar_impuesto = "DELETE FROM impuesto;"
    #QueriesSQLite.execute_query(connection, borrar_impuesto, tuple())

    #crear_margen_ganancia = """
    #INSERT INTO
    #    margen_ganancia (margen_ganancia)
    #VALUES
    #    (?);
    #"""
    #QueriesSQLite.execute_query(connection, crear_margen_ganancia, (15.0,))

    #crear_producto = """
    #INSERT INTO
    #    inventario (id, nombre, proveedor, precio, costo, stock)
    #VALUES
    #    (1, 'leche 1l', 'Nestle', 4.85, 3.25, 20),
    #    (2, 'cereal 500g', 'Nestle', 7.5, 4.45, 15), 
    #    (3, 'yogurt 1L', 'Nestle', 2.5, 1.15, 10),
    #    (4, 'helado 2L', 'Nestle', 8.25, 3.45, 20),
    #    (5, 'alimento para perro 20kg', 'Nestle', 150.0, 75.0, 5),
    #    (6, 'shampoo', 'Nestle', 10.85, 5.0, 25),
    #    (7, 'papel higiénico 4 rollos', 'Nestle', 5.5, 2.35, 30),
    #    (8, 'jabón para trastes', 'Nestle', 3.0, 1.15, 5)
    # """
    #QueriesSQLite.execute_query(connection, crear_producto, tuple()) 

    # select_products = "SELECT * from productos"
    # productos = QueriesSQLite.execute_read_query(connection, select_products)
    # for producto in productos:
    #     print(producto)


    #usuario_tuple=('admin', 'admin')
    #crear_usuario = """
    #INSERT INTO
    #  usuarios (username, password)
    #VALUES
    #    (?,?);
    #"""
    #QueriesSQLite.execute_query(connection, crear_usuario, usuario_tuple) 


    # select_users = "SELECT * from usuarios"
    # usuarios = QueriesSQLite.execute_read_query(connection, select_users)
    # for usuario in usuarios:
    #     print("type:", type(usuario), "usuario:",usuario)

    # neuva_data=('Persona 55', '123', 'admin', 'persona1')
    # actualizar = """
    # UPDATE
    #   usuarios
    # SET
    #   nombre=?, password=?, tipo = ?
    # WHERE
    #   username = ?
    # """
    # QueriesSQLite.execute_query(connection, actualizar, neuva_data)

    
    