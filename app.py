import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Estilo moderno para todas las plataformas
    
    # Forzar tema claro para la aplicación
    app.setStyleSheet("""
        QWidget {
            background-color: #F5F5F5;
            color: #000000;
        }
        QGraphicsView {
            background-color: #FFFFFF;
        }
        QLabel {
            color: #000000;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
