# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 20:34:18 2018

Error Modules

@author: Usagi
"""

'''This module was devised to manage all errors from the main and vinculed
classes, mainly it will harbor all message box and each one specifics, but
any future error that need a more thoughout management, will be adressed here'''

from PyQt5.QtWidgets import (QMessageBox)
import logging
# from PyQt5.QtCore import pyqtSlot, QCoreApplication, Qt

logger = logging.getLogger(__name__)

# each error code is given simply by cronological order
class gd_errors():
    # this error will prompt if something happens during server connection
    def db_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("01: Banco de Usuários não encontrado!")
        error.setWindowTitle("Banco não encontrado")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 01: Banco de Usuários não encontrado.")

    # unnused
    # def preen_error(self):
    #    error = QMessageBox()
    #    error.setIcon(QMessageBox.Critical)
    #    error.setText("Ao menos um dos campos deve ser preenchido!")
    #    error.setWindowTitle("Erro de Preenchimento")
    #    error.setStandardButtons(QMessageBox.Ok)
    #    error.exec_()

    # this errors will prompt if the user didn't fill an username or email or
    # the login don't exist in the users DB
    def rec_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("02: Campos não preenchidos corretamente ou informações não encontradas!")
        error.setWindowTitle("Erro de Preenchimento")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 02: Campos não preenchidos corretamente ou informações não encontradas.")

    # this errors will prompt if the user didn't fill all the spaces
    def reg_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("03: Todos os campos são obrigatórios!")
        error.setWindowTitle("Erro de Preenchimento")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 03: Todos os campos são obrigatórios.")

    # this errors will prompt if the attempted login is already taken
    def reg_nf_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("04: Login já cadastrado, por favor tente outro.")
        error.setWindowTitle("Login já cadastrado")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 04: Login já cadastrado")

    # this error will prompt if the attempted registering information is considered a badword
    def reg_bw_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("05: Palavra maliciosa identificada, registro negado.")
        error.setWindowTitle("Parametros considerados maliciosos")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 05: Palavra maliciosa identificada, registro negado.")

    # this error will prompt if, at login, the login don't exist or is left blank
    def login_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("06: Usuário não encontrado ou em branco.")
        error.setWindowTitle("Usuário não encontrado.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 06: Usuário não encontrado ou em branco.")

    # this error will prompt if the login and password doesn't match
    def userpass_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("06: Usuário e senha não batem, tente novamente.")
        error.setWindowTitle("Usuário e senha não batem")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 06: Usuário e senha não batem")

    # this error will prompt if something bad happens when sending the pw recovery mail
    # although this error is a bit generic, theres 4 or 5 errors that could trigger this
    def email_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("07: Error ao enviar email, tente novamente.")
        error.setWindowTitle("Erro ao enviar email.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 07: Error ao enviar email")

    def inv_email(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("08: Email inválido, teste outro")
        error.setWindowTitle("Erro ao enviar email.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 07: Error ao enviar email")

    def serv_opt_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("08: Informações do servidor estão incompletas ou incorretas, não será possível conectar ao servidor.")
        error.setWindowTitle("Informações incompletas.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 08: Informações incompletas/incorretas.")

    def email_opt_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("09: Informações de email estão incompletas ou incorretas, não será possível registrar o email.")
        error.setWindowTitle("Informações incompletas.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 09: Informações incompletas/incorretas.")

    def conn_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("10: Erro de conexão.")
        error.setWindowTitle("Informações incompletas.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 10: Erro de conexão.")

    def smtp_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("11: SMTP não identificado. Utilize um dos provedores suportados")
        error.setWindowTitle("SMTP não identificado.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 11: Erro de conexão.")

    def conn_error_flag(self, _type):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)

        if _type == "user":
            error.setText("12: Login/endereço do servidor de usuários inválido, corrija e reinicie o programa.")
        elif _type == "sampat":
            error.setText("12: Login/endereço do servidor principal invalido, corrija e reinicie o programa.")

        error.setWindowTitle("Erro ao criar sessão.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 12: Erro ao criar sessão.")

    def res_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("13: Erro ao reiniciar aplicativo.")
        error.setWindowTitle("Erro ao reiniciar aplicativo.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 13: Erro ao reiniciar aplicativo.")

    def id_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("14: ID não pode ser vazio.")
        error.setWindowTitle("ID não pode ser vazio.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 14: ID não pode ser vazio.")

    def unlogged_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("15: Função apenas para registrados.")
        error.setWindowTitle("Necessário realizar login para acessar.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 15: Função apenas para registrados.")

    def wrong_access_level_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("16: Ação limitada pelo nível de acesso.")
        error.setWindowTitle("Login sem permissão para esta atividade.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 16: Ação limitada pelo nível de acesso.")

    def fk_error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("17: Lembre-se de cadastrar sempre na ordem Paciente -> Amostra -> Exame, para manter a integridade do banco de dados.")
        error.setWindowTitle("Erro de ID/Integridade.")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - 17: Erro de ID/Integridade.")

    def custom_error(self, err):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText(err)
        error.setWindowTitle(err)
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
        logger.error("ERROR - X: Erro/Teste")
