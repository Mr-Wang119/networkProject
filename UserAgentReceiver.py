from socket import *
import ssl
import base64


class MailReceiver:

    def __init__(self, mail_server, mail_name, mail_pass, port_num=995):
        self.mail_server = mail_server
        self.mail_name = mail_name
        self.mail_pass = mail_pass
        self.port_num = port_num

    def check_mill_address(self):
        # Email message
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket = ssl.wrap_socket(client_socket)

        # Client socket
        # Establish TCP connection with mail server
        client_socket.connect((self.mail_server, self.port_num))
        recv = client_socket.recv(1024)
        print(recv)

        # send USERNAME
        client_socket.send(b'user ' + self.mail_name + b'\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)

        # send PASSWORD
        client_socket.send(b'pass ' + self.mail_pass + b'\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)
        client_socket.close()
        return recv1

    def receive_mail_list(self, i):
        # Email message
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket = ssl.wrap_socket(client_socket)

        # Client socket
        # Establish TCP connection with mail server
        client_socket.connect((self.mail_server, self.port_num))
        recv = client_socket.recv(1024)
        print(recv)

        # send USERNAME
        client_socket.send(b'user '+self.mail_name+b'\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)

        # send PASSWORD
        client_socket.send(b'pass ' + self.mail_pass+b'\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)

        # get the mail summary
        client_socket.send(b'stat\r\n')
        recv1 = client_socket.recv(1024)
        temp = recv1.split(b' ')
        cout = temp[1]
        length = temp[2]

        count = 0
        result = []
        for mail_headers in range(int(bytes.decode(cout)), int(bytes.decode(cout))-4, -1):
            client_socket.send(b'retr '+bytes(str(mail_headers), encoding='utf8')+b'\r\n')
            recv1 = client_socket.recv()
            tmp = ''
            while True:
                recv1 = client_socket.recv()
                recv1 = str(recv1, encoding='utf-8')
                tmp = tmp + recv1
                print(recv1)
                if recv1[-3] == '.':
                    print(tmp)
                    result.append(tmp)
                    break
            count += 1
            if count == i:
                break
        client_socket.close()
        return result
        #return count

