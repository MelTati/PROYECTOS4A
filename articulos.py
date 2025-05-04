import mysql.connector
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QCheckBox, QComboBox, QLabel, QHeaderView
)

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="mydb_conejo_feliz"
)
cursor = conexion.cursor(dictionary=True)

class VentanaArticulos(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Artículos")
        self.resize(950, 500)
        self.init_ui()
        self.cargar_combo_categoria_asignar()
        self.cargar_combo_marcas_asignar()
        self.cargar_combo_categoria_filtrar()
        self.cargar_combo_marcas_filtrar()
        self.cargar_datos() 

    def init_ui(self):
        layout = QVBoxLayout()

        # Filtros
        filtro_layout = QHBoxLayout()

        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar por Código o Nombre...")
        self.buscador.textChanged.connect(self.cargar_datos) 

        self.filtro_categoria = QComboBox()
        self.filtro_categoria.currentIndexChanged.connect(self.cargar_datos)

        self.filtro_marca = QComboBox()
        self.filtro_marca.currentIndexChanged.connect(self.cargar_datos)

        filtro_layout.addWidget(QLabel("Buscar:"))
        filtro_layout.addWidget(self.buscador)
        filtro_layout.addWidget(QLabel("Filtrar por Categoría:"))
        filtro_layout.addWidget(self.filtro_categoria)
        filtro_layout.addWidget(QLabel("Filtrar por Marca:"))
        filtro_layout.addWidget(self.filtro_marca)
        layout.addLayout(filtro_layout)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Código", "Nombre", "Activo", "Precio", "Costo", "Categoría", "Marca", "Descripción"
        ])
        self.tabla.cellClicked.connect(self.seleccionar_fila)
        layout.addWidget(self.tabla)

        # Ajuste de ancho para todas las columnas (0 al 7)
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Código
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Nombre
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Precio
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Costo
        self.tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Stock
        self.tabla.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)           # Marca
        self.tabla.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)           # Categoría

        # Formulario
        form_layout = QHBoxLayout()
        self.input_codigo = QLineEdit()
        self.input_nombre = QLineEdit()
        self.checkbox_activado = QCheckBox("¿Activo?")
        self.input_precio = QLineEdit()
        self.input_costo = QLineEdit()
        self.combo_categoria = QComboBox()
        self.combo_marca = QComboBox()
        self.input_descripcion = QLineEdit()


        self.input_codigo.setPlaceholderText("Codigo")
        self.input_nombre.setPlaceholderText("Nombre")
        self.input_precio.setPlaceholderText("Precio")
        self.input_costo.setPlaceholderText("Costo")
        self.input_descripcion.setPlaceholderText("Descripcion")

    
        form_layout.addWidget(self.input_codigo)
        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(self.checkbox_activado)
        form_layout.addWidget(self.input_precio)
        form_layout.addWidget(self.input_costo)
        form_layout.addWidget(self.combo_categoria)
        form_layout.addWidget(self.combo_marca)
        form_layout.addWidget(self.input_descripcion)
        layout.addLayout(form_layout)

        # Botones
        botones_layout = QHBoxLayout()
        btn_agregar = QPushButton("Agregar")
        btn_actualizar = QPushButton("Actualizar")
        btn_eliminar = QPushButton("Eliminar")

        btn_agregar.clicked.connect(self.agregar_articulo)
        btn_actualizar.clicked.connect(self.actualizar_articulo)
        btn_eliminar.clicked.connect(self.eliminar_articulo)

        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_actualizar)
        botones_layout.addWidget(btn_eliminar)
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)

    def cargar_combo_marcas_asignar(self):
        cursor.execute("SELECT id_marca, nombre_marca FROM marcas")
        marcas = cursor.fetchall()
        self.combo_marca.clear()
        for marca in marcas:
            self.combo_marca.addItem(marca["nombre_marca"], marca["id_marca"])

    def cargar_combo_categoria_asignar(self):
        cursor.execute("SELECT id_categorias, tipo_categoria FROM categorias")
        categorias = cursor.fetchall()
        self.combo_categoria.clear()
        for cat in categorias:
            self.combo_categoria.addItem(cat["tipo_categoria"], cat["id_categorias"])

    def cargar_combo_categoria_filtrar(self):
        cursor.execute("SELECT id_categorias, tipo_categoria FROM categorias")
        categorias = cursor.fetchall()
        self.filtro_categoria.clear()
        self.filtro_categoria.addItem("Todas", None)
        for cat in categorias:
            self.filtro_categoria.addItem(cat["tipo_categoria"], cat["id_categorias"])

    def cargar_combo_marcas_filtrar(self):
        cursor.execute("SELECT id_marca, nombre_marca FROM marcas")
        marcas = cursor.fetchall()
        self.filtro_marca.clear()
        self.filtro_marca.addItem("Todas", None)
        for marca in marcas:
            self.filtro_marca.addItem(marca["nombre_marca"], marca["id_marca"])

    def cargar_datos(self):
        categoria_id = self.filtro_categoria.currentData()
        marca_id = self.filtro_marca.currentData()
        texto_busqueda = self.buscador.text().strip()

        query = """
            SELECT a.codigo_articulo, a.nombre_articulo, a.activacion_articulo,
                   a.precio_articulo, a.costo_articulo,
                   c.tipo_categoria, m.nombre_marca, a.descr_caracteristicas
            FROM articulos a
            JOIN categorias c ON a.id_categorias = c.id_categorias
            JOIN marcas m ON a.id_marca = m.id_marca
            WHERE (%s IS NULL OR a.id_categorias = %s)
              AND (%s IS NULL OR a.id_marca = %s)
              AND (a.codigo_articulo LIKE %s OR a.nombre_articulo LIKE %s)
        """
        texto_busqueda_wildcard = f"%{texto_busqueda}%"

        cursor.execute(query, (categoria_id,categoria_id, marca_id, marca_id, texto_busqueda_wildcard, texto_busqueda_wildcard))
        resultados = cursor.fetchall()

        self.tabla.setRowCount(0)
        for fila, art in enumerate(resultados):
            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(art["codigo_articulo"]))
            self.tabla.setItem(fila, 1, QTableWidgetItem(art["nombre_articulo"] or ""))
            self.tabla.setItem(fila, 2, QTableWidgetItem("Sí" if art["activacion_articulo"] else "No"))
            self.tabla.setItem(fila, 3, QTableWidgetItem(str(art["precio_articulo"])))
            self.tabla.setItem(fila, 4, QTableWidgetItem(str(art["costo_articulo"])))
            self.tabla.setItem(fila, 5, QTableWidgetItem(art["tipo_categoria"]))
            self.tabla.setItem(fila, 6, QTableWidgetItem(art["nombre_marca"]))
            self.tabla.setItem(fila, 7, QTableWidgetItem(art["descr_caracteristicas"] or ""))


    def seleccionar_fila(self, fila, _):
        self.codigo_seleccionado = self.tabla.item(fila, 0).text()
        self.input_codigo.setText(self.codigo_seleccionado)
        self.input_nombre.setText(self.tabla.item(fila, 1).text())
        self.checkbox_activado.setChecked(self.tabla.item(fila, 2).text() == "Sí")
        self.input_precio.setText(self.tabla.item(fila, 3).text())
        self.input_costo.setText(self.tabla.item(fila, 4).text())

        try:
            self.combo_categoria.setCurrentIndex(self.combo_categoria.findText(self.tabla.item(fila, 5).text()))
        except (ValueError, AttributeError):
            pass

        try:
            self.combo_marca.setCurrentIndex(self.combo_marca.findText(self.tabla.item(fila, 6).text()))
        except (ValueError, AttributeError):
            pass

        self.input_descripcion.setText(self.tabla.item(fila, 7).text())

    def validar_campos(self):
        if not self.input_codigo.text().strip() or \
            not self.input_nombre.text().strip() or \
            not self.input_descripcion.text().strip() or \
            not self.input_precio.text().strip().replace('.', '', 1).isdigit() or \
            not self.input_costo.text().strip().replace('.', '', 1).isdigit() or \
            self.combo_categoria.currentIndex() == -1 or \
            self.combo_marca.currentIndex() == -1:
                QMessageBox.warning(self, "Advertencia", "Por favor complete todos los campos.")
                return False
        return True

    def agregar_articulo(self):
        if not self.validar_campos():
            return
        datos = (
            self.input_codigo.text().strip(),
            self.input_nombre.text().strip() or None,
            1 if self.checkbox_activado.isChecked() else 0,
            float(self.input_precio.text()) if self.input_precio.text() else None,
            float(self.input_costo.text()) if self.input_costo.text() else None,
            self.combo_categoria.currentData(),
            self.combo_marca.currentData(),
            self.input_descripcion.text().strip()
        )
        cursor.execute("""
            INSERT INTO articulos (codigo_articulo, nombre_articulo, activacion_articulo,
                                   precio_articulo, costo_articulo, id_categorias, id_marca, descr_caracteristicas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, datos)
        conexion.commit()
        QMessageBox.information(self, "Éxito", "Artículo agregado correctamente")
        self.cargar_datos()
        self.limpiar_campos()

    def actualizar_articulo(self):
        if not self.validar_campos():
            return
        datos = (
            self.input_nombre.text().strip() or None,
            1 if self.checkbox_activado.isChecked() else 0,
            float(self.input_precio.text()) if self.input_precio.text() else None,
            float(self.input_costo.text()) if self.input_costo.text() else None,
            self.combo_categoria.currentData(),
            self.combo_marca.currentData(),
            self.input_descripcion.text().strip() or None,
            self.codigo_seleccionado        
        )
        cursor.execute("""
            UPDATE articulos
            SET nombre_articulo = %s, activacion_articulo = %s, precio_articulo = %s,
                costo_articulo = %s, id_categorias = %s, id_marca = %s, descr_caracteristicas = %s
            WHERE codigo_articulo = %s
        """, datos)
        conexion.commit()
        QMessageBox.information(self, "Éxito", "Artículo actualizado correctamente")
        self.cargar_datos()
        self.limpiar_campos()

    def eliminar_articulo(self):
        if not hasattr(self, 'codigo_seleccionado') or not self.codigo_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Selecciona un artículo.")
            return
        
        # Confirmación antes de eliminar
        respuesta = QMessageBox.question(
            self, "Confirmación", "¿Estás seguro de que deseas eliminar este artículo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            cursor.execute("DELETE FROM articulos WHERE codigo_articulo = %s", (self.codigo_seleccionado,))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Artículo eliminado correctamente")
            self.cargar_datos()
            self.limpiar_campos()


    def limpiar_campos(self):
        self.input_codigo.clear()
        self.input_nombre.clear()
        self.checkbox_activado.setChecked(False)
        self.input_precio.clear()
        self.input_costo.clear()
        self.combo_categoria.setCurrentIndex(0)
        self.combo_marca.setCurrentIndex(0)
        self.input_descripcion.clear()

