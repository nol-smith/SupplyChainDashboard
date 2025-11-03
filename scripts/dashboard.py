import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
                               QLabel, QLineEdit, QComboBox, QGroupBox, QMessageBox,
                               QTabWidget, QTextEdit)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from blockchain_helper import BlockchainManager

class BlockchainWorker(QThread):
    """Worker thread for blockchain operations to prevent UI freezing"""
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args
    
    def run(self):
        try:
            result = self.operation(*self.args)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

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
        
        header.setLayout(layout)
        return header
    
    def create_view_tab(self):
        """Tab for viewing deliveries"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Search section
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Delivery ID:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("e.g., D0001")
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_delivery)
        search_layout.addWidget(search_btn)
        
        load_all_btn = QPushButton("Load First 10")
        load_all_btn.clicked.connect(self.load_deliveries)
        search_layout.addWidget(load_all_btn)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Table
        self.delivery_table = QTableWidget()
        self.delivery_table.setColumnCount(9)
        self.delivery_table.setHorizontalHeaderLabels([
            "ID", "Status", "Origin Lat", "Origin Lon", 
            "Dest Lat", "Dest Lon", "Current Lat", "Current Lon", "Timestamp"
        ])
        self.delivery_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.delivery_table)
        
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
    
    def connect_blockchain(self):
        """Connect to blockchain"""
        try:
            self.bc = BlockchainManager()
            self.blockchain_status.setText("🟢 Blockchain: Connected")
            self.blockchain_status.setStyleSheet("color: green;")
            self.contract_label.setText(f"Contract: {self.bc.contract.address[:10]}...")
            self.statusBar().showMessage("Connected to blockchain")
        except Exception as e:
            self.blockchain_status.setText("🔴 Blockchain: Disconnected")
            self.blockchain_status.setStyleSheet("color: red;")
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
            self.delivery_table.setRowCount(1)
            self.populate_table_row(0, delivery)
            self.statusBar().showMessage(f"Found delivery: {delivery_id}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Delivery not found:\n{str(e)}")
    
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
    
    def populate_table_row(self, row, delivery):
        """Populate a table row with delivery data"""
        self.delivery_table.setItem(row, 0, QTableWidgetItem(delivery['id']))
        self.delivery_table.setItem(row, 1, QTableWidgetItem(delivery['status']))
        self.delivery_table.setItem(row, 2, QTableWidgetItem(f"{delivery['origin_lat']:.4f}"))
        self.delivery_table.setItem(row, 3, QTableWidgetItem(f"{delivery['origin_lon']:.4f}"))
        self.delivery_table.setItem(row, 4, QTableWidgetItem(f"{delivery['dest_lat']:.4f}"))
        self.delivery_table.setItem(row, 5, QTableWidgetItem(f"{delivery['dest_lon']:.4f}"))
        self.delivery_table.setItem(row, 6, QTableWidgetItem(f"{delivery['current_lat']:.4f}"))
        self.delivery_table.setItem(row, 7, QTableWidgetItem(f"{delivery['current_lon']:.4f}"))
        self.delivery_table.setItem(row, 8, QTableWidgetItem(str(delivery['timestamp'])))
    
    def add_delivery(self):
        """Add new delivery to blockchain"""
        if not self.bc:
            QMessageBox.warning(self, "Connection Error", "Not connected to blockchain")
            return
        
        try:
            delivery_id = self.add_id.text().strip()
            origin_lat = float(self.add_origin_lat.text())
            origin_lon = float(self.add_origin_lon.text())
            dest_lat = float(self.add_dest_lat.text())
            dest_lon = float(self.add_dest_lon.text())
            current_lat = float(self.add_current_lat.text())
            current_lon = float(self.add_current_lon.text())
            status = self.add_status.currentText()
            
            if not delivery_id:
                raise ValueError("Delivery ID is required")
            
            self.add_log.append(f"Adding {delivery_id} to blockchain...")
            tx = self.bc.add_delivery(delivery_id, origin_lat, origin_lon, dest_lat, 
                                     dest_lon, status, current_lat, current_lon)
            
            self.add_log.append(f"✓ Success! Transaction: {tx.txid}")
            self.add_log.append(f"  Status: {status}")
            self.add_log.append("-" * 50)
            
            QMessageBox.information(self, "Success", f"Delivery {delivery_id} added to blockchain!")
            self.clear_add_form()
            
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
            delivery_id = self.update_status_id.text().strip()
            new_status = self.update_status_combo.currentText()
            
            if not delivery_id:
                raise ValueError("Delivery ID is required")
            
            self.update_log.append(f"Updating status for {delivery_id}...")
            tx = self.bc.update_status(delivery_id, new_status)
            
            self.update_log.append(f"✓ Status updated to: {new_status}")
            self.update_log.append(f"  Transaction: {tx.txid}")
            self.update_log.append("-" * 50)
            
            QMessageBox.information(self, "Success", f"Status updated to: {new_status}")
            
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

def main():
    app = QApplication(sys.argv)
    dashboard = SupplyChainDashboard()
    dashboard.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
