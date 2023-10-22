import os
import csv
import threading
import server.tools.damageTracker as damageTracker
import server.tools.evoTracker as evoTracker
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
    def __init__(self):
        self.running_threads = {}

    def runVideoDecompositionTool(self, options):
        decomp = videoDecompositionTool.VideoDecompositionTool()
        self.running_threads['video-decomposition'] = decomp
        decomp.start_in_thread(options)

    def runPlayerKillTracker(self, socketio):
        kill_tracker = playerKillTracker.KillTracker()
        kill_tracker.set_socketio(socketio)
        self.running_threads['kill-tracker'] = kill_tracker
        kill_tracker.start_in_thread()

    def runPlayerGunTracker():
        playerGunTracker.GunTracker().main()

    def runPlayerHealthTrackerAndTeammates():
        playerHealthTracker.HealthTracker('/playerHealth').main()
        playerHealthTracker.HealthTracker('/teammate1Health').main()
        # playerHealthTracker.HealthTracker('/teammate2Health').main()

    def runPlayerShieldTrackerAndTeammates():
        playerShieldTracker.ShieldTracker('/playerShield').main()
        playerShieldTracker.ShieldTracker('/teammate1Shield').main()
        # playerShieldTracker.ShieldTracker('/teammate2Shield').main()

    def runPlayerHealthTracker():
        playerHealthTracker.HealthTracker('/playerHealth').main()

    def runPlayerShieldTracker():
        playerShieldTracker.ShieldTracker('/playerShield').main()

    def runPlayerUltTracker():
        playerUltTracker.UltTracker().main()

    def runPlayerTacFinder():
        playerTacTracker.TacTracker().main()

    def runKillFeedNameFinder():
        print("skipping kill feed name finder")
        return
        # killFeedNameFinder.KillFeedNameFinder().main()

    def runEvoTracker():
        evoTracker.EvoTracker().main()

    def runDamageTracker():
        damageTracker.DamageTracker().main()

    def runMiniMapPlotter(map, ratio):
        print("skipping mini map plotter")
        return
        # miniMapPlotter.MiniMapPlotter(map, ratio).main()

    def runZoneTimer():
        ZoneTimerTracker.ZoneTimerTracker().main()

    def cancel(self, operation_name):
        print(f"Attempting to cancel {operation_name}")
        if operation_name in self.running_threads:
            self.running_threads[operation_name].stop()
            del self.running_threads[operation_name]
            print(f"Successfully cancelled {operation_name}")
            return True
        return False

        # if __name__ == '__main__':
        #     tracker = Coordinator('all', False)
        #     tracker.runTrackers()
        #     util.ApexUtils().combineAllCSVs()
        #     util.ApexUtils().visualize()
