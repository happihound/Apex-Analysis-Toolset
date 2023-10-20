from flask import Flask
from flask_restful import Resource, Api
from server.api.server_api import Home, Video_Decomp
app = Flask(__name__)
api = Api(app)

api.add_resource(Home, '/')

api.add_resource(Video_Decomp, '/video-decomposition')

if __name__ == '__main__':
    app.run(debug=True)
