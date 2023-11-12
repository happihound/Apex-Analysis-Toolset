import os
import csv
import threading
import src.server.tools.damageTracker as damageTracker
from src.server.tools.evoTracker import EvoTracker
import src.server.tools.killFeedNameFinder as killFeedNameFinder
import src.server.tools.miniMapPlotter as miniMapPlotter
import src.server.tools.playerGunTracker as playerGunTracker
import src.server.tools.playerHealthTracker as playerHealthTracker
import src.server.tools.playerKillTracker as playerKillTracker
import src.server.tools.playerShieldTracker as playerShieldTracker
import src.server.tools.playerTacTracker as playerTacTracker
import src.server.tools.playerUltTracker as playerUltTracker
import src.server.tools.videoDecompositionTool as videoDecompositionTool
import src.util.apexUtils as util
import src.server.tools.ZoneTimerTracker as ZoneTimerTracker
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

    def runHealthTracker(self, options):
        health_tracker = playerHealthTracker.HealthTracker(self.socketio)
        self.running_threads['health-tracker'] = health_tracker
        health_tracker.start_in_thread(options)

    def runShieldTracker(self, options):
        shield_tracker = playerShieldTracker.ShieldTracker(self.socketio)
        self.running_threads['shield-tracker'] = shield_tracker
        shield_tracker.start_in_thread(options)

    def runPlayerUltTracker(self):
        ult_tracker = playerUltTracker.UltTracker(self.socketio)
        self.running_threads['ult-tracker'] = ult_tracker
        ult_tracker.start_in_thread()

    def runPlayerTacTracker(self):
        tac_tracker = playerTacTracker.TacTracker(self.socketio)
        self.running_threads['tac-tracker'] = tac_tracker
        tac_tracker.start_in_thread()

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

    def runMiniMapPlotter(self, options):
        minimap_plotter = miniMapPlotter.MiniMapPlotter(self.socketio)
        self.running_threads['minimap-plotter'] = minimap_plotter
        minimap_plotter.start_in_thread(options)

    def runZoneTimer(self):
        zone_tracker = ZoneTimerTracker.ZoneTimerTracker(self.socketio)
        self.running_threads['zone-tracker'] = zone_tracker
        zone_tracker.start_in_thread()

    def runCombineAllCSVs(self):
        util.ApexUtils.combineAllCSVs()

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
