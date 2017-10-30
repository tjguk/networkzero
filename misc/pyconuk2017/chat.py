import os, sys

import networkzero as nw0
from guizero import App, Box, Text, TextBox

app = App(width=400)
box = Box(app)
chatter = Text(box, align="top")
speaking = TextBox(box, align="bottom", width=400)

chatter.append("Hello\n")
chatter.append("World\n")
chatter.color("blue")
chatter.append("!")

app.display()
