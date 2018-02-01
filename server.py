#coding=utf-8
# student name: Qinyuan Yang
# student number: 14302747
# Date: DEC 3rd
# Program Description:
# This program is to finish the lab3 version1
# The main purpose is to build a chatroom.
# There are 4 main functions:
# 1. login: use account and password, the information is stored in info.txt
# 2. newuser: account should be less than 32 and password should between 4-8
# 3. send message: both to the server and the client
# 4. logout: logout from the chatroom
# I use socket to build the network connection.
# Need at least 2 socket, server and client
# Build the connection between sockets:
# 1. build the socket of the server, bind the host and port, listen the client
# 2. the socket of client requests for connection
# 3. server answers the request

import socket, select, thread, SocketServer

host = '127.0.0.1'
port = 12747
server_addr = (host, port)

# read list of the waitable sockets
inputs = []
# the name of the client
fd_name = {}
# the status of the client
status = {}
# set max number of client
maxnum = 3

# judge if the client has logged in
def online(fd_name, status):
    onlinelist = []
    for client_conn in fd_name:
        if status[client_conn] == True:
            onlinelist.append(fd_name[client_conn])
    return onlinelist

# build and initial server socket
def serverInit():
    print 'Server Start'
    ss = socket.socket()  # build server socket
    ss.bind(server_addr)  # bind server addr
    ss.listen(5)          # listen ports, set the maxnum to 5
    return ss             # return to server socket

# build a new socket connection
def newConnection(ss):
    client_conn, client_addr = ss.accept()  # answer a request of a client
    # if more than 3 clients tries to login
    if len(inputs) > maxnum:
        try:
            inputs.append(client_conn)
            fd_name[client_conn] = client_addr
            status[client_conn] = False
            client_conn.send('Sorry, the chatroom is full, maybe you can login later')
            inputs.remove(client_conn)
        except Exception as e:
            pass
    # less than 3 clients tries to login
    else:
        try:
            # welcome message
            client_conn.send("welcome to chatroom, please use /login or /newuser before send message or /logout to logout.")
            client_conn.send(" Also you can use /who to get the online list and /to + name to send to one person.")
            inputs.append(client_conn)
            fd_name[client_conn] = client_addr
            status[client_conn] = False
        except Exception as e:
            print e

def closeConnection():
    pass

def run():
    ss = serverInit()
    inputs.append(ss)
    print "server is running..."
    while True:
        # r-readlist, w-writelist, e-errorlist
        r, w, e = select.select(inputs, [], [])
        # when there is no fd, close the server
        if not r:
            print "timeout..."
            ss.close()  # close server socket
            break
        for t in r:
            if t is ss:  # server socket, which means new client request coming
                newConnection(ss)
            else:          # new data from client arrive to server
                disconnect = False
                try:
                    data = t.recv(1024)  # reveive data
                except socket.error:
                    data = fd_name[t] + " leaved the room"
                    disconnect = True
                else:
                    pass
                if disconnect:
                    inputs.remove(t)
                    print data
                    for other in inputs:
                        if other != ss and other != t:  # not happen in server and unconnected client
                            try:
                                other.send(data)
                            except Exception as e:
                                print e
                            else:
                                pass
                    # delete name
                    del fd_name[t]
                else:
                    if isinstance(fd_name[t], tuple):
                        print fd_name[t][0] + ' : ' + data
                    else:
                        print fd_name[t] + ' : ' + data
                try:
                    # chose the commends
                    if data[0] == '/':
                        splitter = data.split(' ',1)
                        if splitter[0] == '/login':
                            login(splitter[1], t)
                        elif splitter[0] == '/newuser':
                            newuser(splitter[1], t)
                        elif splitter[0] == '/logout':
                            logout(t)
                        elif splitter[0] == '/who':
                            who(t)
                        elif splitter[0] == '/to':
                            to(splitter[1], t)
                        else:
                            t.send('invalid commend')
                    else:
                        sendmessage(data, t)
                except Exception as e:
                    print e

    ss.close()

def sendmessage(data, client):
    # send message
    # if not login
    if not status[client]:
        resp = 'You need to login first'
        client.send(resp)
        print 'To' + fd_name[client][0] + ' : ' + resp
    else:
        for others in inputs:
            if others != client:
                try:
                    others.send(fd_name[client] + ' say: ' + data)
                    print fd_name[client] + ' say: ' + data
                except Exception as e:
                    pass

def login(inf, client):
    # login
    infofile = open('info.txt')
    resp = ''
    try:
        splitter1 = inf.split(' ',1)
        acc = splitter1[0]
        pwd = splitter1[1]
        for line in infofile:
            splitter2 = line.split(' ',1)
            account = splitter2[0]
            password = splitter2[1][:-1]
            if account == acc and password == pwd:
                resp = 'login success'
                fd_name[client] = account
                status[client] = True
                client.send(resp)
                print fd_name[client] + ' ' + resp
                break
        else:
            resp = ' wrong account or password'
            client.send(resp)
            print fd_name[client][0] + ' : ' + resp
    finally:
        infofile.close()

def newuser(inf, client):
    #newuser
    infofile = open('info.txt', 'r+')
    try:
        # find if the account is exsist
        flag = 0
        splitter1 = inf.split(' ',1)
        acc = splitter1[0]
        for line in infofile:
            splitter2 = line.split(' ',1)
            account = splitter2[0]
            if account == acc:
                flag = 1
    finally:
        if flag == 0:
            # check if the acc and pwd are legal
            if len(splitter1[0]) > 0 and len(splitter1[0]) < 32 and 4 <= len(splitter1[1]) and len(splitter1[1]) <= 8:
                with open('info.txt', 'a') as infofile2:
                    infofile2.write(inf+'\n')
                    infofile2.close()
                    resp = ' new account success, you can login now'
            else:
                resp = ' the format of the account or password is wrong'
        else:
            resp = ' account exsited, please login or create a new account'
        infofile.close()
        client.send(resp)
        print fd_name[client][0] + resp

def logout(client):
    #logout
    if not status[client]:
        resp = 'you should login first'
        client.send(resp)
        print fd_name[client][0] + ' : ' + resp
    else:
        resp = ' logout success'
        client.send(resp)
        print fd_name[client] + resp
        del fd_name[client]
        del status[client]
        inputs.remove(client)

def who(client):
    #online people
    if not status[client]:
        resp = 'you should login first'
        client.send(resp)
        print fd_name[client][0] + resp
    else:
        resp = '%s are online' % (online(fd_name, status))
        client.send(resp)
        print fd_name[client] + ' consult ' + resp

def to(inf, client):
    #send to who
    if not status[client]:
        resp = 'you should login first'
        client.send(resp)
        print fd_name[client][0] + resp
    else:
        try:
            splitter1 = inf.split(' ', 1)
            keys = []
            values = []
            for key, value in fd_name.items():
                keys.append(key)
                values.append(value)
            # try to find the object person
            if splitter1[0] in values:
                object = keys[values.index(splitter1[0])]
                object.send(fd_name[client] + ' send to you: ' + splitter1[1])
                print fd_name[client] + ' send ' + inf
            # if cannot find the object
            else:
                client.send(splitter1[0] + ' is not online or not exsit')
        except Exception as e:
            print e


if __name__ == "__main__":
    run()