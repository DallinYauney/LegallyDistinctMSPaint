import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton


# subclass QMainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        button = QPushButton("Press Me!")

        self.setCentralWidget(button)


# sys.argv is passed in to be able to use command line arguments
app = QApplication(sys.argv)


# all windows are invisible by default so you must call .show()
# all widgets can create windows
window = MainWindow()
window.show()

# starts the event loop QApplication class holds the Qt event loop[]
app.exec()
