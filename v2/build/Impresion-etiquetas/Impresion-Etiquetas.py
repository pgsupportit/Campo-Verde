import json
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from  ttkthemes import ThemedStyle
import pyodbc
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import textwrap
from tkcalendar import DateEntry
import os
import babel.numbers
import threading
import subprocess  # Para abrir el PDF

# Definir variables globales
conn = None
fecha_modificacion_entry = None
show_printed = None
search_entry = None  # Campo para la búsqueda

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
          REPLACE(CONVERT(VARCHAR, CAST(GVA17.PRECIO AS DECIMAL(18, 2)), 1), '.', ',') AS [PRECIO],
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
          REPLACE(CONVERT(VARCHAR, CAST(GVA17.PRECIO AS DECIMAL(18, 2)), 1), '.', ',') AS [PRECIO],
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

# Función para buscar productos
def search_products(event):
    try:
        search_term = search_entry.get()
        populate_table(conn, search_term, use_filters=False)  # Usar query sin filtros
    except Exception as e:
        messagebox.showerror("Error de Búsqueda", f"Error al buscar productos: {e}")

# Función para generar PDF en un hilo separado
def generate_pdf_thread(cod_articu):
    threading.Thread(target=generate_pdf, args=(cod_articu,)).start()

# Función para generar PDF de un artículo específico y abrirlo
def generate_pdf(cod_articu):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT STA11.DESCRIPCIO, STA11.COD_BARRA, REPLACE(CONVERT(VARCHAR, CAST(GVA17.PRECIO AS DECIMAL(18, 2)), 1), '.', ',') AS PRECIO, CONVERT(VARCHAR, GVA17.FECHA_MODI, 103) AS [FECHA MODIFICACIÓN] FROM STA11 JOIN GVA17 ON STA11.COD_ARTICU = GVA17.COD_ARTICU WHERE STA11.COD_ARTICU = ?", (cod_articu,))
        product = cursor.fetchone()

        if not product:
            messagebox.showwarning("No encontrado", f"No se encontró el artículo con código: {cod_articu}")
            return

        pdf_path = os.path.expanduser(f"~/Desktop/etiquetas_{cod_articu}.pdf")
        pdf = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        label_width = 60 / 25.4 * inch
        label_height = 30 / 25.4 * inch
        x_center = (width - label_width) / 2
        y_position = height - label_height - 0.5 * inch

        descripcion = product[0].upper()
        precio = product[2]
        if precio.endswith(',00'):
            precio = precio[:-3]

        pdf.rect(x_center, y_position, label_width, label_height, stroke=1, fill=0)
        pdf.setFont("Helvetica-Bold", 12)
        lines = textwrap.wrap(descripcion, width=21)
        y_text = y_position + label_height - 0.3 * inch
        for line in lines:
            pdf.drawCentredString(x_center + label_width / 2, y_text, line)
            y_text -= 12

        precio_str = f"$ {precio}"
        pdf.setFont("Helvetica-Bold", 35)
        pdf.drawCentredString(x_center + label_width / 2, y_text - 20, precio_str)

        # Posicionar el código de barras abajo a la izquierda
        cod_barra = product[1]
        pdf.setFont("Helvetica", 8)
        pdf.drawString(x_center + 5, y_position + 2, cod_barra)

        # Posicionar la fecha abajo a la derecha
        fecha_modificacion = product[3]
        pdf.drawString(x_center + label_width - 70, y_position + 2, fecha_modificacion)  # Abajo a la derecha

        y_position -= label_height + 0.2 * inch  # Espacio entre etiquetas

        pdf.save()
        messagebox.showinfo("PDF Generado", f"PDF generado correctamente en: {pdf_path}")

        # Abrir el PDF después de generarlo
        subprocess.Popen(['start', pdf_path], shell=True)  # Abre el PDF

    except Exception as e:
        messagebox.showerror("Error al generar PDF", f"Ocurrió un error al generar el PDF: {e}")

def generate_all_pdfs():
    products = tree.get_children()
    if not products:
        messagebox.showinfo("Información", "No hay productos seleccionados para generar PDF.")
        return

    pdf_path = os.path.expanduser("~/Desktop/etiquetas_todos.pdf")
    pdf = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    label_width = 60 / 25.4 * inch
    label_height = 30 / 25.4 * inch
    x_center = (width - label_width) / 2
    y_position = height - label_height - 0.5 * inch

    for product in products:
        product_values = tree.item(product, 'values')
        cod_articu = product_values[0]

        cursor = conn.cursor()
        cursor.execute("SELECT STA11.DESCRIPCIO, STA11.COD_BARRA, REPLACE(CONVERT(VARCHAR, CAST(GVA17.PRECIO AS DECIMAL(18, 2)), 1), '.', ',') AS PRECIO, CONVERT(VARCHAR, GVA17.FECHA_MODI, 103) AS [FECHA MODIFICACIÓN] FROM STA11 JOIN GVA17 ON STA11.COD_ARTICU = GVA17.COD_ARTICU WHERE STA11.COD_ARTICU = ?", (cod_articu,))
        product_data = cursor.fetchone()

        if product_data:
            descripcion = product_data[0].upper()
            precio = product_data[2]
            if precio.endswith(',00'):
                precio = precio[:-3]

            pdf.rect(x_center, y_position, label_width, label_height, stroke=1, fill=0)
            pdf.setFont("Helvetica-Bold", 12)
            lines = textwrap.wrap(descripcion, width=21)
            y_text = y_position + label_height - 0.3 * inch
            for line in lines:
                pdf.drawCentredString(x_center + label_width / 2, y_text, line)
                y_text -= 12

            precio_str = f"$ {precio}"
            pdf.setFont("Helvetica-Bold", 35)
            pdf.drawCentredString(x_center + label_width / 2, y_text - 20, precio_str)

            # Posicionar el código de barras pegado a la línea de abajo
            cod_barra = product_data[1]
            pdf.setFont("Helvetica", 8)
            pdf.drawString(x_center + 5, y_position + 2, cod_barra)  # Pegado a la línea de abajo a la izquierda

            # Posicionar la fecha pegada a la línea de abajo a la derecha
            fecha_modificacion = product_data[3]
            pdf.drawString(x_center + label_width - 70, y_position + 2, fecha_modificacion)  # Pegado a la línea de abajo a la derecha

            y_position -= label_height + 0.2 * inch  # Espacio entre etiquetas

            if y_position < 0:  # Si se sale del área de la página, crear una nueva página
                pdf.showPage()
                y_position = height - label_height - 0.5 * inch

    pdf.save()
    messagebox.showinfo("PDF Generado", f"PDF generado correctamente en: {pdf_path}")

    # Abrir el PDF después de generarlo
    subprocess.Popen(['start', pdf_path], shell=True)  # Abre el PDF

# Manejar el doble clic en la tabla para generar y abrir el PDF
def on_item_double_click(event):
    selected_item = tree.selection()  # Obtiene el artículo seleccionado
    if selected_item:
        cod_articu = tree.item(selected_item, 'values')[0]  # Obtiene el código del artículo
        generate_pdf(cod_articu)  # Genera y abre el PDF del artículo específico

# Interfaz de usuario con Tkinter
def create_gui():
    global tree, search_entry, show_printed, fecha_modificacion_entry

    root = ThemedTk(theme="breeze")

    root.title("Impresión de Etiquetas")
    root.geometry("900x600")

    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    search_frame = ttk.Frame(main_frame)
    search_frame.pack(pady=10)

    ttk.Label(search_frame, text="Buscar producto:").pack(side="left", padx=(0, 5))
    search_entry = ttk.Entry(search_frame, width=50)
    search_entry.pack(side="left", padx=(0, 5))
    search_entry.bind("<KeyRelease>", search_products)  # Evento para búsqueda

    show_printed = tk.IntVar()
    show_printed_checkbox = ttk.Checkbutton(search_frame, text="Mostrar impresos", variable=show_printed, command=toggle_printed_products)
    show_printed_checkbox.pack(side="left", padx=(0, 5))

    ttk.Label(search_frame, text="Fecha de modificación:").pack(side="left", padx=(0, 5))
    fecha_modificacion_entry = DateEntry(search_frame, date_pattern="yyyy-mm-dd", width=12)
    fecha_modificacion_entry.pack(side="left", padx=(0, 5))

    tree_frame = ttk.Frame(main_frame)
    tree_frame.pack(fill="both", expand=True)

    tree_scroll = ttk.Scrollbar(tree_frame)
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(tree_frame, columns=("codigo", "descripcion", "barra", "precio", "modificacion"), show="headings", yscrollcommand=tree_scroll.set)
    tree.pack(fill="both", expand=True)

    tree_scroll.config(command=tree.yview)

    tree.heading("codigo", text="Código")
    tree.heading("descripcion", text="Descripción")
    tree.heading("barra", text="Código de Barras")
    tree.heading("precio", text="Precio")
    tree.heading("modificacion", text="Fecha Modificación")

    tree.column("codigo", width=100)
    tree.column("descripcion", width=250)
    tree.column("barra", width=150)
    tree.column("precio", width=100)
    tree.column("modificacion", width=100)

    # Asignar la función de doble clic a la tabla
    tree.bind("<Double-1>", on_item_double_click)

    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(pady=10)

    generate_pdf_button = ttk.Button(buttons_frame, text="Imprimir", command=generate_all_pdfs)
    generate_pdf_button.pack(side="left", padx=(0, 5))

    refresh_button = ttk.Button(buttons_frame, text="Refrescar", command=refresh_table)
    refresh_button.pack(side="left", padx=(0, 5))

    root.mainloop()

# Iniciar la aplicación
if __name__ == "__main__":
    connection_string = load_config()
    conn = connect_to_database(connection_string)

    if conn:
        create_gui()
