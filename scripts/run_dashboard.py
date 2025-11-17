import sys
from PySide6.QtWidgets import QApplication
from scripts.dashboard import SupplyChainDashboard

def main():
    app = QApplication(sys.argv)
    dashboard = SupplyChainDashboard()
    dashboard.show()
    sys.exit(app.exec())
