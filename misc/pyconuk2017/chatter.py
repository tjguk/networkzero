import os, sys

from PyQt5 import QtCore, QtGui, QtWidgets

import networkzero as nw0

"""Screen display containing a panel for an accompanying image; a large
box for descriptive text; a smaller box for inventory, strength & other
attributes; and a line for entering commands
"""

class FeedbackReader(QtCore.QThread):

    message_received = QtCore.pyqtSignal(str, str)

    def __init__(self, chattery):
        super(FeedbackReader, self).__init__()
        self.chattery = chattery

    def run(self):
        while True:
            topic, message = nw0.wait_for_news_from(self.chattery)
            if topic and message:
                self.message_received.emit(topic, message)

class Chatter(QtWidgets.QWidget):

    def __init__(self, name, parent=None):
        super(Chatter, self).__init__(parent)
        self.name = name

        self.text_panel = QtWidgets.QTextEdit()
        self.text_panel.setReadOnly(True)
        self.input = QtWidgets.QLineEdit()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.text_panel, 3)
        layout.addWidget(self.input, 1)

        self.setLayout(layout)
        self.setWindowTitle("Chatter")

        self.input.editingFinished.connect(self.input_changed)
        self.input.setFocus()

        self.chattery = nw0.discover("chattery/news")
        self.responder = FeedbackReader(self.chattery)
        self.responder.message_received.connect(self.handle_response)
        self.responder.start()

    def handle_response(self, topic, message):
        text = self.text_panel.toPlainText()
        if text:
            text += "\n"
        if topic == self.name:
            topic = "ME"
        text += "%s: %s" % (topic, message)
        self.text_panel.setPlainText(text)

    def input_changed(self):
        text = self.input.text().strip()
        if text:
            nw0.send_news_to(self.chattery, self.name, text)
        self.input.clear()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Chatter = Chatter(sys.argv[1])
    Chatter.show()
    sys.exit(app.exec_())
