import sqlite3

from flask import Flask, request, render_template, jsonify
from sqlite3 import Error


app = Flask(__name__)
# DB = 'todo.db'
DB = 'test.db'


@app.route('/')
@app.route('/home/')
def home():
    return render_template('home.html', title='Home')


@app.route('/api/tasks/', methods=['GET'])
def show_tasks():
    args = request.args
    if args:
        conditions = [f'{key} = "{args[key]}"' for key in args]
        conditions = f'WHERE {" AND ".join(conditions)}'
    else:
        conditions = ''
    fields = 'id, title, category, expired_date, is_done, completed_date'
    query = f'SELECT {fields} FROM task {conditions}'

    try:
        with sqlite3.connect(DB) as con:
            rows = [r for r in con.execute(query)]
    except Error as e:
        return {'success': False,
                "error": f'Error <{e}> occurred during select data',
                }, 404

    if not rows:
        return jsonify({'success': False,
                        'error': 'Not found tasks according query'
                        }), 404

    tasks = []
    for row in rows:
        tasks.append(dict(zip(fields.split(', '), row)))
    return jsonify(tasks)


@app.route('/api/tasks/', methods=['POST'])
def add_task():
    recv_data = request.json
    new_task = [recv_data.get('id'),
                recv_data.get('title'),
                recv_data.get('category'),
                recv_data.get('expired_date'),
                recv_data.get('is_done', 'underway'),
                recv_data.get('completed_date', '')
                ]
    try:
        with sqlite3.connect(DB) as con:
            con.execute('INSERT INTO task VALUES(?, ?, ?, ?, ?, ?)', new_task)
    except Error as e:
        return f'Error <{e}> occurred during add new data in database', 400

    return f'Task {recv_data.get("id")} added!', 201


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def show_task_by_id(task_id):
    fields = 'id, title, category, expired_date, is_done, completed_date'

    try:
        with sqlite3.connect(DB) as con:
            task = [r for r in con.execute(f'SELECT {fields} '
                                           f'FROM task WHERE id = {task_id}')][0]
    except Error as e:
        return f'Error <{e}> occurred during search ' \
               f'task {task_id} in database', 400

    if task is None:
        return f'<h4>Not found task with id {task_id}</h4>', 404
    task = dict(zip(fields.split(', '), task))
    return task


@app.route('/api/tasks/<int:task_id>/delete', methods=['DELETE'])
def delete_task(task_id):
    try:
        with sqlite3.connect(DB) as con:
            rows = con.execute(f'DELETE FROM task WHERE rowid = {task_id}').rowcount
    except Error as e:
        return f'Error <{e}> occurred during search ' \
               f'task {task_id} in database', 400
    if not rows:
        return str(rows), 404
    return str(rows)


@app.route('/api/tasks/<int:task_id>/update', methods=['PUT'])
def update(task_id):
    recv_data = request.json
    new_values = ', '.join([f'{key} = "{value}"'
                            for key, value in recv_data.items()])

    try:
        with sqlite3.connect(DB) as con:
            con.execute(f'UPDATE task SET {new_values} WHERE id = {task_id}')
    except Error as e:
        return f'Error <{e}> occurred during update ' \
               f'task {task_id} in database', 400

    return f'Task {task_id} updated'


if __name__ == '__main__':
    app.run()
