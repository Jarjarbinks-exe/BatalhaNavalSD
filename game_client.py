import threading
import pygame
import client_stub
from desenho_x import Xdrawing
from navios import Navio


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
        self.ships = pygame.sprite.LayeredDirty()
        self.ships_list = []
        self.drawn_squares = []
        self.hit_location = []
        self.shot_location = []
        self.lock = threading.Lock()
        self.is_player_turn = False
        self.my_number = 0
        self.pl = dict()

        self.x_group = pygame.sprite.LayeredDirty()
        self.width, self.height = self.x_max * grid_size, self.y_max * grid_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Batalha Naval")
        self.clock = pygame.time.Clock()
        self.grid_size = grid_size
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((30, 144, 255))
        self.screen.blit(self.background, (0, 0))
        self.draw_grid((0, 0, 0))
        pygame.display.update()

    def draw_grid(self, colour: tuple):
        """
        Desenha a grelha
        :param colour: Cor rgb
        :return: None
        """
        for x in range(0, self.x_max):
            pygame.draw.line(self.screen, colour, (x * self.grid_size, 0), (x * self.grid_size, self.height))
        for y in range(0, self.y_max):
            pygame.draw.line(self.screen, colour, (0, y * self.grid_size), (self.width, y * self.grid_size))

    def find_ships(self):
        """
        Função responsável por encontrar os navios, ao encontrar estes é posto na lista listagem_navios um tuplo com
        a primeira posição ocupada pelo navio, o seu comprimento e a sua orientação
        :return: uma lista de tuplos
        """
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
                for k in range(1, 7):
                    if (aux[i][0] + k, aux[i][1]) in aux:
                        val_y += 1
                        auxv2.append((aux[i][0] + k, aux[i][1]))
                    else:
                        listagem_navios.append((aux[i], val_y, "vertical"))
                        break
                val_y = 1
            elif (aux[i][0], aux[i][1] + 1) in aux and (aux[i][0], aux[i][1] + 1) not in auxv2:
                for k in range(1, 7):
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
        """
        Função responsável por criar os objetos Navio, ao criar-los este são postos dentro da lista self.ship_list
        :param size: Tamanho de cada célula
        :return: None
        """
        listagem_navios = self.find_ships()
        for i in listagem_navios:
            pos_x = int(i[0][1])
            pos_y = int(i[0][0])
            length = int(i[1])
            direcao = str(i[2])
            navioadd = Navio(pos_x, pos_y, length, direcao, size)
            self.ships_list.append(navioadd)
            self.ships.add(navioadd)

    def ship_size(self, y, x):
        """
        Função responsável por calcular o tamanho do navio
        :param y: Valor y
        :param x: Valor x
        :return: tamanho do navio
        """
        size = 0
        x -= 1
        y -= 1
        j = y
        i = x
        if self.grid[x][y] == 1:
            size += 1
            while j + 1 < self.y_max and self.grid[x][j + 1] == 1:
                j += 1
                size += 1
            while y - 1 >= 0 and self.grid[x][y - 1] == 1:
                y -= 1
                size += 1
            while i + 1 < self.x_max and self.grid[i + 1][y] == 1:
                i += 1
                size += 1
            while x - 1 >= 0 and self.grid[x - 1][y] == 1:
                x -= 1
                size += 1
        return size

    def hit_or_miss(self, x, y):
        """
        Função responsável por procurar se uma posição foi acertada ou não
        :param x:
        :param y:
        :return: uma string
        """
        if self.grid[y-1][x-1] == 1:
            return "hit"
        return "miss"

    def draw_x_miss(self, pos):
        """
        Função que desenha a sprite X de falhar
        :param pos: posição
        :return: None
        """
        x = pos[0]
        y = pos[1]
        self.x_group.add(Xdrawing(x, y, 2, self.grid_size))
        rects = self.x_group.draw(self.screen)
        pygame.display.update(rects)

    def draw_x_sunken(self, pos, player):
        """
        Função que desenha a sprite X de acertar
        :param pos: posição
        :return: None
        """
        x = pos[0]
        y = pos[1]
        self.x_group.add(Xdrawing(x, y, player, self.grid_size))
        rects = self.x_group.draw(self.screen)
        pygame.display.update(rects)

    def check_hit(self):
        """
        Função que verifica se acertou num navio
        :return: None
        """
        self.hit_location = self.stub.get_hit()
        for i in self.hit_location:
            if i[0] not in self.drawn_squares:
                self.draw_x_sunken((i[0][0], i[0][1]), i[1])
                self.drawn_squares.append(i[0])

    def set_players(self):
        """
        Recebe os jogadores e o numero de jogadores do servidor
        :return: None
        """
        self.pl = self.stub.get_players()
        nr_players = self.stub.get_nr_players()
        print("Nr. de jogadores:", nr_players)
        print("Jogadores no jogo:", self.pl)

    def add_player(self, name: str) -> int:
        return self.stub.add_player(name)

    def run(self):
        """
        Função que corre o game_client
        :return: None
        """
        self.create_ships(self.grid_size)
        rects = self.ships.draw(self.screen)
        pygame.display.update(rects)
        nome = input("Insira o seu nome: ")
        self.my_number = self.add_player(nome)
        self.stub.start_game()
        self.set_players()
        end = False
        while not end:
            self.shot_location = self.stub.get_shot()
            if len(self.shot_location) == 0:
                self.is_player_turn = self.my_number == 0
            else:
                if self.shot_location[-1][1] == self.my_number:
                    self.is_player_turn = False
                else:
                    self.is_player_turn = True
            data = self.stub.get_end()
            if data[0] == 9:
                print("Pontuação obtida:", data[1][self.my_number])
                end = True
            self.check_hit()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    end = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    end = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    end = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_player_turn:
                        with self.lock:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            grid_x = mouse_x // self.grid_size + 1
                            grid_y = mouse_y // self.grid_size + 1
                            if self.hit_or_miss(grid_x, grid_y) == "hit":
                                if not any(coord[0][0] == grid_x - 1 and coord[0][1] == grid_y - 1 for coord in
                                           self.hit_location):
                                    print("Acertou num barco com o tamanho:", self.ship_size(grid_x, grid_y))
                                    self.stub.send_hit(((grid_x - 1, grid_y - 1), self.my_number))
                                    self.stub.send_shot(((grid_x - 1, grid_y - 1), self.my_number))
                                    self.draw_x_sunken((grid_x - 1, grid_y - 1), self.my_number)
                            elif self.hit_or_miss(grid_x, grid_y) == "miss":
                                self.draw_x_miss((grid_x - 1, grid_y - 1))
                                self.stub.send_shot(((grid_x - 1, grid_y - 1), self.my_number))
                                print("Não acertou em nenhum barco.")
                                self.is_player_turn = False
                    pygame.time.wait(100)
