import pstats
import cProfile

import miniMapPlotter

cProfile.runctx("profile()", globals(), locals(), "Profile.prof")

s = pstats.Stats("Profile.prof")
s.strip_dirs().sort_stats("time").print_stats()
