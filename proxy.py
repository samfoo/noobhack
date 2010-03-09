import threading

class Input(threading.Thread):
    def __init__(self, conn):
        self.filter_callbacks = []
        self.conn = conn
        threading.Thread.__init__(self)

    def set_filter_callback(self, name, callback):
        self.filter_callbacks.append(callback)

    def run(self):
        while True:
            try:
                # TODO: How do I properly hijack input.
                input = sys.stdin.read(1)

                send_command = True

                for callback in self.filter_callbacks:
                    if callback(input) != True:
                        send_command = False

                if send_command:
                    self.conn.get_socket().send(input)
            except socket.error, e:
                break

class Output(threading.Thread):
    """Otherwise known as: Pam's Gossip Train"""

    def __init__(self, conn):
        self.conn = conn
        threading.Thread.__init__(self)

    def set_filter_callback(self, pattern, callback):
        self.filter_callbacks[pattern] = callback

    def run(self):
        while True:
            try:
                output = self.conn.read_very_eager()

                for pattern, callback in self.filter_callbacks.value():
                    if re.search(pattern, output) is not None:
                        callback(output)

                sys.stdout.write(output)
                sys.stdout.flush()
            except socket.error, e:
                # Oh snap, forearm shiver to the gut, Pam
                break

