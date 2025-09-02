# controllers.py (fixed syntax error and QPrinter typo)
import os
from datetime import datetime
from PyQt5.QtWidgets import (QFileDialog, QTableWidgetItem, QMessageBox, 
                             QInputDialog, QCompleter, QDialog, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTextEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import QSizeF  # Added import for QSizeF

from ui_main import MainUI, ItemScanDialog
import models

try:
    import cv2
except Exception:
    cv2 = None

try:
    from pyzbar.pyzbar import decode as zbar_decode
except Exception:
    zbar_decode = None

ASSETS_PHOTOS_DIR = os.path.join("assets", "photos")
os.makedirs(ASSETS_PHOTOS_DIR, exist_ok=True)

ALLOWED_BARCODE_LENGTHS = {8, 12, 13}

def is_valid_barcode(code: str) -> bool:
    return code.isdigit() and (len(code) in ALLOWED_BARCODE_LENGTHS)

def fmt_qty(val):
    return f"{val:.0f}" if val == int(val) else f"{val:.1f}"

def fmt_money(val):
    return f"{val:.0f}" if val == int(val) else f"{val:.2f}"

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
        
        # Sale details
        details = models.get_sale_details(self.sale_id)
        sale_info = models.get_sale_by_id(self.sale_id)
        
        # Create a scrollable text area for the sale details
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Format the sale details as HTML
        html_content = self.format_sale_details(details, sale_info)
        text_edit.setHtml(html_content)
        
        layout.addWidget(text_edit)
        
        # Close button
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def format_sale_details(self, details, sale_info):
        total_revenue = sale_info["total_price"] if sale_info else 0
        total_purchase = sale_info["total_purchase_price"] if sale_info else 0
        total_profit = total_revenue - total_purchase
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        html = f"""
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; text-align: right; margin: 20px; }}
            .header {{ text-align: center; margin-bottom: 20px; border-bottom: 2px solid #ccc; padding-bottom: 10px; }}
            .shop-name {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
            .sale-info {{ margin: 10px 0; }}
            .items-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .items-table th, .items-table td {{ border: 1px solid #ccc; padding: 8px; text-align: right; }}
            .items-table th {{ background-color: #f2f2f2; font-weight: bold; }}
            .summary {{ margin-top: 20px; font-weight: bold; border-top: 2px solid #ccc; padding-top: 10px; }}
        </style>
        </head>
        <body>
            <div class="header">
                <div class="shop-name">تفاصيل الفاتورة #{self.sale_id}</div>
                <div class="sale-info">التاريخ: {sale_info['datetime'] if sale_info else 'غير معروف'}</div>
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>الصنف</th>
                        <th>الكمية</th>
                        <th>سعر الوحدة ({self.currency})</th>
                        <th>المجموع ({self.currency})</th>
                        <th>سرمال الشراء ({self.currency})</th>
                        <th>الربح ({self.currency})</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in details:
            purchase_price = item.get("purchase_price_each", 0) or 0
            profit = (item["price_each"] - purchase_price) * item["quantity"]
            
            html += f"""
                    <tr>
                        <td>{item['item_name']}</td>
                        <td>{fmt_qty(item['quantity'])}</td>
                        <td>{fmt_money(item['price_each'])}</td>
                        <td>{fmt_money(item['subtotal'])}</td>
                        <td>{fmt_money(purchase_price)}</td>
                        <td>{fmt_money(profit)}</td>
                    </tr>
            """
        
        html += f"""
                </tbody>
            </table>
            
            <div class="summary">
                <div>إجمالي الإيرادات: {fmt_money(total_revenue)} {self.currency}</div>
                <div>إجمالي تكلفة الشراء: {fmt_money(total_purchase)} {self.currency}</div>
                <div>إجمالي الربح: {fmt_money(total_profit)} {self.currency}</div>
                <div>هامش الربح: {fmt_money(profit_margin)}%</div>
            </div>
        </body>
        </html>
        """
        
        return html

class Controller(MainUI):
    def __init__(self):
        super().__init__()

        self.currency = "د.ج"
        self.current_bill_items = []

        # Load settings
        self._load_settings_or_first_run()

        # Initialize tabs
        self._load_categories()
        self._load_stock_table()
        self._load_sales_tab()
        self._apply_currency_to_inputs()

        # Bill signals
        self.btn_bill_find.clicked.connect(self._bill_find_and_add_item_dialog)
        self.btn_bill_add.clicked.connect(self._bill_find_and_add_item_dialog)
        self.btn_bill_remove.clicked.connect(self._bill_remove_selected)
        self.btn_bill_save.clicked.connect(self._bill_save)
        self.btn_print_bill.clicked.connect(self._bill_print)
        self.btn_scanner_info.clicked.connect(self._show_scanner_info)

        # Autocomplete feature for manual entry
        self.in_name.textChanged.connect(self._on_name_text_changed)
        self._setup_autocomplete()

        # Barcode return pressed
        self.in_barcode.returnPressed.connect(self._handle_scanned_barcode)
        
        # Set focus to barcode field for scanner input
        self.in_barcode.setFocus()

        # Stock signals
        self.btn_stk_browse.clicked.connect(self._browse_photo)
        self.btn_stk_camera.clicked.connect(self._capture_photo)
        self.btn_stk_new_cat.clicked.connect(self._add_new_category)
        self.btn_stk_add.clicked.connect(self._stock_add)
        self.btn_stk_update.clicked.connect(self._stock_update)
        self.btn_stk_delete.clicked.connect(self._stock_delete)
        self.btn_stk_refresh.clicked.connect(self._load_stock_table)
        self.tbl_stock.clicked.connect(self._stock_fill_form_from_selection)

        # Sales signals
        self.btn_sale_refresh.clicked.connect(self._load_sales_tab)
        self.btn_sale_view.clicked.connect(self._sales_view_selected)
        self.btn_sale_delete.clicked.connect(self._sales_delete_selected)
        self.btn_sale_print.clicked.connect(self._sales_print_selected)
        self.tbl_sales.itemSelectionChanged.connect(self._on_sale_selection_changed)

        # Settings
        self.btn_settings_save.clicked.connect(self._save_settings_from_tab)

    def _setup_autocomplete(self):
        all_items = models.get_items()
        suggestions = [item['name'] for item in all_items if item['name']]
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.in_name.setCompleter(completer)
        
        completer.activated.connect(self._on_autocomplete_selected)

    def _load_settings_or_first_run(self):
        s = models.get_settings()
        if not s:
            QMessageBox.information(self, "الإعداد الأول", "مرحبًا! برجاء إدخال معلومات المتجر أولًا.")
            shop_name, ok1 = QInputDialog.getText(self, "اسم المتجر", "اسم المتجر:")
            if not ok1 or not shop_name.strip():
                shop_name = "متجري"
            contact, _ = QInputDialog.getText(self, "معلومات الاتصال", "هاتف / بريد إلكتروني (اختياري):")
            location, _ = QInputDialog.getText(self, "الموقع", "العنوان / الموقع (اختياري):")
            currency, ok4 = QInputDialog.getText(self, "العملة", "اكتب رمز العملة (مثال: د.ج ، ر.س ، MAD ، USD):")
            if not ok4 or not currency.strip():
                currency = "د.ج"
            models.save_settings(shop_name.strip(), (contact or "").strip(), (location or "").strip(), currency.strip())
            s = models.get_settings()
        self._apply_settings_to_ui(s)

    def _apply_settings_to_ui(self, s):
        self.lbl_title.setText(s["shop_name"])
        self.setWindowTitle(s["shop_name"])
        self.sett_shop_name.setText(s["shop_name"])
        self.sett_contact.setText(s["contact"] or "")
        self.sett_location.setText(s["location"] or "")
        self.sett_currency.setText(s["currency"])
        self.currency = s["currency"]

    def _save_settings_from_tab(self):
        shop_name = self.sett_shop_name.text().strip() or "متجري"
        contact = self.sett_contact.text().strip()
        location = self.sett_location.text().strip()
        currency = self.sett_currency.text().strip() or "د.ج"
        models.save_settings(shop_name, contact, location, currency)
        s = models.get_settings()
        self._apply_settings_to_ui(s)
        self._apply_currency_to_inputs()
        self.msg("تم", "تم حفظ الإعدادات.")

    def _apply_currency_to_inputs(self):
        self.in_price.setPrefix(f"السعر ({self.currency}): ")
        self.stk_price.setPrefix(f"السعر ({self.currency}): ")
        self.stk_purchase_price.setPrefix(f"سعر الشراء ({self.currency}): ")
        self.stk_qty.setPrefix("المخزون: ")
        self.in_qty.setPrefix("الكمية: ")
        self._bill_recalc_total()
        self._load_sales_tab()

    # Categories
    def _load_categories(self):
        cats = models.get_categories()
        self.stk_cat.clear()
        for c in cats:
            self.stk_cat.addItem(c["name"], c["id"])

    def _add_new_category(self):
        name, ok = QInputDialog.getText(self, "تصنيف جديد", "اسم التصنيف:")
        if ok and name.strip():
            try:
                models.add_category(name.strip())
                self._load_categories()
                self.msg("تم", "تم إضافة التصنيف.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر إضافة التصنيف:\n{e}")

    # Stock Methods
    def _browse_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "اختر صورة", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.stk_photo.setText(path)
            self.set_preview_image(path)

    def _capture_photo(self):
        if cv2 is None:
            QMessageBox.warning(self, "الكاميرا", "OpenCV غير مثبت.")
            return
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            QMessageBox.warning(self, "الكاميرا", "تعذر فتح الكاميرا.")
            return
        QMessageBox.information(self, "التقاط", "سيتم فتح نافذة الكاميرا.")
        path_saved = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Camera - Press C to capture, Q to cancel", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                fname = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                path_saved = os.path.join(ASSETS_PHOTOS_DIR, fname)
                cv2.imwrite(path_saved, frame)
                break
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        if path_saved:
            self.stk_photo.setText(path_saved)
            self.set_preview_image(path_saved)
            self.msg("تم", f"تم حفظ الصورة: {path_saved}")

    def _stock_add(self):
        try:
            name = self.stk_name.text().strip()
            if not name:
                self.msg("تنبيه", "الرجاء إدخال الاسم.")
                return
            barcode = self.stk_barcode.text().strip()
            if barcode and not is_valid_barcode(barcode):
                self.msg("خطأ", "الباركود غير صالح")
                return
            cat_id = self.stk_cat.currentData()
            price = float(self.stk_price.value())
            purchase_price = float(self.stk_purchase_price.value())
            qty = float(self.stk_qty.value())
            
            if qty < 0:
                self.msg("خطأ", "لا يمكن إضافة كمية مخزون سالبة.")
                return
                
            photo = self.stk_photo.text().strip() or None
            models.add_item(name, cat_id, barcode or None, price, qty, photo, purchase_price=purchase_price)
            self._load_stock_table()
            self.msg("تم", "تمت إضافة الصنف.")
            self._clear_stock_form()
            self._setup_autocomplete()
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر إضافة الصنف:\n{e}")

    def _stock_update(self):
        row = self._selected_row(self.tbl_stock)
        if row is None:
            self.msg("تنبيه", "اختر صفًا للتعديل.")
            return
        item_id = int(self.tbl_stock.item(row, 0).text())
        try:
            name = self.stk_name.text().strip()
            if not name:
                self.msg("تنبيه", "الرجاء إدخال الاسم.")
                return
            barcode = self.stk_barcode.text().strip()
            # FIXED: Added missing closing parenthesis
            if barcode and not is_valid_barcode(barcode):
                self.msg("خطأ", "الباركود غير صالح")
                return
            cat_id = self.stk_cat.currentData()
            price = float(self.stk_price.value())
            purchase_price = float(self.stk_purchase_price.value())
            qty = float(self.stk_qty.value())
            
            if qty < 0:
                self.msg("خطأ", "لا يمكن إضافة كمية مخزون سالبة.")
                return
                
            photo = self.stk_photo.text().strip() or None
            models.update_item(item_id, name, cat_id, barcode or None, price, qty, photo, purchase_price=purchase_price)
            self._load_stock_table()
            self.msg("تم", "تم تعديل الصنف.")
            self._setup_autocomplete()
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر تعديل الصنف:\n{e}")

    def _stock_delete(self):
        row = self._selected_row(self.tbl_stock)
        if row is None:
            self.msg("تنبيه", "اختر صفًا للحذف.")
            return
        item_id = int(self.tbl_stock.item(row, 0).text())
        confirm = QMessageBox.question(self, "تأكيد", "سيتم حذف الصنف وجميع تفاصيل البيع المرتبطة به.\nهل أنت متأكد؟", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                models.delete_item(item_id)
                self._load_stock_table()
                self.msg("تم", "تم حذف الصنف.")
                self._setup_autocomplete()
                self._load_sales_tab()
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر حذف الصنف:\n{e}")

    def _clear_stock_form(self):
        self.stk_name.clear()
        self.stk_barcode.clear()
        self.stk_price.setValue(0)
        self.stk_purchase_price.setValue(0)
        self.stk_qty.setValue(0)
        self.stk_photo.clear()
        self.set_preview_image("")

    def _stock_fill_form_from_selection(self):
        row = self._selected_row(self.tbl_stock)
        if row is None:
            return
        self.stk_name.setText(self.tbl_stock.item(row, 1).text())
        cat_name = self.tbl_stock.item(row, 2).text()
        idx = self.stk_cat.findText(cat_name)
        if idx >= 0:
            self.stk_cat.setCurrentIndex(idx)
        self.stk_barcode.setText(self.tbl_stock.item(row, 3).text())
        self.stk_price.setValue(float(self.tbl_stock.item(row, 4).text()))
        self.stk_qty.setValue(float(self.tbl_stock.item(row, 5).text()))
        if self.tbl_stock.columnCount() > 10:
            purchase_price = float(self.tbl_stock.item(row, 10).text() or "0")
            self.stk_purchase_price.setValue(purchase_price)
        self.stk_photo.setText(self.tbl_stock.item(row, 7).text())
        self.set_preview_image(self.tbl_stock.item(row, 7).text())

    def _load_stock_table(self):
        items = models.get_items()
        self.tbl_stock.setRowCount(0)
        for r in items:
            row = self.tbl_stock.rowCount()
            self.tbl_stock.insertRow(row)
            self.tbl_stock.setItem(row, 0, QTableWidgetItem(str(r["id"])))
            name_item = QTableWidgetItem(r["name"])
            name_item.setFont(QFont("Arial", 11, QFont.Bold))
            self.tbl_stock.setItem(row, 1, name_item)
            self.tbl_stock.setItem(row, 2, QTableWidgetItem(r.get("category_name", "غير مصنّف") or "غير مصنّف"))
            self.tbl_stock.setItem(row, 3, QTableWidgetItem(r["barcode"] or ""))
            self.tbl_stock.setItem(row, 4, QTableWidgetItem(fmt_money(r['price'])))
            
            stock_count = max(0, r['stock_count'] or 0)
            stock_item = QTableWidgetItem(fmt_qty(stock_count))
            if stock_count <= 0:
                stock_item.setForeground(Qt.red)
            self.tbl_stock.setItem(row, 5, stock_item)
            
            status_text = "نفد المخزون" if stock_count <= 0 else "متاح"
            status_item = QTableWidgetItem(status_text)
            if stock_count <= 0:
                status_item.setForeground(Qt.red)
            self.tbl_stock.setItem(row, 6, status_item)
            self.tbl_stock.setItem(row, 7, QTableWidgetItem(r["photo_path"] or ""))
            self.tbl_stock.setItem(row, 8, QTableWidgetItem(r["add_date"] or ""))
            self.tbl_stock.setItem(row, 9, QTableWidgetItem(str(r["category_id"] or "")))
            self.tbl_stock.setItem(row, 10, QTableWidgetItem(str(r["purchase_price"] or "0")))

    # Bill Methods
    def _handle_scanned_barcode(self):
        barcode = self.in_barcode.text().strip()
        self.in_barcode.clear()
        
        if not barcode:
            return
        
        item_row = models.get_item_by_barcode(barcode)
        item_data_dict = dict(item_row) if item_row else None

        dialog = ItemScanDialog(self, item_data=item_data_dict, currency=self.currency)
        
        if item_data_dict is None:
            dialog.in_barcode.setText(barcode)
            # For new items, default to saving to database
            dialog.chk_save_to_db.setChecked(True)
        else:
            # For existing items, don't show save to database option
            dialog.chk_save_to_db.setVisible(False)

        result = dialog.exec_()
        
        if result == ItemScanDialog.Accepted:
            item_details = dialog._return_details
            self._process_item_from_dialog_result(item_details)
        
        self.in_barcode.setFocus()

    def _process_item_from_dialog_result(self, item_details):
        # FIXED: Only save to database if it's a new item AND the user explicitly chose to save it
        if item_details["save_to_db"] and item_details["id"] == -1:
            name = item_details["name"]
            barcode_to_save = item_details["barcode"]
            price = item_details["price"]
            qty = item_details["qty"]

            if not name:
                self.msg("خطأ", "اسم المنتج مطلوب لحفظه في المخزون.")
                return False
            if barcode_to_save and not is_valid_barcode(barcode_to_save):
                self.msg("خطأ", "الباركود غير صالح لحفظ المنتج.")
                return False

            try:
                default_cat = models.get_category_by_name("غير مصنّف")
                cat_id = default_cat["id"] if default_cat else None
                
                models.add_item(name, cat_id, barcode_to_save or None, price, qty, None, purchase_price=price)
                self.msg("تم", f"تم حفظ المنتج '{name}' في قاعدة البيانات.")
                self._load_stock_table()
                self._setup_autocomplete()
                
                # Get the newly created item from database
                item_from_db = models.get_item_by_barcode(barcode_to_save) or models.search_items_by_name(name)[0]
                return self._add_item_to_current_bill(
                    item_from_db["id"], 
                    item_from_db["name"], 
                    item_from_db["barcode"], 
                    item_from_db["price"],
                    item_details["qty"], 
                    item_from_db["purchase_price"]
                )
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر حفظ المنتج:\n{e}")
                return False
        else:
            # For existing items or custom items that shouldn't be saved to DB
            item = None
            if item_details["id"] != -1:
                item = models.get_item(item_details["id"])

            purchase_price = item["purchase_price"] if item else item_details["price"]

            return self._add_item_to_current_bill(
                item_details["id"], 
                item_details["name"], 
                item_details["barcode"], 
                item_details["price"], 
                item_details["qty"], 
                purchase_price,
                is_custom=(item_details["id"] == -1)
            )

    def _bill_find_and_add_item_dialog(self):
        barcode = self.in_barcode.text().strip()
        name = self.in_name.text().strip()

        item_row = None
        if barcode:
            item_row = models.get_item_by_barcode(barcode)
        elif name:
            items_found = models.search_items_by_name(name)
            if items_found:
                item_row = items_found[0]
        
        item_data_dict = dict(item_row) if item_row else None

        dialog = ItemScanDialog(self, item_data=item_data_dict, currency=self.currency)

        if not item_data_dict and barcode:
            dialog.in_barcode.setText(barcode)
            # For new items, default to saving to database
            dialog.chk_save_to_db.setChecked(True)
        elif not item_data_dict and name:
            dialog.in_item_name.setText(name)
            dialog.in_item_name.setReadOnly(False)
            dialog.chk_manual_price.setChecked(True)
            dialog.in_price.setEnabled(True)
            # For new items, default to saving to database
            dialog.chk_save_to_db.setChecked(True)
        elif not item_data_dict and not barcode and not name:
            dialog = ItemScanDialog(self, item_data=None, currency=self.currency)
            # For new items, default to saving to database
            dialog.chk_save_to_db.setChecked(True)
        else:
            # For existing items, don't show save to database option
            dialog.chk_save_to_db.setVisible(False)

        result = dialog.exec_()
        
        if result == ItemScanDialog.Accepted:
            item_details = dialog._return_details
            self._process_item_from_dialog_result(item_details)
        
        self.in_barcode.clear()
        self.in_name.clear()
        self.in_price.setValue(0.0)
        self.in_qty.setValue(1.0)
        self.in_barcode.setFocus()

    def _on_autocomplete_selected(self, text):
        items_found = models.search_items_by_name(text)
        if items_found:
            item = dict(items_found[0])
            self.in_barcode.setText(item["barcode"] or "")
            self.in_price.setValue(float(item["price"]))
            self.in_qty.setValue(1.0)
            self.chk_manual.setChecked(False) 
            self.in_price.setEnabled(False) 
            self.in_qty.setFocus()

    def _on_name_text_changed(self, text):
        pass
        
    def _add_item_to_current_bill(self, item_id, name, barcode, price, qty, purchase_price, is_custom=False):
        if not is_custom and item_id != -1:
            db_item = models.get_item(item_id)
            
            if db_item:
                available_stock = max(0, db_item["stock_count"] or 0)
                if qty > available_stock:
                    self.msg("خطأ", f"الكمية المطلوبة ({qty}) أكبر من المخزون المتاح ({available_stock}) للصنف {name}.")
                    return False
            else:
                self.msg("خطأ", f"تعذر العثور على الصنف {name} في المخزون للتحقق من الكمية.")
                return False

        row = self.tbl_bill.rowCount()
        self.tbl_bill.insertRow(row)
        
        total = price * qty
        
        self.tbl_bill.setItem(row, 0, QTableWidgetItem(barcode or ""))
        name_item = QTableWidgetItem(name)
        name_item.setFont(QFont("Arial", 11, QFont.Bold))
        self.tbl_bill.setItem(row, 1, name_item)
        self.tbl_bill.setItem(row, 2, QTableWidgetItem(fmt_money(price)))
        self.tbl_bill.setItem(row, 3, QTableWidgetItem(fmt_qty(qty)))
        self.tbl_bill.setItem(row, 4, QTableWidgetItem(fmt_money(total)))
        self.tbl_bill.setItem(row, 5, QTableWidgetItem(str(item_id if not is_custom else "CUSTOM")))
        
        self.current_bill_items.append({
            "id": item_id,
            "name": name,
            "barcode": barcode,
            "price": price,
            "qty": qty,
            "total": total,
            "purchase_price": purchase_price,
            "is_custom": is_custom
        })
        
        self._bill_recalc_total()
        return True

    def _bill_remove_selected(self):
        row = self._selected_row(self.tbl_bill)
        if row is None:
            self.msg("تنبيه", "اختر صفًا للحذف.")
            return
        self.tbl_bill.removeRow(row)
        if row < len(self.current_bill_items):
            self.current_bill_items.pop(row)
        self._bill_recalc_total()

    def _bill_recalc_total(self):
        total_price = 0
        total_purchase_price = 0
        for item_data in self.current_bill_items:
            total_price += item_data["total"]
            total_purchase_price += item_data["qty"] * item_data["purchase_price"]
        
        self.lbl_total.setText(f"الإجمالي: {fmt_money(total_price)} {self.currency}")
        self._current_bill_total_purchase_price = total_purchase_price

    def _bill_save(self):
        if not self.current_bill_items:
            self.msg("تنبيه", "لا توجد أصناف في الفاتورة.")
            return
        try:
            total_sale_price = 0
            total_sale_purchase_price = 0
            items_to_save_details = []

            for item_data in self.current_bill_items:
                if not item_data["is_custom"]:
                    total_sale_price += item_data["total"]
                    total_sale_purchase_price += item_data["qty"] * item_data["purchase_price"]
                    items_to_save_details.append(item_data)
            
            if not items_to_save_details:
                self.msg("تنبيه", "لا توجد أصناف قابلة للحفظ في الفاتورة (جميعها منتجات مخصصة وغير محفوظة).")
                return

            sale_id = models.add_sale(total_sale_price, total_sale_purchase_price)
            
            for item_data in items_to_save_details:
                models.add_sale_detail(
                    sale_id, 
                    item_data["id"], 
                    item_data["qty"], 
                    item_data["price"], 
                    item_data["purchase_price"]
                )
            
            self.tbl_bill.setRowCount(0)
            self.current_bill_items.clear()
            self._bill_recalc_total()
            
            self.msg("تم", f"تم حفظ الفاتورة رقم {sale_id}.")
            
            self._load_sales_tab()
            self._load_stock_table()
            
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر حفظ الفاتورة:\n{e}")

    def _bill_print(self):
        if not self.current_bill_items:
            self.msg("تنبيه", "لا توجد أصناف في الفاتورة للطباعة.")
            return
        
        # Ask for print format
        format_choice = QMessageBox.question(self, "تنسيق الطباعة", 
                                           "اختر تنسيق الطباعة:\n\nنعم: فاتورة A4\nلا: تذكرة صغيرة",
                                           QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        
        if format_choice == QMessageBox.Cancel:
            return
            
        is_a4 = (format_choice == QMessageBox.Yes)
        
        printer = QPrinter(QPrinter.HighResolution)
        if not is_a4:
            # Small receipt format - use Custom paper size correctly
            printer.setPageSize(QPrinter.Custom)
            printer.setPaperSize(QSizeF(80, 297), QPrinter.Millimeter)  # Fixed: Use QSizeF instead of QSize
            printer.setPageMargins(5, 5, 5, 5, QPrinter.Millimeter)
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() != QPrintDialog.Accepted:
            return
        
        settings = models.get_settings()
        shop_name = settings["shop_name"] if settings else "متجري"
        contact = settings["contact"] if settings else ""
        location = settings["location"] if settings else ""

        # Create HTML content for receipt
        if is_a4:
            html = self._generate_a4_receipt_html(shop_name, contact, location)
        else:
            html = self._generate_small_receipt_html(shop_name, contact, location)
        
        # Print the document
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)

    def _generate_a4_receipt_html(self, shop_name, contact, location):
        html = f"""
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; text-align: right; margin: 20px; font-size: 14px; }}
            .header {{ text-align: center; margin-bottom: 20px; border-bottom: 2px dashed #000; padding-bottom: 10px; }}
            .shop-name {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
            .contact {{ font-size: 16px; margin-bottom: 5px; }}
            .receipt-info {{ margin: 20px 0; border-bottom: 2px dashed #000; padding-bottom: 10px; }}
            .info-line {{ margin-bottom: 10px; font-size: 16px; }}
            .items-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .items-table th, .items-table td {{ border: 1px solid #000; padding: 8px; text-align: right; font-size: 14px; }}
            .items-table th {{ background-color: #f2f2f2; font-weight: bold; }}
            .total-row {{ font-weight: bold; font-size: 18px; text-align: left; padding-top: 10px; }}
            .footer {{ margin-top: 20px; text-align: center; font-size: 14px; border-top: 2px dashed #000; padding-top: 10px; }}
        </style>
        </head>
        <body>
            <div class="header">
                <div class="shop-name">{shop_name}</div>
                <div class="contact">{contact}</div>
                <div class="contact">{location}</div>
            </div>
            
            <div class="receipt-info">
                <div class="info-line">التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div class="info-line">رقم الفاتورة: (لم تحفظ بعد)</div>
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>الصنف</th>
                        <th>السعر ({self.currency})</th>
                        <th>الكمية</th>
                        <th>المجموع ({self.currency})</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in self.current_bill_items:
            html += f"""
                    <tr>
                        <td>{item['name']}</td>
                        <td>{fmt_money(item['price'])}</td>
                        <td>{fmt_qty(item['qty'])}</td>
                        <td>{fmt_money(item['total'])}</td>
                    </tr>
            """
        
        total = sum(item["total"] for item in self.current_bill_items)
        html += f"""
                </tbody>
            </table>
            
            <div class="total-row">المجموع الكلي: {fmt_money(total)} {self.currency}</div>
            
            <div class="footer">
                شكرًا لزيارتكم<br>
                {contact}
            </div>
        </body>
        </html>
        """
        return html

    def _generate_small_receipt_html(self, shop_name, contact, location):
        html = f"""
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; text-align: right; margin: 5px; font-size: 10px; }}
            .header {{ text-align: center; margin-bottom: 5px; border-bottom: 1px dashed #000; padding-bottom: 5px; }}
            .shop-name {{ font-size: 14px; font-weight: bold; margin-bottom: 3px; }}
            .contact {{ font-size: 10px; margin-bottom: 2px; }}
            .receipt-info {{ margin: 5px 0; border-bottom: 1px dashed #000; padding-bottom: 5px; }}
            .info-line {{ margin-bottom: 3px; font-size: 10px; }}
            .items-table {{ width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 10px; }}
            .items-table th, .items-table td {{ border: none; padding: 2px; text-align: right; }}
            .items-table th {{ font-weight: bold; }}
            .total-row {{ font-weight: bold; font-size: 12px; text-align: left; padding-top: 5px; border-top: 1px dashed #000; }}
            .footer {{ margin-top: 5px; text-align: center; font-size: 9px; border-top: 1px dashed #000; padding-top: 5px; }}
        </style>
        </head>
        <body>
            <div class="header">
                <div class="shop-name">{shop_name}</div>
                <div class="contact">{contact}</div>
            </div>
            
            <div class="receipt-info">
                <div class="info-line">التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>الصنف</th>
                        <th>السعر</th>
                        <th>الكمية</th>
                        <th>المجموع</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in self.current_bill_items:
            html += f"""
                    <tr>
                        <td>{item['name'][:20] + ('...' if len(item['name']) > 20 else '')}</td>
                        <td>{fmt_money(item['price'])}</td>
                        <td>{fmt_qty(item['qty'])}</td>
                        <td>{fmt_money(item['total'])}</td>
                    </tr>
            """
        
        total = sum(item["total"] for item in self.current_bill_items)
        html += f"""
                </tbody>
            </table>
            
            <div class="total-row">المجموع: {fmt_money(total)} {self.currency}</div>
            
            <div class="footer">
                شكرًا لكم<br>
                {contact}
            </div>
        </body>
        </html>
        """
        return html

    # Sales Methods
    def _load_sales_tab(self):
        sales = models.get_sales()
        self.tbl_sales.setRowCount(0)
        
        # Load sales table
        for r in sales:
            row = self.tbl_sales.rowCount()
            self.tbl_sales.insertRow(row)
            self.tbl_sales.setItem(row, 0, QTableWidgetItem(str(r["id"])))
            self.tbl_sales.setItem(row, 1, QTableWidgetItem(r["datetime"]))
            self.tbl_sales.setItem(row, 2, QTableWidgetItem(f"{fmt_money(r['total_price'])} {self.currency}"))
            self.tbl_sales.setItem(row, 3, QTableWidgetItem(f"{fmt_money(r['total_price'] - r['total_purchase_price'])} {self.currency}"))

    def _on_sale_selection_changed(self):
        selected = self.tbl_sales.selectionModel().hasSelection()
        self.btn_sale_view.setEnabled(selected)
        self.btn_sale_delete.setEnabled(selected)
        self.btn_sale_print.setEnabled(selected)

    def _sales_view_selected(self):
        row = self._selected_row(self.tbl_sales)
        if row is None:
            self.msg("تنبيه", "اختر فاتورة للعرض.")
            return
        sale_id = int(self.tbl_sales.item(row, 0).text())
        
        # Show the sale details in a popup dialog
        dialog = SaleDetailsDialog(sale_id, self.currency, self)
        dialog.exec_()

    def _sales_delete_selected(self):
        row = self._selected_row(self.tbl_sales)
        if row is None:
            self.msg("تنبيه", "اختر فاتورة للحذف.")
            return
        sale_id = int(self.tbl_sales.item(row, 0).text())
        confirm = QMessageBox.question(self, "تأكيد", f"سيتم حذف الفاتورة رقم {sale_id}.\nهل أنت متأكد؟", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                models.delete_sale(sale_id)
                self._load_sales_tab()
                self.msg("تم", f"تم حذف الفاتورة رقم {sale_id}.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر حذف الفاتورة:\n{e}")

    def _sales_print_selected(self):
        row = self._selected_row(self.tbl_sales)
        if row is None:
            self.msg("تنبيه", "اختر فاتورة للطباعة.")
            return
        
        sale_id = int(self.tbl_sales.item(row, 0).text())
        sale_info = models.get_sale_by_id(sale_id)
        sale_details = models.get_sale_details(sale_id)
        
        if not sale_info:
            self.msg("خطأ", "تعذر العثور على الفاتورة.")
            return
        
        # Ask for print format
        format_choice = QMessageBox.question(self, "تنسيق الطباعة", 
                                           "اختر تنسيق الطباعة:\n\nنعم: فاتورة A4\nلا: تذكرة صغيرة",
                                           QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        
        if format_choice == QMessageBox.Cancel:
            return
            
        is_a4 = (format_choice == QMessageBox.Yes)
        
        # FIXED: Changed QPrriter to QPrinter
        printer = QPrinter(QPrinter.HighResolution)
        if not is_a4:
            # Small receipt format - use Custom paper size correctly
            printer.setPageSize(QPrinter.Custom)
            printer.setPaperSize(QSizeF(80, 297), QPrinter.Millimeter)  # Fixed: Use QSizeF instead of QSize
            printer.setPageMargins(5, 5, 5, 5, QPrinter.Millimeter)
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() != QPrintDialog.Accepted:
            return
        
        settings = models.get_settings()
        shop_name = settings["shop_name"] if settings else "متجري"
        contact = settings["contact"] if settings else ""
        location = settings["location"] if settings else ""

        # Create HTML content for receipt
        if is_a4:
            html = self._generate_a4_sale_receipt_html(sale_id, sale_info, sale_details, shop_name, contact, location)
        else:
            html = self._generate_small_sale_receipt_html(sale_id, sale_info, sale_details, shop_name, contact, location)
        
        # Print the document
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)

    def _generate_a4_sale_receipt_html(self, sale_id, sale_info, sale_details, shop_name, contact, location):
        html = f"""
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; text-align: right; margin: 20px; font-size: 14px; }}
            .header {{ text-align: center; margin-bottom: 20px; border-bottom: 2px dashed #000; padding-bottom: 10px; }}
            .shop-name {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
            .contact {{ font-size: 16px; margin-bottom: 5px; }}
            .receipt-info {{ margin: 20px 0; border-bottom: 2px dashed #000; padding-bottom: 10px; }}
            .info-line {{ margin-bottom: 10px; font-size: 16px; }}
            .items-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .items-table th, .items-table td {{ border: 1px solid #000; padding: 8px; text-align: right; font-size: 14px; }}
            .items-table th {{ background-color: #f2f2f2; font-weight: bold; }}
            .total-row {{ font-weight: bold; font-size: 18px; text-align: left; padding-top: 10px; }}
            .footer {{ margin-top: 20px; text-align: center; font-size: 14px; border-top: 2px dashed #000; padding-top: 10px; }}
        </style>
        </head>
        <body>
            <div class="header">
                <div class="shop-name">{shop_name}</div>
                <div class="contact">{contact}</div>
                <div class="contact">{location}</div>
            </div>
            
            <div class="receipt-info">
                <div class="info-line">التاريخ: {sale_info['datetime']}</div>
                <div class="info-line">رقم الفاتورة: {sale_id}</div>
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>الصنف</th>
                        <th>السعر ({self.currency})</th>
                        <th>الكمية</th>
                        <th>المجموع ({self.currency})</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in sale_details:
            html += f"""
                    <tr>
                        <td>{item['item_name']}</td>
                        <td>{fmt_money(item['price_each'])}</td>
                        <td>{fmt_qty(item['quantity'])}</td>
                        <td>{fmt_money(item['subtotal'])}</td>
                    </tr>
            """
        
        total = sale_info['total_price']
        html += f"""
                </tbody>
            </table>
            
            <div class="total-row">المجموع الكلي: {fmt_money(total)} {self.currency}</div>
            
            <div class="footer">
                شكرًا لزيارتكم<br>
                {contact}
            </div>
        </body>
        </html>
        """
        return html

    def _generate_small_sale_receipt_html(self, sale_id, sale_info, sale_details, shop_name, contact, location):
        html = f"""
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; text-align: right; margin: 5px; font-size: 10px; }}
            .header {{ text-align: center; margin-bottom: 5px; border-bottom: 1px dashed #000; padding-bottom: 5px; }}
            .shop-name {{ font-size: 14px; font-weight: bold; margin-bottom: 3px; }}
            .contact {{ font-size: 10px; margin-bottom: 2px; }}
            .receipt-info {{ margin: 5px 0; border-bottom: 1px dashed #000; padding-bottom: 5px; }}
            .info-line {{ margin-bottom: 3px; font-size: 10px; }}
            .items-table {{ width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 10px; }}
            .items-table th, .items-table td {{ border: none; padding: 2px; text-align: right; }}
            .items-table th {{ font-weight: bold; }}
            .total-row {{ font-weight: bold; font-size: 12px; text-align: left; padding-top: 5px; border-top: 1px dashed #000; }}
            .footer {{ margin-top: 5px; text-align: center; font-size: 9px; border-top: 1px dashed #000; padding-top: 5px; }}
        </style>
        </head>
        <body>
            <div class="header">
                <div class="shop-name">{shop_name}</div>
                <div class="contact">{contact}</div>
            </div>
            
            <div class="receipt-info">
                <div class="info-line">التاريخ: {sale_info['datetime'][:16]}</div>
                <div class="info-line">الفاتورة: #{sale_id}</div>
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>الصنف</th>
                        <th>السعر</th>
                        <th>الكمية</th>
                        <th>المجموع</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in sale_details:
            html += f"""
                    <tr>
                        <td>{item['item_name'][:20] + ('...' if len(item['item_name']) > 20 else '')}</td>
                        <td>{fmt_money(item['price_each'])}</td>
                        <td>{fmt_qty(item['quantity'])}</td>
                        <td>{fmt_money(item['subtotal'])}</td>
                    </tr>
        """
        
        total = sale_info['total_price']
        html += f"""
                </tbody>
            </table>
            
            <div class="total-row">المجموع: {fmt_money(total)} {self.currency}</div>
            
            <div class="footer">
                شكرًا لكم<br>
                {contact}
            </div>
        </body>
        </html>
        """
        return html

    # Utility
    def _selected_row(self, table):
        selected = table.selectedItems()
        if not selected:
            return None
        return selected[0].row()

    def msg(self, title, text):
        QMessageBox.information(self, title, text)

    def _show_scanner_info(self):
        QMessageBox.information(self, "معلومات الماسح الضوئي", 
                              "لتسهيل استخدام الماسح الضوئي:\n\n"
                              "1. تأكد من أن حقل الباركود هو الحقل النشط (يظهر حوله إطار)\n"
                              "2. عند مسح الباركود، سيتم التعرف عليه تلقائيًا\n"
                              "3. إذا كان المنتج غير موجود، ستظهر نافذة لإدخال بياناته\n"
                              "4. اضغط على Enter في حقل الباركود لفتح نافذة البحث يدويًا")