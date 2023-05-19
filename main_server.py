from game_mechanics import GameMech
from server_skeleton import SkeletonServer


def main():
    gm = GameMech()
    skeleton = SkeletonServer(gm)
    skeleton.run()


main()
