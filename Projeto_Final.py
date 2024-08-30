import sqlite3
from flask import request, jsonify, Flask, Response, abort

app = Flask(__name__)

from dataclasses import dataclass, asdict
from typing import Optional, Tuple, Union


@dataclass
class User:
    id: Optional[int]
    email: Optional[str]
    password: Optional[str]


def extract_body_user(request_context) -> User:
    if request_context.is_json:
        data = request_context.get_json()
        email = data.get('email')
        password = data.get('password')
        user_id = data.get('id')
    elif request_context.form:
        email = request_context.form.get('email')
        password = request_context.form.get('password')
        user_id = request_context.form.get('id')
    else:
        abort(400, description='Not a valid request body')
    # Convert user_id to an integer if it's provided and not None
    if user_id is not None:
        try:
            user_id = int(user_id)
        except ValueError:
            abort(400, description='Invalid ID format')
    return User(id=user_id, email=email, password=password)




#criação do banco de dados
def get_database():
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    conn.row_factory = sqlite3.Row
    return conn, cur


#criação da table
@app.route('/', methods=['GET'])
def create_table():
    conn, cur = get_database()
    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        password TEXT)""")
        conn.commit()
    finally:
        conn.close()
    return jsonify({'Success': 'Created a table success'})


#criar conta
@app.route('/register', methods=['POST'])
def register():
    try:
        body_user= extract_body_user(request)
    except Response as err:
        return err  # Return the error response immediately
    conn, cur = get_database()

    result = cur.execute("SELECT email FROM users WHERE email = ?", (body_user.email,)).fetchone()
    if result:
        return jsonify({'Error': 'User is already registered'}), 409

    cur.execute("INSERT INTO users (email,password) VALUES (?,?)", (body_user.email, body_user.password))
    conn.commit()
    conn.close()
    return jsonify({'Success': 'User registered for success'}), 201


#Login
@app.route('/login', methods=['POST'])
def login():
    conn, cur = get_database()
    try:
        body_user = extract_body_user(request)
    except Response as err:
        return err  # Return the error response immediately

    selected_user = cur.execute("SELECT id, email FROM users WHERE email = ? AND password = ?",
                                (body_user.email, body_user.password)).fetchone()

    conn.close()

    if selected_user:
        return jsonify({'login': 'Success'})
    return jsonify({'Error': 'User is not authenticated'}), 401


#MOSTRAR TODOS os usuarios ##Estudar alguns trechos do código ao mais tardar..
@app.route('/users', methods=['GET'])
def get_users():
    conn, cur = get_database()

    cur.execute('SELECT id, email, password FROM users')  # Ensure 'password' is included if needed
    rows = cur.fetchall()

    # Create User instances from rows
    users = [User(id=row[0], email=row[1], password=row[2]) for row in rows]

    conn.close()

    # Convert User instances to dictionaries and return as JSON
    return jsonify([asdict(user) for user in users])



#Deletar usuarios
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn, cur = get_database()

    cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    if cur.rowcount > 0:
        return jsonify({'Success': 'user is deleted'}), 200
    return jsonify({'Error': 'User not found'}), 404


#Mostrar um único usuario
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_id(user_id):
    conn, cur = get_database()
    if user_id is None:
        return jsonify({'Error': 'No ID provided'}), 400

    result = cur.execute('SELECT email,id FROM users WHERE  id = ?', (user_id,)).fetchone()
    returned_user = User(id=result[0], email=result[1],password='')

    if returned_user:
        return jsonify(asdict(returned_user))

    return jsonify({'Error': 'User not found.'}), 402

#Atualizar usuario
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    body_user = extract_body_user(request)
    try:
        conn, cur = get_database()
        cur.execute('UPDATE users SET email = ? WHERE id = ?', (body_user.email, user_id))
        conn.commit()
        conn.close()

        if cur.rowcount > 0:
            return jsonify({'Success': 'Email updated successfully'}), 200
        return jsonify({'Error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'Error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
