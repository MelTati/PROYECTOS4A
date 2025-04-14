import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QApplication, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from principal import VentanaPrincipal

# Conexión a MySQL
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="mydb_conejo_feliz"
)
cursor = conexion.cursor(dictionary=True)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión")
        self.setFixedSize(380, 320)  # Ventana más compacta
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(8)
        layout_principal.setContentsMargins(10, 10, 10, 10)  # Márgenes reducidos

        # Logo
        logo_container = QLabel()
        logo_container.setFixedHeight(85)  # Altura fija para el contenedor del logo
        logo_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_container.setStyleSheet("background-color: white; border-radius: 5px;")
        
        logo = QLabel(logo_container)
        logo.setPixmap(QPixmap("logo.png").scaled(75, 75, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.addWidget(logo)

        # Título
        titulo = QLabel("🐰 Conejo Feliz - Acceso")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #1a365d; margin: 5px 0;")

        # Caja de contenido
        caja = QFrame()
        caja.setFrameShape(QFrame.Shape.StyledPanel)
        caja.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #ccc;
                padding: 15px;
            }
        """)
        
        # Layout del contenido dentro de la caja
        caja_layout = QVBoxLayout(caja)
        caja_layout.setSpacing(12)
        caja_layout.setContentsMargins(15, 15, 15, 15)
        
        # Campos de entrada con colores contrastantes
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Ingrese su usuario")
        self.input_usuario.setMinimumHeight(32)
        self.input_usuario.setStyleSheet("""
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #3498db;
                border-radius: 5px;
                background-color: #ffffff;
                color: #000000;
                font-size: 13px;
            }
        """)

        self.input_contrasena = QLineEdit()
        self.input_contrasena.setPlaceholderText("Ingrese su contraseña")
        self.input_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_contrasena.setMinimumHeight(32)
        self.input_contrasena.setStyleSheet("""
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #3498db;
                border-radius: 5px;
                background-color: #ffffff;
                color: #000000;
                font-size: 13px;
            }
        """)

        # Botón de ingreso con alto contraste
        self.boton_ingresar = QPushButton("Iniciar sesión")
        self.boton_ingresar.setMinimumHeight(35)
        self.boton_ingresar.setFixedWidth(150)  # Ancho fijo para el botón
        self.boton_ingresar.clicked.connect(self.verificar_credenciales)
        self.boton_ingresar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_ingresar.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)

        # Agregar todo al layout de la caja
        caja_layout.addWidget(self.input_usuario)
        caja_layout.addWidget(self.input_contrasena)
        caja_layout.addWidget(self.boton_ingresar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Agregar widgets al layout principal
        layout_principal.addWidget(logo_container)
        layout_principal.addWidget(titulo)
        layout_principal.addWidget(caja, 1)  # El 1 da más espacio a la caja

        self.setLayout(layout_principal)

    def apply_styles(self):
        # Estilo global
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
            }
            QLineEdit::placeholder {
                color: #94a3b8;
            }
        """)

    def verificar_credenciales(self):
        usuario = self.input_usuario.text()
        contrasena = self.input_contrasena.text()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Campos vacíos", "Por favor, ingresa usuario y contraseña.")
            return

        try:
            cursor.execute("""
               SELECT * FROM usuarios u
               JOIN roles r ON u.id_roles = r.id_roles
               WHERE u.nombre_usuario = %s AND u.password = %s AND r.cargo IN ('Supervisor', 'Cajero')
            """, (usuario, contrasena))
            resultado = cursor.fetchone()

            if resultado:
                self.hide()
                self.ventana_principal = VentanaPrincipal()
                self.ventana_principal.show()
            else:
                QMessageBox.critical(self, "Acceso denegado", "Credenciales incorrectas o no eres Supervisor o Cajero.")
        except Exception as e:
            QMessageBox.critical(self, "Error de conexión", f"No se pudo verificar las credenciales: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_login = LoginWindow()
    ventana_login.show()
    sys.exit(app.exec())