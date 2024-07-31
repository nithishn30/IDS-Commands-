from flask import *
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

python_clients = []
messages = []
client_files = None
client_interfaces = None
interfaces = None

CAPTURES_DIR = 'captures'

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        command = request.form['command']
        if python_clients:
            for client_id in python_clients:
                socketio.emit('command', {'command': command}, room=client_id)
            flash("Message sent to Python clients")
        else:
            flash("No Python clients connected")
    return render_template('index.html', client_files=client_files,interfaces=interfaces)
@app.route("/analyse/<file>")
def analyse(file):
    socketio.emit('analyse_file', {'command': 'sudo ./jara.py -c jara.conf', 'file': file})
    return redirect(url_for("index"))

@app.route("/captures")
def get_captures():
    files = os.listdir(CAPTURES_DIR)
    return jsonify(files)

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('data')
def get_client_files(data):
    global client_files,interfaces
    client_files = data["files"]
    interfaces = data["interfaces"]

@socketio.on('register_python_client')
def register_python_client():
    python_clients.append(request.sid)
    print(f'Python client registered: {request.sid}')
    messages.append(f'Python client registered: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in python_clients:
        python_clients.remove(request.sid)
        print(f'Python client disconnected: {request.sid}')
        messages.append(f'Python client disconnected: {request.sid}')

@socketio.on('client_message')
def handle_client_message(data):
    print(f'Received message from client: {data["data"]}')
    messages.append(f'Received message from client: {data["data"]}')

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0")
