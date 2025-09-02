# ui_main.py (enhanced UI with modern colors and responsive design)
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QDoubleSpinBox, QGroupBox, QGridLayout, QTextEdit, 
                             QHeaderView, QDialog, QDialogButtonBox, QCheckBox, QScrollArea,
                             QSizePolicy, QSpacerItem, QMessageBox)  # Added QMessageBox
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QIcon
import os

class ModernTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #cccccc; 
                background: #f8f9fa; 
                border-radius: 4px; 
            }
            QTabWidget::tab-bar { 
                alignment: center; 
            }
            QTabBar::tab { 
                background: #e9ecef; 
                border: 1px solid #cccccc; 
                padding: 8px 16px; 
                margin-right: 2px; 
                border-top-left-radius: 4px; 
                border-top-right-radius: 4px; 
                color: #495057;
                font-weight: bold;
            }
            QTabBar::tab:selected { 
                background: #007bff; 
                color: white; 
                border-color: #0056b3; 
            }
            QTabBar::tab:hover:!selected { 
                background: #dee2e6; 
            }
        """)

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #ced4da;
            }
        """)

class ModernTable(QTableWidget):
    def __init__(self, rows=0, columns=0, parent=None):
        super().__init__(rows, columns, parent)
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #cce5ff;
                selection-color: black;
                gridline-color: #dee2e6;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 4px;
                border-right: 1px solid #dee2e6;
                border-bottom: 1px solid #dee2e6;
            }
            QTableWidget::item:selected {
                background-color: #cce5ff;
                color: black;
            }
            QHeaderView::section {
                background-color: #007bff;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
            QTableCornerButton::section {
                background-color: #007bff;
                border: none;
            }
        """)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

class ModernLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px 12px;
                background-color: white;
                selection-background-color: #cce5ff;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
            }
            QLineEdit:disabled {
                background-color: #e9ecef;
                color: #6c757d;
            }
        """)

class ModernComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px 12px;
                background-color: white;
                min-width: 6em;
            }
            QComboBox:focus {
                border: 2px solid #007bff;
            }
            QComboBox:disabled {
                background-color: #e9ecef;
                color: #6c757d;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ced4da;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #495057;
                width: 0;
                height: 0;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ced4da;
                selection-background-color: #cce5ff;
                selection-color: black;
                background-color: white;
            }
        """)

class ModernDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px 12px;
                background-color: white;
                selection-background-color: #cce5ff;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #007bff;
            }
            QDoubleSpinBox:disabled {
                background-color: #e9ecef;
                color: #6c757d;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #ced4da;
            }
            QDoubleSpinBox::up-button {
                subcontrol-position: top right;
                border-bottom: 1px solid #ced4da;
                border-top-right-radius: 3px;
            }
            QDoubleSpinBox::down-button {
                subcontrol-position: bottom right;
                border-bottom-right-radius: 3px;
            }
            QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
            }
            QDoubleSpinBox::up-arrow {
                border-bottom: 6px solid #495057;
            }
            QDoubleSpinBox::down-arrow {
                border-top: 6px solid #495057;
            }
        """)

class ModernGroupBox(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ced4da;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)

class ItemScanDialog(QDialog):
    def __init__(self, parent=None, item_data=None, currency="د.ج"):
        super().__init__(parent)
        self.setWindowTitle("إضافة صنف للفاتورة")
        self.setModal(True)
        self.resize(500, 400)
        self.item_data = item_data
        self.currency = currency
        self._return_details = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Barcode field
        barcode_layout = QHBoxLayout()
        barcode_layout.addWidget(QLabel("الباركود:"))
        self.in_barcode = ModernLineEdit()
        barcode_layout.addWidget(self.in_barcode)
        content_layout.addLayout(barcode_layout)
        
        # Item name field
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("اسم الصنف:"))
        self.in_item_name = ModernLineEdit()
        name_layout.addWidget(self.in_item_name)
        content_layout.addLayout(name_layout)
        
        # Price field
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel(f"السعر ({self.currency}):"))
        self.in_price = ModernDoubleSpinBox()
        self.in_price.setMaximum(999999.99)
        self.in_price.setDecimals(2)
        price_layout.addWidget(self.in_price)
        content_layout.addLayout(price_layout)
        
        # Quantity field
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("الكمية:"))
        self.in_qty = ModernDoubleSpinBox()
        self.in_qty.setMaximum(9999.99)
        self.in_qty.setValue(1.0)
        qty_layout.addWidget(self.in_qty)
        content_layout.addLayout(qty_layout)
        
        # Checkbox for manual price editing
        self.chk_manual_price = QCheckBox("تعديل السعر يدويًا")
        self.chk_manual_price.stateChanged.connect(self.toggle_price_editing)
        content_layout.addWidget(self.chk_manual_price)
        
        # Checkbox for saving to database
        self.chk_save_to_db = QCheckBox("حفظ المنتج في قاعدة البيانات")
        self.chk_save_to_db.setChecked(True)
        content_layout.addWidget(self.chk_save_to_db)
        
        # If we have item data, pre-fill the form
        if self.item_data:
            self.in_barcode.setText(self.item_data.get("barcode", ""))
            self.in_item_name.setText(self.item_data.get("name", ""))
            self.in_price.setValue(float(self.item_data.get("price", 0)))
            self.in_qty.setValue(1.0)
            self.in_item_name.setReadOnly(True)
            self.chk_manual_price.setChecked(False)
            self.in_price.setEnabled(False)
        else:
            self.chk_manual_price.setChecked(True)
            self.in_price.setEnabled(True)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.btn_ok = ModernButton("موافق")
        self.btn_ok.clicked.connect(self.accept_with_details)
        self.btn_cancel = ModernButton("إلغاء")
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_ok)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)

    def toggle_price_editing(self, state):
        self.in_price.setEnabled(state == Qt.Checked)

    def accept_with_details(self):
        barcode = self.in_barcode.text().strip()
        name = self.in_item_name.text().strip()
        price = self.in_price.value()
        qty = self.in_qty.value()
        save_to_db = self.chk_save_to_db.isChecked()
        
        if not name:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم الصنف")
            return
            
        if price <= 0:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال سعر صحيح")
            return
            
        if qty <= 0:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال كمية صحيحة")
            return
        
        # Prepare return details
        self._return_details = {
            "id": self.item_data["id"] if self.item_data else -1,
            "barcode": barcode,
            "name": name,
            "price": price,
            "qty": qty,
            "save_to_db": save_to_db
        }
        
        self.accept()

class SaleDetailsDialog(QDialog):
    def __init__(self, sale_id, currency, parent=None):
        super().__init__(parent)
        self.sale_id = sale_id
        self.currency = currency
        self.setWindowTitle(f"تفاصيل الفاتورة #{sale_id}")
        self.setModal(True)
        self.resize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create a scrollable text area for the sale details
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Format the sale details as HTML
        html_content = self.format_sale_details()
        text_edit.setHtml(html_content)
        
        layout.addWidget(text_edit)
        
        # Close button
        close_btn = ModernButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def format_sale_details(self):
        # This method should be implemented in the controller
        # For now, return a placeholder
        return f"<h1>تفاصيل الفاتورة #{self.sale_id}</h1><p>سيتم عرض التفاصيل هنا</p>"

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة المبيعات والمخزون")
        self.resize(1200, 700)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            QLabel {
                color: #212529;
                font-weight: bold;
            }
        """)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Title label
        self.lbl_title = QLabel("نظام إدارة المبيعات والمخزون")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #007bff;
                padding: 10px;
                background-color: white;
                border-radius: 4px;
                border: 1px solid #dee2e6;
            }
        """)
        main_layout.addWidget(self.lbl_title)
        
        # Tab widget
        self.tabs = ModernTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self._create_bill_tab()
        self._create_stock_tab()
        self._create_sales_tab()
        self._create_settings_tab()
        
        # Set Arabic font
        self._arabic_font = QFont("Segoe UI", 11)
        self._arabic_font.setBold(True)
        self.lbl_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        
        # Bill item name font
        self.bill_name_font = QFont("Segoe UI", 12)
        self.bill_name_font.setBold(True)

    def _create_bill_tab(self):
        bill_tab = QWidget()
        bill_layout = QVBoxLayout(bill_tab)
        
        # Input group
        input_group = ModernGroupBox("إضافة صنف للفاتورة")
        input_layout = QGridLayout(input_group)
        
        # Barcode input
        input_layout.addWidget(QLabel("باركود:"), 0, 0)
        self.in_barcode = ModernLineEdit()
        self.in_barcode.setPlaceholderText("أدخل الباركود أو امسحه")
        input_layout.addWidget(self.in_barcode, 0, 1)
        
        # Name input
        input_layout.addWidget(QLabel("اسم الصنف:"), 1, 0)
        self.in_name = ModernLineEdit()
        self.in_name.setPlaceholderText("اسم الصنف")
        input_layout.addWidget(self.in_name, 1, 1)
        
        # Price input
        input_layout.addWidget(QLabel("السعر:"), 2, 0)
        self.in_price = ModernDoubleSpinBox()
        self.in_price.setMaximum(999999.99)
        self.in_price.setDecimals(2)
        input_layout.addWidget(self.in_price, 2, 1)
        
        # Quantity input
        input_layout.addWidget(QLabel("الكمية:"), 3, 0)
        self.in_qty = ModernDoubleSpinBox()
        self.in_qty.setMaximum(9999.99)
        self.in_qty.setValue(1.0)
        input_layout.addWidget(self.in_qty, 3, 1)
        
        # Manual checkbox
        self.chk_manual = QCheckBox("إدخال يدوي (لا يخصم من المخزون)")
        input_layout.addWidget(self.chk_manual, 4, 0, 1, 2)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_bill_find = ModernButton("بحث")
        self.btn_bill_add = ModernButton("إضافة")
        self.btn_scanner_info = ModernButton("معلومات الماسح")
        
        btn_layout.addWidget(self.btn_bill_find)
        btn_layout.addWidget(self.btn_bill_add)
        btn_layout.addWidget(self.btn_scanner_info)
        
        input_layout.addLayout(btn_layout, 5, 0, 1, 2)
        
        bill_layout.addWidget(input_group)
        
        # Bill table
        bill_table_group = ModernGroupBox("فاتورة الحاليّة")
        bill_table_layout = QVBoxLayout(bill_table_group)
        
        self.tbl_bill = ModernTable(0, 6)
        self.tbl_bill.setHorizontalHeaderLabels(["باركود", "الصنف", "السعر", "الكمية", "المجموع", "ID"])
        self.tbl_bill.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        bill_table_layout.addWidget(self.tbl_bill)
        
        # Total label and buttons
        bottom_layout = QHBoxLayout()
        self.lbl_total = QLabel("الإجمالي: 0.00")
        self.lbl_total.setStyleSheet("font-size: 16px; font-weight: bold; color: #007bff;")
        
        self.btn_bill_remove = ModernButton("حذف المحدد")
        self.btn_bill_save = ModernButton("حفظ الفاتورة")
        self.btn_print_bill = ModernButton("طباعة الفاتورة")
        
        bottom_layout.addWidget(self.lbl_total)
        bottom_layout.addWidget(self.btn_bill_remove)
        bottom_layout.addWidget(self.btn_bill_save)
        bottom_layout.addWidget(self.btn_print_bill)
        
        bill_table_layout.addLayout(bottom_layout)
        bill_layout.addWidget(bill_table_group)
        
        self.tabs.addTab(bill_tab, "فاتورة جديدة")

    def _create_stock_tab(self):
        stock_tab = QWidget()
        stock_layout = QHBoxLayout(stock_tab)
        
        # Left side - form
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        form_group = ModernGroupBox("بيانات الصنف")
        form_group_layout = QGridLayout(form_group)
        
        # Name
        form_group_layout.addWidget(QLabel("اسم الصنف:"), 0, 0)
        self.stk_name = ModernLineEdit()
        form_group_layout.addWidget(self.stk_name, 0, 1)
        
        # Category
        form_group_layout.addWidget(QLabel("التصنيف:"), 1, 0)
        cat_layout = QHBoxLayout()
        self.stk_cat = ModernComboBox()
        cat_layout.addWidget(self.stk_cat)
        self.btn_stk_new_cat = ModernButton("+")
        self.btn_stk_new_cat.setFixedWidth(30)
        cat_layout.addWidget(self.btn_stk_new_cat)
        form_group_layout.addLayout(cat_layout, 1, 1)
        
        # Barcode
        form_group_layout.addWidget(QLabel("باركود:"), 2, 0)
        self.stk_barcode = ModernLineEdit()
        form_group_layout.addWidget(self.stk_barcode, 2, 1)
        
        # Price
        form_group_layout.addWidget(QLabel("سعر البيع:"), 3, 0)
        self.stk_price = ModernDoubleSpinBox()
        self.stk_price.setMaximum(999999.99)
        self.stk_price.setDecimals(2)
        form_group_layout.addWidget(self.stk_price, 3, 1)
        
        # Purchase price
        form_group_layout.addWidget(QLabel("سعر الشراء:"), 4, 0)
        self.stk_purchase_price = ModernDoubleSpinBox()
        self.stk_purchase_price.setMaximum(999999.99)
        self.stk_purchase_price.setDecimals(2)
        form_group_layout.addWidget(self.stk_purchase_price, 4, 1)
        
        # Quantity
        form_group_layout.addWidget(QLabel("الكمية:"), 5, 0)
        self.stk_qty = ModernDoubleSpinBox()
        self.stk_qty.setMaximum(999999.99)
        self.stk_qty.setDecimals(2)
        form_group_layout.addWidget(self.stk_qty, 5, 1)
        
        # Photo
        form_group_layout.addWidget(QLabel("صورة:"), 6, 0)
        photo_layout = QHBoxLayout()
        self.stk_photo = ModernLineEdit()
        photo_layout.addWidget(self.stk_photo)
        self.btn_stk_browse = ModernButton("استعراض")
        self.btn_stk_browse.setFixedWidth(80)
        photo_layout.addWidget(self.btn_stk_browse)
        self.btn_stk_camera = ModernButton("كاميرا")
        self.btn_stk_camera.setFixedWidth(80)
        photo_layout.addWidget(self.btn_stk_camera)
        form_group_layout.addLayout(photo_layout, 6, 1)
        
        # Preview
        form_group_layout.addWidget(QLabel("معاينة:"), 7, 0)
        self.lbl_preview = QLabel()
        self.lbl_preview.setFixedSize(150, 150)
        self.lbl_preview.setStyleSheet("border: 1px solid #ced4da; background-color: white;")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        form_group_layout.addWidget(self.lbl_preview, 7, 1)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_stk_add = ModernButton("إضافة")
        self.btn_stk_update = ModernButton("تعديل")
        self.btn_stk_delete = ModernButton("حذف")
        self.btn_stk_refresh = ModernButton("تحديث")
        
        btn_layout.addWidget(self.btn_stk_add)
        btn_layout.addWidget(self.btn_stk_update)
        btn_layout.addWidget(self.btn_stk_delete)
        btn_layout.addWidget(self.btn_stk_refresh)
        
        form_group_layout.addLayout(btn_layout, 8, 0, 1, 2)
        
        form_layout.addWidget(form_group)
        form_layout.addStretch()
        
        # Right side - table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        table_group = ModernGroupBox("المخزون")
        table_group_layout = QVBoxLayout(table_group)
        
        self.tbl_stock = ModernTable(0, 11)
        self.tbl_stock.setHorizontalHeaderLabels([
            "ID", "الاسم", "التصنيف", "باركود", "السعر", "الكمية", "الحالة", 
            "مسار الصورة", "تاريخ الإضافة", "ID التصنيف", "سرمال الشراء"
        ])
        self.tbl_stock.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table_group_layout.addWidget(self.tbl_stock)
        
        table_layout.addWidget(table_group)
        
        # Add both sides to main layout
        stock_layout.addWidget(form_widget, 1)
        stock_layout.addWidget(table_widget, 2)
        
        self.tabs.addTab(stock_tab, "المخزون")

    def _create_sales_tab(self):
        sales_tab = QWidget()
        sales_layout = QVBoxLayout(sales_tab)
        
        sales_group = ModernGroupBox("الفواتير المحفوظة")
        sales_group_layout = QVBoxLayout(sales_group)
        
        # Table
        self.tbl_sales = ModernTable(0, 4)
        self.tbl_sales.setHorizontalHeaderLabels(["رقم الفاتورة", "التاريخ", "المبلغ الإجمالي", "الربح"])
        self.tbl_sales.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        sales_group_layout.addWidget(self.tbl_sales)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_sale_refresh = ModernButton("تحديث")
        self.btn_sale_view = ModernButton("عرض التفاصيل")
        self.btn_sale_view.setEnabled(False)
        self.btn_sale_delete = ModernButton("حذف الفاتورة")
        self.btn_sale_delete.setEnabled(False)
        self.btn_sale_print = ModernButton("طباعة الفاتورة")
        self.btn_sale_print.setEnabled(False)
        
        btn_layout.addWidget(self.btn_sale_refresh)
        btn_layout.addWidget(self.btn_sale_view)
        btn_layout.addWidget(self.btn_sale_delete)
        btn_layout.addWidget(self.btn_sale_print)
        btn_layout.addStretch()
        
        sales_group_layout.addLayout(btn_layout)
        sales_layout.addWidget(sales_group)
        
        self.tabs.addTab(sales_tab, "المبيعات")

    def _create_settings_tab(self):
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        settings_group = ModernGroupBox("إعدادات المتجر")
        settings_group_layout = QGridLayout(settings_group)
        
        # Shop name
        settings_group_layout.addWidget(QLabel("اسم المتجر:"), 0, 0)
        self.sett_shop_name = ModernLineEdit()
        settings_group_layout.addWidget(self.sett_shop_name, 0, 1)
        
        # Contact
        settings_group_layout.addWidget(QLabel("معلومات الاتصال:"), 1, 0)
        self.sett_contact = ModernLineEdit()
        settings_group_layout.addWidget(self.sett_contact, 1, 1)
        
        # Location
        settings_group_layout.addWidget(QLabel("الموقع:"), 2, 0)
        self.sett_location = ModernLineEdit()
        settings_group_layout.addWidget(self.sett_location, 2, 1)
        
        # Currency
        settings_group_layout.addWidget(QLabel("العملة:"), 3, 0)
        self.sett_currency = ModernLineEdit()
        self.sett_currency.setMaxLength(5)
        settings_group_layout.addWidget(self.sett_currency, 3, 1)
        
        # Save button
        self.btn_settings_save = ModernButton("حفظ الإعدادات")
        settings_group_layout.addWidget(self.btn_settings_save, 4, 0, 1, 2)
        
        settings_layout.addWidget(settings_group)
        settings_layout.addStretch()
        
        self.tabs.addTab(settings_tab, "الإعدادات")

    def set_preview_image(self, path):
        if path and os.path.exists(path):
            try:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.lbl_preview.setPixmap(pixmap)
                    return
            except:
                pass
        self.lbl_preview.clear()
        self.lbl_preview.setText("لا توجد صورة")

# For testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())