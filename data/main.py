import script
import script2
from random import randint
from time import sleep

while(True):
    print("NEW ITERATION")
    try:
        script2.run()
    except:
        print("ERROR WITH HASHTAG SCRIPT")
    try:
        script.run()
    except:
        print("ERROR WITH HASHTAG SCRIPT")

    sleep(randint(0, 20))