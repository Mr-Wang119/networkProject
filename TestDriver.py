from UserAgentReceiver import *

mail_server = b'pop.qq.com'
mail_name = b'714570199@qq.com'
mail_pass = b'auhctrvatgifbdcd'

mailReceiver = MailReceiver(mail_server, mail_name, mail_pass)
mailReceiver.receive_mail_list()
