import os
import sys
import select
import socket
import fcntl

def lines(buf, sep="\r\n"):
    remains = ""
    lines = buf.split(sep)
    if not buf.endswith(sep):
        remains = lines[-1]
        lines = lines[:-1]
    lines = [l for l in lines if l != '']
    return (remains, lines)

def main():
    input_buffer = ""
    output_buffer = ""

    print "Starting debug server..."
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", 31337))
    server.listen(1)

    print "Waiting for client to connect..."
    select.select([server.fileno()], [], [])
    conn, addr = server.accept()

    flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)

    sys.stdout.write("\n>>> ")
    sys.stdout.flush()
    while True:
        available = select.select([conn.fileno(), sys.stdin], [], [])[0]

        if conn.fileno() in available:
            data = conn.recv(1024)
            if len(data) == 0:
                break
            output_buffer, commands = lines(output_buffer + data)
            for c in commands:
                sys.stdout.write("\r    \n    <-> " + c)
            sys.stdout.write("\n>>> ")

        if sys.stdin in available:
            input_buffer += sys.stdin.read()

            input_buffer, commands = lines(input_buffer, "\n")
            for c in commands:
                conn.send(c + "\r\n")

            if len(commands) > 0:
                sys.stdout.write(">>> ")

        sys.stdout.flush()

if __name__ == "__main__":
    main()
