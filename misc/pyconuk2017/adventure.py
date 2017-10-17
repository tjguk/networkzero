import os, sys

from PyQt4 import QtCore, QtGui

"""Screen display containing a panel for an accompanying image; a large
box for descriptive text; a smaller box for inventory, strength & other
attributes; and a line for entering commands
"""

class Adventure(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Adventure, self).__init__(parent)

        #
        # Top-half of the
        #
        self.image_panel = QtGui.QLabel()
        self.image_panel.setAlignment(QtCore.Qt.AlignCenter)
        self.image = QtGui.QPixmap("image.jpg")
        self.image_panel.setPixmap(self.image)

        self.text_panel = QtGui.QTextEdit()
        self.text_panel.setReadOnly(True)
        self.text_panel.setTextBackgroundColor(QtGui.QColor("blue"))
        self.text_panel.setHtml("""<h1>Hello, World!</h1>

        <p>You are in a spacious ballroom with the sound of music playing all around you.</p>
        """)

        self.data_panel = QtGui.QTextEdit()
        self.data_panel.setReadOnly(True)

        self.input = QtGui.QLineEdit()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.image_panel, 1)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(self.text_panel, 3)
        hlayout.addWidget(self.data_panel, 1)
        layout.addLayout(hlayout, 1)
        layout.addWidget(self.input)

        self.setLayout(layout)
        self.setWindowTitle("Westpark Adventure")

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    Adventure = Adventure()
    Adventure.show()
    sys.exit(app.exec_())
