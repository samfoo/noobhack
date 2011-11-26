import os
import sys
import fcntl
import select
import signal
import termios

class ProcError(EnvironmentError):
    def __init__(self, stdout):
        self.stdout = stdout

class Local:
    """
    Runs and manages the input/output of a local nethack game. The game is
    forked into a pty.
    """

    def __init__(self, debug=False):
        self.debug = debug
        self.pipe = None
        self.stdin = None
        self.stdout = None
        self.pid = None

    def open(self):
        """
        Fork a child nethack process into a pty and setup its stdin and stdout
        """

        (self.pid, self.pipe) = os.forkpty()

        if self.pid == 0:
            # I'm the child process in a fake pty. I need to replace myself
            # with an instance of nethack.
            #
            # NOTE: The '--proxy' argument doesn't seem to do anything though
            # it's used by dgamelaunch which is a bit confusing. However, 
            # without *some* argument execvp doesn't seem to like nethack and
            # launches a shell instead? It's quite confusing.
            if self.debug:
                os.execvpe("nethack", ["--proxy", "-D"], os.environ)
            else:
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

    def _close(self, *_):
        """
        Raise an exception signaling that the child process has finished.
        Whoever catches the exception is responsible for flushing the child's 
        stdout.
        """

        raise ProcError(self.stdout)

    def resize_child(self, *_):
        """
        Try to send the right signals to the child that the terminal has
        changed size.
        """

        # Get the host app's terminal size first.
        parent = fcntl.ioctl(sys.stdin, termios.TIOCGWINSZ, 'SSSS')
        # Now set the child (conduit) app's size properly
        fcntl.ioctl(self.stdin, termios.TIOCSWINSZ, parent)

    def fileno(self):
        """ Return the fileno of the pipe.  """

        return self.pipe

    def close(self):
        """ Kill our child process. Cuban hit squad.  """

        os.kill(self.pid, signal.SIGTERM)

    def write(self, buf):
        """ Proxy input to the nethack process' stdin.  """
        self.stdin.write(buf)

    def read(self):
        """ 
        Proxy output from the nethack process' stdout. This shouldn't block 
        """
        buf = ""
        while self.data_is_available(): 
            buf += self.stdout.read(1)
        return buf

    def data_is_available(self):
        """ 
        Return a non-empty list when the nethack process has data to read 
        """
        return select.select([self.stdout], [], [], 0) == ([self.stdout], [], [])
