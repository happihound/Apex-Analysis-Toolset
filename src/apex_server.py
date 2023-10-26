import sys
import io
import threading
import time
from flask import Flask, make_response, request
from flask_restful import Resource, Api
import server.api.server_api as server_api
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
global socketio
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
api = Api(app)

server_api.set_socketio(socketio)


@staticmethod
def get_console_output():
    data = sys.stdout.get_value()
    sys.stdout.clear()
    return data


@staticmethod
def get_website_console_output():
    data = sys.stdout.get_value_website()
    return data


class DualOutput:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.cont_buffer = io.StringIO()
        self.buffer = io.StringIO()

    def write(self, message):
        self.original_stdout.write(message)
        self.cont_buffer.write(message)
        self.buffer.write(message)

    def flush(self):
        self.original_stdout.flush()
        self.cont_buffer.flush()
        self.buffer.flush()

    def get_value(self):
        return self.cont_buffer.getvalue()

    def get_value_website(self):
        toggle = False
        return_list = []
        for line in self.cont_buffer.getvalue().splitlines():
            if "!ON!" in line:
                toggle = True
                continue
            if "!OFF!" in line:
                toggle = False
                continue
            if "!WEBPAGE!" in line or toggle:
                return_list.append(line.replace("!WEBPAGE!", "").replace(
                    "!TOGGLE!", "").replace("!ON!", "").replace("!OFF!", ""))
        if len(return_list) == 0:
            return
        return return_list

    def clear(self):
        return
        self.buffer.seek(0)
        self.buffer.truncate()


class ConsoleOutput(Resource):
    def get(self):
        console_output = get_console_output()
        return console_output


class ConsoleOutputForWebpages(Resource):
    def get(self):
        console_output = get_website_console_output()
        return console_output


sys.stdout = DualOutput(sys.stdout)
sys.stderr = DualOutput(sys.stderr)


def emit_console_output():
    while True:
        console = get_website_console_output()
        if console is not None:
            socketio.emit('console_output', {'data': console})
        time.sleep(1)


@socketio.on('connect', namespace='/image')
def connect():
    client_id = request.args.get('client_id')
    join_room(client_id)
    print(f'Client {client_id} connected in image namespace with {request.sid} as sessid')


@ socketio.on('connect')
def handle_connect():
    print('Client connected')
    client_id = request.args.get('client_id')
    socketio.start_background_task(emit_console_output)
    print(f'Client {client_id} connected with {request.sid} as sessid')


api.add_resource(server_api.Home, '/')

api.add_resource(server_api.CancelOperation, '/cancel')

api.add_resource(server_api.Video_Decomposition, '/video-decomposition')

api.add_resource(ConsoleOutput, '/running_console')

api.add_resource(ConsoleOutputForWebpages, '/get-console-output-for-webpages')

api.add_resource(server_api.KillTracker, '/kill-tracker')

api.add_resource(server_api.PlayerGunTracker, '/gun-tracker')

api.add_resource(server_api.DamageTracker, '/damage-tracker')

api.add_resource(server_api.EvoTracker, '/evo-tracker')

api.add_resource(server_api.HealthTracker, '/health-tracker')


if __name__ == '__main__':
    # threading.Thread(target=emit_console_output).start()
    socketio.run(app, debug=True)
