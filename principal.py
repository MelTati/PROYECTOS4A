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
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet("background-color: #F8F9FA;")

        self.stacked_widget = QStackedWidget()

        # Crear instancias de las ventanas
        self.ventas = VentanaVentas()
        self.clientes = VentanaClientes()
        self.articulos = VentanaArticulos()
        self.usuarios = VentanaUsuarios()
        self.ticket = VentanaTickets()

        # Agregar widgets al stack
        self.stacked_widget.addWidget(self.ventas)    # index 0
        self.stacked_widget.addWidget(self.clientes)  # index 1
        self.stacked_widget.addWidget(self.articulos) # index 2
        self.stacked_widget.addWidget(self.usuarios)  # index 3
        self.stacked_widget.addWidget(self.ticket)    # index 4

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        header = QLabel("Bienvenido al Sistema de Gestión")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #333; margin: 10px;")
        main_layout.addWidget(header)

        # Botonera lateral
        botones_layout = QHBoxLayout()

        botones = [
            ("Ventas", "#28A745", lambda: self.stacked_widget.setCurrentIndex(0)),
            ("Clientes", "#17A2B8", lambda: self.stacked_widget.setCurrentIndex(1)),
            ("Artículos", "#007BFF", lambda: self.stacked_widget.setCurrentIndex(2)),
            ("Usuarios", "#6F42C1", lambda: self.stacked_widget.setCurrentIndex(3)),
            ("Tickets", "#FD7E14", lambda: self.stacked_widget.setCurrentIndex(4)),
            ("Compras", "#DC3545", self.abrir_compras)
        ]

        for texto, color, accion in botones:
            btn = QPushButton(texto)
            btn.setFont(QFont("Segoe UI", 11))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 10px 20px;
                    border-radius: 8px;
                    margin: 5px;
                }}
                QPushButton:hover {{
                    background-color: #444;
                }}
            """)
            btn.clicked.connect(accion)
            botones_layout.addWidget(btn)

        main_layout.addLayout(botones_layout)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def abrir_compras(self):
        QMessageBox.information(self, "Compras", "Aquí iría la lógica para gestionar compras.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
