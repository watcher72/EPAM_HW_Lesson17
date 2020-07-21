import sqlite3

# from collections import namedtuple

from flask import Flask, request, render_template, jsonify
from sqlite3 import Error


# Row = namedtuple('Row', 'id, title, category, expired_date, '
#                         'is_done, completed_date')

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
    # print(query)

    con = sqlite3.connect(DB)
    cur = con.cursor()
    try:
        cur.execute(query)
        rows = cur.fetchall()
    except Error as e:
        # print(e)
        return f'Error <{e}> occurred during select data from database', 400
    finally:
        cur.close()
        con.close()

    if not rows:
        return "Not found tasks according query", 404

    tasks = []
    for row in rows:
        tasks.append(dict(zip(fields.split(', '), row)))
    # return render_template('tasks.html', tasks=tasks, fields=fields.split(', '))
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
    # print(new_task)

    con = sqlite3.connect(DB)
    cur = con.cursor()
    try:
        cur.execute('INSERT INTO task VALUES(?, ?, ?, ?, ?, ?)', new_task)
        con.commit()
    except Error as e:
        # print(e)
        return f'Error <{e}> occurred during add new data in database', 400
    finally:
        cur.close()
        con.close()

    # return render_template('tasks.html', tasks=TASKS)
    return f'Task {recv_data.get("id")} added!', 201


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def show_task_by_id(task_id):
    fields = 'id, title, category, expired_date, is_done, completed_date'

    con = sqlite3.connect(DB)
    cur = con.cursor()
    try:
        cur.execute(f'SELECT {fields} FROM task WHERE id = {task_id}')
        task = cur.fetchone()
    except Error as e:
        # print(e)
        return f'Error <{e}> occurred during search ' \
               f'task {task_id} in database', 400
    finally:
        cur.close()
        con.close()

    if task is None:
        return f'<h4>Not found task with id {task_id}</h4>', 404
    task = dict(zip(fields.split(', '), task))
    # return render_template('task_by_id.html', task=task)
    return task


@app.route('/api/tasks/<int:task_id>/delete', methods=['DELETE'])
def delete_task(task_id):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    try:
        rows = cur.execute(f'DELETE FROM task WHERE rowid = {task_id}').rowcount
        con.commit()
    except Error as e:
        # print(e)
        return f'Error <{e}> occurred during search ' \
               f'task {task_id} in database', 400
    finally:
        cur.close()
        con.close()
    # return render_template('tasks.html', tasks=TASKS)
    if not rows:
        return str(rows), 404
    return str(rows)


@app.route('/api/tasks/<int:task_id>/update', methods=['PUT'])
def update(task_id):
    recv_data = request.json
    new_values = ', '.join([f'{key} = "{value}"'
                            for key, value in recv_data.items()])
    # print(new_values)

    con = sqlite3.connect(DB)
    cur = con.cursor()
    try:
        cur.execute(f'UPDATE task SET {new_values} WHERE id = {task_id}')
        con.commit()
    except Error as e:
        # print(e)
        return f'Error <{e}> occurred during update ' \
               f'task {task_id} in database', 400
    finally:
        cur.close()
        con.close()

    return f'Task {task_id} updated'


if __name__ == '__main__':
    app.run()
