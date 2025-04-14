from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)


# データベースの初期化
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL)''')
    conn.commit()
    conn.close()


# ユーザーをデータベースに追加
def add_user(name):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (name) VALUES (?)', (name, ))
    conn.commit()
    conn.close()


# ユーザーリストを取得
def get_users():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM users')
    users = c.fetchall()
    conn.close()
    return users


@app.route('/')
def index():
    return render_template_string("""
        <h1>Flask + SQLite Example</h1>
        <form method="post" action="/add">
            <label for="name">Name:</label>
            <input type="text" id="name" name="name">
            <button type="submit">Add User</button>
        </form>
        <h2>Users:</h2>
        <ul>
        {% for user in users %}
            <li>{{ user[1] }}</li>
        {% endfor %}
        </ul>
    """,
                                  users=get_users())


@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    if name:
        add_user(name)
    return index()


if __name__ == '__main__':
    init_db()  # アプリケーション開始時にデータベースを初期化
    app.run(host='0.0.0.0', port=3000)  # Replitでのホスティング用に0.0.0.0にバインド
