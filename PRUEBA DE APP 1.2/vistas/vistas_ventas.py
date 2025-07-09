# vistas/vistas_ventas.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                             QLineEdit, QDialog, QFormLayout, QComboBox, QSpinBox,
                             QDialogButtonBox, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import database

# --- Ventana Emergente para Registrar Venta ---
class RegisterSaleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Nueva Venta")
        
        layout = QFormLayout(self)
        
        self.product_combo = QComboBox()
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 999)
        self.customer_input = QLineEdit()
        
        # Cargar productos en el ComboBox
        self.products = database.get_all_products()
        for product in self.products:
            # product: (code, name, category, supplier, stock, sale_price, cost_price)
            self.product_combo.addItem(f"{product[1]} (Stock: {product[4]})", userData=product[0])

        layout.addRow("Producto:", self.product_combo)
        layout.addRow("Cantidad:", self.quantity_spinbox)
        layout.addRow("Nombre del Cliente:", self.customer_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_sale_data(self):
        product_code = self.product_combo.currentData()
        quantity = self.quantity_spinbox.value()
        customer = self.customer_input.text()
        if not customer:
            return None # Cliente es obligatorio
        return {
            "product_code": product_code,
            "quantity": quantity,
            "customer_name": customer
        }

# --- Clase Principal de la Vista de Ventas ---
class VistaVentas(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            /* ... (Estilos existentes sin cambios) ... */
        """)
        self.setObjectName("main_widget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = self.crear_header()
        
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(20)

        title_layout = QHBoxLayout()
        title = QLabel("Historial de Salidas (Ventas)")
        title.setFont(QFont("Manrope", 18, QFont.Weight.Bold))
        add_button = QPushButton("＋ Registrar Venta")
        add_button.setStyleSheet("background-color: #0c7ff2; color: white; font-weight: bold; padding: 10px;")
        add_button.clicked.connect(self.abrir_dialogo_venta)
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(add_button)

        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(7)
        self.tabla_ventas.setHorizontalHeaderLabels(["Fecha", "Factura", "Producto", "Categoría", "Cliente", "Total Venta", "Vendedor"])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.cargar_datos_tabla()

        content_layout.addLayout(title_layout)
        content_layout.addWidget(self.tabla_ventas)

        layout.addWidget(header)
        layout.addWidget(content_area, 1)

    def crear_header(self):
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 15, 25, 15)
        self.boton_dashboard = QPushButton("← Volver al Dashboard")
        self.boton_dashboard.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_dashboard.setStyleSheet("border: none; font-size: 14px; font-weight: bold; color: #0c7ff2;")
        header_layout.addWidget(self.boton_dashboard)
        header_layout.addStretch()
        return header

    def cargar_datos_tabla(self):
        """Carga el historial de ventas desde la base de datos."""
        self.tabla_ventas.setRowCount(0)
        datos = database.get_sales_history()
        self.tabla_ventas.setRowCount(len(datos))
        for fila, data_row in enumerate(datos):
            for col, data_cell in enumerate(data_row):
                # Formatear el precio a 2 decimales si es la columna de total
                if col == 5:
                    data_cell = f"${float(data_cell):,.2f}"
                self.tabla_ventas.setItem(fila, col, QTableWidgetItem(str(data_cell)))

    def abrir_dialogo_venta(self):
        dialog = RegisterSaleDialog(self)
        if dialog.exec():
            sale_data = dialog.get_sale_data()
            if sale_data:
                # El vendedor se podría obtener del usuario logueado, por ahora es fijo
                result = database.register_sale(
                    sale_data["product_code"],
                    sale_data["quantity"],
                    sale_data["customer_name"],
                    "Admin User" 
                )
                QMessageBox.information(self, "Resultado de la Venta", result)
                self.cargar_datos_tabla() # Recargar para ver la nueva venta
            else:
                QMessageBox.warning(self, "Error", "El nombre del cliente es obligatorio.")
