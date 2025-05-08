import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QApplication
)

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="mydb_conejo_feliz"
)
cursor = conexion.cursor(dictionary=True)

class VentanaCategorias(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Categorías")
        self.resize(300, 200)
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout()

        # Tabla de categorías
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["ID", "Tipo de Categoría"])
        self.tabla.cellClicked.connect(self.seleccionar_fila)
        layout.addWidget(self.tabla)

        # Formulario
        form_layout = QHBoxLayout()
        self.input_id = QLineEdit()
        self.input_tipo = QLineEdit()

        self.input_id.setPlaceholderText("ID (auto)")
        self.input_id.setDisabled(True)
        self.input_tipo.setPlaceholderText("Tipo de Categoría")

        form_layout.addWidget(self.input_id)
        form_layout.addWidget(self.input_tipo)
        layout.addLayout(form_layout)

        # Botones
        botones_layout = QHBoxLayout()
        btn_agregar = QPushButton("Agregar")
        btn_actualizar = QPushButton("Actualizar")
        btn_eliminar = QPushButton("Eliminar")

        btn_agregar.clicked.connect(self.agregar_categoria)
        btn_actualizar.clicked.connect(self.actualizar_categoria)
        btn_eliminar.clicked.connect(self.eliminar_categoria)

        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_actualizar)
        botones_layout.addWidget(btn_eliminar)
        layout.addLayout(botones_layout)

        self.setLayout(layout)

    def cargar_datos(self):
        try:
            cursor.execute("SELECT * FROM categorias")
            resultados = cursor.fetchall()
            self.tabla.setRowCount(0)
            for i, fila in enumerate(resultados):
                self.tabla.insertRow(i)
                self.tabla.setItem(i, 0, QTableWidgetItem(str(fila["id_categorias"])))
                self.tabla.setItem(i, 1, QTableWidgetItem(fila["tipo_categoria"] or ""))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la tabla: {e}")

    def seleccionar_fila(self, fila, _):
        self.input_id.setText(self.tabla.item(fila, 0).text())
        self.input_tipo.setText(self.tabla.item(fila, 1).text())

    def validar_campos(self):
        if not self.input_tipo.text().strip():
            QMessageBox.warning(self, "Advertencia", "Ingrese el tipo de categoría.")
            return False
        return True

    def agregar_categoria(self):
        if not self.validar_campos():
            return
        try:
            cursor.execute(
                "INSERT INTO categorias (tipo_categoria) VALUES (%s)",
                (self.input_tipo.text().strip(),)
            )
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Categoría agregada correctamente.")
            self.cargar_datos()
            self.limpiar_campos()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar la categoría: {e}")

    def actualizar_categoria(self):
        if not self.validar_campos() or not self.input_id.text().strip():
            QMessageBox.warning(self, "Advertencia", "Seleccione una categoría de la tabla.")
            return
        try:
            cursor.execute(
                "UPDATE categorias SET tipo_categoria=%s WHERE id_categorias=%s",
                (self.input_tipo.text().strip(), self.input_id.text().strip())
            )
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Categoría actualizada correctamente.")
            self.cargar_datos()
            self.limpiar_campos()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la categoría: {e}")

    def eliminar_categoria(self):
        id_categoria = self.input_id.text().strip()
        if not id_categoria:
            QMessageBox.warning(self, "Advertencia", "Seleccione una categoría de la tabla.")
            return
        confirmacion = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro de eliminar la categoría con ID '{id_categoria}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmacion == QMessageBox.StandardButton.Yes:
            try:
                cursor.execute("DELETE FROM categorias WHERE id_categorias=%s", (id_categoria,))
                conexion.commit()
                QMessageBox.information(self, "Éxito", "Categoría eliminada correctamente.")
                self.cargar_datos()
                self.limpiar_campos()
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar la categoría: {e}")

    def limpiar_campos(self):
        self.input_id.clear()
        self.input_tipo.clear()

    def closeEvent(self, event):
        cursor.close()
        conexion.close()
        event.accept()
