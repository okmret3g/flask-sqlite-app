from flask import Flask, request, render_template, redirect, url_for, jsonify
import markdown
import sqlite3

app = Flask(__name__)


# データベースの初期化
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL)''')
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


# markdown文字列をデータベースに追加
def add_post(mdstr):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO posts (content) VALUES (?)', (mdstr, ))
    conn.commit()
    conn.close()


# markdown文字列リストを取得
def get_posts():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, content FROM posts ORDER BY id desc')
    posts = c.fetchall()
    conn.close()
    return [(post[0], markdown.markdown(post[1])) for post in posts]

# 全ポスト取得（非同期）
@app.route('/getPosts')
def get_posts_api():
    posts = get_posts()
    return jsonify([
        {'id': pid, 'html': html}
        for pid, html in posts
    ])


# postを別画面として見る
@app.route('/post/<int:post_id>')
def view_post(post_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT content FROM posts WHERE id = ?', (post_id, ))
    row = c.fetchone()
    conn.close()

    if row:
        html = markdown.markdown(row[0])
        return render_template('post.html', post_id=post_id, content=html)
    else:
        return "Post not found", 404


# markdown文字列をデータベースに追加
def del_post(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM posts WHERE id = (?)', (id, ))
    conn.commit()
    conn.close()


@app.route('/')
def index():
    posts = get_posts()
    # MarkdownをHTMLに変換
    posts_html = [(post[0], markdown.markdown(post[1])) for post in posts]
    return render_template('index.html', posts=posts_html, users=get_users())


@app.route('/addName', methods=['POST'])
def addName():
    name = request.form.get('name')
    if name:
        add_user(name)
    return redirect(url_for('index'))


@app.route('/addMD', methods=['POST'])
def addMD():
    content = request.form.get('content', '')
    if content:
        add_post(content)
        html = markdown.markdown(content)
        return jsonify({'status': 'ok', 'html': html})
    return jsonify({'status': 'error'}), 400
    # return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()  # アプリケーション開始時にデータベースを初期化
    app.run(host='0.0.0.0', port=3000)  # Replitでのホスティング用に0.0.0.0にバインド
