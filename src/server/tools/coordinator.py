import os
import csv
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

    # __slots__ = ['run_all_methods', 'methods_to_run', 'run_frame_extraction']

    # def __init__(self, methods_to_run='all', do_frame_extraction=False):
    #     if do_frame_extraction:
    #         self.run_frame_extraction = True
    #     else:
    #         self.run_frame_extraction = False
    #     if methods_to_run is None or type(methods_to_run) is str and methods_to_run.lower() == 'all':
    #         self.run_all_methods = True
    #         self.methods_to_run = []
    #     else:
    #         self.run_all_methods = False
    #         self.methods_to_run = methods_to_run

    # def runTrackers(self):
    #     print("Running the following trackers:", end='\n')
    #     if self.run_all_methods:
    #         print("all")
    #     else:
    #         print(self.methods_to_run)
    #     if (self.run_all_methods or 'videoDecompositionTool' in self.methods_to_run) and self.run_frame_extraction:
    #         print("Running video decomposition tool", end='\n\t')
    #         self.runVideoDecompositionTool()
    #     if self.run_all_methods or 'playerKillTracker' in self.methods_to_run:
    #         print("Running player kill tracker", end='\n\t')
    #         self.runPlayerKillTracker()
    #     if self.run_all_methods or 'playerGunTracker' in self.methods_to_run:
    #         print("Running player gun tracker", end='\n\t')
    #         self.runPlayerGunTracker()
    #     if self.run_all_methods or 'playerHealthTrackerAndTeammates' in self.methods_to_run:
    #         print("Running player health tracker and teammates", end='\n\t')
    #         self.runPlayerHealthTrackerAndTeammates()
    #     if self.run_all_methods or 'playerShieldTrackerAndTeammates' in self.methods_to_run:
    #         print("Running player shield tracker and teammates", end='\n\t')
    #         self.runPlayerShieldTrackerAndTeammates()
    #     if not self.run_all_methods or 'playerHealthTracker' in self.methods_to_run:
    #         print("Running player health tracker", end='\n\t')
    #         self.runPlayerHealthTracker()
    #     if not self.run_all_methods or 'playerShieldTracker' in self.methods_to_run:
    #         print("Running player shield tracker", end='\n\t')
    #         self.runPlayerShieldTracker()
    #     if self.run_all_methods or 'playerUltTracker' in self.methods_to_run:
    #         print("Running player ult tracker", end='\n\t')
    #         self.runPlayerUltTracker()
    #     if self.run_all_methods or 'playerTacFinder' in self.methods_to_run:
    #         print("Running player tac finder", end='\n\t')
    #         self.runPlayerTacFinder()
    #     if self.run_all_methods or 'killFeedNameFinder' in self.methods_to_run:
    #         print("Running kill feed name finder", end='\n\t')
    #         self.runKillFeedNameFinder()
    #     if self.run_all_methods or 'evoTracker' in self.methods_to_run:
    #         print("Running evo tracker", end='\n\t')
    #         self.runEvoTracker()
    #     if self.run_all_methods or 'damageTracker' in self.methods_to_run:
    #         print("Running damage tracker", end='\n\t')
    #         self.runDamageTracker()
    #     if self.run_all_methods or 'miniMapPlotter' in self.methods_to_run:
    #         print("Running mini map plotter", end='\n\t')
    #         self.runMiniMapPlotter()
    #     if self.run_all_methods or 'zoneTimer' in self.methods_to_run:
    #         print("Running zone timer", end='\n\t')
    #         self.runZoneTimer()

    def runVideoDecompositionTool(options=None):
        videoDecompositionTool.VideoDecompositionTool().decompose_video(options)

    def runPlayerKillTracker():
        playerKillTracker.KillTracker().main()

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


# if __name__ == '__main__':
#     tracker = Coordinator('all', False)
#     tracker.runTrackers()
#     util.ApexUtils().combineAllCSVs()
#     util.ApexUtils().visualize()
