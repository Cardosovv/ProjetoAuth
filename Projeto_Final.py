import sqlite3
from flask import request, jsonify, Flask

app = Flask(__name__)

#criação do banco de dados
def get_database():
    conn = sqlite3.connect('Banco2.0.db')
    cur = conn.cursor()
    conn.row_factory = sqlite3.Row
    return conn, cur

#criação da table
@app.route('/', methods = ['GET'])
def create_table():
    conn,cur = get_database()
    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gmail TEXT NOT NULL,
        password TEXT)""")
        conn.commit()
    finally:
        conn.close()
    return jsonify({'Success':'Created a table success'})

#criar conta
@app.route('/register', methods=['POST'])
def register():
    conn , cur = get_database()
    gmail = request.form.get('gmail')
    password = request.form.get('password')
 
    if not gmail or not password:
        return jsonify ({'Error':'Gmail or Password not defined'}), 400

    cur.execute("SELECT gmail FROM users WHERE gmail = ?", (gmail,))
    results = cur.fetchone()
    if results:
        return jsonify({'Error':'Gmail is registered'}), 409

    cur.execute("INSERT INTO users (gmail,password) VALUES (?,?)", (gmail,password))
    conn.commit()
    conn.close()
    return jsonify({'Success':'User registred for success'}), 201

#Login
@app.route('/logins', methods=['POST'])
def login():
    conn,cur = get_database()
    gmail = request.form.get('gmail')
    password = request.form.get('password')

    if not gmail or not password:
        return jsonify ({'Error':'Gmail or Password not defined'}), 400

    cur.execute("SELECT id, gmail FROM users WHERE gmail = ? AND password = ?", (gmail,password))
    user = cur.fetchone()
    conn.close()
    
    if user:
        return jsonify({'login':'Success'})
    return jsonify({'Error':'Gmail not registred'}), 401


#DELETAR usuario
@app.route('/logins/user', methods=['DELETE'])
def user():
    conn,cur = get_database()

    gmail = request.args.get('gmail')
    password = request.args.get('password') 
    
    if not password or not gmail:
        return jsonify({'Error':'Dont insert gmail or password'})

    cur.execute('select id, gmail from users where gmail = ? AND password = ?',(gmail, password))
    user = cur.fetchone()
    cur.execute('DELETE FROM users WHERE gmail = ? AND password = ?', (gmail,password))
    conn.close()

    if user:
        id = user[0]
        gmail = user[1]
        return jsonify({'DELETED', {'id':id,'gmail':gmail})
    return jsonify({'Error':'user not found'})
if __name__ == '__main__':
    app.run(debug=True)
