import pickle
import socket
from typing import Union

import numpy as np

import constante


# Stub do lado do cliente: como comunicar com o servidor...

class StubClient:

    def __init__(self):
        self.s: socket = socket.socket()
        self.s.connect((constante.ENDERECO_SERVIDOR, constante.PORTO))

    def dimension_size(self):
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
        msg = constante.GRID
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        dados = self.s.recv(1024)
        grid = pickle.loads(dados)
        return grid

    def send_hit(self, data):
        msg = constante.HIT
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        self.s.send(pickle.dumps(data))

    def send_miss(self, data):
        msg = constante.MISS
        self.s.send(msg.encode(constante.CODIFICACAO_STR))
        self.s.send(pickle.dumps(data))

    def send_sunken(self):
        msg = constante.SUNKEN
        self.s.send(msg.encode(constante.SUNKEN))


    # def add(self, value1: int, value2: int) -> Union[int, None]:
    #
    #     msg = constante.SOMA
    #     self.s.send(msg.encode(constante.CODIFICACAO_STR))
    #     self.s.send(value1.to_bytes(constante.N_BYTES, byteorder="big", signed=True))
    #     self.s.send(value2.to_bytes(constante.N_BYTES, byteorder="big", signed=True))
    #     dados_recebidos: bytes = self.s.recv(constante.N_BYTES)
    #     return int.from_bytes(dados_recebidos, byteorder='big', signed=True)
    #     #if msg != constante.END:
    #     #    dados_recebidos: bytes = self.s.recv(constante.TAMANHO_MENSAGEM)
    #     #    return dados_recebidos.decode(constante.CODIFICACAO_STR)
    #     #else:
    #     #    self.s.close()
