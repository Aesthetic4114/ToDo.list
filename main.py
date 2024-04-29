import json
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Jūsu īpašā atslēga


def create_connection():
    conn = sqlite3.connect('tasks.db')
    return conn


def create_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_ID INTEGER,
                 description TEXT NOT NULL, 
                 completed BOOLEAN NOT NULL DEFAULT 0, 
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (
                 account_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 username VARCHAR(50) NOT NULL UNIQUE,
                 password VARCHAR(50) NOT NULL)''')
    conn.commit()
    conn.close()

create_table()

def read_text_data(tab):
  text_file = open('Data/texts.json', encoding='utf8')
  tab_text = json.load(text_file)
  text_file.close()
  if tab == "index":
    return tab_text.get("index")
  elif tab == "register":
    return tab_text.get("register")
  elif tab == "login":
    return tab_text.get("login")
  elif tab == "list":
    return tab_text.get("list")



@app.route('/')
def index():
    texts = read_text_data("index")
    if 'account_ID' in session:
        account_ID = session['account_ID']
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE user_ID=?", (account_ID,))
        tasks = c.fetchall()
        conn.close()
        return render_template('index.html', texts=texts, tasks=tasks)
    else:
        return render_template('index.html', texts=texts)


@app.route('/list')
def list():
    account_ID = session.get('account_ID')
    if account_ID:
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE user_ID=?", (account_ID,))
        tasks = c.fetchall()
        conn.close()
        return render_template('list.html', tasks=tasks)
    else:
        return render_template('login.html')


@app.route('/add_task', methods=['POST'])
def add_task():
    if request.method == 'POST':
        if 'account_ID' in session:
            user_ID = session['account_ID']
            description = request.form['description']
            conn = create_connection()
            c = conn.cursor()
            c.execute("INSERT INTO tasks (user_ID, description) VALUES (?, ?)", (user_ID, description))
            conn.commit()
            conn.close()
            flash('Uzdevums pievienots!', 'success')
            return redirect('/list')
        else:
            flash('Lūdzu, pieslēdzieties, lai pievienotu uzdevumu!', 'error')
    return redirect('/')


@app.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    if request.method == 'POST':
        if 'account_ID' in session:
            new_description = request.form['new_description']
            conn = create_connection()
            c = conn.cursor()
            c.execute("UPDATE tasks SET description=? WHERE id=?", (new_description, task_id))
            conn.commit()
            conn.close()
            flash('Uzdevuma apraksts veiksmīgi labots!', 'success')
            return redirect('/list')
        else:
            flash('Lūdzu, pieslēdzieties, lai rediģētu uzdevumu!', 'error')
    return redirect('/')


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'account_ID' in session:
        conn = create_connection()
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
        flash('Uzdevums veiksmīgi dzēsts!', 'success')
        return redirect('/list')
    else:
        flash('Lūdzu, pieslēdzieties, lai dzēstu uzdevumu!', 'error')
    return redirect('/')


@app.route('/toggle_completed/<int:task_id>')
def toggle_completed(task_id):
    if 'account_ID' in session:
        conn = create_connection()
        c = conn.cursor()
        c.execute("UPDATE tasks SET completed = NOT completed WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
        flash('Uzdevums veiksmīgi atzīmēts!', 'success')
        return redirect('/list')
    else:
        flash('Lūdzu, pieslēdzieties, lai atzīmētu uzdevumu!', 'error')
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM accounts WHERE username=? AND password=?", (username, password))
        account = c.fetchone()

        if account:
            session['account_ID'] = account[0]
            session['username'] = account[1]
            flash('Pieslēgšanās veiksmīga!', 'success')
            conn.close()
            return redirect('/list')
        else:
            flash('Nepareizs lietotājvārds vai parole!', 'error')
            conn.close()
            return redirect('/login')
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM accounts WHERE username=?", (username,))
        existing_account = c.fetchone()

        if existing_account:
            flash('Šis lietotājvārds jau ir aizņemts!', 'error')
            conn.close()
            return redirect('/register')
        else:
            c.execute("INSERT INTO accounts (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            flash('Reģistrācija veiksmīga, lūdzu pieslēdzieties!', 'success')
            return redirect('/')
    else:
        return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('account_ID', None)
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8080)