import mysql.connector
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QApplication
)
from PyQt6.QtCore import pyqtSignal

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="mydb_conejo_feliz"
)
cursor = conexion.cursor(dictionary=True)

class VentanaClientes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Clientes")
        self.resize(600, 400)
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout()

        # Tabla de clientes
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono"])
        self.tabla.cellClicked.connect(self.seleccionar_fila)
        layout.addWidget(self.tabla)

        # Campos de entrada (sin ID porque es autoincremental)
        form_layout = QHBoxLayout()
        self.input_nombre = QLineEdit()
        self.input_telefono = QLineEdit()

        self.input_nombre.setPlaceholderText("Nombre")
        self.input_telefono.setPlaceholderText("Teléfono")

        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(self.input_telefono)
        layout.addLayout(form_layout)

        # Botones
        botones_layout = QHBoxLayout()
        btn_agregar = QPushButton("Agregar")
        btn_actualizar = QPushButton("Actualizar")
        btn_eliminar = QPushButton("Eliminar")

        btn_agregar.clicked.connect(self.agregar_cliente)
        btn_actualizar.clicked.connect(self.actualizar_cliente)
        btn_eliminar.clicked.connect(self.eliminar_cliente)

        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_actualizar)
        botones_layout.addWidget(btn_eliminar)
        layout.addLayout(botones_layout)

        self.setLayout(layout)

    def cargar_datos(self):
        try:
            cursor.execute("SELECT * FROM cliente")
            resultados = cursor.fetchall()
            self.tabla.setRowCount(0)
            for fila_num, cliente in enumerate(resultados):
                self.tabla.insertRow(fila_num)
                self.tabla.setItem(fila_num, 0, QTableWidgetItem(str(cliente["id_cliente"])))
                self.tabla.setItem(fila_num, 1, QTableWidgetItem(cliente["nombre"] or ""))
                self.tabla.setItem(fila_num, 2, QTableWidgetItem(cliente["telefono"]))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la tabla: {e}")

    def seleccionar_fila(self, fila, _):
        self.id_seleccionado = int(self.tabla.item(fila, 0).text())
        self.input_nombre.setText(self.tabla.item(fila, 1).text())
        self.input_telefono.setText(self.tabla.item(fila, 2).text())

    def validar_campos(self):
        if not self.input_nombre.text().strip() or not self.input_telefono.text().strip():
            QMessageBox.warning(self, "Advertencia", "Por favor complete todos los campos.")
            return False
        return True

    def agregar_cliente(self):
        if not self.validar_campos():
            return
        try:
            datos = (
                self.input_nombre.text().strip(),
                self.input_telefono.text().strip()
            )
            cursor.execute("INSERT INTO cliente (nombre, telefono) VALUES (%s, %s)", datos)
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Cliente agregado correctamente")
            self.cargar_datos()
            self.input_nombre.clear()
            self.input_telefono.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar: {e}")

    def actualizar_cliente(self):
        if not hasattr(self, "id_seleccionado"):
            QMessageBox.warning(self, "Advertencia", "Seleccione un cliente de la tabla.")
            return
        if not self.validar_campos():
            return
        try:
            datos = (
                self.input_nombre.text().strip(),
                self.input_telefono.text().strip(),
                self.id_seleccionado
            )
            cursor.execute("UPDATE cliente SET nombre=%s, telefono=%s WHERE id_cliente=%s", datos)
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
            self.cargar_datos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")

    def eliminar_cliente(self):
        if not hasattr(self, "id_seleccionado"):
            QMessageBox.warning(self, "Advertencia", "Seleccione un cliente de la tabla.")
            return
        try:
            cursor.execute("DELETE FROM cliente WHERE id_cliente=%s", (self.id_seleccionado,))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
            self.cargar_datos()
            self.input_nombre.clear()
            self.input_telefono.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")