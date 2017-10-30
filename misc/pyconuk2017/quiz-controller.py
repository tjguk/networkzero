#!python2
import os, sys
import socket
import subprocess

import Pyro4
from PyQt4 import QtCore, QtGui

import core
import screen
import screens

class FeedbackReader(QtCore.QThread):

    message_received = QtCore.pyqtSignal(unicode, tuple)

    def __init__(self, proxy):
        super(FeedbackReader, self).__init__()
        self.feedback = proxy

    def run(self):
        while True:
            feedback = self.feedback.get()
            core.log.debug("feedback: %r", feedback)
            if feedback:
                message, args = feedback
                self.message_received.emit(message, args)

class Panel(QtGui.QGroupBox):

    def __init__(self, controller, position, *args, **kwargs):
        super(Panel, self).__init__(position.title(), *args, **kwargs)
        self.instructions = controller
        self.position = position.lower()

        layout = QtGui.QVBoxLayout()
        self.selector = QtGui.QComboBox()
        self.selector.currentIndexChanged.connect(self.on_selector)

        layout.addWidget(self.selector)
        self.stack = QtGui.QStackedWidget()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        for cls in screen.ScreenWidget.__subclasses__():
            self.selector.addItem(cls.name)
            self.stack.addWidget(cls(controller, position))

    def on_selector(self, index):
        core.log.debug("on_selector: %d, item %r", index, self.selector.itemText(index))
        self.stack.setCurrentIndex(index)
        screen_name = unicode(self.selector.itemText(index))
        self.instructions.send_command("SWITCH", self.position, screen_name)

class QuizController(QtGui.QWidget):

    COMMAND_MAILSLOT_NAME = "quiz"
    RESPONSE_MAILSLOT_NAME = "sub"

    def __init__(self, *args, **kwargs):
        super(QuizController, self).__init__(*args, **kwargs)
        self.setWindowTitle("Quiz Controller")

        self.instructions = Pyro4.Proxy("PYRO:quiz.instructions@localhost:1234")
        self.responder = FeedbackReader(Pyro4.Proxy("PYRO:quiz.feedback@localhost:1234"))
        self.responder.message_received.connect(self.handle_response)
        self.responder.start()

        overall_layout = QtGui.QVBoxLayout()
        self.add_teams(overall_layout)

        self.panel_layout = QtGui.QHBoxLayout()
        self.panels = {}
        for position in "left", "right":
            panel = self.panels[position.lower()] = Panel(self, position)
            self.panel_layout.addWidget(panel)
        overall_layout.addLayout(self.panel_layout)
        self.add_controller(overall_layout)
        self.setLayout(overall_layout)

        #
        # The first response is always lost. Not sure why.
        #
        self.send_command("COLOURS?")
        self.send_command("COLOURS?")
        self.send_command("SCORES?")
        self.send_command("TEAMS?")

    def add_teams(self, overall_layout):
        self.teams = []
        for i in range(4):
            team = (
                team_name,
                team_score,
                team_plus,
                team_minus
            ) = (
                QtGui.QLineEdit(),
                QtGui.QLineEdit(""),
                QtGui.QPushButton("+"),
                QtGui.QPushButton("-")
            )
            self.teams.append(team)
            layout = QtGui.QHBoxLayout()
            for widget in team:
                layout.addWidget(widget)
            overall_layout.addLayout(layout)

            def set_team_name(new_name, n_team=i, team_name=team_name, team_score=team_score):
                self.send_command("name", n_team, unicode(team_name.text()))
                if not team_name.styleSheet():
                    self.send_command("COLOURS?")
            def set_team_score(new_score, n_team=i):
                self.send_command("SCORE", str(n_team), str(new_score))
            def set_team_plus(n_team=i, team_score=team_score):
                score = 1 + int(team_score.text() or 0)
                team_score.setText(str(score))
            def set_team_minus(n_team=i, team_score=team_score):
                score = int(team_score.text() or 0) - 1
                team_score.setText(str(score))

            team_name.textEdited.connect(set_team_name)
            team_score.textChanged.connect(set_team_score)
            team_plus.pressed.connect(set_team_plus)
            team_minus.pressed.connect(set_team_minus)

    def add_controller(self, overall_layout):
        command_label = QtGui.QLabel("Command")
        self.command = QtGui.QLineEdit()
        self.send = QtGui.QPushButton("&Send")
        controller_layout = QtGui.QHBoxLayout()
        controller_layout.addWidget(command_label)
        controller_layout.addWidget(self.command)
        controller_layout.addWidget(self.send)
        overall_layout.addLayout(controller_layout)
        self.send.clicked.connect(self.send_command)

        self.responses = QtGui.QLabel()
        responses_layout = QtGui.QHBoxLayout()
        responses_layout.addWidget(self.responses)
        overall_layout.addLayout(responses_layout)

    def send_command(self, message=None, *args):
        if not message:
            commands = unicode(self.command.text()).encode("iso-8859-1").split()
            if not commands:
                core.log.warn("No command")
                return
            else:
                message, args = commands[0], commands[1:]

        args = [(unicode(arg) if isinstance(arg, QtCore.QString) else arg) for arg in args]
        command = "%s %s" % (message, " ".join(str(arg) for arg in args))
        core.log.debug("send_command: %s", command)
        if hasattr(self, "command"):
            self.command.setText(command)
        self.instructions.put(message, *args)

    def position_widget(self, position):
        return self.groups.get(position.lower())

    def handle_default(self, *args, **kwargs):
        core.log.debug("handle_default: %s, %s", str(args), str(kwargs))

    #~ def add_positions(self):
        #~ for position in "left", "right":
            #~ panel = self.panels[position.lower()] = Panel(self, position)
            #~ self.panel_layout.addWidget(panel)

    #~ def handle_position(self, position, screen_name):
        #~ """Handle the POSITION event by selecting the corresponding
        #~ screen from the stacked widget.
        #~ """
        #~ panel = self.panels[position.lower()]
        #~ if panel.selector.currentText() != screen_name:
            #~ panel.selector.setCurrentIndex(panel.selector.findText(screen_name))
            #~ #
            #~ # Changing the selector will cause a STATE? query to fire
            #~ #

    #~ def _handle_position(self, position, cls_name, state):
        #~ core.log.debug("handle_position: %s, %s", position, rest)

        #~ group = self.groups[position]
        #~ group.selector.setCurrentIndex(group.selector.findText(cls_name))
        #~ screen_widget = group.stack.currentWidget()

        #~ styles_combo = screen_widget.styles
        #~ if "styles" in state:
            #~ styles_combo.clear()
            #~ styles_combo.addItems([item.strip() for item in state.pop("styles")])
        #~ if "style" in state:
            #~ screen_widget.styles.setCurrentIndex(screen_widget.styles.findText(state.pop("style")))
        #~ for k, v in state.items():
            #~ subwidget = getattr(screen_widget, k.lower(), None)
            #~ if subwidget:
                #~ subwidget.setText(v)

    #~ def handle_left(self, *args, **kwargs):
        #~ self._handle_position("left", *args, **kwargs)

    #~ def handle_right(self, *args, **kwargs):
        #~ self._handle_position("right", *args, **kwargs)

    def handle_teams(self, teams):
        for n_team, new_name in enumerate(teams):
            name, _, _, _ = self.teams[n_team]
            name.setText(new_name)

    def handle_colours(self, colours):
        for n_team, new_colour in enumerate(colours):
            name, _, _, _ = self.teams[n_team]
            name.setStyleSheet("* { background-color : %s; }" % new_colour)

    def handle_scores(self, scores):
        for n_team, new_score in enumerate(scores):
            _, score, _, _ = self.teams[n_team]
            score.setText(unicode(new_score))

    def handle_quit(self):
        self.close()

    def handle_response(self, message, args):
        core.log.debug("Response received: %s, %s", message, args)
        message = unicode(message)
        response = "%s %s" % (message, " ".join("%r" % arg for arg in args))
        self.responses.setText(response)
        handler = getattr(self, "handle_" + message.lower(), self.handle_default)
        return handler(*args)

def main():
    app = QtGui.QApplication([])
    quiz_controller = QuizController()
    quiz_controller.show()
    return app.exec_()

if __name__ == '__main__':
    try:
        socket.socket().connect(("localhost", 1234))
    except socket.error:
        subprocess.Popen([sys.executable, "quiz.py"])
    sys.exit(main(*sys.argv[1:]))
