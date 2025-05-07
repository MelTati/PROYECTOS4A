import mysql.connector
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QLabel, QLineEdit, QDateEdit, QMessageBox, QApplication
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QIcon
from detalles_compras import VentanaDetallesCompras  # Asegúrate de tener este archivo

# Conexión
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="mydb_conejo_feliz"
)
conexion.autocommit = True
cursor = conexion.cursor(dictionary=True)

class VentanaCompras(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Compras")
        self.resize(1000, 500)
        self.setWindowIcon(QIcon("icons/shopping-cart.png"))

        self.init_ui()
        self.cargar_comboboxes()
        self.cargar_compras()

    def init_ui(self):
        layout = QVBoxLayout()

        filtros = QHBoxLayout()

        self.combo_proveedor = QComboBox()
        filtros.addWidget(QLabel("Proveedor:"))
        filtros.addWidget(self.combo_proveedor)

        self.fecha_compra = QDateEdit(QDate.currentDate())
        self.fecha_compra.setCalendarPopup(True)
        filtros.addWidget(QLabel("Fecha:"))
        filtros.addWidget(self.fecha_compra)

        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Ingrese ID de Compra")
        filtros.addWidget(QLabel("ID de Compra:"))
        filtros.addWidget(self.input_codigo)

        btn_agregar = QPushButton("Agregar Compra")
        btn_agregar.clicked.connect(self.agregar_compra)
        filtros.addWidget(btn_agregar)

        btn_eliminar = QPushButton("Eliminar Compra")
        btn_eliminar.clicked.connect(self.eliminar_compra)
        filtros.addWidget(btn_eliminar)

        btn_detalles = QPushButton("Ver Detalles")
        btn_detalles.clicked.connect(self.ver_detalles)
        filtros.addWidget(btn_detalles)

        layout.addLayout(filtros)

        # --- Tabla de compras ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Proveedor", "Fecha", "Subtotal"])
        layout.addWidget(self.tabla)

        self.setLayout(layout)

    def cargar_comboboxes(self):
        self.combo_proveedor.clear()
        cursor.execute("SELECT RFC, nombre_proveedor FROM proveedor")
        for proveedor in cursor.fetchall():
            self.combo_proveedor.addItem(proveedor["nombre_proveedor"], proveedor["RFC"])

    def cargar_compras(self):
        self.tabla.setRowCount(0)

        cursor.execute("""
            SELECT c.id_compras, p.nombre_proveedor, c.fecha_compras,
                   IFNULL(SUM(dc.subtotal), 0) AS total
            FROM compras c
            JOIN proveedor p ON c.RFC = p.RFC 
            LEFT JOIN detalles_compras dc ON c.id_compras = dc.id_compras
            GROUP BY c.id_compras
            ORDER BY c.id_compras DESC
        """)
        compras = cursor.fetchall()
        for fila, compra in enumerate(compras):
            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(compra["id_compras"])))
            self.tabla.setItem(fila, 1, QTableWidgetItem(compra["nombre_proveedor"]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(str(compra["fecha_compras"])))
            self.tabla.setItem(fila, 3, QTableWidgetItem(f"${compra['total']:.2f}"))

    def agregar_compra(self):
        id_compra = self.input_codigo.text().strip()  # Obtener el ID de Compra desde el QLineEdit
        rfc_proveedor = self.combo_proveedor.currentData()  # Usamos RFC en lugar de id_proveedor
        fecha = self.fecha_compra.date().toString("yyyy-MM-dd")

        if not id_compra:  # Verificar que el campo del ID de Compra no esté vacío
            QMessageBox.warning(self, "Advertencia", "El ID de compra es obligatorio")
            return

        try:
            cursor.execute("""
                INSERT INTO compras (id_compras, RFC, fecha_compras)
                VALUES (%s, %s, %s)
            """, (id_compra, rfc_proveedor, fecha))
            conexion.commit()

            self.cargar_compras()
            QMessageBox.information(self, "Éxito", f"Compra #{id_compra} agregada correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar la compra: {e}")

    def eliminar_compra(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Selecciona una compra para eliminar")
            return

        id_compra = self.tabla.item(fila, 0).text()

        confirmar = QMessageBox.question(
            self, "Confirmar", f"¿Eliminar la compra #{id_compra}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmar == QMessageBox.StandardButton.Yes:
            try:
                cursor.execute("DELETE FROM detalles_compras WHERE id_compras = %s", (id_compra,))
                cursor.execute("DELETE FROM compras WHERE id_compras = %s", (id_compra,))
                conexion.commit()
                self.cargar_compras()
                QMessageBox.information(self, "Éxito", "Compra eliminada")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar la compra: {e}")

    def ver_detalles(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Selecciona una compra para ver detalles")
            return

        id_compra = int(self.tabla.item(fila, 0).text())
        self.detalle_ventana = VentanaDetallesCompras(id_compras=id_compra)
        self.detalle_ventana.detalle_modificado.connect(self.cargar_compras)
        self.detalle_ventana.show()

    def actualizar_compra(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Selecciona una compra para actualizar")
            return

        id_compra = self.tabla.item(fila, 0).text()
        rfc_proveedor = self.combo_proveedor.currentData()
        fecha = self.fecha_compra.date().toString("yyyy-MM-dd")

        try:
            cursor.execute("""
                UPDATE compras
                SET RFC = %s, fecha_compras = %s
                WHERE id_compras = %s
            """, (rfc_proveedor, fecha, id_compra))
            conexion.commit()
            self.cargar_compras()
            QMessageBox.information(self, "Éxito", "Compra actualizada correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la compra: {e}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ventana = VentanaCompras()
    ventana.show()
    sys.exit(app.exec())
