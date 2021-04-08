import asyncio
from collections import namedtuple

requests = namedtuple('requests', 'put get all') # all = '*\n'
request = requests(put = 'put', get = 'get', all = '*')


def run_server(host, port):
    server_loop = asyncio.get_event_loop()
    server_obj = server_loop.create_server(ClientServer, host, port) #creates a TCP server and returns server object. Server objects are asynchronous context managers

    server = server_loop.run_until_complete(server_obj) # loop.run_until_complete(future) - Run until the future (an instance of Future) has completed.

    try:
        server_loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    server_loop.run_until_complete(server.wait_closed())
    server_loop.close()

class Storage:
    data_to_save = {}

    def return_all(self):
        output = ''

        if self.data_to_save:
            for key in self.data_to_save:
                for value in self.data_to_save[key]:
                    output += f'{key} {value[0]} {value[1]}\n'
            return 'ok\n' + output + '\n'

        else:
            return 'ok\n\n'

    def return_part(self, key):
        output = ''

        if key in self.data_to_save:
            for value in self.data_to_save[key]:
                output += f'{key} {value[0]} {value[1]}\n'
            return 'ok\n' + output + '\n'
        else:
            return 'ok\n\n'

    def put_in(self, raw):
        try:
            key, value, timestamp = raw.split()
            if key not in self.data_to_save:
                self.data_to_save[key] = []

            self.data_to_save[key] = list(filter(lambda saved_values: saved_values[1] != int(timestamp), self.data_to_save[key])) #filtering timestamps

            self.data_to_save[key].append((float(value), int(timestamp)))

            return 'ok\n\n'

        except Exception:

            return 'error\nwrong command\n\n'

storage = Storage()

class ClientServer(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        print('data received: {}'.format(data))
        resp = self.save(data.decode())
        self.transport.write(resp.encode())

    def save(self, input):
        try:
            query, input = input.split(' ', maxsplit=1)

            if query not in request:
                return 'error\nwrong command\n\n'

            elif query == request.get and len(input.split()) == 1:
                return self.getting(input)

            elif query == request.put and len(input.split()) == 3:
                return self.putting(input)

            else:
                return 'error\nwrong command\n\n'

        except Exception:
            return 'error\nwrong command\n\n'

    def getting(self, input):
        try:
            key = input.strip('\n')

            if key == request.all:
                return storage.return_all()

            else:
                return storage.return_part(key)

        except Exception:
            return 'error\nwrong command\n\n'

    def putting(self, input):

        raw = input.strip('\n')

        return storage.put_in(raw)


# run_server('127.0.0.1', 8888)
