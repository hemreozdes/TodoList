from flask import Flask,render_template,request,jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class TodoItem(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    priority = db.Column(db.String(10), nullable=False)
    name=db.Column(db.String(999))
    status=db.Column(db.Boolean)

@app.route("/")
def index():
    tasks = TodoItem.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    global todo_id
    data = request.get_json() 
    name = data['name']
    priority = data['priority']
    new_task = TodoItem(name=name, priority=priority,status=False)
    db.session.add(new_task)
    db.session.commit()
    todo_id=new_task.id
    return jsonify({'id': todo_id, 'name': name, 'priority': priority})

@app.route("/complete/<int:todo_id>", methods=['POST'])
def complete(todo_id):
    todo = TodoItem.query.filter_by(id=todo_id).first()
    if todo:
        todo.status = True
        db.session.commit()
    return '',200

@app.route("/delete/<int:todo_id>", methods=['POST'])
def delete(todo_id):
    task = TodoItem.query.filter_by(id=todo_id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
    return jsonify({'status': 'success'}),200

@app.route("/end_of_day", methods=["POST"])
def end_of_day():
    completed_tasks = TodoItem.query.filter_by(status=True).all()
    for task in completed_tasks:
        db.session.delete(task)
    db.session.commit()
    return '',200

@app.route('/update-task-priority', methods=['POST'])
def update_task_priority():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        new_priority = data.get('new_priority')
        task = TodoItem.query.get(task_id)
        if task:
            task.priority = new_priority
            db.session.commit()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Task not found'}), 404
    except Exception as e:
        print(f'Error updating priority: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)