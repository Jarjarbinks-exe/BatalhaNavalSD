import socket
import logging
import client_session_management
import constante
import shared
from game_mechanics import GameMech
from typing import Union


# Está no lado do servidor: Skeleton to user interface (permite ter informação
# de como comunicar com o cliente)
class SkeletonServer:

    def __init__(self, gm_obj: GameMech):
        # Inicialização do SkeletonServer
        self.gm = gm_obj
        self.s = socket.socket()
        self.s.bind((constante.ENDERECO_SERVIDOR, constante.PORTO))
        self.s.listen()
        self.s.settimeout(constante.ACCEPT_TIMEOUT)
        self.keep_running = True
        self.shared = shared.Shared()

    def accept(self) -> Union['Socket', None]:
        """
        Uma nova definição de accept() para fornecer um return se ocorrer um timeout
        A new definition of accept() to provide a return if a timeout occurs.
        """
        try:
            client_connection, address = self.s.accept()
            logging.info("o cliente com endereço " + str(address) + " ligou-se!")

            return client_connection
        except socket.timeout:
            return None

    def run(self):
        """
        Chama a função run do game_mechanics, se tiver uma socket aceitada ele inicializa um objeto ClientSession
        com essa socket.
        :return: None
        """
        self.gm.run()
        logging.info("a escutar no porto " + str(constante.PORTO))
        while self.keep_running:
            socket_client = self.accept()
            if socket_client is not None:
                # Add client
                # self._state.add_client(socket_client)
                client_session_management.ClientSession(socket_client, self.shared, self.gm).start()

        self.s.close()


logging.basicConfig(filename=constante.NOME_FICHEIRO_LOG,
                    level=constante.NIVEL_LOG,
                    format='%(asctime)s (%(levelname)s): %(message)s')
