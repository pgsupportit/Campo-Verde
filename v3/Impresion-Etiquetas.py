import json
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from tkcalendar import DateEntry
import pyodbc
import threading
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import tempfile
import textwrap
from reportlab.lib.units import inch
import babel.numbers

# Definir variables globales
conn = None
fecha_modificacion_entry = None
show_printed = None
search_entry = None  # Campo para la búsqueda
print_queue_tree = None  # Asumir que este es el treeview para la cola de impresión
tree = None  # Inicializamos la variable tree

# Leer la configuración de la base de datos
def load_config():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
            connection_string = (
                f'DRIVER={{{config["driver"]}}};'
                f'SERVER={config["server"]};'
                f'DATABASE={config["database"]};'
                f'UID={config["user"]};'
                f'PWD={config["password"]};'
            )
            return connection_string
    except Exception as e:
        messagebox.showerror("Error de Configuración", f"Error al cargar la configuración: {e}")
        return None

# Función para conectar a la base de datos
def connect_to_database(connection_string):
    try:
        return pyodbc.connect(connection_string)
    except pyodbc.Error as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos: {e}")
        return None

# Query sin filtros
def fetch_all_products(conn, search_term=None):
    try:
        cursor = conn.cursor()

        if search_term:
            search_term = f"%{search_term}%"
        else:
            search_term = "%%"

        query_1 = """
        SELECT
          STA11.COD_ARTICU AS [CÓDIGO DE ARTÍCULO],
          STA11.DESCRIPCIO AS [DESCRIPCIÓN ARTÍCULO],
          STA11.COD_BARRA AS [CÓDIGO DE BARRAS],
          REPLACE(CONVERT(VARCHAR, CAST(GVA17.PRECIO AS INT), 1), '.', ',') AS [PRECIO],
          CONVERT(VARCHAR, GVA17.FECHA_MODI, 103) AS [FECHA MODIFICACIÓN]
        FROM STA11
        JOIN GVA17 ON STA11.COD_ARTICU = GVA17.COD_ARTICU
        WHERE STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_INFORMACION_PARA_BALANZA)[1]', 'NVARCHAR(MAX)') = 'TIPO NO CONTROLA'
        AND (STA11.DESCRIPCIO LIKE ? OR STA11.COD_BARRA LIKE ?)
        """

        cursor.execute(query_1, (search_term, search_term))
        return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Error", f"Error al ejecutar la consulta: {e}")
        return []

# Query con filtros (fecha e impresos)
def fetch_filtered_products(conn, fecha_modificacion=None, search_term=None):
    try:
        cursor = conn.cursor()

        if search_term:
            search_term = f"%{search_term}%"
        else:
            search_term = "%%"

        query_2 = """
        SELECT
          STA11.COD_ARTICU AS [CÓDIGO DE ARTÍCULO],
          STA11.DESCRIPCIO AS [DESCRIPCIÓN ARTÍCULO],
          STA11.COD_BARRA AS [CÓDIGO DE BARRAS],
          REPLACE(CONVERT(VARCHAR, CAST(GVA17.PRECIO AS INT), 1), '.', ',') AS [PRECIO],
          CONVERT(VARCHAR, GVA17.FECHA_MODI, 103) AS [FECHA MODIFICACIÓN],
          STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_SI)[1]', 'nvarchar(max)') AS [IMPRESO]
        FROM STA11
        JOIN GVA17 ON STA11.COD_ARTICU = GVA17.COD_ARTICU
        WHERE STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_INFORMACION_PARA_BALANZA)[1]', 'NVARCHAR(MAX)') = 'TIPO NO CONTROLA'
        AND (STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_SI)[1]', 'NVARCHAR(MAX)') = 'N' OR ? = 1)
        AND GVA17.NRO_DE_LIS = '10'
        AND (STA11.DESCRIPCIO LIKE ? OR STA11.COD_BARRA LIKE ?)
        """

        params = [show_printed.get(), search_term, search_term]

        # Agregar filtro por fecha si se proporciona
        if fecha_modificacion:
            query_2 += " AND CAST(GVA17.FECHA_MODI AS DATE) = CAST(? AS DATE)"
            params.append(fecha_modificacion)

        cursor.execute(query_2, params)
        return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Error", f"Error al ejecutar la consulta: {e}")
        return []

# Función para llenar la tabla con los productos de la query
def populate_table(conn, search_term=None, use_filters=False):
    global tree
    try:
        for row in tree.get_children():
            tree.delete(row)

        # Usar query sin filtros si no se deben aplicar
        if use_filters:
            fecha_modificacion = fecha_modificacion_entry.get_date().strftime('%Y-%m-%d') if fecha_modificacion_entry.get() else None
            products = fetch_filtered_products(conn, fecha_modificacion, search_term)
        else:
            products = fetch_all_products(conn, search_term)

        if products:
            for product in products:
                tree.insert("", "end", values=(product[0], product[1], product[2], product[3], product[4]))
        else:
            if search_term:
                search_entry.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"Error al poblar la tabla: {e}")

# Función para refrescar la tabla
def refresh_table():
    populate_table(conn, None, use_filters=True)  # Refrescar tabla con filtros

# Función para refrescar la tabla al cambiar el estado del checkbox
def toggle_printed_products():
    refresh_table()

# Función para buscar productos en tiempo real
def search_products(event):
    try:
        search_term = search_entry.get()
        populate_table(conn, search_term, use_filters=False)  # Buscar sin filtros
    except Exception as e:
        messagebox.showerror("Error", f"Error al buscar productos: {e}")

# Función para verificar si el producto ya está en la cola de impresión
def is_product_in_queue(codigo_articulo):
    for item in print_queue_tree.get_children():
        values = print_queue_tree.item(item, 'values')
        if values[0] == codigo_articulo:  # Comparar con el código de artículo
            return True
    return False

# Función para agregar el producto seleccionado a la cola de impresión
def add_to_print_queue(event):
    selected_item = tree.selection()
    if not selected_item:
        return  # No hacemos nada si no hay selección

    for item in selected_item:
        product_values = tree.item(item, 'values')
        codigo_articulo = product_values[0]

        # Verificar si el producto ya está en la cola
        if is_product_in_queue(codigo_articulo):
            messagebox.showwarning("Producto Duplicado", f"El producto {codigo_articulo} ya está en la cola de impresión.")
            continue  # No añadir el producto si ya está en la cola

        print_queue_tree.insert("", "end", values=product_values)

def create_pdf_with_labels(items):
    """
    Crea un PDF con etiquetas a partir de los elementos seleccionados en la cola de impresión.
    
    Args:
    - items: Lista de elementos en la cola de impresión.
    
    Returns:
    - Ruta del archivo PDF generado.
    """
    # Crear un archivo temporal
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = temp_file.name
    temp_file.close()

    # Configurar el PDF
    pdf = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Definir dimensiones de la etiqueta
    label_width = 60 / 25.4 * inch  # Ancho de la etiqueta en pulgadas
    label_height = 30 / 25.4 * inch  # Alto de la etiqueta en pulgadas
    x_center = (width - label_width) / 2
    y_position = height - label_height - 0.5 * inch

    for item in items:
        # Obtener los datos del producto
        values = print_queue_tree.item(item, 'values')
        
        descripcion = values[1].upper()
        precio = values[3]

        # Eliminar la parte de ",00" si existe
        if precio.endswith(',00'):
            precio = precio[:-3]

        # Dibujar la etiqueta
        pdf.rect(x_center, y_position, label_width, label_height, stroke=1, fill=0)
        pdf.setFont("Helvetica-Bold", 12)

        # Ajustar la descripción en múltiples líneas
        lines = textwrap.wrap(descripcion, width=21)
        y_text = y_position + label_height - 0.3 * inch
        for line in lines:
            pdf.drawCentredString(x_center + label_width / 2, y_text, line)
            y_text -= 12  # Espacio entre líneas

        # Dibujar el precio centrado
        precio_str = f"$ {precio}"
        pdf.setFont("Helvetica-Bold", 35)
        pdf.drawCentredString(x_center + label_width / 2, y_text - 20, precio_str)

        # Posicionar el código de barras
        cod_barra = values[2]
        pdf.setFont("Helvetica", 8)
        pdf.drawString(x_center + 5, y_position + 2, cod_barra)

        # Posicionar la fecha
        fecha_modificacion = values[4]
        pdf.drawString(x_center + label_width - 50, y_position + 2, fecha_modificacion)

        # Ajustar la posición para la próxima etiqueta
        y_position -= label_height + 0.2 * inch

        # Verificar si necesitamos una nueva página
        if y_position < 0:
            pdf.showPage()
            y_position = height - label_height - 0.5 * inch

    pdf.save()
    return pdf_path

def clear_print_after_print():
    for item in print_queue_tree.get_children():
        print_queue_tree.delete(item)

# Función para imprimir las etiquetas
def print_labels():
    items = print_queue_tree.get_children()
    if not items:
        messagebox.showwarning("Cola Vacía", "No hay productos en la cola de impresión.")
        return

    pdf_path = create_pdf_with_labels(items)
    
    # Abrir el PDF generado
    os.startfile(pdf_path, "open")

    # Limpia la cola de impresión después de imprimir
    clear_print_after_print()

# Función para limpiar la cola de impresión
def clear_print_queue():
    """
    Limpia todos los elementos de la cola de impresión.
    """
    if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas limpiar la cola de impresión?"):
        print_queue_tree.delete(*print_queue_tree.get_children())

# Función para eliminar el producto seleccionado de la cola de impresión
def remove_from_print_queue():
    selected_item = print_queue_tree.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar.")
        return

    for item in selected_item:
        print_queue_tree.delete(item)

# Configuración de la ventana principal
def setup_window():
    global root, tree, search_entry, print_queue_tree, fecha_modificacion_entry, show_printed

    root = ThemedTk(theme="breeze")
    root.title("Sistema de Etiquetas")
    root.geometry("1050x800")

    # Frame para la búsqueda y el filtrado
    search_frame = ttk.Frame(root)
    search_frame.pack(pady=10)

    # Campo de búsqueda
    ttk.Label(search_frame, text='Buscar Producto').pack(side='left', padx=(0, 5))
    search_entry = ttk.Entry(search_frame)
    search_entry.pack(side="left", padx=(0, 5))
    search_entry.bind("<KeyRelease>", search_products)

    # Checkbox para mostrar productos impresos
    show_printed = tk.IntVar()
    printed_checkbox = ttk.Checkbutton(search_frame, text="Mostrar productos impresos", variable=show_printed, command=toggle_printed_products)
    printed_checkbox.pack(side=tk.LEFT, padx=(0, 5))

    # Campo de fecha de modificación
    fecha_modificacion_entry = DateEntry(search_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
    fecha_modificacion_entry.pack(side=tk.LEFT, padx=(5, 5))

    # Botón para refrescar la tabla
    refresh_button = ttk.Button(search_frame, text="Refrescar", command=refresh_table)
    refresh_button.pack(side=tk.LEFT, padx=(5, 5))

    # Configurar la tabla de productos
    tree = ttk.Treeview(root, columns=("CÓDIGO DE ARTÍCULO", "DESCRIPCIÓN ARTÍCULO", "CÓDIGO DE BARRAS", "PRECIO", "FECHA MODIFICACIÓN"), show='headings')
    tree.pack(expand=True, fill='both', padx=10)

    for col in tree["columns"]:
        tree.heading(col, text=col)

    # Añadir barra de desplazamiento para la primera tabla
    #scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    #tree.configure(yscroll=scrollbar.set)
    #scrollbar.pack(side="right", fill="y")

    # Separación entre las tablas
    separator_frame = ttk.Frame(root)
    separator_frame.pack(pady=20)  # Aumenta el "pady" para más separación si es necesario

    # Crear un estilo personalizado para la segunda tabla (tabla de impresión)
    style = ttk.Style()
    style.configure("Custom.Treeview", background="#c7f2a7", fieldbackground="#c7f2a7")  # Cambiar el color de fondo

    # Treeview para la cola de impresión (segunda tabla) con el nuevo estilo
    print_queue_tree = ttk.Treeview(root, style="Custom.Treeview", columns=("CÓDIGO DE ARTÍCULO", "DESCRIPCIÓN ARTÍCULO", "CÓDIGO DE BARRAS", "PRECIO", "FECHA MODIFICACIÓN"), show='headings')
    print_queue_tree.pack(expand=True, fill='both', padx=10)

    for col in print_queue_tree["columns"]:
        print_queue_tree.heading(col, text=col)

    # Añadir barra de desplazamiento para la segunda tabla
    #print_queue_scrollbar = ttk.Scrollbar(root, orient="vertical", command=print_queue_tree.yview)
    #print_queue_tree.configure(yscroll=print_queue_scrollbar.set)
    #print_queue_scrollbar.pack(side="right", fill="y")

    # Frame para los botones de imprimir y limpiar cola
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Botón para imprimir etiquetas
    print_button = ttk.Button(button_frame, text="Imprimir Etiquetas", command=print_labels)
    print_button.pack(side=tk.LEFT, padx=(0, 5))

    # Botón para limpiar la cola
    clear_button = ttk.Button(button_frame, text="Limpiar Tabla", command=clear_print_queue)
    clear_button.pack(side=tk.LEFT, padx=(5, 5))

    # Vincular la acción de añadir a la cola con el evento de selección
    tree.bind("<Double-1>", add_to_print_queue)

    # Vincular el doble clic en el treeview de la cola de impresión
    print_queue_tree.bind("<Double-1>", lambda event: remove_from_print_queue())

    # Conectar a la base de datos
    connection_string = load_config()
    if connection_string:
        global conn
        conn = connect_to_database(connection_string)
        populate_table(conn)


# Ejecutar la aplicación
if __name__ == "__main__":
    setup_window()
    root.mainloop()

    # Cerrar la conexión cuando se cierra la aplicación
    if conn:
        conn.close()
