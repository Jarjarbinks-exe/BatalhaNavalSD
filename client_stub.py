import pickle
import socket
import constante
import json

# Stub do lado do cliente: como comunicar com o servidor...

class StubClient:

    def __init__(self):
        # Inicialização do StubClient
        self.s: socket = socket.socket()
        self.s.connect((constante.ENDERECO_SERVIDOR, constante.PORTO))

    def dimension_size(self):
        """
        Protocolo:
        -- Envia a mensagem 'max x'
        -- Recebe o X máximo
        -- Envia a mensagem 'max y'
        -- Recebe o Y máximo
        :return: Tuplo x máximo y máximo
        """

        msg = constante.X_MAX
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        valor = self.s.recv(constante.N_BYTES)
        x_max = int.from_bytes(valor, byteorder="big", signed=True)

        msg = constante.Y_MAX
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        valor = self.s.recv(constante.N_BYTES)
        y_max = int.from_bytes(valor, byteorder="big", signed=True)
        return x_max, y_max

    def get_grid(self):
        """
        Protocolo:
        -- Envia a mensagem 'grid'
        -- Recebe a grid
        :return: A grid
        """
        msg = constante.GRID
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        dados = self.s.recv(1024)
        grid = pickle.loads(dados)
        return grid

    def get_sunken(self):
        """
        Protocolo:
        -- Envia a mensagem 'sunken'
        -- Recebe os dados de navios afundados
        :return: Navios afundados
        """
        msg = constante.SUNKEN
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        dados = self.s.recv(1024)
        sunken_ships = pickle.loads(dados)
        return sunken_ships

    def get_hit(self):
        """
        Protocolo:
        -- Envia a mensagem 'get hit'
        -- Recebe oos dados do hit
        :return: Localização do hit
        """
        msg = constante.GET_HIT
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        dados = self.s.recv(1024)
        hit_location = pickle.loads(dados)
        return hit_location

    def get_shot(self):
        """
        Protocolo:
        -- Envia a mensagem 'get shot'
        -- Recebe os dados do shot
        :return: A localização do shot
        """
        msg = constante.GET_SHOT
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        dados = self.s.recv(1024)
        shot_location = pickle.loads(dados)
        return shot_location

    def send_hit(self, data):
        """
        Protocolo:
        -- Envia a mensagem 'hit'
        -- Envia os dados do hit
        :return: None
        """
        msg = constante.HIT
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        self.s.send(pickle.dumps(data))

    def send_shot(self, data):
        """
        Protocolo:
        -- Envia a mensagem 'shot'
        -- Envia os dados do shot
        :return: None
        """
        msg = constante.SHOT
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        self.s.send(pickle.dumps(data))

    def get_players(self) -> dict:
        """
        Protocolo:
        -- Envia type de msg 'get players'
        -- Receber dimensão do objeto dicionário
        -- Recebe objeto dicionário com todos os jogadores
        :return:
        """
        msg = constante.GET_PLAYERS
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        data: bytes = self.s.recv(constante.N_BYTES)
        dim = int.from_bytes(data, byteorder='big', signed=True)
        rec: bytes = self.s.recv(dim)
        players = json.loads(rec)
        return players

    def get_nr_players(self) -> int:
        """
        Protocolo:
        -- Envia a mensagem 'nr players'
        -- Recebe o número de players
        :return: O numero de players
        """
        msg = constante.NR_PLAYERS
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        data: bytes = self.s.recv(constante.N_BYTES)
        nr = int.from_bytes(data, byteorder='big', signed=True)
        return nr

    def add_player(self, name: str) -> int:
        """
        Protocolo:
        - enviar msg com o nome associado ao pedido 'add player'
        - enviar o nome do jogador
        - receber o número do jogador
        :param name:
        :return:
        """
        msg = constante.ADD_PLAYER
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        # Send the length of the name and the name
        sz = len(name)
        self.s.send(sz.to_bytes(constante.N_BYTES, byteorder="big", signed=True))
        self.s.send(name.encode(constante.CODIFICACAO_STR))
        rec: bytes = self.s.recv(constante.N_BYTES)
        number = int.from_bytes(rec, byteorder='big', signed=True)
        return number

    def start_game(self) -> None:
        """
        Pergunta ao servidor para começar o jogo. O servidor retorna que sim quando o número de jogadores é 2
        :return: None
        """
        msg = constante.START_GAME
        print("À espera de mais jogadores...")
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        rec: bytes = self.s.recv(constante.N_BYTES)
        res = rec.decode(constante.CODIFICACAO_STR)
        print("Começando o jogo:", res)

    def get_end(self):
        """
        -- Envia a mensagem 'end game'
        -- Recebe um tuplo com o número de navios afundados e a pontuação do jogador
        :return: Tuplo com o número de navios afundados e a pontuação do jogador
        """
        msg = constante.END_GAME
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        dados = self.s.recv(1024)
        end_game = pickle.loads(dados)
        return end_game
