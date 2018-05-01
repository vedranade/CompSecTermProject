import re
s1 = "thishasadigit4here"
m = re.search("\d", s1)
if m:
    print "Digit found at position %d" % m.start()
else:
    print "No digit in that string"