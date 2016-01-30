#!/usr/bin/python3
import re
import socket
try:
    import simplejson as json
except ImportError:
    import json


class TS(object):
    def __init__(self):
        with open("config.json", "r") as f:
            config = json.loads(f.read())

        self.host = (config['host'], config['port'])
        self.user = config['user']
        self.passwd = config['passwd']
        self.size = 1024
        self.buf = ""

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.connect(self.host)

    def close(self):
        self.sock.close()

    def login(self):
        buf = self.sock.recv(self.size)
        if "TS3" in buf.decode("utf-8"):
            if "Welcome " not in buf.decode("utf-8"):
                buf = self.sock.recv(self.size)
                if "Welcome " not in buf.decode("utf-8"):
                    exit("cannot connect")
                    self.sock.close()

        self.send("use 1")
        self.send("login {0} {1}".format(self.user, self.passwd))

    def clientlist(self):
        rex_clist = re.compile(("clid=(\d+).*? client_nickname=(.*?) "
                                "client_type=(\d+)"))

        clientlist = self.send("clientlist", recv_count=2, recv_errorcheck=2)
        clientlist = clientlist.split("|")
        result = []

        for client in clientlist:
            if rex_clist.search(client):
                (clid, clnick, cltype) = rex_clist.search(client).groups()
                if "\\sfrom\\s" in clnick:
                    clnick = clnick.split("\\sfrom\\s")[0] + " (telnet)"
                result.append(clnick)

        return result

    def send(self, msg, recv_count=1, recv_errorcheck=1):
        endl = "\r\n"
        buf = ""
        result = ""
        recv_errorcheck -= 1

        self.sock.sendall(bytes(msg + endl, "utf-8"))
        for i in range(0, recv_count):
            buf = self.sock.recv(self.size)
            if i == recv_errorcheck:
                if "error id=0 msg=ok" not in buf.decode("utf-8"):
                    self.sock.close()
                    exit("error: {0}".format(buf))
            else:
                result += buf.decode("utf-8")

        return result

def filter(string):
    return ''.join([i if ord(i) < 128 else '_' for i in string])

if __name__ == "__main__":
    ts = TS()
    ts.connect()
    ts.login()
    clist = ts.clientlist()
    for c in clist:
        try:
            print(c)
        except:
            print(filter(c))
    ts.close()

