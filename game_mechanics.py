import pygame
import random
import numpy as np
from navios import Navio
from desenho_x import Xdrawing

class GameMech(object):
    def __init__(self, x_max:int = 10, y_max:int = 10, grid_size:int  = 50):
        self.x_max = x_max
        self.y_max = y_max

        self.width, self.height = x_max * grid_size, y_max * grid_size
        self.screen = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption("Batalha Naval")
        self.clock = pygame.time.Clock()
        self.grid_size = grid_size
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((30,144,255))
        self.screen.blit(self.background,(0,0))
        self.draw_grid((0,0,0))
        self.grid = self.create_grid(10,10)
        self.x_group = pygame.sprite.LayeredDirty()
        pygame.display.update()

    def create_grid(self, linhas: int, colunas: int):
        self.gridTemp = np.array([[0] * linhas] * colunas)
        return self.gridTemp


    # Drawing a square grid
    def draw_grid(self, colour:tuple):

        for x in range(0, self.x_max):
            pygame.draw.line(self.screen, colour, (x * self.grid_size,0), ( x * self.grid_size, self.height))
        for y in range(0,self.y_max):
            pygame.draw.line(self.screen, colour, (0, y * self.grid_size), (self.width, y * self.grid_size))


    def transform_rect(self, rect: pygame.Rect, tamanho: int):
        rect.height = tamanho
        rect.width = tamanho
        return rect

    def create_grid(self, linhas: int, colunas: int):
        self.grid = np.array([[0] * linhas] * colunas)
        return self.grid

    def find_ships(self):
        aux = []
        val_x = 1
        val_y = 1
        listagem_navios = []
        auxv2 = []

        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if self.grid[x][y] == 1:
                    aux.append((x, y))

        for i in range(len(aux)):
            if (aux[i][0] + 1, aux[i][1]) in aux and (aux[i][0] + 1, aux[i][1]) not in auxv2:
                for k in range(1,7):
                    if (aux[i][0] + k, aux[i][1]) in aux:
                        val_y += 1
                        auxv2.append((aux[i][0] + k, aux[i][1]))
                    else:
                        listagem_navios.append((aux[i], val_y, "vertical"))
                        break
                val_y = 1
            elif (aux[i][0], aux[i][1] + 1) in aux and (aux[i][0], aux[i][1] + 1) not in auxv2:
                for k in range(1,7):
                    if (aux[i][0], aux[i][1] + k) in aux:
                        val_x += 1
                        auxv2.append((aux[i][0], aux[i][1] + k))
                    else:
                        listagem_navios.append((aux[i], val_x, "horizontal"))
                        break
                val_x = 1
            elif (aux[i][0], aux[i][1]) not in auxv2:
                listagem_navios.append((aux[i], 1, "vertical"))
        return listagem_navios

    def create_ships(self, size: int):
        listagem_navios = self.find_ships()
        self.navios = pygame.sprite.LayeredDirty()
        for i in listagem_navios:
            pos_x = int(i[0][1])
            pos_y = int(i[0][0])
            length = int(i[1])
            direcao = str(i[2])
            navioadd = Navio(pos_x, pos_y, length, direcao, size)
            self.navios.add(navioadd)

    def sink_ships(self, pos: tuple):
        x = pos[0]
        y = pos[1]
        for i in self.navios:
            if i.get_x() == x or i.get_y() == y:
                i.dirty = 1

    def draw_x_sunken(self, pos):
        x = pos[0]
        y = pos[1]
        self.x_group.add(Xdrawing(x, y, 1, self.grid_size))



    def execute(self):
        self.create_world([(5,1), (1,4), (4,1), (3,1), (1,3), (2,1), (1,2), (1,1), (1,1)])
        print(self.grid)
        self.create_ships(self.grid_size)
        rects = self.navios.draw(self.screen)
        pygame.display.update(rects)
        return


    def check_valid(self, x, y, shape):
        # Check that the object does not overlap with any existing objects
        for i in range(x - 1, x + shape[0] + 1):
            for j in range(y - 1, y + shape[1] + 1):
                if (i >= 0 and i < 10 and j >= 0 and j < 10 and
                        self.grid[i, j] == 1):
                    return False
        return True

    def create_world(self, shapes):
        for shape in shapes:
            # Generate a random position for the object
            while True:
                x = random.randint(0, 10 - shape[0])
                y = random.randint(0, 10 - shape[1])
                if self.check_valid(x, y, shape) and x + shape[0] and y + shape[1]:
                    break

            # Place the object on the grid
            self.grid[x:x + shape[0], y:y + shape[1]] = 1

    def recv_data(self, data):
        print(data)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pygame.init()
    gm = GameMech()
    gm.run()
