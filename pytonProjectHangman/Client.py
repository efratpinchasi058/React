import json
import uuid
from requests import session
import User
import levels
import logo
from colorama import init, Fore
init(autoreset=True)  # מאתחל את colorama

word = ""
session = session()
basic_url = "http://127.0.0.1:5000"
new_id = str(uuid.uuid4())
played_words = []
current_user = {"name": "", "ID": "", "password": "","word":[], "countP": 0, "wins": 0}


def my_play():
    global current_user
    global played_words
    hide_word = ""
    word = ran_w()
    my_list = list(word)
    hide_word = ["💚" if char != " " else " " for char in word]
    print("".join(hide_word))
    attempts = 0
    attempts_left = 7
    wrong_guesses = []  # רשימה של תווים שהוזנו לא נכונים

    while attempts < 7:
        x = input(Fore.YELLOW+"enter a letter: ").lower()
        while len(x) != 1 or not x.isalpha():
            print(Fore.RED+"input only one letter!")
            x = input(Fore.YELLOW+"enter a letter: ").lower()
        if x in wrong_guesses or x in hide_word:
            print(Fore.RED+"You already guessed this letter.")
            continue
        if x in my_list:
            for i in range(len(my_list)):
                if my_list[i] == x:
                    hide_word[i] = x
            print(Fore.BLUE+"Good guess!")
        else:
            wrong_guesses.append(x)
            attempts_left -= 1
            attempts += 1
            print(Fore.MAGENTA+levels.levels[attempts - 1])
            print(f"The number of disqualifications:{attempts_left}")

        print("".join(hide_word))  # הדפסת המילה המוסתרת

        # אם המילה נחשפה לחלוטין
        if "".join(hide_word) == word:
            print("You win!!!!, the word was " + "".join(hide_word))
            played_words.append(word)  # הוספת המילה להיסטוריה של המילים שהוגרלו
            current_user["wins"] += 1
            break
    if attempts == 7:  # אם הנסיונות נגמרו
        print(Fore.RED+f"Game over! The word was: {word}")
        played_words.append(word)  # הוספת המילה להיסטוריה של המילים שהוגרלו

def choice():
    user_message = Fore.BLUE+"""
       Enter your choice:
       1.To login press 1
       2.To register press 2
       3.To play press 3
       4.To see your history press 4
       5.To exit press 5
       """
    while True:
        try:
            choice1 = int(input(user_message))
            if not choice1:
                print("Please enter a valid choice.")
                choice1 = int(input(user_message))
                continue
            elif not 0 < choice1 < 6:
                print("Invalid input. Try again")
                continue
            elif choice1 == 1:
                login_user2()
            elif choice1 == 2:
                register_user1()
            elif choice1 == 3:
                my_play()
            elif choice1 == 4:
                vew_history()
            elif choice1 == 5:
                print("Goodbye!")
                break
        except ValueError:
            print("Invalid input. Please enter a number.")


def register_user1():
    print("Register:")
    # הכנת הנתונים לרישום המשתמש
    payload = {
        "name": input("Enter your username: ").strip(),
        "ID": new_id,
        "password": input("Enter your password: ").strip(),
        "countP": 0,
        "word": [],
        "wins": 0
    }
    # שליחת בקשת POST לשרת כדי לרשום משתמש חדש
    response = session.post(f"{basic_url}/register_user", json=payload)
    # אם הרישום הצליח (קוד 200)
    if response.status_code == 200:
        print("User registered successfully!")
        print(response.json())
        login_user2()
        # הגדרת Cookie עם שם המשתמש
    # אם הבקשה נכשלה (קוד 400)
    elif response.status_code == 400:
        print(response.json())
        register_user1()
    elif response.status_code == 401:
        register_user1()


def login_user2():
    global current_user
    print(Fore.GREEN+"Login:")
    payload1 = {
        "name": input(Fore.GREEN+"Enter your username: ").strip(),
        "ID": new_id,
        "password": input(Fore.GREEN+"Enter your password: ").strip(),
        "countP": 0,
        "word": [],
        "wins": 0
    }
    print(Fore.RED+"Sending login request...")
    response2 = session.post(f"{basic_url}/login", json=payload1)
    current_user = response2.json()
    # print(response2.status_code)

    if response2.status_code == 200:
        current_user = response2.json()  # קבלת נתוני המשתמש ב-JSON
        # לוודא שהנתונים שהתקבלו כוללים את כל המפתחות הנדרשים
        current_user["wins"] = current_user.get("wins", 0)
        current_user["countP"] = current_user.get("countP", 0)
        current_user["words"] = current_user.get("words", [])
        current_user["name"] = current_user.get("name", payload1["name"])  # הוספת שם המשתמש
        cookie_payload = {"user_name": payload1["name"]}
        cookie_response = session.post(f"{basic_url}/set_cookie", json=cookie_payload)
        if cookie_response.status_code == 200:
            print(Fore.YELLOW + f"Hello {payload1["name"]}, welcome back!!")
            # print("Cookie set successfully!")
            choice()  # קריאה ל- choice אם ההתחברות הצליחה
        else:
            print("Failed to set Cookie:", cookie_response.text)

    elif response2.status_code == 404:
        print("User not found, registering user...")
        choice()

    elif response2.status_code == 400:
        print("Both username and password are required!")
        login_user2()  # אם יש בעיה עם פרטי ההתחברות, ננסה שוב

def vew_history():
    global played_words
    global current_user

    current_user["countP"] += 1  # עדכון כמות המשחקים
    current_user["word"] = played_words  # עדכון רשימת המילים ששוחקו

    response = session.post(f"{basic_url}/update_history", json=current_user)
    if response.status_code == 200:
        print(f"counts play: {current_user['countP']} ,wins: {current_user['wins']}")
    else:
        print(f"Error: {response.status_code} - {response.json().get('error')}")

def ran_w():
    num = int(input(Fore.YELLOW+"enter a number: "))
    response = session.get(f"{basic_url}/random_word/{num}")
    if response.status_code == 200:
            return response.json()["word"]
    if response.status_code == 400:
        print(response.json())
        return ""
    if response.status_code == 403:
        print(response.json())
        login_user2()


choice()
