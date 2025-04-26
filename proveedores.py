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

class VentanaProveedor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Proveedores")
        self.resize(700, 400)
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout()

        # Tabla de proveedores
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["RFC", "Nombre", "Dirección", "Teléfono", "Email"])
        self.tabla.cellClicked.connect(self.seleccionar_fila)
        layout.addWidget(self.tabla)

        # Formulario
        form_layout = QHBoxLayout()
        self.input_RFC = QLineEdit()
        self.input_nombre = QLineEdit()
        self.input_direccion = QLineEdit()
        self.input_telefono = QLineEdit()
        self.input_email = QLineEdit()

        self.input_RFC.setPlaceholderText("RFC")
        self.input_nombre.setPlaceholderText("Nombre")
        self.input_direccion.setPlaceholderText("Dirección")
        self.input_telefono.setPlaceholderText("Teléfono")
        self.input_email.setPlaceholderText("Email")

        form_layout.addWidget(self.input_RFC)
        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(self.input_direccion)
        form_layout.addWidget(self.input_telefono)
        form_layout.addWidget(self.input_email)
        layout.addLayout(form_layout)

        # Botones
        botones_layout = QHBoxLayout()
        btn_agregar = QPushButton("Agregar")
        btn_actualizar = QPushButton("Actualizar")
        btn_eliminar = QPushButton("Eliminar")

        btn_agregar.clicked.connect(self.agregar_proveedor)
        btn_actualizar.clicked.connect(self.actualizar_proveedor)
        btn_eliminar.clicked.connect(self.eliminar_proveedor)

        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_actualizar)
        botones_layout.addWidget(btn_eliminar)
        layout.addLayout(botones_layout)

        self.setLayout(layout)

    def cargar_datos(self):
        try:
            cursor.execute("SELECT * FROM proveedor")
            resultados = cursor.fetchall()
            self.tabla.setRowCount(0)
            for fila_num, proveedor in enumerate(resultados):
                self.tabla.insertRow(fila_num)
                self.tabla.setItem(fila_num, 0, QTableWidgetItem(proveedor["RFC"]))
                self.tabla.setItem(fila_num, 1, QTableWidgetItem(proveedor["nombre_proveedor"] or ""))
                self.tabla.setItem(fila_num, 2, QTableWidgetItem(proveedor["direccion"] or ""))
                self.tabla.setItem(fila_num, 3, QTableWidgetItem(proveedor["telefono"] or ""))
                self.tabla.setItem(fila_num, 4, QTableWidgetItem(proveedor["email"] or ""))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la tabla: {e}")

    def seleccionar_fila(self, fila, _):
        self.input_RFC.setText(self.tabla.item(fila, 0).text())
        self.input_nombre.setText(self.tabla.item(fila, 1).text())
        self.input_direccion.setText(self.tabla.item(fila, 2).text())
        self.input_telefono.setText(self.tabla.item(fila, 3).text())
        self.input_email.setText(self.tabla.item(fila, 4).text())

    def validar_campos(self):
        if not self.input_RFC.text().strip() or not self.input_nombre.text().strip() or \
           not self.input_direccion.text().strip() or not self.input_telefono.text().strip() or \
           not self.input_email.text().strip():
            QMessageBox.warning(self, "Advertencia", "Por favor complete todos los campos.")
            return False
        return True

    def agregar_proveedor(self):
        if not self.validar_campos():
            return
        try:
            datos = (
                self.input_RFC.text().strip(),
                self.input_nombre.text().strip(),
                self.input_direccion.text().strip(),
                self.input_telefono.text().strip(),
                self.input_email.text().strip()
            )
            cursor.execute(
                "INSERT INTO proveedor (RFC, nombre_proveedor, direccion, telefono, email) VALUES (%s, %s, %s, %s, %s)",
                datos
            )
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Proveedor agregado correctamente.")
            self.cargar_datos()
            self.limpiar_campos()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el proveedor: {e}")

    def actualizar_proveedor(self):
        if not self.validar_campos():
            return
        try:
            datos = (
                self.input_nombre.text().strip(),
                self.input_direccion.text().strip(),
                self.input_telefono.text().strip(),
                self.input_email.text().strip(),
                self.input_RFC.text().strip()
            )
            cursor.execute(
                "UPDATE proveedor SET nombre_proveedor=%s, direccion=%s, telefono=%s, email=%s WHERE RFC=%s",
                datos
            )
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Proveedor actualizado correctamente.")
            self.cargar_datos()
            self.limpiar_campos()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el proveedor: {e}")

    def eliminar_proveedor(self):
        rfc = self.input_RFC.text().strip()
        if not rfc:
            QMessageBox.warning(self, "Advertencia", "Seleccione un proveedor de la tabla.")
            return
        confirmacion = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro de eliminar el proveedor con RFC '{rfc}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmacion == QMessageBox.StandardButton.Yes:
            try:
                cursor.execute("DELETE FROM proveedor WHERE RFC=%s", (rfc,))
                conexion.commit()
                QMessageBox.information(self, "Éxito", "Proveedor eliminado correctamente.")
                self.cargar_datos()
                self.limpiar_campos()
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el proveedor: {e}")

    def limpiar_campos(self):
        self.input_RFC.clear()
        self.input_nombre.clear()
        self.input_direccion.clear()
        self.input_telefono.clear()
        self.input_email.clear()
