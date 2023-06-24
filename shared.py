import socket
import constante
import threading
from typing import Set
#
# Esta classe tem como objetivo dar permissão através de locks à
# acesso de dados partilhados por mais do que uma thread.
# Faz a ponte entre o pedido de execução de uma ação e a permissão
# para essa ação através do lock.
# Mas iremos apenas utilizá-lo para contar o número de clientes.
# Guarda, também o número de clientes ligados, desbloqueando o arranque
# do jogo apenas quando existem mais que x clientes ligados.
# Usa o conceito de semáforo:
# -- Quando está zero, o semáforo bloquei todos os que vão para a sua fila.
# -- Quando fica um - recebe instrução, permite passar o primeiro thread que está na fila e fica a zero novamente.
# -- Se o semáforo ficar a 2, passam os primeiros dois threads e o semáforo fica a zero.
# -- Se o semáforo for x, e se passam z threads, o semáforo fica x-z, ou zero se z >= x.
#


class Shared:
    def __init__(self):
        # Um conjunto não permite ter clientes iguais. No conjunto iremos
        # guardar os socket dos clientes.
        self._clients: Set[socket.socket] = set()
        self._clients_lock = threading.Lock()
        # Semáforo impedindo os clientes de arrancar...
        self._clients_control = threading.Semaphore(0)

    def add_client(self, client: socket.socket) -> None:
        """
        Adiciona um cliente à lista de clientes de forma protegida
        :param client:
        :return:
        """
        self._clients_lock.acquire()
        self._clients.add(client)
        self._clients_lock.release()

    def remove_client(self, client_socket: socket.socket) -> None:
        """
        Remove cliente. Se o número de clientes é menor que o número máximo, permite
        a entrada de mais um, abrindo o semáforo para passar apenas 1 (semáforo fica 1)
        :param self:
        :param client_socket:
        :return:
        """
        self._clients_lock.acquire()
        self._clients.remove(client_socket)
        if len(self._clients) < constante.NR_CLIENTS:
            # It signals that there is one client that can enter...
            self._clients_control.release()
        self._clients_lock.release()

    def control_nr_clients(self):
        """
        Se tiver o número de clientes suposto, ele começa o jogo ao dar release ao semáforo
        :return: None
        """
        if len(self._clients) >= constante.NR_CLIENTS:
            # Test
            print("Number of clients is", len(self._clients))
            for _ in range(len(self._clients)):
                # Allow the exact number of clients starting the game
                self._clients_control.release()
