import os
import sys
import fcntl
import select
import signal
import termios

class Local:
    """
    Runs and manages the input/output of a local nethack game. The game is
    forked into a pty.
    """

    def __init__(self):
        self.pipe = None
        self.stdin = None
        self.stdout = None
        self.pid = None

    def open(self):
        (self.pid, self.pipe) = os.forkpty()

        if self.pid == 0:
            # I'm the child process in a fake pty. I need to replace myself
            # with an instance of nethack.
            #
            # NOTE: The '--proxy' argument doesn't seem to do anything though
            # it's used by dgamelaunch which is a bit confusing. However, 
            # without *some* argument execvp doesn't seem to like nethack and
            # launches a shell instead? It's quite confusing.
            os.execvpe("nethack", ["--proxy"], os.environ)
        else:
            # Before we do anything else, it's time to establish some boundries
            signal.siginterrupt(signal.SIGCHLD, True)
            signal.signal(signal.SIGCHLD, self._close)

            # When my tty resizes, the child's pty should resize too.
            signal.signal(signal.SIGWINCH, self.resize_child)

            # Setup out input/output proxies
            self.stdout = os.fdopen(self.pipe, "rb", 0)
            self.stdin = os.fdopen(self.pipe, "wb", 0)

            # Set the initial size of the child pty to my own size.
            self.resize_child()

    def _close(self, *args):
        try:
            self.stdout.close()
            self.stdin.close()
        except IOError:
            # The child is dead, the pipe is invalid, trying to close the files
            # throws an IOError that we can safely ignore here.
            pass

        raise IOError("Nethack exited.")

    def resize_child(self, *args):
        # Get the host app's terminal size first.
        parent = fcntl.ioctl(sys.stdin, termios.TIOCGWINSZ, 'SSSS')
        # Now set the child (conduit) app's size properly
        fcntl.ioctl(self.stdin, termios.TIOCSWINSZ, parent)

    def fileno(self):
        return self.pipe

    def close(self):
        # Kill our child process. Cuban hit squad.
        os.kill(self.pid, signal.SIGTERM)

    def write(self, buf):
        self.stdin.write(buf)

    def read(self):
        buf = ""
        while self.data_is_available(): 
            buf += self.stdout.read(1)
        return buf

    def data_is_available(self):
        return select.select([self.stdout], [], [], 0) == ([self.stdout], [], [])
