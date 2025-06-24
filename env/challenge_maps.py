"""Define EEE466 map configs for use with pysc2."""

from pysc2.maps import lib


class EEE466Map(lib.Map):
    directory = "EEE466"
    players = 2
    game_steps_per_episode = 0


maps = ["3v3", "10v10", "bonus", "bonus_pvp", "lab3"]

for name in maps:
    globals()[name] = type(name, (EEE466Map,), dict(filename=name))
