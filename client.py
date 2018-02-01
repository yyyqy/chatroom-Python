import socket, select, threading, sys;

host = '127.0.0.1'

addr = (host, 12747)

# set up connectionwhowho
def conn():
    s = socket.socket()
    s.connect(addr)
    return s
# listen to the socket of the server
def lis(s):
    my = [s]
    while True:
        r, w, e = select.select(my, [], [])
        if s in r:
            try:
                print s.recv(1024)
            except socket.error:
                print 'socket is error'
                exit()

# get input of the client
def talk(s):
    while True:
        try:
            info = raw_input()
        except Exception, e:
            print 'can\'t input'
            exit()
        # if the input is '/logout', exit the client
        try:
            s.send(info)
            if info == '/logout':
                exit()
        except Exception, e:
            print e
            exit()

def main():
    ss = conn()
    t = threading.Thread(target=lis, args=(ss,))
    t.start()
    t1 = threading.Thread(target=talk, args=(ss,))
    t1.start()

if __name__ == '__main__':
    main()