import sys
import io

from server.tools.coordinator import *
from flask_restful import Resource, reqparse, request  # NOTE: Import from flask_restful, not python
from flask import render_template, make_response
import server.tools.coordinator as coordinator


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
                     'simple_options': 'do_frame_extraction=True, do_teammate_extraction=True, do_ocr_extractions=True, do_mini_map_plotter=True, methods_to_run=None - if None, all methods will be run otherwise pass a list of methods to run',
                     'detailed_options': 'do_kill_feed_extraction=False, do_player_evo_extraction=False, do_player_damage_extraction=False, do_mini_map_extraction=False, do_player_gun_extraction=False, do_player_health_extraction=False, do_player_kill_extraction=False, do_player_shield_extraction=False, do_player_tac_extraction=False, do_player_ult_extraction=False, do_teammate_1_health_extraction=False, do_teammate_1_shield_extraction=False, do_teammate_2_health_extraction=False, do_teammate_2_shield_extraction=False, do_zone_timer_extraction=False, do_frames_extraction=False, methods_to_run=None - if None, all methods will be run otherwise pass a list of methods to run'}
        return make_response(render_template('video-decomposition.html', **data_dict))

    # options are which sections to extract
    # These are: killFeed, PlayerEvo, PlayerDamage, miniMap, PlayerGuns, PlayerHealth, PlayerKills, PlayerShield, PlayerTac, PlayerUlt, Teammate1Health, Teammate1Shield, Teammate2Health, Teammate2Shield, ZoneTimer, frames

    def post(self):
        # We should let the user choose which sections to extract using a checkbox
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
        }

        for key, value in options.items():
            if value is None:
                options[key] = False

        # coordinator.runVideoDecompositionTool(options)
        # return make_response(render_template('video_decomp.html', data=options))
        # print(str(options)+"test_not_webpage")
        # print("!WEBPAGE!"+" test")
        print("!WEBPAGE! " + str(options))
        return options
