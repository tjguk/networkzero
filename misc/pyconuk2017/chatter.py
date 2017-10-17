import os, sys

from PyQt5 import QtCore, QtGui, QtWidgets

import networkzero as nw0

"""Screen display containing a panel for an accompanying image; a large
box for descriptive text; a smaller box for inventory, strength & other
attributes; and a line for entering commands
"""

class Chatter(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(Chatter, self).__init__(parent)

        self.text_panel = QtWidgets.QTextEdit()
        self.text_panel.setReadOnly(True)

        self.input = QtWidgets.QLineEdit()
        self.input.editingFinished.connect(self.input_changed)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.text_panel, 3)
        layout.addWidget(self.input, 1)

        self.setLayout(layout)
        self.setWindowTitle("Chatter")

    def input_changed(self):
        self.text_panel.setPlainText(self.text_panel.toPlainText() + "\n" + self.input.text())
        self.input.clear()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Chatter = Chatter()
    Chatter.show()
    sys.exit(app.exec_())
