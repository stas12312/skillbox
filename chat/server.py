from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor


class Client(Protocol):
    ip: str = None
    login: str = None
    factory: 'Chat'

    def __init__(self, factory):
        """
        Инициализация фабрики клиента
        :param factory:
        """
        self.factory = factory

    def connectionMade(self):
        """
        Обработчик подключения нового клиента
        """
        self.ip = self.transport.getHost().host
        self.factory.clients.append(self)

        print(f"Client connected: {self.ip}")

        self.transport.write("Welcome to the chat v0.2\n".encode())

    def dataReceived(self, data: bytes):
        """
        Обработчик нового сообщения от клиента
        :param data:
        """
        message = data.decode().replace('\n', '')

        if self.login is not None:
            server_message = f"{self.login}: {message}"
            self.factory.notify_all_users(server_message, self)
            print(server_message)
        else:
            if message.startswith("login:"):
                login = message.replace("login:", "")

                # Проверяем занятость логина
                if self.factory.check_login(login):
                    self.transport.write(f"Error: Login {login} is exist".encode())
                    reactor.callLater(2, self.transport.loseConnection)
                    print(f'Error: Login {login} is exist')
                else:
                    self.login = login
                    self.factory.send_history(self)  # Отправляем клиенту историю сообщений
                    notification = f"New user connected: {self.login}"

                    self.factory.notify_all_users(notification, self)
                    print(notification)
            else:
                print("Error: Invalid client login")

    def connectionLost(self, reason=None):
        """
        Обработчик отключения клиента
        :param reason:
        """
        self.factory.clients.remove(self)
        print(f"Client disconnected: {self.ip}")


class Chat(Factory):
    clients: list
    history: str  # Строка для хранения отправленных сообщений

    def __init__(self):
        """
        Инициализация сервера
        """
        self.history = ''
        self.clients = []
        print("*" * 10, "\nStart server \nCompleted [OK]")

    def startFactory(self):
        """
        Запуск процесса ожидания новых клиентов
        :return:
        """
        print("\n\nStart listening for the clients...")

    def buildProtocol(self, addr):
        """
        Инициализация нового клиента
        :param addr:
        :return:
        """
        return Client(self)

    def notify_all_users(self, data: str, sender: Client = None):
        """
        Отправка сообщений всем текущим пользователям
        :param data:
        :param sender:
        :return:
        """
        self.history += f'{data}\n'  # Добавляем сообщение в историю

        # Копируем список и удаляем из него отправителя
        clients = self.clients[:]
        clients.remove(sender)

        # Отправка сообщения всем, кроме отправителя
        for user in clients:
            user.transport.write(f"{data}\n".encode())

    def check_login(self, login: str):
        """
        Проверка занятости логина
        :param login:
        :return:
        """
        for client in self.clients:
            if client.login == login:
                return True
        return False

    def send_history(self, client: Client):
        """
        Отправляет историю сообщений клиенту
        :param client:
        :return:
        """
        client.transport.write(self.history.encode())


if __name__ == '__main__':
    reactor.listenTCP(7410, Chat())
    reactor.run()
