import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton


# subclass QMainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Press me!")
        button.setCheckable(True)
        button.clicked.connect(self.the_button_was_clicked)
        button.clicked.connect(self.the_button_was_toggled)

        self.setCentralWidget(button)

    def the_button_was_clicked(self):
        print("ClIcKeD")

    def the_button_was_toggled(self, checked):
        print("Checked?", checked)


# sys.argv is passed in to be able to use command line arguments
app = QApplication(sys.argv)


# all windows are invisible by default so you must call .show()
# all widgets can create windows
window = MainWindow()
window.show()

# starts the event loop QApplication class holds the Qt event loop[]
app.exec()
