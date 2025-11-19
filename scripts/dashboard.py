import sys
import os
import webbrowser
import folium
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
                               QLabel, QLineEdit, QComboBox, QGroupBox, QMessageBox,
                               QTabWidget, QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Add parent directory to path to import blockchain_helper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blockchain_helper import BlockchainManager
from ml_predictor import predict_delay
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SupplyChainDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bc = None
        self.init_ui()
        self.connect_blockchain()
    
    def init_ui(self):
        self.setWindowTitle("Supply Chain Tracking Dashboard - Blockchain Enabled")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self.create_view_tab(), "View Deliveries")
        tabs.addTab(self.create_add_tab(), "Add Delivery")
        tabs.addTab(self.create_update_tab(), "Update Delivery")
        tabs.addTab(self.create_ml_tab(), "Delay Risk & ML")
        tabs.addTab(self.create_map_tab(), "Live Map")
        main_layout.addWidget(tabs)
        

        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_header(self):
        """Create header with blockchain status"""
        header = QGroupBox()
        layout = QHBoxLayout()
        
        title = QLabel("Supply Chain Dashboard")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        self.blockchain_status = QLabel("⚫ Blockchain: Disconnected")
        self.blockchain_status.setFont(QFont("Arial", 10))
        layout.addWidget(self.blockchain_status)
        
        self.contract_label = QLabel("Contract: N/A")
        self.contract_label.setFont(QFont("Arial", 9))
        layout.addWidget(self.contract_label)
        
        self.delivery_count_badge = QLabel("📦 Deliveries: 0")
        self.delivery_count_badge.setFont(QFont("Arial", 10, QFont.Bold))
        self.delivery_count_badge.setStyleSheet("background-color: #2196F3; color: white; padding: 5px 10px; border-radius: 5px;")
        layout.addWidget(self.delivery_count_badge)
        
        wipe_btn = QPushButton("Wipe Blockchain")
        wipe_btn.clicked.connect(self.wipe_blockchain)
        wipe_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")
        layout.addWidget(wipe_btn)
        
        header.setLayout(layout)
        return header
    
    def create_view_tab(self):
        """Tab for viewing deliveries"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Left side - charts
        left_layout = QVBoxLayout()
        chart_label = QLabel("Delivery Status Distribution")
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setFont(QFont("Arial", 16, QFont.Bold))
        left_layout.addWidget(chart_label)
        
        self.pie_figure = Figure(figsize=(4, 3))
        self.pie_canvas = FigureCanvas(self.pie_figure)
        left_layout.addWidget(self.pie_canvas)
        
        # Performance chart
        bar_label = QLabel("On-Time Performance")
        bar_label.setAlignment(Qt.AlignCenter)
        bar_label.setFont(QFont("Arial", 16, QFont.Bold))
        left_layout.addWidget(bar_label)
        
        self.bar_figure = Figure(figsize=(4, 3))
        self.bar_canvas = FigureCanvas(self.bar_figure)
        left_layout.addWidget(self.bar_canvas)
        
        refresh_chart_btn = QPushButton("Refresh Charts")
        refresh_chart_btn.clicked.connect(self.update_charts)
        left_layout.addWidget(refresh_chart_btn)
        
        # Average delivery time widget
        avg_time_group = QGroupBox("Average Delivery Time")
        avg_time_layout = QVBoxLayout()
        self.avg_time_label = QLabel("--")
        self.avg_time_label.setAlignment(Qt.AlignCenter)
        self.avg_time_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.avg_time_label.setStyleSheet("color: #4CAF50; padding: 10px;")
        avg_time_layout.addWidget(self.avg_time_label)
        avg_time_group.setLayout(avg_time_layout)
        left_layout.addWidget(avg_time_group)
        
        layout.addLayout(left_layout, 30)
        
        # Right side - table
        right_layout = QVBoxLayout()
        
        # Search section
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Delivery ID:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("e.g., D0001")
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_delivery)
        search_layout.addWidget(search_btn)
        
        load_all_btn = QPushButton("Load All Deliveries")
        load_all_btn.clicked.connect(self.load_all_deliveries)
        search_layout.addWidget(load_all_btn)
        
        search_layout.addStretch()
        right_layout.addLayout(search_layout)
        
        # Column management
        column_layout = QHBoxLayout()
        
        hide_col_btn = QPushButton("Hide/Show Columns")
        hide_col_btn.clicked.connect(self.toggle_columns)
        hide_col_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        column_layout.addWidget(hide_col_btn)
        
        column_layout.addStretch()
        right_layout.addLayout(column_layout)
        
        # Table
        self.delivery_table = QTableWidget()
        self.delivery_table.setColumnCount(15)
        self.delivery_table.setHorizontalHeaderLabels([
            "ID", "Delay Risk %", "Status", "On-Time Status", "Origin Lat", "Origin Lon", 
            "Dest Lat", "Dest Lon", "Current Lat", "Current Lon", 
            "Timestamp", "Expected Date", "Actual Date", "Edit", "History"
        ])
        self.delivery_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.delivery_table.setSortingEnabled(True)
        self.delivery_table.horizontalHeader().setStretchLastSection(True)
        
        # Hide coordinate columns by default
        self.delivery_table.setColumnHidden(4, True)  # Origin Lat
        self.delivery_table.setColumnHidden(5, True)  # Origin Lon
        self.delivery_table.setColumnHidden(6, True)  # Dest Lat
        self.delivery_table.setColumnHidden(7, True)  # Dest Lon
        self.delivery_table.setColumnHidden(8, True)  # Current Lat
        self.delivery_table.setColumnHidden(9, True)  # Current Lon
        
        right_layout.addWidget(self.delivery_table)
        
        layout.addLayout(right_layout, 70)
        
        widget.setLayout(layout)
        return widget
    
    def create_add_tab(self):
        """Tab for adding new deliveries"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        form = QGroupBox("Add New Delivery to Blockchain")
        form_layout = QVBoxLayout()
        
        # Delivery ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Delivery ID:"))
        self.add_id = QLineEdit()
        self.add_id.setPlaceholderText("e.g., D9999")
        id_layout.addWidget(self.add_id)
        form_layout.addLayout(id_layout)
        
        # Origin
        origin_layout = QHBoxLayout()
        origin_layout.addWidget(QLabel("Origin Lat:"))
        self.add_origin_lat = QLineEdit()
        self.add_origin_lat.setPlaceholderText("40.5")
        origin_layout.addWidget(self.add_origin_lat)
        origin_layout.addWidget(QLabel("Lon:"))
        self.add_origin_lon = QLineEdit()
        self.add_origin_lon.setPlaceholderText("-74.5")
        origin_layout.addWidget(self.add_origin_lon)
        form_layout.addLayout(origin_layout)
        
        # Destination
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Destination Lat:"))
        self.add_dest_lat = QLineEdit()
        self.add_dest_lat.setPlaceholderText("42.0")
        dest_layout.addWidget(self.add_dest_lat)
        dest_layout.addWidget(QLabel("Lon:"))
        self.add_dest_lon = QLineEdit()
        self.add_dest_lon.setPlaceholderText("-73.0")
        dest_layout.addWidget(self.add_dest_lon)
        form_layout.addLayout(dest_layout)
        
        # Current Location
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("Current Lat:"))
        self.add_current_lat = QLineEdit()
        self.add_current_lat.setPlaceholderText("41.0")
        current_layout.addWidget(self.add_current_lat)
        current_layout.addWidget(QLabel("Lon:"))
        self.add_current_lon = QLineEdit()
        self.add_current_lon.setPlaceholderText("-74.0")
        current_layout.addWidget(self.add_current_lon)
        form_layout.addLayout(current_layout)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.add_status = QComboBox()
        self.add_status.addItems(["In Transit", "Delivered", "Delayed", "Preparing for Shipment"])
        status_layout.addWidget(self.add_status)
        status_layout.addStretch()
        form_layout.addLayout(status_layout)
        
        # Expected delivery days
        days_layout = QHBoxLayout()
        days_layout.addWidget(QLabel("Expected Delivery (days from now):"))
        self.add_expected_days = QLineEdit()
        self.add_expected_days.setPlaceholderText("3")
        self.add_expected_days.setMaximumWidth(100)
        days_layout.addWidget(self.add_expected_days)
        days_layout.addStretch()
        form_layout.addLayout(days_layout)
        
        # Add button
        add_btn = QPushButton("Add to Blockchain")
        add_btn.clicked.connect(self.add_delivery)
        add_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 14px;")
        form_layout.addWidget(add_btn)
        
        form.setLayout(form_layout)
        layout.addWidget(form)
        
        # Transaction log
        log_group = QGroupBox("Transaction Log")
        log_layout = QVBoxLayout()
        self.add_log = QTextEdit()
        self.add_log.setReadOnly(True)
        self.add_log.setMaximumHeight(150)
        log_layout.addWidget(self.add_log)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_update_tab(self):
        """Tab for updating deliveries"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Update Status Section
        status_group = QGroupBox("Update Delivery Status")
        status_layout = QVBoxLayout()
        
        status_id_layout = QHBoxLayout()
        status_id_layout.addWidget(QLabel("Delivery ID:"))
        self.update_status_id = QLineEdit()
        self.update_status_id.setPlaceholderText("e.g., D0001")
        status_id_layout.addWidget(self.update_status_id)
        status_layout.addLayout(status_id_layout)
        
        status_select_layout = QHBoxLayout()
        status_select_layout.addWidget(QLabel("New Status:"))
        self.update_status_combo = QComboBox()
        self.update_status_combo.addItems(["In Transit", "Delivered", "Delayed", "Preparing for Shipment"])
        status_select_layout.addWidget(self.update_status_combo)
        status_layout.addLayout(status_select_layout)
        
        update_status_btn = QPushButton("Update Status on Blockchain")
        update_status_btn.clicked.connect(self.update_status)
        update_status_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        status_layout.addWidget(update_status_btn)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Update Location Section
        location_group = QGroupBox("Update Delivery Location")
        location_layout = QVBoxLayout()
        
        loc_id_layout = QHBoxLayout()
        loc_id_layout.addWidget(QLabel("Delivery ID:"))
        self.update_loc_id = QLineEdit()
        self.update_loc_id.setPlaceholderText("e.g., D0001")
        loc_id_layout.addWidget(self.update_loc_id)
        location_layout.addLayout(loc_id_layout)
        
        loc_coords_layout = QHBoxLayout()
        loc_coords_layout.addWidget(QLabel("New Lat:"))
        self.update_lat = QLineEdit()
        self.update_lat.setPlaceholderText("40.5")
        loc_coords_layout.addWidget(self.update_lat)
        loc_coords_layout.addWidget(QLabel("Lon:"))
        self.update_lon = QLineEdit()
        self.update_lon.setPlaceholderText("-74.5")
        loc_coords_layout.addWidget(self.update_lon)
        location_layout.addLayout(loc_coords_layout)
        
        update_loc_btn = QPushButton("Update Location on Blockchain")
        update_loc_btn.clicked.connect(self.update_location)
        update_loc_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        location_layout.addWidget(update_loc_btn)
        
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # Update log
        update_log_group = QGroupBox("Update Log")
        update_log_layout = QVBoxLayout()
        self.update_log = QTextEdit()
        self.update_log.setReadOnly(True)
        self.update_log.setMaximumHeight(150)
        update_log_layout.addWidget(self.update_log)
        update_log_group.setLayout(update_log_layout)
        layout.addWidget(update_log_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def load_risk_data(self):
        """Load risk data from JSON file"""
        try:
            with open('risk_data.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_risk_data(self, data):
        """Save risk data to JSON file"""
        with open('risk_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_risk_values(self, delivery_id):
        """Get weather and traffic risk for a delivery"""
        risk_data = self.load_risk_data()
        if delivery_id in risk_data:
            return risk_data[delivery_id].get('weather', 2), risk_data[delivery_id].get('traffic', 2)
        return 2, 2
    
    def connect_blockchain(self):
        """Connect to blockchain"""
        try:
            self.bc = BlockchainManager()
            self.blockchain_status.setText("🟢 Blockchain: Connected")
            self.blockchain_status.setStyleSheet("color: green;")
            self.contract_label.setText(f"Contract: {self.bc.contract.address[:10]}...")
            self.statusBar().showMessage("Connected to blockchain")
            # Auto-load deliveries and charts
            self.load_all_deliveries()
        except Exception as e:
            self.blockchain_status.setText("🔴 Blockchain: Disconnected")
            self.blockchain_status.setStyleSheet("color: red;")
            if "contract_address.txt" not in str(e):
                QMessageBox.warning(self, "Connection Error", 
                                  f"Failed to connect to blockchain:\n{str(e)}\n\nMake sure Ganache is running!")
    
    def search_delivery(self):
        """Search for a specific delivery"""
        delivery_id = self.search_input.text().strip()
        if not delivery_id:
            QMessageBox.warning(self, "Input Error", "Please enter a Delivery ID")
            return
        
        if not self.bc:
            QMessageBox.warning(self, "Connection Error", "Not connected to blockchain")
            return
        
        try:
            delivery = self.bc.get_delivery(delivery_id)
            if not delivery['id'] or delivery['id'] == '':
                QMessageBox.warning(self, "Not Found", f"Delivery '{delivery_id}' does not exist on the blockchain.")
                return
            self.delivery_table.setRowCount(1)
            self.populate_table_row(0, delivery)
            self.statusBar().showMessage(f"Found delivery: {delivery_id}")
        except Exception as e:
            QMessageBox.warning(self, "Not Found", f"Delivery '{delivery_id}' does not exist on the blockchain.")
    
    def load_deliveries(self):
        """Load first 10 deliveries"""
        if not self.bc:
            QMessageBox.warning(self, "Connection Error", "Not connected to blockchain")
            return
        
        self.delivery_table.setRowCount(0)
        for i in range(1, 11):
            delivery_id = f'D{i:04d}'
            try:
                delivery = self.bc.get_delivery(delivery_id)
                row = self.delivery_table.rowCount()
                self.delivery_table.insertRow(row)
                self.populate_table_row(row, delivery)
            except:
                pass
        
        self.statusBar().showMessage("Loaded first 10 deliveries from blockchain")
        self.update_delivery_count()
        self.update_charts()
    
    def load_all_deliveries(self):
        """Load all deliveries"""
        if not self.bc:
            QMessageBox.warning(self, "Connection Error", "Not connected to blockchain")
            return
        
        self.delivery_table.setRowCount(0)
        count = 0
        empty_count = 0
        i = 1
        
        # Stop after finding 50 consecutive empty IDs
        while empty_count < 50 and i < 10000:
            delivery_id = f'D{i:04d}'
            try:
                delivery = self.bc.get_delivery(delivery_id)
                if delivery['id']:
                    row = self.delivery_table.rowCount()
                    self.delivery_table.insertRow(row)
                    self.populate_table_row(row, delivery)
                    count += 1
                    empty_count = 0
                else:
                    empty_count += 1
            except:
                empty_count += 1
            i += 1
        
        self.statusBar().showMessage(f"Loaded {count} deliveries from blockchain")
        self.update_delivery_count()
        self.update_charts()
    
    def populate_table_row(self, row, delivery):
        """Populate a table row with delivery data"""
        from PySide6.QtGui import QColor
        from datetime import datetime
        
        self.delivery_table.setItem(row, 0, QTableWidgetItem(delivery['id']))
        
        # Delay Risk - initially empty
        self.delivery_table.setItem(row, 1, QTableWidgetItem("-"))
        
        # Color-coded status
        status_item = QTableWidgetItem(delivery['status'])
        color_map = {
            'In Transit': QColor(0, 0, 139),
            'Delivered': QColor(0, 100, 0),
            'Delayed': QColor(220, 20, 60),
            'Preparing for Shipment': QColor(255, 140, 0)
        }
        if delivery['status'] in color_map:
            status_item.setBackground(color_map[delivery['status']])
        self.delivery_table.setItem(row, 2, status_item)
        
        # On-Time Status
        import time as time_module
        current_time = int(time_module.time())
        expected = delivery['expected_delivery_date']
        actual = delivery['actual_delivery_date']
        
        if delivery['status'] == 'Delivered':
            if actual > 0 and actual <= expected:
                on_time_status = 'On-Time'
                on_time_color = QColor(0, 100, 0)
            else:
                on_time_status = 'Late'
                on_time_color = QColor(220, 20, 60)
        else:
            if current_time > expected:
                on_time_status = 'At Risk'
                on_time_color = QColor(220, 20, 60)
            else:
                on_time_status = 'On Track'
                on_time_color = QColor(0, 0, 139)
        
        on_time_item = QTableWidgetItem(on_time_status)
        on_time_item.setBackground(on_time_color)
        self.delivery_table.setItem(row, 3, on_time_item)
        
        self.delivery_table.setItem(row, 4, QTableWidgetItem(f"{delivery['origin_lat']:.4f}"))
        self.delivery_table.setItem(row, 5, QTableWidgetItem(f"{delivery['origin_lon']:.4f}"))
        self.delivery_table.setItem(row, 6, QTableWidgetItem(f"{delivery['dest_lat']:.4f}"))
        self.delivery_table.setItem(row, 7, QTableWidgetItem(f"{delivery['dest_lon']:.4f}"))
        self.delivery_table.setItem(row, 8, QTableWidgetItem(f"{delivery['current_lat']:.4f}"))
        self.delivery_table.setItem(row, 9, QTableWidgetItem(f"{delivery['current_lon']:.4f}"))
        self.delivery_table.setItem(row, 10, QTableWidgetItem(str(delivery['timestamp'])))
        
        # Expected delivery date
        expected_str = datetime.fromtimestamp(delivery['expected_delivery_date']).strftime('%Y-%m-%d %H:%M') if delivery['expected_delivery_date'] > 0 else 'N/A'
        self.delivery_table.setItem(row, 11, QTableWidgetItem(expected_str))
        
        # Actual delivery date
        actual_str = datetime.fromtimestamp(delivery['actual_delivery_date']).strftime('%Y-%m-%d %H:%M') if delivery['actual_delivery_date'] > 0 else 'N/A'
        self.delivery_table.setItem(row, 12, QTableWidgetItem(actual_str))
        
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 5px;")
        edit_btn.clicked.connect(lambda checked, d_id=delivery['id']: self.show_edit_dialog(d_id))
        self.delivery_table.setCellWidget(row, 13, edit_btn)
        
        # View History button
        history_btn = QPushButton("View History")
        history_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        history_btn.clicked.connect(lambda checked, d_id=delivery['id']: self.view_delivery_history(d_id))
        self.delivery_table.setCellWidget(row, 14, history_btn)
    
    def add_delivery(self):
        """Add new delivery to blockchain"""
        if not self.bc:
            QMessageBox.warning(self, "Connection Error", "Not connected to blockchain")
            return
        
        try:
            import time as time_module
            
            delivery_id = self.add_id.text().strip()
            origin_lat = float(self.add_origin_lat.text())
            origin_lon = float(self.add_origin_lon.text())
            dest_lat = float(self.add_dest_lat.text())
            dest_lon = float(self.add_dest_lon.text())
            current_lat = float(self.add_current_lat.text())
            current_lon = float(self.add_current_lon.text())
            status = self.add_status.currentText()
            
            # Expected delivery date
            days_text = self.add_expected_days.text().strip()
            days = int(days_text) if days_text else 3
            expected_date = int(time_module.time()) + (days * 24 * 60 * 60)
            
            if not delivery_id:
                raise ValueError("Delivery ID is required")
            
            self.add_log.append(f"Adding {delivery_id} to blockchain...")
            tx = self.bc.add_delivery(delivery_id, origin_lat, origin_lon, dest_lat, 
                                     dest_lon, status, current_lat, current_lon, expected_date)
            
            self.add_log.append(f"✓ Success! Transaction: {tx.txid}")
            self.add_log.append(f"  Status: {status}")
            self.add_log.append(f"  Expected in {days} days")
            self.add_log.append("-" * 50)
            
            QMessageBox.information(self, "Success", f"Delivery {delivery_id} added to blockchain!")
            self.clear_add_form()
            self.load_deliveries()
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Invalid input:\n{str(e)}")
        except Exception as e:
            self.add_log.append(f"✗ Error: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to add delivery:\n{str(e)}")
    
    def update_status(self):
        """Update delivery status"""
        if not self.bc:
            QMessageBox.warning(self, "Connection Error", "Not connected to blockchain")
            return
        
        try:
            from PySide6.QtWidgets import QInputDialog
            
            delivery_id = self.update_status_id.text().strip()
            new_status = self.update_status_combo.currentText()
            
            if not delivery_id:
                raise ValueError("Delivery ID is required")
            
            reason = ""
            if new_status == "Delayed":
                reason, ok = QInputDialog.getText(self, "Delay Reason", "Please enter reason for delay:")
                if not ok or not reason:
                    QMessageBox.warning(self, "Required", "Delay reason is required")
                    return
            
            self.update_log.append(f"Updating status for {delivery_id}...")
            tx = self.bc.update_status(delivery_id, new_status, reason)
            
            self.update_log.append(f"✓ Status updated to: {new_status}")
            if reason:
                self.update_log.append(f"  Reason: {reason}")
            self.update_log.append(f"  Transaction: {tx.txid}")
            self.update_log.append("-" * 50)
            
            QMessageBox.information(self, "Success", f"Status updated to: {new_status}")
            self.load_deliveries()
            
        except Exception as e:
            self.update_log.append(f"✗ Error: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to update status:\n{str(e)}")
    
    def update_location(self):
        """Update delivery location"""
        if not self.bc:
            QMessageBox.warning(self, "Connection Error", "Not connected to blockchain")
            return
        
        try:
            delivery_id = self.update_loc_id.text().strip()
            lat = float(self.update_lat.text())
            lon = float(self.update_lon.text())
            
            if not delivery_id:
                raise ValueError("Delivery ID is required")
            
            self.update_log.append(f"Updating location for {delivery_id}...")
            tx = self.bc.update_location(delivery_id, lat, lon)
            
            self.update_log.append(f"✓ Location updated to: ({lat}, {lon})")
            self.update_log.append(f"  Transaction: {tx.txid}")
            self.update_log.append("-" * 50)
            
            QMessageBox.information(self, "Success", f"Location updated!")
            self.load_deliveries()
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Invalid input:\n{str(e)}")
        except Exception as e:
            self.update_log.append(f"✗ Error: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to update location:\n{str(e)}")
    
    def clear_add_form(self):
        """Clear add delivery form"""
        self.add_id.clear()
        self.add_origin_lat.clear()
        self.add_origin_lon.clear()
        self.add_dest_lat.clear()
        self.add_dest_lon.clear()
        self.add_current_lat.clear()
        self.add_current_lon.clear()
        self.add_expected_days.clear()
    
    def wipe_blockchain(self):
        """Wipe blockchain by restarting Ganache and redeploying contract"""
        reply = QMessageBox.question(self, "Wipe Blockchain",
                                    "This will delete ALL blockchain data and restart Ganache.\n\nAre you sure?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                import subprocess
                import time
                
                # Kill Ganache
                subprocess.run(['pkill', '-f', 'ganache'], check=False)
                time.sleep(2)
                
                # Remove database and contract address
                import shutil
                if os.path.exists('ganache_db'):
                    shutil.rmtree('ganache_db')
                if os.path.exists('contract_address.txt'):
                    os.remove('contract_address.txt')
                
                # Start Ganache
                subprocess.Popen(['./start_ganache.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(3)
                
                # Reconnect (will auto-deploy new contract)
                self.bc = None
                self.connect_blockchain()
                self.delivery_table.setRowCount(0)
                QMessageBox.information(self, "Success", "Blockchain wiped and new contract deployed!")
                    
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to wipe blockchain:\n{str(e)}\n\nYou may need to manually restart Ganache.")
    

    def create_ml_tab(self):
        """Tab for risk factors and delay prediction"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Single delivery section
        single_group = QGroupBox("Calculate Risk for Single Delivery")
        single_layout = QVBoxLayout()
        
        # Delivery ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Delivery ID:"))
        self.ml_single_id = QLineEdit()
        self.ml_single_id.setPlaceholderText("e.g., D0001")
        id_layout.addWidget(self.ml_single_id)
        single_layout.addLayout(id_layout)
        
        # Weather Risk
        weather_layout = QHBoxLayout()
        weather_layout.addWidget(QLabel("Weather Risk (1-5):"))
        self.ml_weather = QComboBox()
        self.ml_weather.addItems(["1", "2", "3", "4", "5"])
        self.ml_weather.setCurrentIndex(1)
        weather_layout.addWidget(self.ml_weather)
        weather_layout.addWidget(QLabel("(1=Clear, 5=Severe)"))
        weather_layout.addStretch()
        single_layout.addLayout(weather_layout)
        
        # Traffic Risk
        traffic_layout = QHBoxLayout()
        traffic_layout.addWidget(QLabel("Traffic Difficulty (1-5):"))
        self.ml_traffic = QComboBox()
        self.ml_traffic.addItems(["1", "2", "3", "4", "5"])
        self.ml_traffic.setCurrentIndex(1)
        traffic_layout.addWidget(self.ml_traffic)
        traffic_layout.addWidget(QLabel("(1=Light, 5=Heavy)"))
        traffic_layout.addStretch()
        single_layout.addLayout(traffic_layout)
        
        # Calculate button
        calc_single_btn = QPushButton("Calculate Delay Risk")
        calc_single_btn.clicked.connect(self.calculate_single_delay_risk)
        calc_single_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 14px;")
        single_layout.addWidget(calc_single_btn)
        
        # Result display
        self.ml_single_result = QLabel("Result: -")
        self.ml_single_result.setAlignment(Qt.AlignCenter)
        self.ml_single_result.setStyleSheet("font-size: 18px; font-weight: bold; padding: 15px; border: 2px solid #ccc; border-radius: 5px;")
        single_layout.addWidget(self.ml_single_result)
        
        single_group.setLayout(single_layout)
        layout.addWidget(single_group)
        
        # Batch calculation section
        batch_group = QGroupBox("Calculate Risk for All Loaded Deliveries")
        batch_layout = QVBoxLayout()
        
        calc_all_btn = QPushButton("Calculate Delay Risk for All")
        calc_all_btn.clicked.connect(self.calculate_all_delay_risks)
        calc_all_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 15px; font-size: 14px;")
        batch_layout.addWidget(calc_all_btn)
        
        self.ml_status = QLabel("Status: Ready")
        self.ml_status.setAlignment(Qt.AlignCenter)
        batch_layout.addWidget(self.ml_status)
        
        batch_group.setLayout(batch_layout)
        layout.addWidget(batch_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def calculate_single_delay_risk(self):
        """Calculate delay risk for a single delivery"""
        from PySide6.QtGui import QColor
        
        delivery_id = self.ml_single_id.text().strip()
        if not delivery_id:
            QMessageBox.warning(self, "Input Error", "Please enter a Delivery ID")
            return
        
        if not self.bc:
            QMessageBox.warning(self, "Connection Error", "Not connected to blockchain")
            return
        
        try:
            # Get delivery data
            delivery = self.bc.get_delivery(delivery_id)
            if not delivery['id']:
                QMessageBox.warning(self, "Not Found", f"Delivery '{delivery_id}' not found")
                return
            
            # Get risk values from form
            weather_risk = int(self.ml_weather.currentText())
            traffic_risk = int(self.ml_traffic.currentText())
            
            # Save risk factors
            risk_data = self.load_risk_data()
            risk_data[delivery_id] = {'weather': weather_risk, 'traffic': traffic_risk}
            self.save_risk_data(risk_data)
            
            # If already delivered, risk is 0
            if delivery['status'] == 'Delivered':
                delay_prob = 0.0
            else:
                # Predict
                delay_prob = predict_delay(delivery, weather_risk, traffic_risk)
            
            if delay_prob is not None:
                # Determine risk level and color
                if delay_prob < 30:
                    risk_level = "Low Risk"
                    color = "background-color: #4CAF50; color: white;"
                elif delay_prob < 60:
                    risk_level = "Medium Risk"
                    color = "background-color: #FF9800; color: white;"
                else:
                    risk_level = "High Risk"
                    color = "background-color: #f44336; color: white;"
                
                self.ml_single_result.setText(f"Delay Probability: {delay_prob:.1f}% - {risk_level}")
                self.ml_single_result.setStyleSheet(f"font-size: 18px; font-weight: bold; padding: 15px; border-radius: 5px; {color}")
                
                # Update table if delivery is loaded
                for row in range(self.delivery_table.rowCount()):
                    item = self.delivery_table.item(row, 0)
                    if item and item.text() == delivery_id:
                        risk_item = QTableWidgetItem(f"{delay_prob:.1f}%")
                        if delay_prob < 30:
                            risk_item.setBackground(QColor(0, 100, 0))
                        elif delay_prob < 60:
                            risk_item.setBackground(QColor(255, 140, 0))
                        else:
                            risk_item.setBackground(QColor(220, 20, 60))
                        self.delivery_table.setItem(row, 1, risk_item)
                        break
                
                QMessageBox.information(self, "Success", 
                    f"Delay risk calculated: {delay_prob:.1f}%\nRisk factors saved for {delivery_id}")
            else:
                self.ml_single_result.setText("Error: Prediction failed")
                self.ml_single_result.setStyleSheet("font-size: 18px; font-weight: bold; padding: 15px; border: 2px solid #f44336; border-radius: 5px; color: #f44336;")
                QMessageBox.warning(self, "Error", "Failed to calculate prediction. Check Julia installation.")
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to calculate risk:\n{str(e)}")
    
    def calculate_all_delay_risks(self):
        """Calculate delay risk for all deliveries in table"""
        from PySide6.QtGui import QColor
        
        if not self.bc:
            QMessageBox.warning(self, "Connection Error", "Not connected to blockchain")
            return
        
        self.ml_status.setText("Status: Calculating predictions...")
        
        success_count = 0
        fail_count = 0
        
        # Process each row in the table
        for row in range(self.delivery_table.rowCount()):
            delivery_id_item = self.delivery_table.item(row, 0)
            if not delivery_id_item:
                continue
            
            delivery_id = delivery_id_item.text()
            
            try:
                # Get delivery data
                delivery = self.bc.get_delivery(delivery_id)
                weather_risk, traffic_risk = self.get_risk_values(delivery_id)
                
                # If already delivered, risk is 0
                if delivery['status'] == 'Delivered':
                    delay_prob = 0.0
                else:
                    # Predict
                    delay_prob = predict_delay(delivery, weather_risk, traffic_risk)
                
                if delay_prob is not None:
                    # Update table
                    risk_item = QTableWidgetItem(f"{delay_prob:.1f}%")
                    if delay_prob < 30:
                        risk_item.setBackground(QColor(0, 100, 0))
                    elif delay_prob < 60:
                        risk_item.setBackground(QColor(255, 140, 0))
                    else:
                        risk_item.setBackground(QColor(220, 20, 60))
                    
                    self.delivery_table.setItem(row, 1, risk_item)
                    success_count += 1
                else:
                    self.delivery_table.setItem(row, 1, QTableWidgetItem("Error"))
                    fail_count += 1
            except Exception as e:
                self.delivery_table.setItem(row, 1, QTableWidgetItem("Error"))
                fail_count += 1
        
        self.ml_status.setText(f"Status: Complete - {success_count} successful, {fail_count} failed")
        
        if success_count > 0:
            QMessageBox.information(self, "Predictions Complete", 
                f"Calculated delay risk for {success_count} deliveries.\nCheck the View Deliveries tab to see results.")
        else:
            QMessageBox.warning(self, "Prediction Failed", 
                "Failed to calculate predictions. Make sure Julia is installed and the model is trained.")
    
    def create_map_tab(self):
        """Tab for interactive map visualization"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls = QGroupBox("Map Controls")
        controls_layout = QVBoxLayout()
        
        # Status filters
        filter_label = QLabel("Filter by Status:")
        filter_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        controls_layout.addWidget(filter_label)
        
        filter_layout = QHBoxLayout()
        from PySide6.QtWidgets import QCheckBox
        self.filter_in_transit = QCheckBox("In Transit")
        self.filter_in_transit.setChecked(True)
        filter_layout.addWidget(self.filter_in_transit)
        
        self.filter_delivered = QCheckBox("Delivered")
        self.filter_delivered.setChecked(True)
        filter_layout.addWidget(self.filter_delivered)
        
        self.filter_delayed = QCheckBox("Delayed")
        self.filter_delayed.setChecked(True)
        filter_layout.addWidget(self.filter_delayed)
        
        self.filter_preparing = QCheckBox("Preparing")
        self.filter_preparing.setChecked(True)
        filter_layout.addWidget(self.filter_preparing)
        
        controls_layout.addLayout(filter_layout)
        
        gen_btn = QPushButton("Generate Interactive Map")
        gen_btn.clicked.connect(self.generate_and_open_map)
        gen_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 20px; font-size: 18px; font-weight: bold; margin-top: 10px;")
        controls_layout.addWidget(gen_btn)
        
        self.map_status = QLabel("Map: Not generated")
        self.map_status.setAlignment(Qt.AlignCenter)
        self.map_status.setStyleSheet("font-size: 14px; padding: 10px;")
        controls_layout.addWidget(self.map_status)
        
        controls.setLayout(controls_layout)
        layout.addWidget(controls)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def generate_and_open_map(self):
        """Refresh the map with current delivery locations"""
        if not self.bc:
            QMessageBox.warning(self, "Connection Error", "Not connected to blockchain")
            return
        
        try:
            # Create map centered on US
            m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
            
            # Get selected filters
            show_statuses = []
            if self.filter_in_transit.isChecked():
                show_statuses.append('In Transit')
            if self.filter_delivered.isChecked():
                show_statuses.append('Delivered')
            if self.filter_delayed.isChecked():
                show_statuses.append('Delayed')
            if self.filter_preparing.isChecked():
                show_statuses.append('Preparing for Shipment')
            
            # Load deliveries and add markers
            delivery_count = 0
            for i in range(1, 101):  # Try first 100 deliveries
                delivery_id = f'D{i:04d}'
                try:
                    delivery = self.bc.get_delivery(delivery_id)
                    
                    # Filter by selected statuses
                    if delivery['status'] not in show_statuses:
                        continue
                    
                    # Color based on status
                    color_map = {
                        'In Transit': '#00008B',
                        'Delivered': '#006400',
                        'Delayed': '#DC143C',
                        'Preparing for Shipment': '#FF8C00'
                    }
                    hex_color = color_map.get(delivery['status'], 'gray')
                    
                    # Origin marker (small circle)
                    folium.CircleMarker(
                        location=[delivery['origin_lat'], delivery['origin_lon']],
                        radius=5,
                        popup=f"<b>Origin</b><br>{delivery['id']}",
                        color='gray',
                        fill=True,
                        fillColor='white',
                        fillOpacity=0.8
                    ).add_to(m)
                    
                    # Destination marker (star)
                    folium.Marker(
                        location=[delivery['dest_lat'], delivery['dest_lon']],
                        popup=f"<b>Destination</b><br>{delivery['id']}",
                        icon=folium.Icon(color='black', icon='star', prefix='fa')
                    ).add_to(m)
                    
                    # Calculate distance to destination (Haversine formula)
                    import math
                    lat1, lon1 = math.radians(delivery['current_lat']), math.radians(delivery['current_lon'])
                    lat2, lon2 = math.radians(delivery['dest_lat']), math.radians(delivery['dest_lon'])
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                    c = 2 * math.asin(math.sqrt(a))
                    distance_km = 6371 * c  # Earth radius in km
                    distance_miles = distance_km * 0.621371
                    
                    # Current location marker (truck) with custom color
                    folium.Marker(
                        location=[delivery['current_lat'], delivery['current_lon']],
                        popup=f"""<b>{delivery['id']}</b><br>
                                  Status: {delivery['status']}<br>
                                  Current: ({delivery['current_lat']:.2f}, {delivery['current_lon']:.2f})<br>
                                  Destination: ({delivery['dest_lat']:.2f}, {delivery['dest_lon']:.2f})<br>
                                  <b>Distance to Destination: {distance_miles:.1f} miles ({distance_km:.1f} km)</b>""",
                        tooltip=f"{delivery['id']}: {distance_miles:.0f} mi remaining",
                        icon=folium.DivIcon(html=f'<div style="font-size: 24px; color: {hex_color};"><i class="fa fa-truck"></i></div>')
                    ).add_to(m)
                    
                    # Draw route: origin -> current -> destination
                    folium.PolyLine(
                        locations=[
                            [delivery['origin_lat'], delivery['origin_lon']],
                            [delivery['current_lat'], delivery['current_lon']],
                            [delivery['dest_lat'], delivery['dest_lon']]
                        ],
                        color=hex_color,
                        weight=2,
                        opacity=0.6,
                        dash_array='5, 10'
                    ).add_to(m)
                    
                    delivery_count += 1
                except:
                    pass
            
            # Add legend
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; right: 50px; width: 220px; height: 200px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:13px; padding: 10px">
            <p><b>Map Legend</b></p>
            <p><i class="fa fa-circle" style="color:gray"></i> Origin</p>
            <p><i class="fa fa-star" style="color:black"></i> Destination</p>
            <p><i class="fa fa-truck" style="color:#00008B"></i> In Transit</p>
            <p><i class="fa fa-truck" style="color:#006400"></i> Delivered</p>
            <p><i class="fa fa-truck" style="color:#DC143C"></i> Delayed</p>
            <p><i class="fa fa-truck" style="color:#FF8C00"></i> Preparing</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Save to file and open in browser
            map_file = 'supply_chain_map.html'
            m.save(map_file)
            
            # Open in default browser
            webbrowser.open('file://' + os.path.abspath(map_file))
            
            self.map_status.setText(f"✓ Map generated with {delivery_count} deliveries")
            
            QMessageBox.information(self, "Map Generated", 
                                  f"Map with {delivery_count} deliveries opened in your browser!")
            
        except Exception as e:
            self.map_status.setText(f"Error: {str(e)}")
            QMessageBox.warning(self, "Map Error", f"Failed to generate map:\n{str(e)}")
    
    def update_delivery_count(self):
        """Update delivery count badge"""
        if not self.bc:
            return
        
        count = 0
        empty_count = 0
        i = 1
        
        while empty_count < 50 and i < 10000:
            try:
                delivery = self.bc.get_delivery(f'D{i:04d}')
                if delivery['id']:
                    count += 1
                    empty_count = 0
                else:
                    empty_count += 1
            except:
                empty_count += 1
            i += 1
        
        self.delivery_count_badge.setText(f"📦 Deliveries: {count}")
    
    def update_charts(self):
        """Update both pie chart and bar chart"""
        self.update_pie_chart()
        self.update_bar_chart()
        self.update_avg_delivery_time()
    
    def update_avg_delivery_time(self):
        """Calculate and display average delivery time"""
        if not self.bc:
            return
        
        try:
            import time as time_module
            total_time = 0
            count = 0
            
            empty_count = 0
            i = 1
            while empty_count < 50 and i < 10000:
                delivery_id = f'D{i:04d}'
                try:
                    delivery = self.bc.get_delivery(delivery_id)
                    if not delivery['id']:
                        empty_count += 1
                        i += 1
                        continue
                    empty_count = 0
                    if delivery['status'] == 'Delivered' and delivery['actual_delivery_date'] > 0:
                        delivery_time = delivery['actual_delivery_date'] - delivery['timestamp']
                        total_time += delivery_time
                        count += 1
                except:
                    empty_count += 1
                i += 1
            
            if count > 0:
                avg_seconds = total_time / count
                avg_hours = avg_seconds / 3600
                avg_days = avg_hours / 24
                
                if avg_days >= 1:
                    self.avg_time_label.setText(f"{avg_days:.1f} days")
                else:
                    self.avg_time_label.setText(f"{avg_hours:.1f} hours")
            else:
                self.avg_time_label.setText("No data")
        except Exception as e:
            print(f"Error calculating avg delivery time: {e}")
    
    def update_pie_chart(self):
        """Update pie chart with delivery status distribution"""
        if not self.bc:
            return
        
        try:
            status_counts = {'In Transit': 0, 'Delivered': 0, 'Delayed': 0, 'Preparing for Shipment': 0}
            
            empty_count = 0
            i = 1
            while empty_count < 50 and i < 10000:
                delivery_id = f'D{i:04d}'
                try:
                    delivery = self.bc.get_delivery(delivery_id)
                    if not delivery['id']:
                        empty_count += 1
                        i += 1
                        continue
                    empty_count = 0
                    if delivery['status'] in status_counts:
                        status_counts[delivery['status']] += 1
                except:
                    empty_count += 1
                i += 1
            
            self.pie_figure.clear()
            ax = self.pie_figure.add_subplot(111)
            
            labels = []
            sizes = []
            colors = []
            color_map = {'In Transit': '#00008B', 'Delivered': '#006400', 'Delayed': '#DC143C', 'Preparing for Shipment': '#FF8C00'}
            
            for status, count in status_counts.items():
                if count > 0:
                    labels.append(f"{status}\n({count})")
                    sizes.append(count)
                    colors.append(color_map[status])
            
            if sizes:
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, 
                      textprops={'fontsize': 7, 'color': 'white'}, pctdistance=0.85, labeldistance=1.05)
                ax.axis('equal')
            else:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes, color='white')
            
            self.pie_figure.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')
            self.pie_figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
            self.pie_canvas.draw()
        except Exception as e:
            print(f"Error updating pie chart: {e}")
    
    def update_bar_chart(self):
        """Update bar chart with on-time performance"""
        if not self.bc:
            return
        
        try:
            import time as time_module
            current_time = int(time_module.time())
            
            performance = {'On-Time': 0, 'Late': 0, 'At Risk': 0, 'On Track': 0}
            
            empty_count = 0
            i = 1
            while empty_count < 50 and i < 10000:
                delivery_id = f'D{i:04d}'
                try:
                    delivery = self.bc.get_delivery(delivery_id)
                    if not delivery['id']:
                        empty_count += 1
                        i += 1
                        continue
                    empty_count = 0
                    
                    expected = delivery['expected_delivery_date']
                    actual = delivery['actual_delivery_date']
                    
                    if delivery['status'] == 'Delivered':
                        if actual > 0 and actual <= expected:
                            performance['On-Time'] += 1
                        else:
                            performance['Late'] += 1
                    else:
                        if current_time > expected:
                            performance['At Risk'] += 1
                        else:
                            performance['On Track'] += 1
                except:
                    empty_count += 1
                i += 1
            
            self.bar_figure.clear()
            ax = self.bar_figure.add_subplot(111)
            
            categories = list(performance.keys())
            counts = list(performance.values())
            colors = ['#006400', '#DC143C', '#FF8C00', '#00008B']
            
            if sum(counts) > 0:
                bars = ax.barh(categories, counts, color=colors)
                ax.set_xlabel('Deliveries', fontsize=9, color='white')
                ax.tick_params(axis='both', labelsize=8, colors='white')
                ax.grid(True, alpha=0.3, axis='x', color='white')
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.spines['right'].set_color('white')
                
                for bar, count in zip(bars, counts):
                    if count > 0:
                        ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2, 
                               f' {count}', va='center', fontsize=9, fontweight='bold', color='white')
            else:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes, color='white')
            
            self.bar_figure.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')
            self.bar_figure.tight_layout()
            self.bar_canvas.draw()
        except Exception as e:
            print(f"Error updating bar chart: {e}")
    
    def show_edit_dialog(self, delivery_id):
        """Show edit dialog for delivery"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QInputDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Delivery - {delivery_id}")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"<h3>Update {delivery_id}</h3>")
        layout.addWidget(title)
        
        # Update Status Section
        status_group = QGroupBox("Update Status")
        status_layout = QVBoxLayout()
        
        status_combo = QComboBox()
        status_combo.addItems(["In Transit", "Delivered", "Delayed", "Preparing for Shipment"])
        status_layout.addWidget(status_combo)
        
        update_status_btn = QPushButton("Update Status")
        update_status_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        status_layout.addWidget(update_status_btn)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Update Location Section
        location_group = QGroupBox("Update Location")
        location_layout = QVBoxLayout()
        
        loc_layout = QHBoxLayout()
        loc_layout.addWidget(QLabel("Lat:"))
        lat_input = QLineEdit()
        lat_input.setPlaceholderText("40.5")
        loc_layout.addWidget(lat_input)
        loc_layout.addWidget(QLabel("Lon:"))
        lon_input = QLineEdit()
        lon_input.setPlaceholderText("-74.5")
        loc_layout.addWidget(lon_input)
        location_layout.addLayout(loc_layout)
        
        update_loc_btn = QPushButton("Update Location")
        update_loc_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px;")
        location_layout.addWidget(update_loc_btn)
        
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Connect update buttons
        def do_update_status():
            try:
                new_status = status_combo.currentText()
                reason = ""
                if new_status == "Delayed":
                    reason, ok = QInputDialog.getText(dialog, "Delay Reason", "Please enter reason for delay:")
                    if not ok or not reason:
                        QMessageBox.warning(dialog, "Required", "Delay reason is required")
                        return
                
                tx = self.bc.update_status(delivery_id, new_status, reason)
                QMessageBox.information(dialog, "Success", f"Status updated to: {new_status}")
                self.load_deliveries()
                dialog.accept()
            except Exception as e:
                QMessageBox.warning(dialog, "Error", f"Failed to update status:\n{str(e)}")
        
        def do_update_location():
            try:
                lat = float(lat_input.text())
                lon = float(lon_input.text())
                tx = self.bc.update_location(delivery_id, lat, lon)
                QMessageBox.information(dialog, "Success", f"Location updated to: ({lat}, {lon})")
                self.load_deliveries()
                dialog.accept()
            except ValueError:
                QMessageBox.warning(dialog, "Input Error", "Please enter valid coordinates")
            except Exception as e:
                QMessageBox.warning(dialog, "Error", f"Failed to update location:\n{str(e)}")
        
        update_status_btn.clicked.connect(do_update_status)
        update_loc_btn.clicked.connect(do_update_location)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def view_delivery_history(self, delivery_id):
        """View delivery update history"""
        if not self.bc:
            return
        
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
            from datetime import datetime
            
            status_history = self.bc.get_status_history(delivery_id)
            location_history = self.bc.get_location_history(delivery_id)
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Update History - {delivery_id}")
            dialog.setMinimumSize(500, 400)
            layout = QVBoxLayout()
            
            history_text = QTextEdit()
            history_text.setReadOnly(True)
            
            content = f"<h2>Delivery History: {delivery_id}</h2>"
            
            if status_history:
                content += "<h3>Status Updates:</h3><ul>"
                for update in reversed(status_history):
                    timestamp = datetime.fromtimestamp(update['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                    content += f"<li><b>{timestamp}</b> - Status changed to: <b>{update['status']}</b>"
                    if update.get('reason'):
                        content += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;<i>Reason: {update['reason']}</i>"
                    content += "</li>"
                content += "</ul>"
            else:
                content += "<p>No status updates recorded.</p>"
            
            if location_history:
                content += "<h3>Location Updates:</h3><ul>"
                for update in reversed(location_history):
                    timestamp = datetime.fromtimestamp(update['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                    content += f"<li><b>{timestamp}</b> - Location: ({update['lat']:.4f}, {update['lon']:.4f})</li>"
                content += "</ul>"
            else:
                content += "<p>No location updates recorded.</p>"
            
            history_text.setHtml(content)
            layout.addWidget(history_text)
            
            buttons = QDialogButtonBox(QDialogButtonBox.Close)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load history:\n{str(e)}")
    
    def toggle_columns(self):
        """Show dialog to hide/show columns"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Hide/Show Columns")
        layout = QVBoxLayout()
        
        checkboxes = []
        for i in range(self.delivery_table.columnCount()):
            header = self.delivery_table.horizontalHeaderItem(i).text()
            checkbox = QCheckBox(header)
            checkbox.setChecked(not self.delivery_table.isColumnHidden(i))
            checkbox.col_index = i
            checkboxes.append(checkbox)
            layout.addWidget(checkbox)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec():
            for checkbox in checkboxes:
                self.delivery_table.setColumnHidden(checkbox.col_index, not checkbox.isChecked())
            self.statusBar().showMessage("Column visibility updated")
    
    def closeEvent(self, event):
        """Handle window close"""
        event.accept()

def main():
    app = QApplication(sys.argv)
    dashboard = SupplyChainDashboard()
    dashboard.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
