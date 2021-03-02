import os
import json
from time import time
import requests
import smtplib, ssl
from dotenv import load_dotenv
load_dotenv()

def checkStreak(user):
    numOfQues = 50
    day = 60 * 60 * 24

    url = f"https://codeforces.com/api/user.status?handle={user}&from=1&count={numOfQues}"   
    
    data = requests.get(url)
    obj = json.loads(data.text)

    if obj["status"] != "OK":
        return "Server Failed"

    problems = obj["result"]

    ok = False
    for problem in problems:
        flag = False
        try:
            if problem["problem"]["rating"] >= 1700:
                flag = True
        except:
            if problem["problem"]["index"] >= "C":
                flag = True
        if problem["verdict"] == "OK" and  flag and  problem["creationTimeSeconds"] - (time() - time() % day) >= 0:
            ok = True

    return "OK" if ok else "!OK"

port = 465  # For SSL
email = os.getenv("email")
password = os.getenv("pass")


message = """\
Subject: Your Streak is in danger!

Your codeforces Streak is in danger, hurry up and solve a question.

This message is sent from Python."""

errMsg = """\
Subject: Python Streak Checker Error!

Your codeforces streak checker (on heroku) has run into some issue 
with the api, please look into this.

This message is sent from Python."""

# Create a secure SSL context
context = ssl.create_default_context()

def main(server):
    
    global message, errMsg
    day = 60 * 60 * 24
    twoHrs = 60 * 60 * 2
    letItTHrough = True
    reportMail = True
    users = os.getenv("user").split("/")
    usersEmail = os.getenv("userEmail").split("/")
    email = os.getenv("email")
    n = len(users)
    isStreakBroken = [False] * n

    while 1:
        if (time() + 60 * 30) % twoHrs < 25 and letItTHrough:           # This condition lets this if run once every 2 hrs (runs at 7:00, 9:00...) 
            cur = time() + 60 * 30 * 11                                 # adding 5:30 hrs to convert UTC to IST
            cur = int(cur % day)                                        # extracting seconds elapsed from this day
            if cur > 60 * 60 * 18:                                      # checking if its over 6pm or not                    
                i = 0
                for user in users:
                    res = checkStreak(user)
                    if res == "OK":
                        print(user + "'s " + "streak is saved")
                    elif res == "!OK":
                        print(user + "'s " + "streak is in danger!")
                        server.sendmail(email, usersEmail[i], message)
                    else:
                        server.sendmail(email, usersEmail[0], errMsg)
                    if res == "OK":
                        isStreakBroken[i] = False
                    elif res == "!OK":
                        isStreakBroken[i] = True
                    i += 1
                        
            else:
                print ("Not time yet!")

        if (time() + 60 * 30) % twoHrs < 25:
            letItTHrough = False
        if (time() + 60 * 30) % twoHrs > 25:
            letItTHrough = True

# Report Mailing System

        if (time() + 60 * 30 * 11) % day > day - 30 and reportMail:
            i = 0
            msg = """\
Subject: Yesterday's Streak Report.

    """
            for user in users:
                res = checkStreak(user)
                if res == "OK":
                    isStreakBroken[i] = False
                elif res == "!OK":
                    isStreakBroken[i] = True
                msg = msg + "{}'s Streak was {}\n".format(user, "Broken" if isStreakBroken[i] else "Alive")
                i = i + 1

                i = 0

            for user in users:
                server.sendmail(email, usersEmail[i], msg)
                i = i   + 1
                reportMail = False
        elif (time() + 60 * 30 * 11) % day < day - 30:
            reportMail = True

# Putting everything in main so that we only need to log in once.
# https://accounts.google.com/DisplayUnlockCaptcha : use this link to clear captcha when you start the script.

with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    server.login(email, password)
    print("Logged in!")
    main(server)



        
