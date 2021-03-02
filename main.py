import os
import json
from time import time
import requests
import smtplib, ssl
from dotenv import load_dotenv
load_dotenv()

def checkStreak(user):
    url = f"https://codeforces.com/api/user.status?handle={user}&from=1&count={numOfQues}"   
    
    data = requests.get(url)
    obj = json.loads(data.text)

    if obj["status"] != "OK":
        return "Server Failed"

    problems = obj["result"]

    ok = False
    for problem in problems:
        if(problem["verdict"] == "OK" and problem["problem"]["rating"] >= 1700) and  problem["creationTimeSeconds"] - (time() - time() % day) >= 0:
            ok = True

    return "OK" if ok else "!OK"

numOfQues = 50
users = os.getenv("user").split("/")
usersEmail = os.getenv("userEmail").split("/")
port = 465  # For SSL
email = os.getenv("email")
password = os.getenv("pass")
n = len(users)
isStreakBroken = [False] * n

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
day = 60 * 60 * 24
twoHrs = 60 * 60 * 2
letItTHrough = True
reportMail = True

while 1:
    if (time() - 60 * 60) % twoHrs < 25 and letItTHrough:   # This condition lets this if run once every 2 hrs (runs at 6:30, 8:30...) 
        cur = time() + 60 * 30 * 11                         # adding 5:30 hrs to convert UTC to IST
        cur = int(cur % day)                                # extracting seconds elapsed from this day
        if cur > 60 * 60 * 18:                              # checking if its over 6pm or not                    
            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                server.login(email, password)
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

    if (time() - 60 * 60) % twoHrs < 25:
        letItTHrough = False
    if (time() - 60 * 60) % twoHrs > 25:
        letItTHrough = True

# Report Mailing System

    if (time() + 60 * 30 * 11) % day < 25 and reportMail:
        i = 0
        msg = """\
Subject: Yesterday's Streak Report.

"""
        for user in users:
            msg = msg + "{}'s Streak was {}\n".format(user, "Broken" if isStreakBroken[i] else "Alive")
            i = i + 1

        i = 0
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email, password)
            for user in users:
                server.sendmail(email, usersEmail[i], msg)
                i = i + 1
        reportMail = False
    elif (time() + 60 * 30 * 11) % day > 25:
        reportMail = True

        
