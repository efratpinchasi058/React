import json
import os
import random
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
from User import User

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'your_unique_secret_key'

FILENAME = 'users.json'
WORDS = "words.txt"


def read_users():
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {"users": []}
    return {"users": []}


def write_users(data):
    with open(FILENAME, 'w') as file:
        json.dump(data, file, indent=4)


def requires_permission(func):
    def wrapper(*args, **kwargs):
        response_message = get_cookie_func().get_data(as_text=True)
        if response_message != "Cookie found!":
            return jsonify({"error": "Permission denied"}), 403
        return func(*args, **kwargs)
    return wrapper


@app.route('/register_user', methods=['POST'])
def register_user():
    use1 = User(
        name=request.json['name'],
        ID=request.json['ID'],
        password=request.json['password'],
        countP=request.json['countP'],
        wins=request.json['wins'],
        word=request.json['word']
    )
    if not use1.name or not use1.password:
        return jsonify("Both username and password are required!"), 401
    users_data = read_users()["users"]
    # Check if the user already exists
    for user in users_data:
        if user["username"] == use1.name:
            return jsonify("User already exists!"), 400

    # Add new user to the list
    users_data.append({
        "username": use1.name,
        "password": use1.password,
        "ID": use1.ID,
        "countP": use1.countP,
        "words": use1.word,
        "wins": use1.wins
    })

    # Save data back to the file
    write_users({"users": users_data})

    return jsonify(f"Hello {use1.name}!!!")


@app.route('/random_word/<int:num>', methods=['GET'])
@requires_permission
def random_word(num):
    try:
        with open(WORDS, "r") as file:
            words = file.readlines()
        words = [word.strip() for word in words]
        random.shuffle(words)
        selected_word = words[num % len(words)]
        return jsonify({"word": selected_word})
    except FileNotFoundError:
        return jsonify({"error": "The words file not found."}), 404


@app.route('/login', methods=['POST'])
def login():
    use = User(
        name=request.json['name'],
        ID=request.json['ID'],
        password=request.json['password'],
        countP=request.json['countP'],
        wins=request.json['wins'],
        word=request.json['word']
    )
    if not use.name or not use.password:
        return jsonify({"error": "Both username and password are required!"}), 400

    users_data = read_users()["users"]
    user = next((u for u in users_data if u["username"] == use.name and u["password"] == use.password), None)

    if user:
        return user, 200
    return jsonify({"error": "User not found. Please register."}), 404


@cross_origin(app, supports_credentials=True)
@app.route('/set_cookie', methods=['POST'])
def set_cookie_func():
    obj = request.json
    response = make_response("Cookie set!")
    response.set_cookie("user", obj['user_name'], max_age=600, httponly=True, secure=False, samesite='None')
    return response


@app.route('/get_cookie', methods=['GET'])
def get_cookie_func():
    user_name = request.cookies.get('user')
    if user_name:
        return make_response("Cookie found!")
    return make_response("Cookie not found")


@app.route('/update_history', methods=['POST'])
def update_history():
    # קבלת הנתונים מהבקשה
    updated_user = request.json
    # קבלת נתוני המשתמשים מהקובץ
    users_data = read_users()["users"]

    # חיפוש המשתמש בנתונים
    user = next((u for u in users_data if u["username"] == updated_user["name"] and u["password"] == updated_user["password"]), None)

    if user:
        # עדכון הפרטים של המשתמש
        user["countP"] += 1  # הגדלת ספירת המשחקים
        user["wins"] = updated_user.get("wins", user["wins"])  # עדכון ניצחונות
        # שילוב רשימת המילים הקיימת עם החדשה, תוך הימנעות מכפילויות
        user["words"] = list(set(user["words"] + updated_user.get("word", [])))

        # כתיבה מחדש של הנתונים לקובץ
        write_users({"users": users_data})

        return jsonify({"message": f"History updated successfully for user: {user['username']}!"}), 200

    return jsonify({"error": "User not found!"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
