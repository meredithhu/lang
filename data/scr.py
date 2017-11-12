import json
import sqlite3 as lite
import sys
import urllib3
import time
from random import randint
from time import sleep
from instagram_web_api import Client, ClientCompatPatch, ClientError, ClientLoginError

urllib3.disable_warnings()
http = urllib3.PoolManager()
web_api = Client(auto_patch=True, drop_incompat_keys=False)


def saveJsonDump(media_id):
    f = open('temp.json', 'w')
    f.write(json.dumps(media_id))
    f.close()
    return

"""
returns all users from the db
return: list((user_id,username))
"""
def getUserList():
    user_list = []
    con = lite.connect("tagfeed.db")
    with con:
        cur = con.cursor()
        for row in cur.execute('SELECT * FROM Users'):
            user_list.append(row)
    return user_list

def updatePost(x,timestamp):
    s = (timestamp,x["id"],x["shortcode"], int(x["likes"]["count"]),int(x["comments"]["count"]) )

    try:
        con = lite.connect("tagfeed.db")

        with con:
            cur = con.cursor()
            cur.execute("INSERT INTO PostsUpdate VALUES(?, ?, ?,?,?)", s)
    except:
        print("ERROR WHILE SAVING POSTUPDATE..ABORT")
        #ADD kill()


def setUserUpdate(response, username, user_id, timestamp):
    temp = []
    temp.append((timestamp, int(user_id), username, int(response["counts"]["media"]),
                 int(response["counts"]["followed_by"]), int(response["counts"]["follows"])))
    print("Processing: " + username)
    try:

        con = lite.connect("tagfeed.db")

        with con:
            cur = con.cursor()
            cur.executemany("INSERT INTO UsersUpdate VALUES(?,?,?,?,?,?)", temp)
    except:
        print("Error while updating user")


def checkImageExists(mediaCode):
    con = lite.connect("tagfeed.db")

    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Images WHERE MediaCode=:Id", {"Id": mediaCode})
        con.commit()

        row = cur.fetchone()
        if row is None:
            # print("Not Found")
            return False
    return True


def downloadImageFromItem(x):
    if checkImageExists(x["shortcode"]) is True:
        return


    response = http.request('GET', x["images"]["thumbnail"]["url"].replace("150", "480", 2))
    img = response.data
    # print(img)
    con = lite.connect("tagfeed.db")

    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO Images VALUES(?, ?, ?)", (x["id"], x["shortcode"], lite.Binary(img)))


def getMediaUser(response, user_id, username, timestamp):
    x = 0
    temp = 0
    for i in [19, 8, 3]:
        try:

            temp = web_api.user_feed(user_id=str(user_id), count=i)
            x = temp
            return x
        except:
            continue
    return x


# Get Info for UserUpdate
def run():

    timestamp = int(time.time())
    user_list = getUserList()
    start = time.time()
    for i in user_list:
        temp = []
        response = web_api.user_info(user_id=str(i[0]))
        setUserUpdate(response, i[1], i[0], timestamp)
        a = getMediaUser(response, i[0], i[1], timestamp)
        if a == 0:
            continue
        print("Processing " + str(len(a)) + " posts...")
        for x in a:
            x = x["node"]

            updatePost(x, timestamp)
            downloadImageFromItem(x)
            temp.append((x["id"], x["shortcode"], x["caption"]["text"], int(x["created_time"]),
                         0 if x["location"] is 0 else 1, int(x["is_video"]), "none", i[0], i[1]))

        try:
            con = lite.connect("tagfeed.db")

            with con:
                cur = con.cursor()

                # print("HELLO")
                cur.executemany("INSERT OR IGNORE INTO Posts VALUES(?,?,?,?,?,?,?,?,?)", temp)
        except:
            print("ERROR WHILE SAVING POST..ABORT")
            # ADD kill()

    end = time.time()
    elapsed = end - start
    print("Time " + str(elapsed))


