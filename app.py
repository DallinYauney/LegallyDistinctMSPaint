from PyQt6.QtWidgets import QApplication, QWidget

import sys


# sys.argv is passed in to be able to use command line arguments
app = QApplication(sys.argv)

# all windows are invisible by default so you must call .show()
# all widgets can create windows
window = QWidget()
window.show()

# starts the event loop QApplication class holds the Qt event loop[]
app.exec()
