import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox
)

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="mydb_conejo_feliz"
)
cursor = conexion.cursor(dictionary=True)

class VentanaTickets(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Tickets")
        self.resize(800, 400)
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout()

        # Tabla de tickets
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels([
            "ID Ticket", "Establecimiento", "Dirección", "Modo de Pago"
        ])
        self.tabla.cellClicked.connect(self.seleccionar_fila)
        layout.addWidget(self.tabla)

        # Campos de entrada
        form_layout = QHBoxLayout()
        self.input_id = QLineEdit()
        self.input_nombre = QLineEdit()
        self.input_direccion = QLineEdit()
        self.combo_pago = QComboBox()

        self.input_id.setPlaceholderText("ID Ticket")
        self.input_nombre.setPlaceholderText("Nombre Establecimiento")
        self.input_direccion.setPlaceholderText("Dirección Establecimiento")

        form_layout.addWidget(self.input_id)
        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(self.input_direccion)
        form_layout.addWidget(self.combo_pago)
        layout.addLayout(form_layout)

        # Botones
        btn_layout = QHBoxLayout()
        btn_agregar = QPushButton("Agregar")
        btn_actualizar = QPushButton("Actualizar")
        btn_eliminar = QPushButton("Eliminar")

        btn_agregar.clicked.connect(self.agregar_ticket)
        btn_actualizar.clicked.connect(self.actualizar_ticket)
        btn_eliminar.clicked.connect(self.eliminar_ticket)

        btn_layout.addWidget(btn_agregar)
        btn_layout.addWidget(btn_actualizar)
        btn_layout.addWidget(btn_eliminar)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def cargar_datos(self):
        try:
            # Cargar modos de pago
            cursor.execute("SELECT id_modo_pago, tipo FROM modo_pago")
            pagos = cursor.fetchall()
            self.combo_pago.clear()
            for pago in pagos:
                self.combo_pago.addItem(pago["tipo"], pago["id_modo_pago"])

            # Cargar tickets
            cursor.execute("""
                SELECT 
                    t.id_ticket,
                    t.nombre_establec,
                    t.direcc_establec,
                    m.tipo AS modo_pago
                FROM ticket t
                JOIN modo_pago m ON t.id_modo_pago = m.id_modo_pago
            """)
            resultados = cursor.fetchall()

            self.tabla.setRowCount(0)
            for i, ticket in enumerate(resultados):
                self.tabla.insertRow(i)
                self.tabla.setItem(i, 0, QTableWidgetItem(ticket["id_ticket"]))
                self.tabla.setItem(i, 1, QTableWidgetItem(ticket["nombre_establec"]))
                self.tabla.setItem(i, 2, QTableWidgetItem(ticket["direcc_establec"]))
                self.tabla.setItem(i, 3, QTableWidgetItem(ticket["modo_pago"]))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos: {e}")

    def seleccionar_fila(self, fila, _):
        self.input_id.setText(self.tabla.item(fila, 0).text())
        self.input_nombre.setText(self.tabla.item(fila, 1).text())
        self.input_direccion.setText(self.tabla.item(fila, 2).text())

        tipo_pago = self.tabla.item(fila, 3).text()
        index_pago = self.combo_pago.findText(tipo_pago)
        if index_pago != -1:
            self.combo_pago.setCurrentIndex(index_pago)

    def limpiar_campos(self):
        self.input_id.clear()
        self.input_nombre.clear()
        self.input_direccion.clear()
        self.combo_pago.setCurrentIndex(0)

    def validar_campos(self):
        if not all([
            self.input_id.text(), self.input_nombre.text(),
            self.input_direccion.text()
        ]):
            QMessageBox.warning(self, "Advertencia", "Por favor, complete todos los campos.")
            return False
        return True

    def agregar_ticket(self):
        if not self.validar_campos():
            return
        try:
            id_modo_pago = self.combo_pago.currentData()
            datos = (
                self.input_id.text(),
                self.input_nombre.text(),
                self.input_direccion.text(),
                id_modo_pago
            )
            cursor.execute("""
                INSERT INTO ticket (id_ticket, nombre_establec, direcc_establec, id_modo_pago)
                VALUES (%s, %s, %s, %s)
            """, datos)
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Ticket agregado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar: {e}")

    def actualizar_ticket(self):
        if not self.validar_campos():
            return
        try:
            id_modo_pago = self.combo_pago.currentData()
            datos = (
                self.input_nombre.text(),
                self.input_direccion.text(),
                id_modo_pago,
                self.input_id.text()
            )
            cursor.execute("""
                UPDATE ticket
                SET nombre_establec=%s, direcc_establec=%s, id_modo_pago=%s
                WHERE id_ticket=%s
            """, datos)
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Ticket actualizado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")

    def eliminar_ticket(self):
        id_ticket = self.input_id.text()
        if not id_ticket:
            QMessageBox.warning(self, "Advertencia", "Ingrese el ID del ticket a eliminar.")
            return
        try:
            cursor.execute("DELETE FROM ticket WHERE id_ticket=%s", (id_ticket,))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Ticket eliminado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")


