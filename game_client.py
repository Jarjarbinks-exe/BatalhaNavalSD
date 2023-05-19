import pygame
import client_stub
from desenho_x import Xdrawing


# ---------------------
# The grid now is built based on the number of squares in x and y.
# This allows us to associate the size of the space to a matrix or to a dictionary
# that will keep data about each position in the environment.
# Moreover, we now can control the movement of the objects.
# We now separate the control of the environment

class GameUI(object):
    def __init__(self, stub: client_stub.StubClient, grid_size: int = 50):
        dim: tuple = stub.dimension_size()
        self.x_max = dim[0]
        self.y_max = dim[1]
        self.grid = stub.get_grid()
        self.stub = stub

        self.x_group = pygame.sprite.LayeredDirty()
        self.width, self.height = self.x_max * grid_size, self.y_max * grid_size
        self.screen = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption("Batalha Naval")
        self.clock = pygame.time.Clock()
        self.grid_size = grid_size
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((30,144,255))
        self.screen.blit(self.background,(0,0))
        self.draw_grid((0,0,0))
        pygame.display.update()

    # Drawing a square grid
    # Drawing a square grid
    def draw_grid(self, colour:tuple):
        for x in range(0, self.x_max):
            pygame.draw.line(self.screen, colour, (x * self.grid_size,0), ( x * self.grid_size, self.height))
        for y in range(0,self.y_max):
            pygame.draw.line(self.screen, colour, (0, y * self.grid_size), (self.width, y * self.grid_size))

    # def set_players(self):
    #     self.pl = self.gm.get_players()
    #     self.players = pygame.sprite.LayeredDirty()
    #     nr_players = self.gm.get_nr_players()
    #     # Test
    #     print("Game2, Nr. of players:", nr_players)
    #     print("Game2, Players:", self.pl)
    #     for nr in range(nr_players):
    #         if self.pl[nr] != []:
    #             # Test
    #             print("Game2, Player added:", nr)
    #             p_x, p_y = self.pl[nr][1][0], self.pl[nr][1][1]
    #             player = player10.Player(nr, self.pl[nr][0], p_x, p_y, self.grid_size, self.players)
    #             self.players.add(player)

    # def set_walls(self, wall_size: int):
    #     self.wl = self.gm.get_obstacles()
    #     # Create Wall (sprites) around world
    #     self.walls = pygame.sprite.Group()
    #     nr_obstacles = self.gm.get_nr_obstacles()
    #     for nr in range(nr_obstacles):
    #         if self.wl[nr] != []:
    #             w_x, w_y = self.wl[nr][1][0], self.wl[nr][1][1]
    #             wall = wall10.Wall(w_x, w_y, self.grid_size, self.walls)
    #             self.walls.add(wall)

    def hit_or_miss(self, x, y):
        if self.grid[y-1][x-1] == 1:
            return "hit"
        return "miss"

    def find_ship(self, y, x):
        tamanho = 0
        x -= 1
        y -= 1
        j = y
        i = x
        if self.grid[x][y] == 1:
            tamanho += 1
            while j + 1 < self.y_max and self.grid[x][j + 1] == 1:
                j += 1
                tamanho += 1
            while y - 1 >= 0 and self.grid[x][y - 1] == 1:
                y -= 1
                tamanho += 1
            while i + 1 < self.x_max and self.grid[i + 1][y] == 1:
                i += 1
                tamanho += 1
            while x - 1 >= 0 and self.grid[x - 1][y] == 1:
                x -= 1
                tamanho += 1
        return tamanho

    def draw_x_miss(self, pos):
        x = pos[0]
        y = pos[1]
        self.x_group.add(Xdrawing(x, y, 2, self.grid_size))
        rects = self.x_group.draw(self.screen)
        pygame.display.update(rects)

    def draw_x_sunken(self, pos):
        x = pos[0]
        y = pos[1]
        self.x_group.add(Xdrawing(x, y, 1, self.grid_size))
        rects = self.x_group.draw(self.screen)
        pygame.display.update(rects)

    def run(self):
        print(self.grid)
        end = False
        while end == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    end = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    end = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    end = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = mouse_x // self.grid_size + 1
                    grid_y = mouse_y // self.grid_size + 1
                    print(f"Clicked on square ({grid_x}, {grid_y})")
                    print(self.hit_or_miss(grid_x, grid_y))
                    print(self.find_ship(grid_x, grid_y))
                    if self.hit_or_miss(grid_x, grid_y) == "hit":
                        self.stub.send_hit(((grid_x, grid_y), self.find_ship(grid_x, grid_y)))
                        self.draw_x_sunken((grid_x-1, grid_y-1))
                    elif self.hit_or_miss(grid_x, grid_y) == "miss":
                        self.draw_x_miss((grid_x-1, grid_y-1))

        return
