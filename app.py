from flask import Flask, session, redirect, url_for, g
from flask import render_template
from flask import request
from UserAgentReceiver import *
from UserAgentSender import *
import email
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import string

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/loginpage')
def loginpage():
    agent_list = []
    if 'list_num' not in session:
        session['list_num'] = 0
    else:
        (agent_list, red) = generate_check_agent_list(session)
    return render_template('about.html', error=0, agent_list=agent_list)


def generate_check_agent_list(session, key=None):
    agent_list = []
    agent_num = []
    red = False
    if 'server1' in session:
        agent_list.append(session['server1'])
        if session['server1']['mail_address'] == key:
            red = True
        agent_num.append(1)
    if 'server2' in session:
        agent_list.append(session['server2'])
        if session['server2']['mail_address'] == key:
            red = True
        agent_num.append(2)
    if 'server3' in session:
        agent_list.append(session['server3'])
        if session['server3']['mail_address'] == key:
            red = True
        agent_num.append(3)
    if 'server4' in session:
        agent_list.append(session['server4'])
        if session['server4']['mail_address'] == key:
            red = True
        agent_num.append(4)
    if 'server5' in session:
        agent_list.append(session['server5'])
        if session['server5']['mail_address'] == key:
            red = True
        agent_num.append(5)
    tmp = 0
    if len(agent_num) != 0:
        for i in agent_num:
            tmp += 1
            session['server'+str(tmp)] = session['server'+str(i)]
            if tmp != i:
                session.pop('server'+str(i))
    session['list_num'] = tmp
    return agent_list, red


@app.route('/logout/<name>', methods=['post'])
def logout(name):
    session.pop(name)
    return redirect(url_for('loginpage'))


@app.route('/redirect', methods=['post'])
def redirect_to_new_url():
    smtp_server = request.form['smtp_server']
    smtp_port = request.form['smtp_port']
    pop_port = request.form['pop_port']
    pop_server = request.form['pop_server']
    mail_address = request.form['mail_address']
    password = request.form['password']
    agent_list = generate_check_agent_list(session, key=None)
    if smtp_server == '' or smtp_port == '' or pop_port == '' or pop_server == '' or mail_address == '' or password == '':
        return render_template('about.html', error=1, agent_list=agent_list)

    useragentsender = MailReceiver(bytes(pop_server, encoding='utf8'), bytes(mail_address, encoding='utf8'),
                                   bytes(password, encoding='utf8'), int(pop_port))
    useragentreceiver = MailSender(bytes(smtp_server, encoding='utf8'), bytes(mail_address, encoding='utf8'),
                                   bytes(password, encoding='utf8'), int(smtp_port))
    check_smtp = True
    check_pop = True
    sender = useragentsender.check_mill_address()
    if sender[:3] != b'+OK':
        check_pop = False
    if useragentreceiver.check_mail_address() != b'220':
        check_smtp = False

    if (not check_pop) or (not check_smtp):
        return render_template('about.html', error=2, agent_list=agent_list)

    server_dict = {'smtp_server':smtp_server, 'smtp_port':smtp_port, 'pop_port':pop_port, 'pop_server':pop_server,
                   'mail_address':mail_address, 'password':password}

    (agent_list, red) = generate_check_agent_list(session, server_dict['mail_address'])
    if not red:
        indx = session['list_num']+1
        session['server'+str(indx)] = server_dict
    return redirect(url_for('loginpage'))


@app.route('/writepage')
def writepage():
    (agent_list, red) = generate_check_agent_list(session)
    return render_template('contact.html', agent_list=agent_list)



@app.route('/writeredrict', methods=['post'])
def writeredrict():
    name = request.form['name']
    mail_address = request.form['mail_address']
    subject = request.form['subject']
    message = request.form['message']
    (server_dict, tp) = find_the_server(session, mail_address)

    useragentsender = MailSender(bytes(server_dict['smtp_server'], encoding='utf8'), bytes(server_dict['mail_address'], encoding='utf8'),
                                   bytes(server_dict['password'], encoding='utf8'), int(server_dict['smtp_port']), bytes(name, encoding='utf8'),
                                   bytes(subject, encoding='utf8'), bytes(message, encoding='utf8'))

    useragentsender.send_mail()
    (agent_list, red) = generate_check_agent_list(session)
    return render_template('contact.html', agent_list=agent_list)


def find_the_server(session, mail_address):
    server_num = session['list_num']
    for i in range(server_num):
        i += 1
        if session['server'+str(i)]['mail_address'] == mail_address:
            return session['server'+str(i)], i
    return None


@app.route('/readpage/<int:i>')
def readpage(i):
    (agent_list, red) = generate_check_agent_list(session)
    if len(agent_list) == 0:
        return "请先输入至少一个邮箱账号（建议QQ邮箱）"
    server_dict1 = agent_list[i]
    useragentreceiver = MailReceiver(bytes(server_dict1['pop_server'], encoding='utf8'),
                                     bytes(server_dict1['mail_address'], encoding='utf8'),
                                     bytes(server_dict1['password'], encoding='utf8'), int(server_dict1['pop_port']))
    contents = useragentreceiver.receive_mail_list(5)
    result = []
    for content in contents:
        msg = email.message_from_string(content)
        tmp_result = {}
        tmp_result = print_info(msg, tmp_result)
        result.append(tmp_result)

    return render_template('gallery.html', mail_list=result, agent_list = agent_list)


@app.route('/readredirct', methods=['post'])
def readredirct():
    mail_address = request.form['mail_address']
    (choice, i) = find_the_server(session, mail_address)
    return redirect(url_for('readpage', i=i-1))



def print_info(msg,  result, indent=0):
    if indent == 0:
        # 邮件的From, To, Subject存在于根对象上:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header=='Subject':
                    # 需要解码Subject字符串:
                    value = decode_str(value)
                else:
                    # 需要解码Email地址:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            if value == '':
                value = '...'
            result[header] = value

    if (msg.is_multipart()):
        # 如果邮件对象是一个MIMEMultipart,
        # get_payload()返回list，包含所有的子对象:
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            if 'text' not in result:
                result['text'] = ''
            result['text'] += ('%spart %s' % ('  ' * indent, n))
            # 递归打印每一个子对象:
            result = print_info(part, result, indent + 1)
    else:
        # 邮件对象不是一个MIMEMultipart,
        # 就根据content_type判断:
        content_type = msg.get_content_type()
        if content_type=='text/plain' or content_type=='text/html':
            # 纯文本或HTML内容:
            content = msg.get_payload(decode=True)
            # 要检测文本编码:
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            if 'text' not in result:
                result['text'] = ''

            result['text'] += ('%sText: %s' % ('  ' * indent, content))
        else:
            # 不是文本,作为附件处理:
            if 'attach' not in result:
                result['attach'] = ''
            result['attach'] += ('%sAttachment: %s' % ('  ' * indent, content_type))

    return result


def guess_charset(msg):
    # 先从msg对象获取编码:
    charset = msg.get_charset()
    if charset is None:
        # 如果获取不到，再从Content-Type字段获取:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode('gb18030', 'ignore')
    return value



if __name__ == '__main__':
    app.run()
