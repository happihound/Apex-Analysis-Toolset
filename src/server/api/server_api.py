from flask import Flask, jsonify, request
import sys
import io


from server.tools.coordinator import *
from flask_restful import Resource, reqparse, request  # NOTE: Import from flask_restful, not python
from flask import render_template, make_response
from util.apexUtils import ApexUtils
from server.tools.coordinator import Coordinator as coord

global coordinator_local


def set_socketio(socketio1):
    global coordinator_local
    coordinator_local = coord(socketio=socketio1)


class Home(Resource):
    def get(self):
        data_dict = {'welcome_message': 'Welcome to the Apex Legends API!',
                     'explain_header': 'What is this tool?',
                     'explain_body': 'This tool is designed to help you extract data from Apex Legends videos. It is currently in development and is not ready for public use.',
                     }
        return make_response(render_template('home.html', **data_dict))


class Video_Decomposition(Resource):
    def get(self):
        data_dict = {'title': 'Video Decomposition Tool',
                     'high_qual': 'High quality - Whether to extract the highest quality frames possible. This will take MUCH longer to run.',
                     'async_mode': 'Async mode - Whether to run the tool asynchronously. This will allow you to run multiple extractions at once, but will take longer to run.', }
        return make_response(render_template('video-decomposition.html', **data_dict))

    # options are which sections to extract
    # These are: killFeed, PlayerEvo, PlayerDamage, miniMap, PlayerGuns, PlayerHealth, PlayerKills, PlayerShield, PlayerTac, PlayerUlt, Teammate1Health, Teammate1Shield, Teammate2Health, Teammate2Shield, ZoneTimer, frames

    def post(self):
        # We should let the user choose which sections to extract using a checkbox
        high_quality = request.form.get('highqual')
        do_async = request.form.get('asyncmode')
        kill_feed = request.form.get('killFeed')
        player_evo = request.form.get('PlayerEvo')
        player_damage = request.form.get('PlayerDamage')
        mini_map = request.form.get('miniMap')
        player_guns = request.form.get('PlayerGuns')
        player_health = request.form.get('PlayerHealth')
        player_kills = request.form.get('PlayerKills')
        player_shield = request.form.get('PlayerShield')
        player_tac = request.form.get('PlayerTac')
        player_ult = request.form.get('PlayerUlt')
        teammate_1_health = request.form.get('Teammate1Health')
        teammate_1_shield = request.form.get('Teammate1Shield')
        teammate_2_health = request.form.get('Teammate2Health')
        teammate_2_shield = request.form.get('Teammate2Shield')
        zone_timer = request.form.get('ZoneTimer')
        frames = request.form.get('frames')

        options = {
            'killFeed': kill_feed,
            'PlayerEvo': player_evo,
            'PlayerDamage': player_damage,
            'miniMap': mini_map,
            'PlayerGuns': player_guns,
            'PlayerHealth': player_health,
            'PlayerKills': player_kills,
            'PlayerShield': player_shield,
            'PlayerTac': player_tac,
            'PlayerUlt': player_ult,
            'Teammate1Health': teammate_1_health,
            'Teammate1Shield': teammate_1_shield,
            'Teammate2Health': teammate_2_health,
            'Teammate2Shield': teammate_2_shield,
            'ZoneTimer': zone_timer,
            'frames': frames,
            'high_quality': high_quality,
            'async_mode': do_async
        }

        for key, value in options.items():
            if value is None:
                options[key] = False
        global coordinator_local
        coordinator_local.runVideoDecompositionTool(options)
        selected_options = []
        for key, value in options.items():
            if value:
                selected_options.append(key)
        return make_response(render_template('video-decomposition-output.html', **{'options': selected_options}))


class KillTracker(Resource):
    def get(self):
        data_dict = {'title': 'Kill Tracker', 'client_id': 'kill-tracker'}
        return make_response(render_template('default.html', **data_dict))

    def post(self):
        global coordinator_local
        coordinator_local.runPlayerKillTracker()


class PlayerGunTracker(Resource):
    def get(self):
        data_dict = {'title': 'Gun Tracker', 'client_id': 'gun-tracker'}
        return make_response(render_template('default.html', **data_dict))

    def post(self):
        global coordinator_local
        coordinator_local.runPlayerGunTracker()


class DamageTracker(Resource):
    def get(self):
        data_dict = {'title': 'Damage Tracker', 'client_id': 'damage-tracker'}
        return make_response(render_template('default.html', **data_dict))

    def post(self):
        global coordinator_local
        coordinator_local.runDamageTracker()


class EvoTracker(Resource):
    def get(self):
        data_dict = {'title': 'Evo Tracker', 'client_id': 'evo-tracker'}
        return make_response(render_template('default.html', **data_dict))

    def post(self):
        global coordinator_local
        coordinator_local.runEvoTracker()


class HealthTracker(Resource):
    def get(self):
        data_dict = {'title': 'Health Tracker', 'client_id': 'health-tracker', 'extact_type': 'health'}
        return make_response(render_template('multi-extract.html', **data_dict))

    def post(self):
        global coordinator_local
        player = request.form.get('Player')
        teammate_1 = request.form.get('Teammate1')
        teammate_2 = request.form.get('Teammate2')
        options = {
            'playerShield': player,
            'teammate1Health': teammate_1,
            'teammate2Health': teammate_2
        }
        for key, value in options.items():
            if value is None:
                options[key] = False
        if not player and not teammate_1 and not teammate_2:
            return {'message': 'No players selected'}, 400
        coordinator_local.runHealthTracker(options)


class CancelOperation(Resource):
    def post(self):
        # Get the referer header to determine the page from which the request was sent
        referer = request.headers.get('Referer')
        referer = referer.split('/')[-1]
        if not referer:
            return {'message': 'Referer not provided'}, 400
        # Logic to determine the operation to cancel based on the referer
        global coordinator_local
        if coordinator_local.cancel(referer):
            return {'message': 'Cancelled operation'}, 200
        else:
            return {'message': 'No operation to cancel'}, 200
