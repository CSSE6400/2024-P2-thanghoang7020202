from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():

   completed_param = request.args.get('completed')

   # get the window parameter from the request can cast it to an int
   window = int(request.args.get('window')) if request.args.get('window') is not None else None
   todos = Todo.query.all()
   result = []

   # If a window is specified, calculate the current time window
   current_time = None
   if window is not None:
      current_time = datetime.now() + timedelta(days=window)

   # Filter todos based on completion status
   if completed_param is not None:
      completed_value = completed_param.lower() == 'true'  # Convert 'true'/'false' to boolean
      todos = Todo.query.filter_by(completed=completed_value).all()

   # Convert todos to dictionary representation
   result = [todo.to_dict() for todo in todos]

   # if the 'window' parameter is provided, pop the todos that don't match the value
   if window is not None:
      for v in result:
         if datetime.fromisoformat(v['deadline_at']) > current_time:
            result.remove(v)
   
   return jsonify(result)


@api.route('/todos/<int:todo_id>', methods=['GET']) 
def get_todo(todo_id): 
   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({'error': 'Todo not found'}), 404 
   return jsonify(todo.to_dict())


@api.route('/todos', methods=['POST']) 
def create_todo(): 
   expected_fields = ['title', 'description', 'completed', 'deadline_at']
   extra_fields = [key for key in request.json if key not in expected_fields]

   if extra_fields:
      return jsonify({"error": "Unexpected fields provided: {}".format(extra_fields)}), 400
   todo = Todo( 
      title=request.json.get('title'), 
      description=request.json.get('description'), 
      completed=request.json.get('completed', False), 
   ) 
   if 'deadline_at' in request.json: 
      timeString : str = request.json.get('deadline_at')
      todo.deadline_at = datetime.fromisoformat(timeString) 
   
   # check title is null in the request
   if todo.title is None:
      return jsonify(todo.to_dict()), 400

   # Adds a new record to the database or will update an existing record 
   db.session.add(todo) 
   # Commits the changes to the database, this must be called for the changes to be saved 
   db.session.commit() 
   return jsonify(todo.to_dict()), 201


@api.route('/todos/<int:todo_id>', methods=['PUT']) 
def update_todo(todo_id): 
   todo = Todo.query.get(todo_id)
   expected_fields = ['title', 'description', 'completed', 'deadline_at']
   extra_fields = [key for key in request.json if key not in expected_fields]

   if extra_fields:
      return jsonify({"error": "Unexpected fields provided: {}".format(extra_fields)}), 400 
   if todo is None: 
      return jsonify({'error': 'Todo not found'}), 404 

   if request.json.get('id', todo.id) != todo_id:
      return jsonify({'error': 'Todo id does not match'}), 400
   

   todo.title = request.json.get('title', todo.title) 
   todo.description = request.json.get('description', todo.description) 
   todo.completed = request.json.get('completed', todo.completed) 
   todo.deadline_at = request.json.get('deadline_at', todo.deadline_at) 
   
   db.session.commit() 
 
   return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id) 
    if todo is None: 
      return jsonify({}), 200 
 
    db.session.delete(todo) 
    db.session.commit() 
    return jsonify(TEST_ITEM)
