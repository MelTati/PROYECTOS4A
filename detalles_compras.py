import mysql.connector
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QSpinBox, QApplication, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="mydb_conejo_feliz"
)
conexion.autocommit = True
cursor = conexion.cursor(dictionary=True)

class VentanaDetallesCompras(QWidget):
    detalle_modificado = pyqtSignal()

    def __init__(self, id_compras=None):
        super().__init__()
        self.id_compras = id_compras
        self.setWindowTitle(f"Detalles de Compra #{self.id_compras}")
        self.resize(1000, 500)
        self.setWindowIcon(QIcon("icons/details.png"))

        if self.id_compras is None:
            self.obtener_ultima_compra()

        self.init_ui()
        self.cargar_datos()

    def obtener_ultima_compra(self):
        cursor.execute("SELECT id_compras FROM compras ORDER BY id_compras DESC LIMIT 1")
        resultado = cursor.fetchone()
        self.id_compras = resultado["id_compras"] if resultado else None

    def init_ui(self):
        layout = QVBoxLayout()

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "ID Compra", "Artículo", "Marca", "Categoría",
            "Precio Unitario", "Cantidad", "Subtotal"
        ])
        self.tabla.setColumnWidth(1, 200)
        self.tabla.setColumnWidth(2, 100)
        self.tabla.setColumnWidth(3, 120)
        layout.addWidget(self.tabla)

        form_layout = QHBoxLayout()

        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Código o nombre del artículo")
        self.input_codigo.returnPressed.connect(self.buscar_articulo_por_codigo)
        form_layout.addWidget(self.input_codigo)

        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 999)
        self.spin_cantidad.setValue(1)
        form_layout.addWidget(QLabel("Cantidad:"))
        form_layout.addWidget(self.spin_cantidad)

        btn_agregar = QPushButton("Agregar")
        btn_agregar.clicked.connect(self.buscar_articulo_por_codigo)
        form_layout.addWidget(btn_agregar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_eliminar.clicked.connect(self.eliminar_detalle)
        form_layout.addWidget(btn_eliminar)

        layout.addLayout(form_layout)
        self.setLayout(layout)

    def cargar_datos(self):
        if not self.id_compras:
            return

        try:
            cursor.execute("""
                SELECT dc.id_compras, dc.codigo_articulo, a.nombre_articulo,
                       a.costo_articulo, dc.cantidad, dc.subtotal,
                       m.nombre_marca, c.tipo_categoria
                FROM detalles_compras dc
                JOIN articulos a ON dc.codigo_articulo = a.codigo_articulo
                JOIN marcas m ON a.id_marca = m.id_marca
                JOIN categorias c ON a.id_categorias = c.id_categorias
                WHERE dc.id_compras = %s
                ORDER BY a.nombre_articulo
            """, (self.id_compras,))
            
            detalles = cursor.fetchall()
            self.tabla.setRowCount(0)

            for fila, detalle in enumerate(detalles):
                self.tabla.insertRow(fila)
                self.tabla.setItem(fila, 0, QTableWidgetItem(str(detalle["id_compras"])))
                self.tabla.setItem(fila, 1, QTableWidgetItem(detalle["nombre_articulo"]))
                self.tabla.setItem(fila, 2, QTableWidgetItem(detalle["nombre_marca"]))
                self.tabla.setItem(fila, 3, QTableWidgetItem(detalle["tipo_categoria"]))
                self.tabla.setItem(fila, 4, QTableWidgetItem(f"${detalle['costo_articulo']:.2f}"))
                self.tabla.setItem(fila, 5, QTableWidgetItem(str(detalle["cantidad"])))
                self.tabla.setItem(fila, 6, QTableWidgetItem(f"${detalle['subtotal']:.2f}"))

            cursor.execute("""
                SELECT SUM(subtotal) as total FROM detalles_compras
                WHERE id_compras = %s
            """, (self.id_compras,))
            total = cursor.fetchone()["total"] or 0

            self.tabla.insertRow(self.tabla.rowCount())
            fila_total = self.tabla.rowCount() - 1
            self.tabla.setItem(fila_total, 5, QTableWidgetItem("TOTAL:"))
            self.tabla.setItem(fila_total, 6, QTableWidgetItem(f"${total:.2f}"))
            self.tabla.item(fila_total, 6).setBackground(Qt.GlobalColor.lightGray)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los detalles: {e}")

    def buscar_articulo_por_codigo(self):
        entrada = self.input_codigo.text().strip()
        cantidad = self.spin_cantidad.value()

        if not entrada:
            QMessageBox.warning(self, "Advertencia", "Ingrese un código o nombre de artículo")
            return

        try:
            cursor.execute("""
                SELECT codigo_articulo, nombre_articulo, costo_articulo 
                FROM articulos 
                WHERE (codigo_articulo = %s OR nombre_articulo LIKE %s) 
                AND activacion_articulo = 1
                LIMIT 1
            """, (entrada, f"%{entrada}%"))
            articulo = cursor.fetchone()

            if not articulo:
                QMessageBox.warning(self, "No encontrado", "Artículo no encontrado o no activo")
                return

            if not self.id_compras:
                QMessageBox.critical(self, "Error", "No hay una compra asociada")
                return

            cursor.execute("""
                SELECT cantidad FROM detalles_compras 
                WHERE id_compras = %s AND codigo_articulo = %s
            """, (self.id_compras, articulo["codigo_articulo"]))
            existente = cursor.fetchone()

            if existente:
                nueva_cantidad = existente["cantidad"] + cantidad
                nuevo_subtotal = nueva_cantidad * articulo["costo_articulo"]

                cursor.execute("""
                    UPDATE detalles_compras
                    SET cantidad = %s, subtotal = %s
                    WHERE id_compras = %s AND codigo_articulo = %s
                """, (nueva_cantidad, nuevo_subtotal, self.id_compras, articulo["codigo_articulo"]))
                mensaje = f"Cantidad actualizada a {nueva_cantidad}"
            else:
                subtotal = cantidad * articulo["costo_articulo"]
                cursor.execute("""
                    INSERT INTO detalles_compras 
                    (id_compras, codigo_articulo, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s)
                """, (self.id_compras, articulo["codigo_articulo"], cantidad, subtotal))
                mensaje = "Artículo agregado a la compra"

            conexion.commit()
            self.cargar_datos()
            self.detalle_modificado.emit()
            QTimer.singleShot(100, lambda: self.detalle_modificado.emit())
            QApplication.processEvents()

            QMessageBox.information(self, "Éxito", mensaje)
            self.input_codigo.clear()
            self.spin_cantidad.setValue(1)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar artículo: {e}")

    def eliminar_detalle(self):
        fila = self.tabla.currentRow()
        if fila < 0 or fila >= self.tabla.rowCount() - 1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un artículo para eliminar")
            return

        nombre_articulo = self.tabla.item(fila, 1).text()

        try:
            cursor.execute("""
                SELECT codigo_articulo FROM articulos 
                WHERE nombre_articulo = %s LIMIT 1
            """, (nombre_articulo,))
            resultado = cursor.fetchone()

            if not resultado:
                QMessageBox.warning(self, "Error", "No se pudo identificar el artículo")
                return

            codigo_articulo = resultado["codigo_articulo"]

            respuesta = QMessageBox.question(
                self, "Confirmar",
                f"¿Eliminar '{nombre_articulo}' de la compra?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                cursor.execute("""
                    DELETE FROM detalles_compras
                    WHERE id_compras = %s AND codigo_articulo = %s
                """, (self.id_compras, codigo_articulo))
                conexion.commit()

                self.cargar_datos()
                self.detalle_modificado.emit()
                QTimer.singleShot(100, lambda: self.detalle_modificado.emit())
                QMessageBox.information(self, "Éxito", "Artículo eliminado")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")

    def closeEvent(self, event):
        self.detalle_modificado.emit()
        event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ventana = VentanaDetallesCompras()
    ventana.show()
    sys.exit(app.exec())