import pygame
import random
import numpy as np
from navios import Navio
import time


class GameMech(object):
    def __init__(self, x_max: int = 10, y_max: int = 10, grid_size: int = 50):
        self._nr_players = 0
        self.x_max = x_max
        self.y_max = y_max
        self.ships = pygame.sprite.LayeredDirty()
        self._play_history = []
        self.ships_list = []
        self.sunken_ships = []
        self.hits = []
        self.shots = []
        self.points = dict()
        self._players = dict()
        self.grid_size = grid_size
        self.grid = self.create_grid(10, 10)

    def create_grid(self, linhas: int, colunas: int):
        self.grid = np.array([[0] * linhas] * colunas)
        return self.grid

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

    def check_valid(self, x, y, shape):
        """

        :param x: Valor x
        :param y: Valor y
        :param shape: Lista com os shapes de todos navios, i.e (1, 1) -> submarino
        :return: False caso a posição for inválida, True caso contrário
        """
        for i in range(x - 1, x + shape[0] + 1):
            for j in range(y - 1, y + shape[1] + 1):
                if 0 <= i < 10 and 0 <= j < 10 and self.grid[i, j] == 1:
                    return False
        return True

    def create_world(self, shapes):
        """
        Função responsável por criar o mundo, cada posição ocupada por um navio é preenchida com 1
        :param shapes: Lista com os shapes de todos navios, i.e (1, 1) -> submarino
        :return: None
        """
        for shape in shapes:
            while True:
                x = random.randint(0, 10 - shape[0])
                y = random.randint(0, 10 - shape[1])
                if self.check_valid(x, y, shape) and x + shape[0] and y + shape[1]:
                    break
            self.grid[x:x + shape[0], y:y + shape[1]] = 1

    def add_player(self, name) -> int:
        """
        Função responsável por adicionar os jogadores
        :param: name: nome do jogador
        :return: o número de jogadores
        """
        nr_player = self._nr_players
        tick = int(1000 * time.time())  # Milliseconds

        self.players[nr_player] = [name, tick]
        self._nr_players += 1
        return nr_player

    def recv_data(self, data):
        """
        Função responsável por receber os hits e calcular se deve-se adicionar pontos aos players.
        :param data: hits
        :return: None
        """
        self.hits.append((data[0], data[1]))
        for s in self.ships_list:
            if not s.get_sunken() and data[0] not in self._play_history:
                if data[0] in s.get_position_grid():
                    if data[1] == 0:
                        s.add_p1_points()
                    else:
                        s.add_p2_points()
        if data[0] not in self._play_history:
            self._play_history.append(data[0])
        self.sink_ship()
        self.sunken_pos()
        self.end_game()

    def sink_ship(self):
        """
        Função responsável por afundar os barcos e adicionar pontos aos jogadores com base no que acertou mais bases no
        navio.
        :return: None
        """
        for s in self.ships_list:
            if not s.get_sunken() and all(pos in self._play_history for pos in s.get_position_grid()):
                s.set_sunken()
                if s.get_p1_points() > s.get_p2_points():
                    winner = 0
                elif s.get_p1_points() < s.get_p2_points():
                    winner = 1
                else:
                    winner = 0
                    if 1 not in self.points:
                        self.points[1] = 1
                    else:
                        self.points[1] += 1

                if winner not in self.points:
                    self.points[winner] = 1
                else:
                    self.points[winner] += 1

    def sunken_pos(self):
        """
        Função que caso um navio esteja afundado este é adicionado à lista de navios afundados
        :return: todos os navios afundados
        """
        for s in self.ships_list:
            if s.get_sunken() and s.get_position_grid() not in self.sunken_ships:
                self.sunken_ships.append(s.get_position_grid())
        return self.sunken_ships

    def end_game(self):
        return len(self.sunken_ships), self.points

    def get_hit_location(self):
        return self.hits

    def get_all_shots(self):
        return self.shots

    def recv_all_shots(self, data):
        self.shots.append((data[0], data[1]))

    def run(self):
        self.create_world([(5, 1), (1, 4), (4, 1), (3, 1), (1, 3), (2, 1), (1, 2), (1, 1), (1, 1)])
        print(self.grid)
        self.create_ships(self.grid_size)

    @property
    def players(self) -> dict:
        return self._players

    @property
    def nr_players(self):
        return self._nr_players
