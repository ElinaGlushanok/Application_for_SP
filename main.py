import sys
from uiClasses import Enter
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Enter()
    ex.show()
    sys.exit(app.exec())