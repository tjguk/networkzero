import networkzero as nw0

reverso = nw0.discover("reverso")
while True:
    word = input("Enter word: ")
    reversed_word = nw0.send_message_to(reverso, word)
    print("Reversed:", reversed_word)
