# vistas/vistas_compras.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                             QLineEdit, QDialog, QFormLayout, QComboBox, QSpinBox,
                             QDialogButtonBox, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import database

# --- Ventana Emergente para Registrar Compra ---
class RegisterPurchaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Nueva Compra")
        
        layout = QFormLayout(self)
        
        self.product_combo = QComboBox()
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 9999)
        self.supplier_input = QLineEdit()
        
        # Cargar productos en el ComboBox
        self.products = database.get_all_products()
        for product in self.products:
            self.product_combo.addItem(f"{product[1]} (Código: {product[0]})", userData=product[0])

        layout.addRow("Producto:", self.product_combo)
        layout.addRow("Cantidad Recibida:", self.quantity_spinbox)
        layout.addRow("Nombre del Proveedor:", self.supplier_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_purchase_data(self):
        product_code = self.product_combo.currentData()
        quantity = self.quantity_spinbox.value()
        supplier = self.supplier_input.text()
        if not supplier:
            return None # Proveedor es obligatorio
        return {
            "product_code": product_code,
            "quantity": quantity,
            "supplier_name": supplier
        }

# --- Clase Principal de la Vista de Compras ---
class VistaCompras(QWidget):
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
        title = QLabel("Seguimiento de Órdenes de Compra")
        title.setFont(QFont("Manrope", 18, QFont.Weight.Bold))
        add_button = QPushButton("＋ Registrar Compra")
        add_button.setStyleSheet("background-color: #0c7ff2; color: white; font-weight: bold; padding: 10px;")
        add_button.clicked.connect(self.abrir_dialogo_compra)
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(add_button)

        self.tabla_compras = QTableWidget()
        self.tabla_compras.setColumnCount(6)
        self.tabla_compras.setHorizontalHeaderLabels(["Fecha", "No. Orden (PO)", "Producto", "Proveedor", "Cantidad Recibida", "Estado"])
        self.tabla_compras.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.cargar_datos_tabla()

        content_layout.addLayout(title_layout)
        content_layout.addWidget(self.tabla_compras)

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
        """Carga el historial de compras desde la base de datos."""
        self.tabla_compras.setRowCount(0)
        datos = database.get_purchase_history()
        self.tabla_compras.setRowCount(len(datos))
        for fila, data_row in enumerate(datos):
            for col, data_cell in enumerate(data_row):
                self.tabla_compras.setItem(fila, col, QTableWidgetItem(str(data_cell)))

    def abrir_dialogo_compra(self):
        dialog = RegisterPurchaseDialog(self)
        if dialog.exec():
            purchase_data = dialog.get_purchase_data()
            if purchase_data:
                result = database.register_purchase(
                    purchase_data["product_code"],
                    purchase_data["quantity"],
                    purchase_data["supplier_name"]
                )
                QMessageBox.information(self, "Resultado de la Compra", result)
                self.cargar_datos_tabla()
            else:
                QMessageBox.warning(self, "Error", "El nombre del proveedor es obligatorio.")
