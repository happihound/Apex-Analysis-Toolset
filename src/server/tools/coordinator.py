import os
import csv
import threading
import server.tools.damageTracker as damageTracker
from server.tools.evoTracker import EvoTracker
import server.tools.killFeedNameFinder as killFeedNameFinder
import server.tools.miniMapPlotter as miniMapPlotter
import server.tools.playerGunTracker as playerGunTracker
import server.tools.playerHealthTracker as playerHealthTracker
import server.tools.playerKillTracker as playerKillTracker
import server.tools.playerShieldTracker as playerShieldTracker
import server.tools.playerTacTracker as playerTacTracker
import server.tools.playerUltTracker as playerUltTracker
import server.tools.videoDecompositionTool as videoDecompositionTool
import util.apexUtils as util
import server.tools.ZoneTimerTracker as ZoneTimerTracker
from PIL import Image, ImageDraw, ImageFont

'''
This class runs all of the other classes and
is responsible for collecting their various outputs into one large table.
'''

'''
Quick options:
do_frame_extraction=True
do_teammate_extraction=True
do_ocr_extractions=True
do_mini_map_plotter=True
methods_to_run=None - if None, all methods will be run otherwise pass a list of methods to run
'''


class Coordinator:
    def __init__(self, socketio):
        self.running_threads = {}
        self.socketio = socketio

    def runVideoDecompositionTool(self, options):
        decomp = videoDecompositionTool.VideoDecompositionTool()
        self.running_threads['video-decomposition'] = decomp
        decomp.start_in_thread(options)

    def runPlayerKillTracker(self):
        kill_tracker = playerKillTracker.KillTracker(self.socketio)
        self.running_threads['kill-tracker'] = kill_tracker
        kill_tracker.start_in_thread()

    def runPlayerGunTracker(self):
        gun_tracker = playerGunTracker.GunTracker(self.socketio)
        self.running_threads['gun-tracker'] = gun_tracker
        gun_tracker.start_in_thread()

    def runPlayerShieldTrackerAndTeammates():
        playerShieldTracker.ShieldTracker('/playerShield').main()
        playerShieldTracker.ShieldTracker('/teammate1Shield').main()
        # playerShieldTracker.ShieldTracker('/teammate2Shield').main()

    def runHealthTracker(self, options):
        health_tracker = playerHealthTracker.HealthTracker(self.socketio)
        self.running_threads['health-tracker'] = health_tracker
        health_tracker.start_in_thread(options)

    def runPlayerShieldTracker(self):
        player_shield_tracker = playerShieldTracker.ShieldTracker('/playerShield', self.socketio)
        self.running_threads['player-shield-tracker'] = player_shield_tracker
        player_shield_tracker.start_in_thread()

    def runTeammate1ShieldTracker(self):
        teammate1_shield_tracker = playerShieldTracker.ShieldTracker('/teammate1Shield', self.socketio)
        self.running_threads['teammate1-shield-tracker'] = teammate1_shield_tracker
        teammate1_shield_tracker.start_in_thread()

    def runPlayerUltTracker():
        playerUltTracker.UltTracker().main()

    def runPlayerTacFinder():
        playerTacTracker.TacTracker().main()

    def runKillFeedNameFinder():
        print("skipping kill feed name finder")
        return
        # killFeedNameFinder.KillFeedNameFinder().main()

    def runEvoTracker(self):
        evoTracker = EvoTracker(self.socketio)
        self.running_threads['evo-tracker'] = evoTracker
        evoTracker.start_in_thread()

    def runDamageTracker(self):
        damage_tracker = damageTracker.DamageTracker(self.socketio)
        self.running_threads['damage-tracker'] = damage_tracker
        damage_tracker.start_in_thread()

    def runMiniMapPlotter(map, ratio):
        print("skipping mini map plotter")
        return
        # miniMapPlotter.MiniMapPlotter(map, ratio).main()

    def runZoneTimer():
        ZoneTimerTracker.ZoneTimerTracker().main()

    def cancel(self, operation_name):
        print(f"!WEBPAGE! Attempting to cancel {operation_name}")
        if operation_name in self.running_threads:
            self.running_threads[operation_name].stop()
            del self.running_threads[operation_name]
            print(f"!WEBPAGE! Successfully cancelled {operation_name}")
            return True
        print(f"!WEBPAGE! Could not find {operation_name} to cancel")
        return False

        # if __name__ == '__main__':
        #     tracker = Coordinator('all', False)
        #     tracker.runTrackers()
        #     util.ApexUtils().combineAllCSVs()
        #     util.ApexUtils().visualize()
