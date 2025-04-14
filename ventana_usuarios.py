import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox
)

# Configuración de la conexión MySQL
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="mydb_conejo_feliz"
)
cursor = conexion.cursor(dictionary=True)

class VentanaUsuarios(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Usuarios")
        self.resize(800, 400)
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Contraseña", "Rol"])
        self.tabla.cellClicked.connect(self.seleccionar_fila)
        layout.addWidget(self.tabla)

        form_layout = QHBoxLayout()
        self.input_id = QLineEdit()
        self.input_nombre = QLineEdit()
        self.input_telefono = QLineEdit()
        self.input_password = QLineEdit()
        
        self.input_id.setPlaceholderText("ID")
        self.input_nombre.setPlaceholderText("Nombre")
        self.input_telefono.setPlaceholderText("Teléfono")
        self.input_password.setPlaceholderText("Contraseña")

        # ComboBox para elegir el rol
        self.combo_roles = QComboBox()
        self.combo_roles.setPlaceholderText("Seleccionar Rol")
        
        form_layout.addWidget(self.input_id)
        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(self.input_telefono)
        form_layout.addWidget(self.input_password)
        form_layout.addWidget(self.combo_roles)
        layout.addLayout(form_layout)

        botones_layout = QHBoxLayout()
        btn_agregar = QPushButton("Agregar")
        btn_actualizar = QPushButton("Actualizar")
        btn_eliminar = QPushButton("Eliminar")

        btn_agregar.clicked.connect(self.agregar_usuario)
        btn_actualizar.clicked.connect(self.actualizar_usuario)
        btn_eliminar.clicked.connect(self.eliminar_usuario)

        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_actualizar)
        botones_layout.addWidget(btn_eliminar)
        layout.addLayout(botones_layout)

        self.setLayout(layout)

    def cargar_datos(self):
        try:
            # Cargar los roles en el ComboBox
            cursor.execute("SELECT id_roles, cargo FROM roles")
            roles = cursor.fetchall()
            self.combo_roles.clear()  # Limpiar combo antes de añadir
            for rol in roles:
                self.combo_roles.addItem(rol["cargo"], rol["id_roles"])

            cursor.execute("""
                SELECT u.id_usuario, u.nombre_usuario, u.telefono, u.password, r.cargo
                FROM usuarios u
                JOIN roles r ON u.id_roles = r.id_roles
            """)
            resultados = cursor.fetchall()
            self.tabla.setRowCount(0)
            for fila_num, usuario in enumerate(resultados):
                self.tabla.insertRow(fila_num)
                self.tabla.setItem(fila_num, 0, QTableWidgetItem(str(usuario["id_usuario"])))
                self.tabla.setItem(fila_num, 1, QTableWidgetItem(usuario["nombre_usuario"]))
                self.tabla.setItem(fila_num, 2, QTableWidgetItem(usuario["telefono"]))
                self.tabla.setItem(fila_num, 3, QTableWidgetItem(usuario["password"]))
                self.tabla.setItem(fila_num, 4, QTableWidgetItem(usuario["cargo"]))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la tabla: {e}")

    def seleccionar_fila(self, fila, _):
        self.input_id.setText(self.tabla.item(fila, 0).text())
        self.input_nombre.setText(self.tabla.item(fila, 1).text())
        self.input_telefono.setText(self.tabla.item(fila, 2).text())
        self.input_password.setText(self.tabla.item(fila, 3).text())
        # Seleccionar el rol por nombre
        rol_nombre = self.tabla.item(fila, 4).text()
        index_rol = self.combo_roles.findText(rol_nombre)
        if index_rol != -1:
            self.combo_roles.setCurrentIndex(index_rol)

    def validar_campos(self):
        if not self.input_nombre.text() or not self.input_telefono.text() or not self.input_password.text() or not self.combo_roles.currentText():
            QMessageBox.warning(self, "Advertencia", "Por favor complete todos los campos.")
            return False
        return True

    def agregar_usuario(self):
        if not self.validar_campos():
            return
        try:
            rol_id = self.combo_roles.currentData()  # Obtener ID del rol seleccionado
            datos = (
                int(self.input_id.text()),
                self.input_nombre.text(),
                self.input_telefono.text(),
                self.input_password.text(),
                rol_id
            )
            cursor.execute("""
                INSERT INTO usuarios (id_usuario, nombre_usuario, telefono, password, id_roles)
                VALUES (%s, %s, %s, %s, %s)
            """, datos)
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Usuario agregado correctamente")
            self.cargar_datos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar: {e}")

    def actualizar_usuario(self):
        if not self.validar_campos():
            return
        try:
            rol_id = self.combo_roles.currentData()  # Obtener ID del rol seleccionado
            datos = (
                self.input_nombre.text(),
                self.input_telefono.text(),
                self.input_password.text(),
                rol_id,
                int(self.input_id.text())
            )
            cursor.execute("""
                UPDATE usuarios
                SET nombre_usuario=%s, telefono=%s, password=%s, id_roles=%s
                WHERE id_usuario=%s
            """, datos)
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente")
            self.cargar_datos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")

    def eliminar_usuario(self):
        if not self.input_id.text():
            QMessageBox.warning(self, "Advertencia", "Por favor ingrese el ID del usuario a eliminar.")
            return
        try:
            id_usuario = int(self.input_id.text())
            cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id_usuario,))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Usuario eliminado correctamente")
            self.cargar_datos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")
