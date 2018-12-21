from socket import *
import ssl
import base64


class MailSender:
    endmsg = b'\r\n.\r\n'

    def __init__(self, mail_server, from_mail, code, port_num=465,  to_mail=None, mail_subject=None, mail_content=None):
        self.mail_server = mail_server
        self.from_mail = from_mail
        self.code = code
        self.to_mail = to_mail
        self.mail_content = mail_content
        self.mail_subject = mail_subject
        self.port_num = port_num

    def check_mail_address(self):
        # Email message
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket = ssl.wrap_socket(client_socket)

        # Client socket
        # Establish TCP connection with mail server
        client_socket.connect((self.mail_server, self.port_num))
        recv = client_socket.recv(1024)
        print(recv)
        if recv[:3] != b'220':
            client_socket.close()
            return recv[:3]

        # Send HELO command and print server response.
        hello_command = b'EHLO localhost\r\n'
        client_socket.send(hello_command)
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'250':
            client_socket.close()
            return recv[:3]

        # start the TLS
        client_socket.send(b'STARTTLS a\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)

        # Authenticate.
        client_socket.send(b'AUTH LOGIN\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'334':
            client_socket.close()
            return recv[:3]

        # Send the id
        self.from_mail = base64.b64encode(self.from_mail)
        client_socket.send(self.from_mail + b'\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'334':
            client_socket.close()
            return recv[:3]

        self.code = base64.b64encode(self.code)
        client_socket.send(self.code + b'\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)
        client_socket.close()
        return recv[:3]

    def send_mail(self):
        mail_content = b'From: wz <'+self.from_mail+b'>\r\n' \
                       b'To: <' + self.to_mail + b'>\r\n' \
                       b'Subject: ' + self.mail_subject+b'\r\n\r\n' \
                       + self.mail_content

        # Email message
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket = ssl.wrap_socket(client_socket)

        # Client socket
        # Establish TCP connection with mail server
        client_socket.connect((self.mail_server, self.port_num))
        recv = client_socket.recv(1024)
        print(recv)
        if recv[:3] != b'220':
            client_socket.close()
            return recv[:3]

        # Send HELO command and print server response.
        hello_command = b'EHLO localhost\r\n'
        client_socket.send(hello_command)
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'250':
            client_socket.close()
            return recv1[:3]

        # start the TLS
        client_socket.send(b'STARTTLS a\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)

        # Authenticate.
        client_socket.send(b'AUTH LOGIN\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'334':
            client_socket.close()
            return recv1[:3]

        # Send the id
        from_mail1 = base64.b64encode(self.from_mail)
        client_socket.send(from_mail1 + b'\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'334':
            client_socket.close()
            return recv1[:3]

        self.code = base64.b64encode(self.code)
        client_socket.send(self.code + b'\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'235':
            client_socket.close()
            return recv1[:3]

        # send MAIL FROM

        client_socket.send(b'MAIL FROM: <' + self.from_mail + b'>\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'250':
            client_socket.close()
            return recv1[:3]

        # send RCPT TO
        client_socket.send(b'RCPT TO:<' + self.to_mail + b'>\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'250':
            client_socket.close()
            return recv1[:3]

        # send DATA to start the mail content
        client_socket.send(b'DATA\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'354':
            client_socket.close()
            return recv1[:3]

        # the mail content
        client_socket.send(mail_content + self.endmsg)
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'250':
            client_socket.close()
            return recv1[:3]

        # send QUIT to exit
        client_socket.send(b'QUIT\r\n')
        recv1 = client_socket.recv(1024)
        print(recv1)
        if recv1[:3] != b'221':
            client_socket.close()
            return recv1[:3]

        client_socket.close()
        return b'200'
