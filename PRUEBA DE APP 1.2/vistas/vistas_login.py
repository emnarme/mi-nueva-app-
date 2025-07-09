# vistas/vistas_login.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
import database # Importamos nuestro gestor de base de datos

class VistaLogin(QWidget):
    login_exitoso = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: Manrope;
            }
            QFrame#form_container {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e9ecef;
            }
            QLabel#titulo {
                font-size: 24px;
                font-weight: bold;
                color: #212529;
            }
            QLabel#subtitulo {
                font-size: 16px;
                color: #6c757d;
            }
            QFrame.input_frame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QLineEdit {
                background-color: transparent;
                border: none;
                padding: 10px;
                font-size: 14px;
                color: #495057;
            }
            QPushButton#login_button {
                background-color: #0c7ff2;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }
            QLabel#error_label {
                color: #dc3545;
                font-size: 13px;
                font-weight: bold;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_container = QFrame()
        form_container.setObjectName("form_container")
        form_container.setFixedWidth(400)
        
        layout = QVBoxLayout(form_container)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Interfaz de Usuario ---
        logo_label = QLabel()
        logo_label.setFixedSize(64, 64)
        logo_label.setStyleSheet("background-color: #e0e0e0; border-radius: 8px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        titulo = QLabel("DEMOGA EMALDO")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitulo = QLabel("BIENVENIDO")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Usamos el correo como usuario para la base de datos
        self.usuario_input, usuario_frame = self.crear_campo_con_icono("📧", "Correo Electrónico (admin)")
        self.password_input, password_frame = self.crear_campo_con_icono("🔒", "Contraseña (1234)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setObjectName("login_button")
        
        self.error_label = QLabel("")
        self.error_label.setObjectName("error_label")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setHidden(True)
        
        layout.addWidget(logo_label)
        layout.addSpacing(10)
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(20)
        layout.addWidget(usuario_frame)
        layout.addWidget(password_frame)
        layout.addWidget(self.error_label)
        layout.addSpacing(10)
        layout.addWidget(self.login_button)
        # --- Fin de la Interfaz ---

        main_layout.addWidget(form_container)

        self.login_button.clicked.connect(self.check_login)

    def crear_campo_con_icono(self, icono, placeholder_text):
        frame = QFrame()
        frame.setObjectName("input_frame")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(5)
        icon_label = QLabel(icono)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        layout.addWidget(icon_label)
        layout.addWidget(line_edit)
        return line_edit, frame

    def check_login(self):
        email = self.usuario_input.text()
        password = self.password_input.text()

        # Usamos la función de nuestro gestor de base de datos
        if database.check_user_credentials(email, password):
            self.error_label.setHidden(True)
            self.login_exitoso.emit()
        else:
            self.error_label.setText("Correo o contraseña incorrectos.")
            self.error_label.setHidden(False)
