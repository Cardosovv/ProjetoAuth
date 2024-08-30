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
@app.route('/user', methods=['POST'])
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


#MOSTRAR TODOS os usuarios ##Estudar alguns trechos do código ao mais tardar..
@app.route('/user', methods=['GET'])
def user():
    conn, cur = get_database()
    
    cur.execute('select * from users')
    rows = cur.fetchall()

    columns = []
    for desc in cur.description:
        columns.append(desc[0])

    users = []
    for row in rows:
        user_dict = dict(zip(columns, row))
        users.append(user_dict)
    
    conn.close()

    return jsonify(users)

#Mostrar um único usuario
@app.route('/user/<int:id>', methods=['GET'])
def get_user_id(id):
    conn, cur = get_database()
    
    cur.execute('SELECT * FROM users WHERE  id = ?',(id ,))
    user = cur.fetchone()
    
    if user:
        return jsonify(user)
    return jsonify({'Error':'User not found.'}), 404

#Deletar usuarios
@app.route('/user/<int:id>', methods=['DELETE'])
def delet_user(id):
    conn , cur = get_database()

    cur.execute('DELETE FROM users WHERE id = ?',(id,))
    conn.commit()
    conn.close()
   
    if cur.rowcount > 0:
        return jsonify({'Success':'user is deleted'}), 200
    return jsonify({'Error':'user not found'}), 404

#Atualizar usuario
@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    conn, cur = get_database()
    gmail = request.form.get('gmail')

    if not gmail:
        return jsonify({'Error':'need only gmail'})
    try:
        cur.execute('UPDATE users SET gmail = ? WHERE id = ?', (gmail, id))
        conn.commit()
        conn.close()
        
        if cur.rowcount > 0:
            return jsonify({'Success':'altered gmail'}), 200
        return jsonify({'Error':'user not found'}), 404
    except Exception as e:
        return jsonify({'Error':str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
