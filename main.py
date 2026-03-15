import sys
from PyQt6.QtWidgets import QApplication
from ui_main import WorldsAlambicApp
from styles import GLOBAL_STYLE

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Application du style global
    app.setStyleSheet(GLOBAL_STYLE)
    
    # Lancement de la fenêtre principale
    window = WorldsAlambicApp()
    window.show()
    
    sys.exit(app.exec())