# vistas/vistas_inventario.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                             QLineEdit, QGridLayout, QMessageBox, QDialog, QFormLayout, 
                             QSpinBox, QDialogButtonBox) # <-- QDialogButtonBox AÑADIDO AQUÍ
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import database

# --- Diálogo para Añadir Producto ---
class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Añadir Nuevo Producto")
        layout = QFormLayout(self)
        
        self.code_input = QLineEdit()
        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.supplier_input = QLineEdit()
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 99999)
        self.sale_price_input = QLineEdit()
        self.cost_price_input = QLineEdit()
        
        layout.addRow("Código (SKU):", self.code_input)
        layout.addRow("Nombre:", self.name_input)
        layout.addRow("Categoría:", self.category_input)
        layout.addRow("Proveedor:", self.supplier_input)
        layout.addRow("Stock Inicial:", self.stock_input)
        layout.addRow("Precio de Venta:", self.sale_price_input)
        layout.addRow("Precio de Costo:", self.cost_price_input)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_data(self):
        # Validar que los campos no estén vacíos y que los precios sean números
        try:
            sale_price = float(self.sale_price_input.text())
            cost_price = float(self.cost_price_input.text())
        except ValueError:
            return None # Error si los precios no son números
            
        if not all([self.code_input.text(), self.name_input.text()]):
            return None # Código y nombre son obligatorios
            
        return {
            "code": self.code_input.text(), "name": self.name_input.text(),
            "category": self.category_input.text(), "supplier": self.supplier_input.text(),
            "stock": self.stock_input.value(), "sale_price": sale_price, "cost_price": cost_price
        }

# --- Clase Principal de la Vista de Inventario ---
class VistaInventario(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_product_code = None
        self.setStyleSheet("""
            #main_widget { background-color: #f8f9fa; font-family: Manrope; }
            #header { background-color: white; border-bottom: 1px solid #dee2e6; }
            #card { background-color: white; border-radius: 8px; border: 1px solid #e9ecef; }
            #filter_input, .form_input { background-color: white; border: 1px solid #dee2e6; border-radius: 6px; padding: 8px 12px; font-size: 14px; }
            QTableWidget { border: none; gridline-color: #e9ecef; selection-behavior: QAbstractItemView.SelectionBehavior.SelectRows; }
            QHeaderView::section { background-color: #f8f9fa; padding: 12px; border: none; font-weight: 500; font-size: 13px; color: #6c757d; }
            QLabel.form_label { font-size: 13px; font-weight: 500; color: #495057; }
            QPushButton#save_button { background-color: #0c7ff2; color: white; font-weight: bold; border: none; border-radius: 6px; padding: 10px 15px; }
        """)
        self.setObjectName("main_widget")
        
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        header = self.crear_header(); content_area = QWidget(); content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 30, 40, 30); content_layout.setSpacing(20)

        title_layout = QHBoxLayout()
        title = QLabel("Gestión de Inventario")
        title.setFont(QFont("Manrope", 18, QFont.Weight.Bold))
        add_button = QPushButton("＋ Añadir Producto")
        add_button.setStyleSheet("background-color: #0c7ff2; color: white; font-weight: bold; padding: 10px;")
        add_button.clicked.connect(self.abrir_dialogo_anadir)
        title_layout.addWidget(title); title_layout.addStretch(); title_layout.addWidget(add_button)
        
        self.filter_input = QLineEdit(); self.filter_input.setPlaceholderText("🔍 Filtrar por Código o Nombre...")
        self.filter_input.textChanged.connect(self.filtrar_tabla)

        table_card = QFrame(); table_card.setObjectName("card"); table_card_layout = QVBoxLayout(table_card)
        table_card_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setColumnCount(8)
        self.tabla_inventario.setHorizontalHeaderLabels(["Código", "Producto", "Categoría", "Proveedor", "Existencias", "P. Venta", "Costo", "Acciones"])
        self.tabla_inventario.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_inventario.cellClicked.connect(self.fila_seleccionada)
        
        table_card_layout.addWidget(self.tabla_inventario)
        form_card = self.crear_formulario_detalles()
        self.cargar_datos_tabla()

        content_layout.addLayout(title_layout)
        content_layout.addWidget(self.filter_input)
        content_layout.addWidget(table_card)
        content_layout.addWidget(form_card)
        layout.addWidget(header); layout.addWidget(content_area, 1)

    def crear_header(self):
        header = QFrame(); header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 15, 25, 15); self.boton_dashboard = QPushButton("← Volver al Dashboard")
        self.boton_dashboard.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_dashboard.setStyleSheet("border: none; font-size: 14px; font-weight: bold; color: #0c7ff2;")
        header_layout.addWidget(self.boton_dashboard); header_layout.addStretch()
        return header

    def crear_formulario_detalles(self):
        form_card = QFrame(); form_card.setObjectName("card"); card_layout = QVBoxLayout(form_card)
        card_layout.setContentsMargins(25, 20, 25, 20); form_layout = QGridLayout(); form_layout.setSpacing(15)
        self.nombre_input = QLineEdit(); self.categoria_input = QLineEdit(); self.proveedor_input = QLineEdit()
        self.precio_venta_input = QLineEdit(); self.costo_unitario_input = QLineEdit()
        for field in [self.nombre_input, self.categoria_input, self.proveedor_input, self.precio_venta_input, self.costo_unitario_input]:
            field.setObjectName("form_input")
        form_layout.addWidget(QLabel("Nombre Producto:"), 0, 0); form_layout.addWidget(self.nombre_input, 0, 1)
        form_layout.addWidget(QLabel("Categoría:"), 0, 2); form_layout.addWidget(self.categoria_input, 0, 3)
        form_layout.addWidget(QLabel("Proveedor:"), 1, 0); form_layout.addWidget(self.proveedor_input, 1, 1)
        form_layout.addWidget(QLabel("Precio Venta:"), 1, 2); form_layout.addWidget(self.precio_venta_input, 1, 3)
        form_layout.addWidget(QLabel("Costo Unitario:"), 2, 0); form_layout.addWidget(self.costo_unitario_input, 2, 1)
        self.save_button = QPushButton("Guardar Cambios"); self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.guardar_cambios)
        card_layout.addLayout(form_layout); card_layout.addWidget(self.save_button, 0, Qt.AlignmentFlag.AlignRight)
        return form_card

    def cargar_datos_tabla(self):
        self.tabla_inventario.setRowCount(0)
        datos = database.get_all_products()
        self.tabla_inventario.setRowCount(len(datos))
        for fila, data_row in enumerate(datos):
            for col, data_cell in enumerate(data_row):
                self.tabla_inventario.setItem(fila, col, QTableWidgetItem(str(data_cell)))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            delete_button = QPushButton("Eliminar")
            delete_button.setStyleSheet("background-color: #fdf2f2; color: #ef4444;")
            delete_button.clicked.connect(lambda checked, r=fila: self.eliminar_producto(r))
            actions_layout.addWidget(delete_button)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            self.tabla_inventario.setCellWidget(fila, 7, actions_widget)
        self.limpiar_formulario()

    def filtrar_tabla(self):
        texto_filtro = self.filter_input.text().lower()
        for fila in range(self.tabla_inventario.rowCount()):
            codigo_producto = self.tabla_inventario.item(fila, 0).text().lower()
            nombre_producto = self.tabla_inventario.item(fila, 1).text().lower()
            if texto_filtro in codigo_producto or texto_filtro in nombre_producto:
                self.tabla_inventario.setRowHidden(fila, False)
            else:
                self.tabla_inventario.setRowHidden(fila, True)

    def fila_seleccionada(self, fila, columna):
        self.selected_product_code = self.tabla_inventario.item(fila, 0).text()
        self.nombre_input.setText(self.tabla_inventario.item(fila, 1).text())
        self.categoria_input.setText(self.tabla_inventario.item(fila, 2).text())
        self.proveedor_input.setText(self.tabla_inventario.item(fila, 3).text())
        self.precio_venta_input.setText(str(self.tabla_inventario.item(fila, 5).text()))
        self.costo_unitario_input.setText(str(self.tabla_inventario.item(fila, 6).text()))
        
    def guardar_cambios(self):
        if self.selected_product_code is None:
            QMessageBox.warning(self, "Error", "Por favor, selecciona un producto de la tabla primero.")
            return
        try:
            sale_price = float(self.precio_venta_input.text().replace('$', '').replace(',', ''))
            cost_price = float(self.costo_unitario_input.text().replace('$', '').replace(',', ''))
        except ValueError:
            QMessageBox.warning(self, "Error de Formato", "El precio de venta y el costo deben ser números válidos.")
            return
        database.update_product(self.selected_product_code, self.nombre_input.text(), self.categoria_input.text(), self.proveedor_input.text(), sale_price, cost_price)
        QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")
        self.cargar_datos_tabla()

    def limpiar_formulario(self):
        self.selected_product_code = None; self.nombre_input.clear(); self.categoria_input.clear()
        self.proveedor_input.clear(); self.precio_venta_input.clear(); self.costo_unitario_input.clear()
        self.tabla_inventario.clearSelection()

    def abrir_dialogo_anadir(self):
        dialog = AddProductDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                success = database.add_product(**data)
                if success:
                    QMessageBox.information(self, "Éxito", "Producto añadido correctamente.")
                    self.cargar_datos_tabla()
                else:
                    QMessageBox.warning(self, "Error", "El código del producto ya existe.")
            else:
                QMessageBox.warning(self, "Error", "Por favor, llena todos los campos correctamente.")

    def eliminar_producto(self, fila):
        code = self.tabla_inventario.item(fila, 0).text()
        name = self.tabla_inventario.item(fila, 1).text()
        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", 
                                            f"¿Estás seguro de que quieres eliminar el producto '{name}'?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmacion == QMessageBox.StandardButton.Yes:
            success = database.delete_product(code)
            if success:
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente.")
                self.cargar_datos_tabla()
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el producto.")
