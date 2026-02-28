import sys
from PyQt5.QtWidgets import QApplication
from main_window import BadmintonLabeler

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BadmintonLabeler()
    window.show()
    sys.exit(app.exec_())