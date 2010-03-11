import os
import sys
import select
import signal

class Local:
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

            # Setup out input/output proxies
            self.stdout = os.fdopen(self.pipe, "rb", 0)
            self.stdin = os.fdopen(self.pipe, "wb", 0)

    def _close(self, sig, sf):
        try:
            self.stdout.close()
            self.stdin.close()
        except IOError:
            # The child is dead, the pipe is invalid, trying to close the files
            # throws an IOError that we can safely ignore here.
            pass

        raise IOError("My child is dead.")

    def fileno(self):
        return self.pipe

    def close(self):
        # Kill our child process. Cuban hit squad.
        os.kill(self.pid, signal.SIGTERM)

    def write(self, buf):
        self.stdin.write(buf)

    def read(self):
        return self.stdout.read(1)
