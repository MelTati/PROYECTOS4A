import mysql.connector
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import pyqtSignal  # 👈 Importar para señales personalizadas

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="mydb_conejo_feliz"
)
cursor = conexion.cursor(dictionary=True)

class VentanaDetallesVentas(QWidget):
    detalle_modificado = pyqtSignal()  # 👈 Señal personalizada
    def __init__(self, id_venta):
        super().__init__()
        self.id_venta = id_venta
        self.setWindowTitle(f"Detalles de Venta #{self.id_venta}")
        self.resize(800, 400)
        self.init_ui()
        self.cargar_articulos()
        self.cargar_detalles()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Código", "Nombre Artículo", "Cantidad", "Subtotal"])
        self.tabla.cellClicked.connect(self.seleccionar_fila)
        layout.addWidget(self.tabla)

        form_layout = QHBoxLayout()

        self.combo_articulos = QComboBox()
        self.combo_articulos.setPlaceholderText("Seleccione un artículo")
        form_layout.addWidget(self.combo_articulos)

        self.input_cantidad = QSpinBox()
        self.input_cantidad.setMinimum(1)
        self.input_cantidad.setMaximum(1000)
        form_layout.addWidget(QLabel("Cantidad:"))
        form_layout.addWidget(self.input_cantidad)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar")
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_eliminar = QPushButton("Eliminar")

        self.btn_agregar.clicked.connect(self.agregar_detalle)
        self.btn_actualizar.clicked.connect(self.actualizar_detalle)
        self.btn_eliminar.clicked.connect(self.eliminar_detalle)

        btn_layout.addWidget(self.btn_agregar)
        btn_layout.addWidget(self.btn_actualizar)
        btn_layout.addWidget(self.btn_eliminar)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def cargar_articulos(self):
        try:
            cursor.execute("SELECT codigo_articulo, nombre_articulo, precio_articulo FROM articulos")
            articulos = cursor.fetchall()
            self.combo_articulos.clear()
            for articulo in articulos:
                self.combo_articulos.addItem(
                    f"{articulo['nombre_articulo']} - ${articulo['precio_articulo']}",
                    (articulo["codigo_articulo"], articulo["precio_articulo"])
                )
            self.cargar_detalles()
            self.detalle_modificado.emit() 
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los artículos: {e}")

    def cargar_detalles(self):
        try:
            cursor.execute(""" 
                SELECT dv.codigo_articulo, a.nombre_articulo, dv.cantidad, dv.subtotal
                FROM detalles_ventas dv
                JOIN articulos a ON dv.codigo_articulo = a.codigo_articulo
                WHERE dv.id_ventas = %s
            """, (self.id_venta,))
            detalles = cursor.fetchall()
            self.tabla.setRowCount(0)
            for row, detalle in enumerate(detalles):
                self.tabla.insertRow(row)
                self.tabla.setItem(row, 0, QTableWidgetItem(str(detalle["codigo_articulo"])))
                self.tabla.setItem(row, 1, QTableWidgetItem(detalle["nombre_articulo"]))
                self.tabla.setItem(row, 2, QTableWidgetItem(str(detalle["cantidad"])))
                self.tabla.setItem(row, 3, QTableWidgetItem(f"${detalle['subtotal']:.2f}"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los detalles: {e}")

    def seleccionar_fila(self, fila, _):
        codigo = int(self.tabla.item(fila, 0).text())
        cantidad = int(self.tabla.item(fila, 2).text())

        for i in range(self.combo_articulos.count()):
            cod_combo, _ = self.combo_articulos.itemData(i)
            if cod_combo == codigo:
                self.combo_articulos.setCurrentIndex(i)
                break

        self.input_cantidad.setValue(cantidad)

    def agregar_detalle(self):
        try:
            codigo_articulo, precio = self.combo_articulos.currentData()
            cantidad = self.input_cantidad.value()
            subtotal = precio * cantidad

            cursor.execute("""
                INSERT INTO detalles_ventas (id_ventas, codigo_articulo, cantidad, subtotal)
                VALUES (%s, %s, %s, %s)
            """, (self.id_venta, codigo_articulo, cantidad, subtotal))
            conexion.commit()

            QMessageBox.information(self, "Éxito", "Detalle agregado correctamente")
            self.cargar_detalles()
            self.detalle_modificado.emit() 
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el detalle: {e}")

    def actualizar_detalle(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione un detalle para actualizar.")
            return

        try:
            codigo_articulo, precio_articulo = self.combo_articulos.currentData()
            cantidad = self.input_cantidad.value()
            subtotal = precio_articulo * cantidad

            cursor.execute("""
                UPDATE detalles_ventas
                SET cantidad=%s, subtotal=%s
                WHERE id_ventas=%s AND codigo_articulo=%s
            """, (cantidad, subtotal, self.id_venta, codigo_articulo))
            conexion.commit()

            QMessageBox.information(self, "Éxito", "Detalle actualizado correctamente")
            self.cargar_detalles()
            self.detalle_modificado.emit() 
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el detalle: {e}")

    def eliminar_detalle(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione un detalle para eliminar.")
            return

        codigo_articulo = int(self.tabla.item(fila, 0).text())

        confirmacion = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Desea eliminar el artículo #{codigo_articulo} de esta venta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmacion == QMessageBox.StandardButton.Yes:
            try:
                cursor.execute("""
                    DELETE FROM detalles_ventas
                    WHERE id_ventas=%s AND codigo_articulo=%s
                """, (self.id_venta, codigo_articulo))
                conexion.commit()
                QMessageBox.information(self, "Éxito", "Detalle eliminado correctamente")
                self.cargar_detalles()
                self.detalle_modificado.emit()  # 👈 Emitir señal
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el detalle: {e}")
