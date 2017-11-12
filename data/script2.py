from InstagramAPI import InstagramAPI
import json
import sqlite3 as lite
import sys
import urllib3
import time
from random import randint
from time import sleep

con = lite.connect("tagfeed.db")


def writeUsers(item):
    temp = []
    print("Writing Users \n ")

    for i in item["ranked_items"]:
        try:
            temp.append((i["caption"]["user_id"], i["caption"]["user"]["username"]))
        except:
            continue
    for i in item["items"]:
        try:
            temp.append((i["caption"]["user_id"], i["caption"]["user"]["username"]))
        except:
            continue
    try:
        with con:
            cur = con.cursor()
            # print("HELLO")
            cur.executemany("INSERT OR IGNORE INTO Users VALUES(?,?)", temp)
    except:
        print("ERROR WHILE SAVING POST..ABORT")
        # ADD kill()


def downloadImageFromItem(item):
    if checkImageExists(item["code"]) is True:
        return

    for s in item["image_versions2"]["candidates"]:
        if s["width"] == 480 and s["height"] == 480:
            sleep(randint(0, 2))
            http = urllib3.PoolManager()
            response = http.request('GET', s["url"])
            img = response.data
            # print(img)
            with con:
                cur = con.cursor()
                cur.execute("INSERT INTO Images VALUES(?, ?, ?)",
                            (item["caption"]["media_id"], item["code"], lite.Binary(img)))

            return


def checkImageExists(mediaCode):
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Images WHERE MediaCode=:Id", {"Id": mediaCode})
        con.commit()

        row = cur.fetchone()
        if row is None:
            # print("Not Found")
            return False
    return True


def writePostsUpdateFeed(media_id, tagFeed, timestamp):
    temp = []
    print("Writing PostsUpdateFeed for " + tagFeed + " \n ")

    # for i in media_id["items"]:
    for i in media_id["ranked_items"]:
        try:
            # print(i["caption"]["media_id"])

            temp.append((timestamp, i["caption"]["media_id"], tagFeed, 1, 0))
        except:
            continue

    for i in media_id["items"]:
        try:
            # print(i["caption"]["media_id"])
            temp.append((timestamp, i["caption"]["media_id"], tagFeed, 0, 1))
        except:
            continue
    try:
        with con:
            cur = con.cursor()
            cur.executemany("INSERT INTO PostsUpdateFeed VALUES(?,?,?,?,?)", temp)
    except:
        print("ERROR WHILE SAVING POST..ABORT")
        # ADD kill()


def writePostsUpdateViaHashtag(media_id, timestamp):
    print("Writing PostsUpdateViaHashtagFeed... \n ")

    temp = []
    for i in media_id["ranked_items"]:
        try:
            # print(i["caption"]["media_id"])
            temp.append((timestamp, i["caption"]["media_id"], i["code"], i["like_count"], i["comment_count"]))
        except:
            continue
    for i in media_id["items"]:
        try:
            # print(i["caption"]["media_id"])
            temp.append((timestamp, i["caption"]["media_id"], i["code"], i["like_count"], i["comment_count"]))
        except:
            continue

    try:
        with con:
            cur = con.cursor()
            cur.executemany("INSERT INTO PostsUpdate VALUES(?, ?, ?,?,?)", temp)
    except:
        print("ERROR WHILE SAVING POST..ABORT")
        # ADD kill()


def writePosts(media_id, tagFeed):
    temp = []
    print("Writing writePosts for " + tagFeed + " \n ")

    for i in media_id["ranked_items"]:
        try:
            #  print(i["caption"]["media_id"])
            temp.append((i["caption"]["media_id"], i["code"], i["caption"]["text"], i["taken_at"],
                         (1 if "lat" in i else 0), i["media_type"], tagFeed, i["caption"]["user_id"],
                         i["caption"]["user"]["username"]))
            downloadImageFromItem(i)
        except:
            continue

    for i in media_id["items"]:
        try:
            #   print(i["caption"]["media_id"])
            temp.append((i["caption"]["media_id"], i["code"], i["caption"]["text"], i["taken_at"],
                         (1 if "lat" in i else 0), i["media_type"], tagFeed, i["caption"]["user_id"],
                         i["caption"]["user"]["username"]))
            downloadImageFromItem(i)
        except:
            continue
    try:
        with con:
            cur = con.cursor()
            # print("HELLO")
            cur.executemany("INSERT OR IGNORE INTO Posts VALUES(?,?,?,?,?,?,?,?,?)", temp)
    except:
        print("ERROR WHILE SAVING POST..ABORT")
        # ADD kill()

def writeToDatabase(media_id, tagFeed, timestamp):
    writePosts(media_id,tagFeed)
    writePostsUpdateFeed(media_id,tagFeed, timestamp)
    writePostsUpdateViaHashtag(media_id,timestamp)
    writeUsers(media_id)

def saveJsonDump(media_id):
    f = open('temp.json', 'w')
    f.write(json.dumps(media_id))
    f.close()
    return

def run():
    # tagFeeds = ["javascript", "dev", "coding", "coder", "developer", "development", "js", "java", "php", "#sublimetext","vim", "webdevelopment", "software"]

    tagFeeds = ["javscript"]

    insta = InstagramAPI("crawlboy23", "instagrampassword123")  # BOT
    insta.login()  # login
    with con:
        cur = con.cursor()

        # cur.execute("CREATE TABLE Usernames(Username TEXT)")
        #  cur.execute("CREATE TABLE Posts(Timestamp INT, MediaId INT, MediaCode TEXT, Likes INT, Comments INT, Caption TEXT, CreatedAt INT, HasLocation INT, IsVideo INT, TopPost INT, NewPost INT, HashTagFeed TEXT, UserId INT, Username TEXT)")
        #  cur.execute("CREATE TABLE Images(MediaId INT, MediaCode TEXT, Image BLOB)")


    start = time.time()

    timestamp = int(time.time())
    for feed in range(0, len(tagFeeds)):
        print(tagFeeds[feed])
        insta.tagFeed(tagFeeds[feed])

        media_id = insta.LastJson
        # saveJsonDump(media_id)
        writeToDatabase(media_id, tagFeeds[feed], timestamp)
        #    except:
        #       print("Error processing the tag "+ tagFeeds[feed])
        sleep(randint(0, 2))

    end = time.time()
    elapsed = end - start
    print("Time "+ str(elapsed))