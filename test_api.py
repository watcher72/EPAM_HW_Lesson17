import requests
import sqlite3

from datetime import datetime


DB = 'test.db'
ID_G = iter(range(1, 10_000))
TIME_FORMAT = '%d-%m-%Y'

init_data = [
    (next(ID_G), 'Prepare a dinner for a week', 'home',
     datetime.today().strftime(TIME_FORMAT), 0, ''),
    (next(ID_G), 'Make the report of the week', 'job',
     datetime.today().replace(day=datetime.today().day + 2).strftime(TIME_FORMAT),
     0, ''),
    (next(ID_G), 'Make a homework for lesson 10', 'studies',
     datetime.today().replace(day=datetime.today().day + 1).strftime(TIME_FORMAT),
     0, ''),
    (next(ID_G), 'Read the documentation about descriptors', 'studies',
     datetime.today().strftime(TIME_FORMAT), 0, '')
]


def test_add_new_task():
    print('test POST')
    new_task = {
        'id': next(ID_G),
        'title': 'Finish task 4',
        'category': 'job',
        'expired_date': datetime.today().replace(day=datetime.today().day + 2).strftime(TIME_FORMAT),
    }

    response = requests.post('http://localhost:5000/api/tasks/', json=new_task)
    assert response.status_code == 201
    response = requests.get(f'http://localhost:5000/api/tasks/{new_task["id"]}')
    assert response.content != []
    print('ok')


def test_delete_task():
    print('test DELETE')
    new_task = {
        'id': next(ID_G),
        'title': 'See the tutorial on Flask',
        'category': 'studies',
        'expired_date': datetime.today().replace(day=datetime.today().day + 1).strftime(TIME_FORMAT),
    }
    response = requests.post('http://localhost:5000/api/tasks/', json=new_task)
    assert response.status_code == 201
    response = requests.delete(f'http://localhost:5000/api/tasks/'
                               f'{new_task["id"]}/delete')
    assert response.status_code == 200
    assert int(response.content) != 0
    response = requests.delete(f'http://localhost:5000/api/tasks/'
                               f'{new_task["id"]}/delete')
    assert response.status_code == 404
    assert int(response.content) == 0
    print('ok')


def test_update_task():
    print('test PUT')
    new_task = {
        'id': next(ID_G),
        'title': 'See the tutorial on Flask',
        'category': 'studies',
        'expired_date': datetime.today().replace(day=datetime.today().day + 1).strftime(TIME_FORMAT),
    }
    response = requests.post('http://localhost:5000/api/tasks/', json=new_task)
    assert response.status_code == 201

    new_values = {
        'is_done': 1,
        'completed_date': datetime.today().strftime(TIME_FORMAT)
    }
    response = requests.put(f'http://localhost:5000/api/tasks/'
                            f'{new_task["id"]}/update', json=new_values)
    assert response.status_code == 200
    response = requests.get(f'http://localhost:5000/api/tasks/{new_task["id"]}')
    task = response.json()
    assert task['is_done'] == 1
    assert task['completed_date'] == datetime.today().strftime(TIME_FORMAT)
    print('ok')


def test_select_by_fields():
    print('test GET')
    response = requests.get(f'http://localhost:5000/api/tasks/')
    assert len(response.json()) == 6
    response = requests.get(f'http://localhost:5000/api/tasks/'
                            f'?category=studies')
    assert len(response.json()) == 3
    response = requests.get(f'http://localhost:5000/api/tasks/'
                            f'?is_done=1')
    assert len(response.json()) == 1
    print('ok')


if __name__ == '__main__':
    # Prepare test database
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS task ')
    cur.execute('CREATE TABLE IF NOT EXISTS task(id INTEGER PRIMARY KEY,'
                                                'title TEXT NOT NULL,'
                                                'category TEXT NOT NULL,'
                                                'expired_date TEXT NOT NULL,'
                                                'is_done INT DEFAULT 0,'
                                                'completed_date TEXT DEFAULT "")')
    cur.executemany('INSERT INTO task VALUES(?, ?, ?, ?, ?, ?)', init_data)
    con.commit()
    cur.close()
    con.close()

    # Testing api functionality
    test_add_new_task()
    test_delete_task()
    test_update_task()
    test_select_by_fields()
