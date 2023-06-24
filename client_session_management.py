from threading import Thread
import shared
from game_mechanics import GameMech
import constante
import json
import pickle
import logging


class ClientSession(Thread):
    """Maintains a session with the client"""

    def __init__(self, socket_client: int, shr: shared.Shared, game_mech: GameMech):
        """
        Constrói uma thread para segurar uma sessão com o cliente
        :param: shared_state: O estado do servidor partilhado pelas threads
        :param: client_socket: A socket do cliente
        """
        Thread.__init__(self)
        self._shared = shr
        self.socket_client = socket_client
        self.gm = game_mech

    def process_x_max(self, s_c):
        # pedir ao gm o tamanho do jogo
        x_max = self.gm.x_max
        # enviar a mensagem com esse valor
        s_c.send(x_max.to_bytes(constante.N_BYTES, byteorder="big", signed=True))

    def process_y_max(self, s_c):
        # pedir ao gm o tamanho do jogo
        y_max = self.gm.y_max
        # enviar a mensagem com esse valor
        s_c.send(y_max.to_bytes(constante.N_BYTES, byteorder="big", signed=True))

    def process_grid(self, s_c):
        """
        Envia a grelha para o cliente
        """
        grid = self.gm.grid
        s_c.send(pickle.dumps(grid))

    def process_sunken(self, s_c):
        """
        Envia as posições afundadas para o cliente
        """
        sunken_ships = self.gm.sunken_pos()
        s_c.send(pickle.dumps(sunken_ships))

    def process_get_hit(self, s_c):
        """
        Envia a localização do hit para o cliente
        :param s_c: Socket do cliente
        :return: None
        """
        hit_location = self.gm.get_hit_location()
        s_c.send(pickle.dumps(hit_location))

    def process_get_shot(self, s_c):
        """
        Envia a localização do tiro para o cliente
        :param s_c: Socket do cliente
        :return: None
        """
        shot_location = self.gm.get_all_shots()
        s_c.send(pickle.dumps(shot_location))

    def process_end_game(self, s_c):
        """
        Envia os navios afundados e a pontuação para o cliente
        :param s_c: Socket do cliente
        :return: None
        """
        end_game = self.gm.end_game()
        s_c.send(pickle.dumps(end_game))

    def process_hit(self, s_c):
        """
        Recebe os dados do hit e envia os para o game_mechanics
        :param s_c: Socket do cliente
        :return: None
        """
        data = s_c.recv(1024)
        hit = pickle.loads(data)
        self.gm.recv_data(hit)

    def process_shot(self, s_c):
        """
        Envia os dados dos shots para o game_mechanics
        :param s_c: Socket do cliente
        :return: None
        """
        data = s_c.recv(1024)
        shot = pickle.loads(data)
        self.gm.recv_all_shots(shot)

    def process_start_game(self, s_c):
        logging.debug("O client pretende inciar o jogo")
        self._shared._clients_control.acquire()
        logging.debug("O client vai iniciar o jogo")

        # Returning 'yes'
        value = constante.TRUE
        s_c.send(value.encode(constante.CODIFICACAO_STR))

    def process_add_player(self, s_c):
        """
        Adiciona jogador com nome e posição
        :param s_c: Socket do cliente
        :return: None
        """
        logging.debug("O cliente define o jogador")
        ln: bytes = s_c.recv(constante.N_BYTES)
        nm: bytes = s_c.recv(int.from_bytes(ln, byteorder='big', signed=True))
        name = nm.decode(constante.CODIFICACAO_STR)
        # Testing for player name and its position
        number = self.gm.add_player(name)
        self._shared.add_client(s_c)
        self._shared.control_nr_clients()
        s_c.send(number.to_bytes(constante.N_BYTES, byteorder="big", signed=True))

    def process_get_players(self, s_c):
        """
        Envia os jogadores para o cliente
        :param s_c: Socket do cliente
        :return: None
        """
        pl = self.gm.players
        msg = json.dumps(pl)
        dim = len(msg)
        s_c.send(dim.to_bytes(constante.N_BYTES, byteorder="big", signed=True))
        s_c.send(msg.encode(constante.CODIFICACAO_STR))

    def process_get_nr_players(self, s_c):
        """
        Envia o número de jogadores para o cliente
        :param s_c: Socket do cliente
        :return: None
        """
        nr_pl = self.gm.nr_players
        s_c.send(nr_pl.to_bytes(constante.N_BYTES, byteorder="big", signed=True))

    def dispatch_request(self, socket_client) -> bool:
        """
        Função que recebe as mensagens do cliente executa funções com base nas diferentes mensagens recebidas
        :return: O ultimo request
        """
        lr = False
        dados_recebidos: bytes = socket_client.recv(constante.COMMAND_SIZE)
        msg = dados_recebidos.decode(constante.CODIFICACAO_STR)
        logging.debug("o cliente enviou: \"" + msg + "\"")

        if msg == constante.X_MAX:
            self.process_x_max(socket_client)
        elif msg == constante.Y_MAX:
            self.process_y_max(socket_client)
        elif msg == constante.GRID:
            self.process_grid(socket_client)
        elif msg == constante.HIT:
            self.process_hit(socket_client)
        elif msg == constante.SHOT:
            self.process_shot(socket_client)
        elif msg == constante.SUNKEN:
            self.process_sunken(socket_client)
        elif msg == constante.GET_HIT:
            self.process_get_hit(socket_client)
        elif msg == constante.GET_SHOT:
            self.process_get_shot(socket_client)
        # Start the game....
        elif msg == constante.START_GAME:
            self.process_start_game(socket_client)
        elif msg == constante.ADD_PLAYER:
            self.process_add_player(socket_client)
        elif msg == constante.GET_PLAYERS:
            self.process_get_players(socket_client)
        elif msg == constante.NR_PLAYERS:
            self.process_get_nr_players(socket_client)
        elif msg == constante.END_GAME:
            self.process_end_game(socket_client)
        return lr

    def run(self):
        """Maintains a session with the client, following the established protocol"""
        last_request = False
        while not last_request:
            last_request = self.dispatch_request(self.socket_client)
        logging.debug("Client " + str(self.socket_client.peer_addr) + " disconnected")
