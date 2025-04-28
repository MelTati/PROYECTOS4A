import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QApplication, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
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
        self.setFixedSize(700, 360)
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # Layout principal horizontal
        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(30, 30, 30, 30)
        layout_principal.setSpacing(30)

        # Caja de fondo con sombra
        contenedor = QFrame()
        contenedor.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(25)
        sombra.setOffset(0, 8)
        sombra.setColor(Qt.GlobalColor.black)
        contenedor.setGraphicsEffect(sombra)

        layout_contenedor = QHBoxLayout(contenedor)
        layout_contenedor.setContentsMargins(20, 20, 20, 20)

        # Panel izquierdo (logo + texto)
        panel_izquierdo = QVBoxLayout()
        panel_izquierdo.setSpacing(15)

        logo = QLabel()
        logo.setPixmap(QPixmap("logo.png").scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)


        panel_izquierdo.addWidget(logo)
        panel_izquierdo.addStretch()

        # Panel derecho (login form)
        panel_derecho = QVBoxLayout()
        panel_derecho.setSpacing(15)

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuario")
        self.input_usuario.setMinimumHeight(36)
        self.input_usuario.setStyleSheet(self.estilo_input())

        self.input_contrasena = QLineEdit()
        self.input_contrasena.setPlaceholderText("Contraseña")
        self.input_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_contrasena.setMinimumHeight(36)
        self.input_contrasena.setStyleSheet(self.estilo_input())

        self.boton_ingresar = QPushButton("Iniciar sesión")
        self.boton_ingresar.setMinimumHeight(36)
        self.boton_ingresar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_ingresar.clicked.connect(self.verificar_credenciales)
        self.boton_ingresar.setStyleSheet("""
            QPushButton {
                background-color: #b300b3 ;
                color: white;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ffe6ff;
            }
        """)

        panel_derecho.addWidget(self.input_usuario)
        panel_derecho.addWidget(self.input_contrasena)
        panel_derecho.addWidget(self.boton_ingresar)
        panel_derecho.addStretch()

        layout_contenedor.addLayout(panel_izquierdo, 1)
        layout_contenedor.addLayout(panel_derecho, 1)

        layout_principal.addWidget(contenedor)
        self.setLayout(layout_principal)

    def estilo_input(self):
        return """
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #b300b3;
                border-radius: 6px;
                background-color: #f9fafb;
                font-size: 13px;
                color: #b300b3;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """

    def apply_styles(self):
        self.setStyleSheet("background-color: #e5e7eb;")

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

