# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 16:24:56 2018

@author: Usagi
"""
'''the recmail module utilizes the smtlib, mimetext and random module to create
a random password and send it via an email'''

import smtplib
from email.mime.text import MIMEText
import random
import logging

logger = logging.getLogger(__name__)

# generate a random 8 character password
def pass_gen():
    """[generates random password]

    Returns:
        [string]: [random password]
    """
    pass_len = 8
    alf = "abdefghojklmnopqrstuwvxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    logger.info("Senha aleatória gerada.")
    return ''.join(random.sample(alf, pass_len))

def check_smtp(email):
    """[check if smtp from string email is valid]

    Args:
        email ([string]): [email adress]

    Raises:
        KeyError: [in case the email inputed is not accounted for]

    Returns:
        [string]: [provider]
    """
    smtp_dict = {"gmail": ['smtp.gmail.com', 587],
                 "yahoo": ['smtp.mail.yahoo.com', 465],
                 "hotmail": ['smtp.live.com', 587]}

    for key in smtp_dict.keys():
        if key in email:
            return smtp_dict[key]
        else:
            raise KeyError("Key Not Found")

# organizes all the info needed for an email and send to the passed email
def send_email(login, sobrenome, email, emailpass):
    """[send email with random password to user]

    Args:
        login ([string]): [login string]
        sobrenome ([string]): [surname string]
        email ([string]): [email adress]
        emailpass ([string]): [random password generated]

    Returns:
        [string]: [random password]
    """
    login = str(login)
    sobrenome = str(sobrenome)
    email = str(email)

    pw = pass_gen()

    email_body = "Olá Sr(a). {}!\n\nUma nova senha de acesso foi solicitada para o login '{}'." \
                 "Caso você não tenha solicitado uma nova senha, ignore este email (recomendamos trocar de senha). " \
                 "Caso tenha sido você mesmo a solicitar uma nova senha de acesso, use a senha gerada abaixo:" \
                 "\n\n{}\n\nSolicitamos que a senha seja alterada mediante o próximo login de acesso.\n\n" \
                 "Agradecidamente, Administrador do Project GD.".format(sobrenome, login, pw)

    msg = MIMEText(email_body)
    me = emailpass[0]
    spw = emailpass[1]

    msg['Subject'] = "Project GD - Nova senha requisitada"
    msg['From'] = me
    msg['To'] = email

    try:
        smtp = check_smtp(me)
    except KeyError as SMTP_ERROR:
        return SMTP_ERROR

    em_sender = smtplib.SMTP(smtp[0], smtp[1])
    em_sender.starttls()

    logger.debug("SMTP Protocol: {}".format(em_sender))
    # try to connect to the gmail and send the email, the errors reflects at
    # what stage the error ocurred
    try:
        em_sender.login(me, spw)
        em_sender.sendmail(me, [email], msg.as_string())
    except smtplib.SMTPNotSupportedError as SMTP_NSE:
        logger.error("SMTP Protocol not supported")
        return SMTP_NSE
    except smtplib.SMTPAuthenticationError as SMTP_AE:
        logger.error("Email login / password denied.")
        return SMTP_AE
    except smtplib.SMTPConnectError as SMTP_CE:
        logger.error("Email login / password denied.")
        return SMTP_CE
    finally:
        logger.info("Quitting email protocol.")
        em_sender.quit()

    # return the random password to be updated in the database
    logger.info("RECMAIL - Returning random password")
    return pw
