import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QApplication, QCheckBox
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
        self.resize(900, 400)
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout()

        # Tabla de artículos (eliminada la columna de Características)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Código", "Nombre", "Activo", "Precio", "Costo"
        ])
        self.tabla.cellClicked.connect(self.seleccionar_fila)
        layout.addWidget(self.tabla)

        # Campos de entrada (eliminada la entrada para ID Características)
        form_layout = QHBoxLayout()
        self.input_codigo = QLineEdit()
        self.input_nombre = QLineEdit()
        self.checkbox_activado = QCheckBox("¿Activo?")
        self.input_precio = QLineEdit()
        self.input_costo = QLineEdit()

        self.input_codigo.setPlaceholderText("Código Artículo")
        self.input_nombre.setPlaceholderText("Nombre")
        self.input_precio.setPlaceholderText("Precio")
        self.input_costo.setPlaceholderText("Costo")

        form_layout.addWidget(self.input_codigo)
        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(self.checkbox_activado)
        form_layout.addWidget(self.input_precio)
        form_layout.addWidget(self.input_costo)
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

    def cargar_datos(self):
        try:
            cursor.execute("SELECT * FROM articulos")
            resultados = cursor.fetchall()
            self.tabla.setRowCount(0)
            for fila_num, art in enumerate(resultados):
                self.tabla.insertRow(fila_num)
                self.tabla.setItem(fila_num, 0, QTableWidgetItem(art["codigo_articulo"]))
                self.tabla.setItem(fila_num, 1, QTableWidgetItem(art["nombre_articulo"] or ""))
                activo = "Sí" if art["activacion_articulo"] else "No"
                self.tabla.setItem(fila_num, 2, QTableWidgetItem(activo))
                self.tabla.setItem(fila_num, 3, QTableWidgetItem(str(art["precio_articulo"])))
                self.tabla.setItem(fila_num, 4, QTableWidgetItem(str(art["costo_articulo"])))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la tabla: {e}")

    def seleccionar_fila(self, fila, _):
        self.codigo_seleccionado = self.tabla.item(fila, 0).text()
        self.input_codigo.setText(self.codigo_seleccionado)
        self.input_nombre.setText(self.tabla.item(fila, 1).text())
        self.checkbox_activado.setChecked(self.tabla.item(fila, 2).text() == "Sí")
        self.input_precio.setText(self.tabla.item(fila, 3).text())
        self.input_costo.setText(self.tabla.item(fila, 4).text())

    def validar_campos(self):
        if not self.input_codigo.text().strip():
            QMessageBox.warning(self, "Advertencia", "Código es obligatorio.")
            return False
        return True

    def agregar_articulo(self):
        if not self.validar_campos():
            return
        try:
            datos = (
                self.input_codigo.text().strip(),
                self.input_nombre.text().strip() or None,
                1 if self.checkbox_activado.isChecked() else 0,
                int(self.input_precio.text()) if self.input_precio.text().strip() else None,
                int(self.input_costo.text()) if self.input_costo.text().strip() else None
            )
            cursor.execute("""
                INSERT INTO articulos (codigo_articulo, nombre_articulo, activacion_articulo, precio_articulo, costo_articulo)
                VALUES (%s, %s, %s, %s, %s)
            """, datos)
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Artículo agregado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar: {e}")


    def actualizar_articulo(self):
        if not self.validar_campos():
            return
        try:
            datos = (
                self.input_nombre.text().strip() or None,
                1 if self.checkbox_activado.isChecked() else 0,
                int(self.input_precio.text()) if self.input_precio.text().strip() else None,
                int(self.input_costo.text()) if self.input_costo.text().strip() else None,
                self.codigo_seleccionado
            )
            cursor.execute("""
                UPDATE articulos
                SET nombre_articulo=%s, activacion_articulo=%s,
                    precio_articulo=%s, costo_articulo=%s
                WHERE codigo_articulo=%s
            """, datos)
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Artículo actualizado correctamente")
            self.cargar_datos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")

    def eliminar_articulo(self):
        if not hasattr(self, "codigo_seleccionado"):
            QMessageBox.warning(self, "Advertencia", "Seleccione un artículo de la tabla.")
            return
        try:
            cursor.execute("DELETE FROM articulos WHERE codigo_articulo=%s", (self.codigo_seleccionado,))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Artículo eliminado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")

    def limpiar_campos(self):
        self.input_codigo.clear()
        self.input_nombre.clear()
        self.checkbox_activado.setChecked(False)
        self.input_precio.clear()
        self.input_costo.clear()
