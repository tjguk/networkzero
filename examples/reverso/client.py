import networkzero as nw0

try:
    # Python 2.7 compat
    input = raw_input
except NameError:
    pass

reverso = nw0.discover("reverso")
while True:
    word = input("Enter word: ")
    reversed_word = nw0.send_message_to(reverso, word)
    print("Reversed:", reversed_word)
