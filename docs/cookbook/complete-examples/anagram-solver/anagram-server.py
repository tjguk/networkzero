import networkzero as nw0

#
# The anagram-solving element of this will be brute-force:
# maintain a list of words and compare against them until
# you get a match or run out of words. There is obvious
# scope for optimisation here, but this will run fast enough
# and should be clear; anything further is left as an exercise
# for the reader!
#
with open("words.txt") as f:
    words = f.read().split()

#
# Advertise service as 'anagram'
#
address = nw0.advertise("anagram")

while True:
    print("Waiting for a word...")
    #
    # Receive an anagram for which we have to find a match
    #
    anagram = nw0.wait_for_message_from(address).lower().strip()
    print("Looking for %s" % anagram)
    
    #
    # To compare two words we'll sort each and compare
    # the result. We need only sort the word we're searching
    # for once.
    #
    letters = "".join(sorted(anagram))
    
    #
    # Compare our incoming anagram, sorted, against each word
    # in turn, sorted. If we get a match, send the matching 
    # word and stop searching
    #
    for word in words:
        if "".join(sorted(word)) == letters:
            print("Found %s" % word)
            nw0.send_reply_to(address, word)
            break
    
    #
    # If we can't find a match, return None
    #
    else:
        print("No match found")
        nw0.send_reply_to(address, None)
