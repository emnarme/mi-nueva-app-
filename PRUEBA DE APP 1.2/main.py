# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from vistas.vistas_login import VistaLogin
from vistas.vistas_dashboard import VistaDashboard
from vistas.vistas_compras import VistaCompras
from vistas.vistas_ventas import VistaVentas
from vistas.vistas_inventario import VistaInventario
from vistas.vistas_entradas import VistaEntradas
from vistas.vistas_usuarios import VistaUsuarios

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DEMOGA EMALDO - Sistema de Gestión")
        self.setGeometry(50, 50, 500, 500)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Instanciación de todas las vistas
        self.vista_login = VistaLogin()
        self.vista_dashboard = VistaDashboard()
        self.vista_compras = VistaCompras()
        self.vista_ventas = VistaVentas()
        self.vista_inventario = VistaInventario()
        self.vista_entradas = VistaEntradas()
        self.vista_usuarios = VistaUsuarios()
        
        # Añadir todas las vistas al QStackedWidget
        for w in [self.vista_login, self.vista_dashboard, self.vista_compras, self.vista_ventas, self.vista_inventario, self.vista_entradas, self.vista_usuarios]:
            self.stacked_widget.addWidget(w)

        # Conectar señales de navegación
        self.vista_login.login_exitoso.connect(self.mostrar_dashboard)
        
        # Conexiones desde el Dashboard
        self.vista_dashboard.boton_compras.clicked.connect(self.mostrar_compras)
        self.vista_dashboard.boton_ventas.clicked.connect(self.mostrar_ventas)
        self.vista_dashboard.boton_inventario.clicked.connect(self.mostrar_inventario)
        self.vista_dashboard.boton_usuarios.clicked.connect(self.mostrar_usuarios)
        self.vista_dashboard.boton_entradas.clicked.connect(self.mostrar_entradas) # <-- CONEXIÓN NUEVA
        
        # Conexiones para "Volver al Dashboard"
        self.vista_compras.boton_dashboard.clicked.connect(self.mostrar_dashboard)
        self.vista_ventas.boton_dashboard.clicked.connect(self.mostrar_dashboard)
        self.vista_inventario.boton_dashboard.clicked.connect(self.mostrar_dashboard)
        self.vista_entradas.boton_dashboard.clicked.connect(self.mostrar_dashboard)
        self.vista_usuarios.boton_dashboard.clicked.connect(self.mostrar_dashboard)

        self.mostrar_login()

    def mostrar_login(self):
        self.stacked_widget.setCurrentWidget(self.vista_login)

    def mostrar_dashboard(self):
        self.vista_dashboard.refresh_data()
        self.stacked_widget.setCurrentWidget(self.vista_dashboard)
        
    def mostrar_compras(self):
        self.vista_compras.cargar_datos_tabla()
        self.stacked_widget.setCurrentWidget(self.vista_compras)

    def mostrar_ventas(self):
        self.vista_ventas.cargar_datos_tabla()
        self.stacked_widget.setCurrentWidget(self.vista_ventas)

    def mostrar_inventario(self):
        self.vista_inventario.cargar_datos_tabla()
        self.stacked_widget.setCurrentWidget(self.vista_inventario)

    def mostrar_entradas(self):
        self.vista_entradas.cargar_datos_tabla()
        self.stacked_widget.setCurrentWidget(self.vista_entradas)

    def mostrar_usuarios(self):
        self.vista_usuarios.cargar_datos_tabla()
        self.stacked_widget.setCurrentWidget(self.vista_usuarios)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
