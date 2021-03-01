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
        if(problem["verdict"] == "OK" and problem["problem"]["rating"] >= 1700):
            ok = True

    return "OK" if ok else "!OK"

numOfQues = 10
users = os.getenv("user").split("/")
usersEmail = os.getenv("userEmail").split("/")
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

start = time()
# Create a secure SSL context
context = ssl.create_default_context()

while 1:
    cur = time()
    if cur - start > 10:
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email, password)
            i = 0
            for user in users:
                res = checkStreak(user)
                if user == "bufftowel":
                    res = "!OK"
                if res == "OK":
                    print(user + "'s " + "Streak Saved")
                elif res == "!OK":
                    server.sendmail(email, usersEmail[i], message)
                else:
                    server.sendmail(email, usersEmail[0], errMsg)
                i += 1
        start = cur
        
