from flask import Flask, request, render_template, jsonify

from datetime import datetime


TASKS = [
    {'id': 1,
     'task': 'Prepare a dinner for a week',
     'category': 'home',
     'expired_date': datetime.today().strftime('%d-%m-%y'),
     'done': 'no',
     'completed_date': 'Not completed'},
    {'id': 2,
     'task': 'Make the report of the week',
     'category': 'job',
     'expired_date': datetime.today().replace(day=datetime.today().day + 2).strftime('%d-%m-%y'),
     'done': 'no',
     'completed_date': 'Not completed'},
    {'id': 3,
     'task': 'Make a homework for lesson 10',
     'category': 'studies',
     'expired_date': datetime.today().replace(day=datetime.today().day + 1).strftime('%d-%m-%y'),
     'done': 'no',
     'completed_date': 'Not completed'},
    {'id': 4,
     'task': 'Read the documentation about descriptors',
     'category': 'studies',
     'expired_date': datetime.today().strftime('%d-%m-%y'),
     'done': 'no',
     'completed_date': 'Not completed'}
]


app = Flask(__name__)


@app.route('/')
@app.route('/home/')
def home():
    return render_template('home.html', title='Home')


@app.route('/api/tasks/', methods=['GET'])
def show_tasks():
    if not request.args:
        return render_template('tasks_without_db.html', tasks=TASKS)
    keys = request.args
    print(keys)
    temp_tasks = TASKS
    tasks = []
    for key in keys:
        if key not in TASKS[0]:
            return f'Task object has not field {key}'
        for task in temp_tasks:
            if str(task[key]) == keys[key]:
                tasks.append(task)
        temp_tasks = tasks
        tasks = []
    return render_template('tasks_without_db.html', tasks=temp_tasks)
    # return jsonify(temp_tasks)


@app.route('/api/tasks/', methods=['POST'])
def add_task():
    print(request)
    new_task = request.json
    print(new_task)
    new_task['id'] = len(TASKS) + 1
    TASKS.append(new_task)
    return render_template('tasks_without_db.html', tasks=TASKS)
    # return f'{new_task} added!'


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def show_task_by_id(task_id):
    task = None
    for t in TASKS:
        if t['id'] == task_id:
            task = t
    if task is None:
        return f'<h4>Not found task with id {task_id}</h4>', 404
    return render_template('task_by_id_without_db.html', task=task)
    # return task


@app.route('/api/tasks/<int:task_id>/delete', methods=['DELETE'])
def delete_task(task_id):
    index = -1
    for i, task in enumerate(TASKS):
        if task['id'] == task_id:
            index = i
            break
    if index == -1:
        return f'<h4>Not found task with id {task_id}</h4>', 404
    deleted = TASKS[index]
    del TASKS[index]
    return render_template('tasks_without_db.html', tasks=TASKS)
    # return f'{deleted} deleted!'


@app.route('/api/tasks/<int:task_id>/update', methods=['PUT'])
def update(task_id):
    new_values = request.form
    print(new_values)
    index = -1
    for i, t in enumerate(TASKS):
        if t['id'] == task_id:
            index = i
            break
    if index == -1:
        return f'<h4>Not found task with id {task_id}</h4>'
    for key in new_values:
        if key not in TASKS[index]:
            return f'Task object has not field {key}'
        TASKS[index][key] = new_values[key]
    return render_template('tasks_without_db.html', tasks=TASKS)
    # return f'Updated task: {TASKS[index]}'


# @app.route('/api/tasks/category=<string:category>', methods=['GET'])
# def show_tasks_by_exp_date(category):
#     tasks_by_exp_date = []
#     for task in TASKS:
#         if task['category'] == category:
#             tasks_by_exp_date.append(task)
#     return render_template('tasks_without_db.html', tasks=tasks_by_exp_date)
#
#
if __name__ == '__main__':
    app.run()
