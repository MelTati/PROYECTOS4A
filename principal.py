import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QMessageBox, QStackedWidget, QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ventas import VentanaVentas
from cliente import VentanaClientes
from articulos import VentanaArticulos
from ventana_usuarios import VentanaUsuarios
from ticket import VentanaTickets


class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #F8F9FA;")

        self.stacked_widget = QStackedWidget()

        # Crear instancias de las ventanas
        self.ventas = VentanaVentas()
        self.clientes = VentanaClientes()
        self.articulos = VentanaArticulos()
        self.usuarios = VentanaUsuarios()
        self.ticket = VentanaTickets()

        # Agregar widgets al stack
        self.stacked_widget.addWidget(self.ventas)
        self.stacked_widget.addWidget(self.clientes)
        self.stacked_widget.addWidget(self.articulos)
        self.stacked_widget.addWidget(self.usuarios)
        self.stacked_widget.addWidget(self.ticket)

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        # Sidebar moderno claro
        sidebar = QVBoxLayout()
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(220)
        sidebar_widget.setStyleSheet("""
            background-color: #E9ECEF;
            border-right: 1px solid #CED4DA;
        """)

        botones = [
            ("Ventas", lambda: self.stacked_widget.setCurrentIndex(0)),
            ("Clientes", lambda: self.stacked_widget.setCurrentIndex(1)),
            ("Artículos", lambda: self.stacked_widget.setCurrentIndex(2)),
            ("Usuarios", lambda: self.stacked_widget.setCurrentIndex(3)),
            ("Tickets", lambda: self.stacked_widget.setCurrentIndex(4)),
            ("Compras", self.abrir_compras)
        ]

        label_title = QLabel("Menú Principal")
        label_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        label_title.setStyleSheet("color: #343A40; padding: 20px 10px;")
        label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar.addWidget(label_title)

        for texto, accion in botones:
            btn = QPushButton(texto)
            btn.setFont(QFont("Segoe UI", 11))
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #343A40;
                    border: 1px solid #CED4DA;
                    border-radius: 8px;
                    margin: 6px 16px;
                }
                QPushButton:hover {
                    background-color: #D0EBFF;
                    border-color: #74C0FC;
                }
            """)
            btn.clicked.connect(accion)
            sidebar.addWidget(btn)

        sidebar.addStretch()
        sidebar_widget.setLayout(sidebar)

        # Área de contenido
        content_layout = QVBoxLayout()
        content_widget = QWidget()

        header = QLabel("Bienvenido al Sistema de Gestión")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #212529; padding: 20px;")

        content_layout.addWidget(header)
        content_layout.addWidget(self.stacked_widget)
        content_widget.setLayout(content_layout)

        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

    def abrir_compras(self):
        QMessageBox.information(self, "Compras", "Aquí iría la lógica para gestionar compras.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
