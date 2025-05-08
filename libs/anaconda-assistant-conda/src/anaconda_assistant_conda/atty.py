import sys

print("hello!!!!")


class PseudoTTY:
    def __init__(self, underlying):
        self.__underlying = underlying

    def __getattr__(self, name):
        return getattr(self.__underlying, name)

    def isatty(self):
        return False


sys.stdin = PseudoTTY(sys.stdin)
sys.stdout = PseudoTTY(sys.stdout)
sys.stderr = PseudoTTY(sys.stderr)

print(sys.stdout.isatty())
