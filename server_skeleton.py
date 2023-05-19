import pickle
import socket
import logging

import numpy as np

from game_mechanics import GameMech
import constante

# Está no lado do servidor: Skeleton to user interface (permite ter informação
# de como comunicar com o cliente)
class SkeletonServer:

    def __init__(self, gm_obj: GameMech):
        self.gm = gm_obj
        self.s = socket.socket()
        self.s.bind((constante.ENDERECO_SERVIDOR, constante.PORTO))
        self.s.listen()

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
        grid = self.gm.grid
        s_c.send(pickle.dumps(grid))

    def process_sunken(self, s_c):
        valor = s_c.recv(constante.N_BYTES)
        sunken = s_c.recv(pickle.loads(valor))
        self.gm.sink_ships(sunken)


    def process_hit(self, s_c):
        data = s_c.recv(1024)
        hit = pickle.loads(data)
        self.gm.recv_data(hit)

    # def processa_soma(self,s_c):
    #     dados_recebidos: bytes = s_c.recv(constante.N_BYTES)
    #     # Receber dois inteiros do cliente!
    #
    #     value1 = int.from_bytes(dados_recebidos, byteorder='big', signed=True)
    #     logging.debug("o cliente enviou: \"" + str(value1) + "\"")
    #
    #     dados_recebidos: bytes = s_c.recv(constante.N_BYTES)
    #     value2 = int.from_bytes(dados_recebidos, byteorder='big', signed=True)
    #     logging.debug("o cliente enviou: \"" + str(value2) + "\"")
    #     # Processa a soma
    #     soma = self.gm.add(value1, value2)
    #     # Devolver ao cliente o resultado da soma
    #     s_c.send(soma.to_bytes(constante.N_BYTES, byteorder="big", signed=True))
    #     # AJUDAS
    #     # -- int.from_bytes(dados_recebidos, byteorder='big', signed=True)
    #     # -- to_bytes(constante.N_BYTES, byteorder="big", signed=True)

    def run(self):
        self.gm.execute()
        logging.info("a escutar no porto " + str(constante.PORTO))
        socket_client, address = self.s.accept()
        logging.info("o cliente com endereço " + str(address) + " ligou-se!")

        msg: str = ""
        fim = False
        while fim == False:
            dados_recebidos: bytes = socket_client.recv(constante.COMMAND_SIZE)
            msg = dados_recebidos.decode(constante.CODIFICACAO_STR)
            logging.debug("o cliente enviou: \"" + msg + "\"")

            if msg == constante.X_MAX:
                self.process_x_max(socket_client)
            elif msg == constante.Y_MAX:
                self.process_y_max(socket_client)
            elif msg == constante.GRID:
                self.process_grid(socket_client)
            elif msg == constante.SUNKEN:
                self.process_sunken(socket_client)
            elif msg == constante.HIT:
                self.process_hit(socket_client)
            elif msg == constante.END:
                fim = True
#            if msg != constante.END:
#                msg = self.eco_obj.eco(msg)
#                socket_client.send(msg.encode(constante.CODIFICACAO_STR))
        socket_client.close()
        logging.info("o cliente com endereço o " + str(address) + " desligou-se!")

        self.s.close()


logging.basicConfig(filename=constante.NOME_FICHEIRO_LOG,
                    level=constante.NIVEL_LOG,
                    format='%(asctime)s (%(levelname)s): %(message)s')
