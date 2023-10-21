import sys
import io
import threading
import time
from flask import Flask, make_response
from flask_restful import Resource, Api
from server.api.server_api import Home, Video_Decomposition
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
api = Api(app)


@staticmethod
def get_console_output():
    data = sys.stdout.get_value()
    sys.stdout.clear()
    return data


@staticmethod
def get_website_console_output():
    data = sys.stdout.get_value_website()
    sys.stdout.clear()
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
        return_list = []
        for line in self.cont_buffer.getvalue().splitlines():
            if "!WEBPAGE!" in line:
                return_list.append(line.replace("!WEBPAGE!", ""))
        return return_list

    def clear(self):
        return
        self.buffer.seek(0)
        self.buffer.truncate()


class ConsoleOutput(Resource):
    def get(self):
        console_output = get_console_output()
        return console_output


class ConsoleOutputFormatted(Resource):
    def get(self):
        console_output = get_console_output()
        formatted_output = "<pre>" + console_output + "</pre>"
        response = make_response(formatted_output)
        response.headers['Content-Type'] = 'text/html'
        return response


class ConsoleOutputForWebpages(Resource):
    def get(self):
        console_output = get_website_console_output()
        return console_output


sys.stdout = DualOutput(sys.stdout)
sys.stderr = DualOutput(sys.stderr)


def emit_console_output():
    while True:
        console_output = get_website_console_output()
        socketio.emit('console_output', {'data': console_output})
        time.sleep(1)


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(emit_console_output)


api.add_resource(Home, '/')

api.add_resource(Video_Decomposition, '/video-decomposition')

api.add_resource(ConsoleOutput, '/get-console-output')

api.add_resource(ConsoleOutputFormatted, '/get-console-output-formatted')

api.add_resource(ConsoleOutputForWebpages, '/get-console-output-for-webpages')

if __name__ == '__main__':
    # threading.Thread(target=emit_console_output).start()
    socketio.run(app, debug=True)
