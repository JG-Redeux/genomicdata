# -*- coding: utf-8 -*-
"""
Spyder Editor

Este é um arquivo de script temporário.
"""
'''this is simply the "main" module which will define the software as a whole,
if any group or class became to complex or to extense (and while not being inside the
"main" concept, it will be made into a module apart)'''

import sys, os, subprocess
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QAction, QMessageBox,
                             QLineEdit, QLabel, QPushButton, QGridLayout, QStackedLayout,
                             QDialog, QGroupBox, QFormLayout, QComboBox, QDialogButtonBox,
                             QVBoxLayout, QTextBrowser, QHBoxLayout, QStackedWidget,
                             QStatusBar, QListWidget, QSpacerItem, QPlainTextEdit, QFileDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import (QIcon, QPalette, QPixmap, QFont)
from PyQt5.QtCore import (pyqtSlot, QCoreApplication, Qt, pyqtSignal, QObject,
                          QSettings, QTimer, QSignalMapper, QProcess)
from datetime import datetime
import recmail, sqlmng, errorex, _logger
import auxiliary as aux

absfilepath = os.path.abspath(__file__)

class Configurations(QSettings):
    
    def __init__(self):
        super(Configurations, self).__init__()
        self.gd_settings = QSettings('Laboratorio de Citogenomica', "Project GD")
        self.gd_settings.Scope(0)
            
    def add_registry(self, group, value_name, value):
        try:
            self.gd_settings.beginGroup(group)
            self.gd_settings.setValue("{}".format(value_name), value)
            self.gd_settings.endGroup()
            logger.debug("{}/{}".format(group, value_name))
            logger.info("CONFIGS - New {} settings registered.".format(group))
        except NameError:
            pass
        except:
            self.gd_settings.status()
            logger.warning(self.gd_settings.status())
    
    def load_registry(self, group, value_name):
        try:
            value = self.gd_settings.value("{}/{}".format(group, value_name))
            return value
        except:
            self.gd_settings.status()
            logger.warning(self.gd_settings.status())

    def _keys(self):
        return self.gd_settings.allKeys()
    
class Spacer(QWidget):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
    def spacer(self):
        self.spacer = QSpacerItem(self.width, self.height)
        return self.spacer

#this class will maintain all the aspects of the current logged user, to exclude
#the necessity of calling the database all the time after the login, the big string
#inside the classe keeps being valid
class User():
    ''' The access_dict is supossed to work as a main driver for wich acess level
        the u"ser will be granted: 0 for dev mode (total access); 1 for total
        core functions acess; 2 for partial acess (input data and visualizations);
        3 (lowest level) for very restricted acess (visualization only)'''
        
    def __init__(self, login_info):
        self.login = login_info[0][1]
        self.pw = login_info[1][1]
        self.pname = login_info[2][1]
        self.sname = login_info[3][1]
        self.nvl = login_info[4][1]
        self.other =  login_info[5][1]
        self.email = login_info[6][1]
        self.access_dict = {"adm": -1, "Analista": 0, "Aluno": 1, "Outros": 2}
        
        logger.info("USER - {} instance of User class created".format(self.login))
        
#One of the layouts of the main window
class Unlogged_window(QWidget):
    
    def __init__(self, parent=None):
        super(Unlogged_window, self).__init__(parent)
        layout = QGridLayout()
        ulabel = QLabel("unlog")
        layout.addWidget(ulabel)
            
        self.setLayout(layout)
        
#One of the layouts of the main window        
class Logged_window(QWidget):
    
    def __init__(self, parent=None):
        super(Logged_window, self).__init__(parent)
        layout = QHBoxLayout()
        ilabel = QLabel("inlog")
        layout.addWidget(ilabel)
        self.setLayout(layout)
        
        #self.ubutton.clicked.connect(self.clicked.emit)

#where the magic happens        

class App(QMainWindow):
    def __init__(self, parent = None):
        super(App, self).__init__(parent)
        self.title = "Project GD"
        self.left = 100
        self.top = 100
        self.height = 400
        self.width = 600
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMaximumSize(screen.size())
        
        self.menu_bar()    
        self.sbar = QStatusBar()
        self.setStatusBar(self.sbar)
        
        self.opt_dialog = Options()
        self.reg_dialog = Register()
        self.log_dialog = Login()
        self.pat_dialog = Patients()
        self.samp_dialog = Samples()
        self.info_dialog = Info()
                
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.unlog = Unlogged_window(self)
        self.inlog = Logged_window(self)
        
        self.central_widget.addWidget(self.unlog)
        self.central_widget.addWidget(self.inlog)
        self.central_widget.setCurrentWidget(self.unlog)
        
        #create an User instance of the current logged user
        self.log_dialog.login_info.connect(self.define_user)
        
        #change layouts
        self.log_dialog.login_signal.connect(self.change_cwidget)
        self.manage_layout()
        
        self.show()
    
    #create the User instance and initiate the update info window
    #also set the status bar
    def define_user(self, login_info):
        self.user = User(login_info)
        self.upd_dialog = Update(self.user)
        nvl_str = "Usuário: {} | Nível: {}".format(self.user.sname, self.user.nvl)
        logger.info("APP - {} permission '{}' defined".format(self.user.login, self.user.nvl))
        self.nvl_status = QLabel(nvl_str)
        self.sbar.addPermanentWidget(self.nvl_status)
        
    #change the current widget on signal
    def change_cwidget(self):
        self.central_widget.setCurrentWidget(self.inlog)
        self.manage_layout()
    
    #hide/show able/disable widgets
    def manage_layout(self):
        self.layout_index = self.central_widget.currentIndex()
        
        if self.layout_index == 0:
            logger.info("APP - Current widget changed: {}".format(0))
            logger.debug("APP - {}".format(self.layout_index))
            self.setWindowTitle("Deslogado")
            self.toolsMenu.setEnabled(True)
            self.switch_user.setVisible(False)
            self.update_user.setVisible(False)
            self.delete_user.setVisible(False)
            self.logoff.setVisible(False)
            self.loginDiag.setVisible(True)
            self.regDiag.setVisible(True)
            self.opt_dialog.opt_list.item(3).setHidden(True)
            
            try:
                self.sbar.removeWidget(self.nvl_status)
            except AttributeError:
                pass
            
        elif self.layout_index == 1:
            logger.info("APP - Current widget changed: {}".format(1))
            logger.debug("APP - {}".format(self.layout_index))
            self.setWindowTitle("Logado")
            self.toolsMenu.setEnabled(True)
            self.switch_user.setVisible(True)
            self.update_user.setVisible(True)
            self.delete_user.setVisible(True)
            self.logoff.setVisible(True)
            self.loginDiag.setVisible(False)
            self.regDiag.setVisible(False)
            self.opt_dialog.opt_list.item(3).setHidden(False)
        
    #defines the top menu bar
    def menu_bar(self):
        ## top menu defnition        
        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu('Arquivo')
        self.toolsMenu = self.mainMenu.addMenu('Ferramentas')
        self.helpMenu = self.mainMenu.addMenu('Ajuda')

        ##login sub-menu dialog
        self.loginDiag = QAction('&Login', self)
        self.loginDiag.triggered.connect(self.login_open)
        
        self.regDiag = QAction('&Registro', self)
        self.regDiag.triggered.connect(self.register_open)
                
        self.update_user = QAction('&Atualizar Cadastro', self)
        self.update_user.triggered.connect(self.update_open)
        
        self.delete_user = QAction('&Deletar Conta', self)
        self.delete_user.triggered.connect(self.acc_delete)
        
        self.switch_user = QAction('&Trocar de Usuário', self)
        self.switch_user.triggered.connect(self.change_user)
        
        self.logoff = QAction('&Sair da Conta', self)
        self.logoff.triggered.connect(self.logout_msg)
        
        self.loginMenu = self.fileMenu.addMenu('Usuários')
        self.loginMenu.addAction(self.loginDiag)
        self.loginMenu.addAction(self.logoff)
        self.loginMenu.addAction(self.regDiag)
        self.loginMenu.addAction(self.switch_user)
        self.loginMenu.addAction(self.update_user)
        self.loginMenu.addAction(self.delete_user)
        
        ##Ferramentas sub-menu dialog

        self.search_db = QAction('&Busca de dados', self)
        #self.search_db.triggered.connect(self.)
        #self.search_db.setEnabled(False)
        
        self.priority_db = QAction('&Prioridades', self)
        #self.priority_db.triggered.connect(self.register_open)
        #self.priority_db.setEnabled(False)
        
        self.patient_db = QAction('&Banco de Pacientes', self)
        self.patient_db.triggered.connect(self.patdb_open)
        self.patient_db.setEnabled(True)
        
        self.sample_db = QAction('&Banco de Amostras', self)
        self.sample_db.triggered.connect(self.smpdb_open)
        self.sample_db.setEnabled(True)
        
        self.info_db = QAction('&Informações', self)
        self.info_db.triggered.connect(self.info_open)
        self.info_db.setEnabled(True)
        
        self.opt_menu = QAction('&Configurações', self)
        self.opt_menu.triggered.connect(self.options_open)
        
        self.toolsMenu.addAction(self.priority_db)
        self.toolsMenu.addAction(self.search_db)
        self.toolsMenu.addAction(self.patient_db)
        self.toolsMenu.addAction(self.sample_db)
        self.toolsMenu.addAction(self.opt_menu)
        self.toolsMenu.addAction(self.info_db)
        
        ## quit sub-menu definition
        self.closeApp = QAction('&Sair', self)
        self.closeApp.triggered.connect(self.close)
                    
        ##file menu sub-menus
        self.fileMenu.addAction(self.closeApp)
                
        ##help menu sub-menus
        self.helpMenu.addAction('Sobre')
        self.helpMenu.addAction('Contato')
    
    #message box for logout confirmation
    def logout_msg(self, event):
        lout = QMessageBox()
        lout.setText("Deseja mesmo sair?")
        lout.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        lout = lout.exec()
        
        if lout == QMessageBox.Yes:
            self.logout()
    
    #the logout method makes logout, change the layout and delete the actual
    #User class instance
    def logout(self):
        logger.info("APP - {} instance of Class user deleted.".format(self.user.login))
        logger.info("APP - {} made loggout.".format(self.user.login))
        del self.user
        self.central_widget.setCurrentWidget(self.unlog)
        self.manage_layout()
        
    #method that apply the logout and recalls the login dialog, for quickies
    def change_user(self, event):
        cuser = QMessageBox()
        cuser.setText("Deseja mesmo trocar de usuário?")
        cuser.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        cuser = cuser.exec()
        
        if cuser == QMessageBox.Yes:
            logger.info("APP - User changed.")
            self.logout()
            self.log_dialog.show()
    
    #quit confirmation, closes the entire app
    def closeEvent(self, event):
        close = QMessageBox()
        close.setText("Tem certeza?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()
        
        if close == QMessageBox.Yes:
            logger.info("APP - Program closed")
            try:
                sampat_psql.close_conn(dsess)
                user_psql.close_conn(usess)
            except:
                pass
            close_all = QCoreApplication.instance()
            close_all.closeAllWindows()
        else:
            event.ignore()
    
    #open the update info widget
    def update_open(self):
        logger.info("APP - Dialog dialog screen opened.")
        self.upd_dialog.show()
    
    #open the login widget
    def login_open(self):
        logger.info("APP - Login dialog screen opened.")
        self.log_dialog.show()
        
    #open the register widget
    def register_open(self):
        logger.info("APP - Register dialog screen opened")
        self.reg_dialog.show()
    
    def options_open(self):
        try:
            logger.info("APP - {} entered option screen".format(self.user.login))
        except:
            logger.info("APP - Non-identified user entered option screen")
        self.opt_dialog.show()
    
    def patdb_open(self):
        logger.info("APP - Patient DB dialog screen opened")
        self.pat_dialog.show()
        
    def smpdb_open(self):
        logger.info("APP - Samples DB dialog screen opened")
        self.samp_dialog.show()
        
    def info_open(self):
        logger.info("APP - Info dialog screen opened")
        self.info_dialog.show()
        
    #delete the current acc, it should ask for password at some point
    def acc_delete(self, event):
        adel = QMessageBox()
        adel.setText("Deseja mesmo deletar a conta?")
        adel.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        adel = adel.exec()
        
        if adel == QMessageBox.Yes:
            logger.info("APP - {} entry in SQL deleted".format(self.user.login))
            user_psql.delete_user(usess, self.user.login, ident = False)
            self.central_widget.setCurrentWidget(self.unlog)
            self.manage_layout()

#defines the login window
class Login(QDialog):
    
    #set custom signals
    login_signal = pyqtSignal()
    login_info = pyqtSignal(list)
    
    def __init__(self):
        super(Login, self).__init__()
        self.title = "Project GD Login"
        self.left = 100
        self.top = 100
        self.height = 150
        self.width = 400
        
        self.setFixedSize(400,150)

        #create the layout widget
        self.create_login_layout()
        
        #Set stacked layout
        self.login_layout = QVBoxLayout()
        self.login_layout.addWidget(self.login_widget)
        self.setLayout(self.login_layout)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)      
        
    def create_login_layout(self):
        #window elements
        self.user_label = QLabel('Usuário:')
        self.pw_label = QLabel('Senha:')
        
        self.reg_label = QLabel("Não tem cadastro? Registre-se!")
        self.reg_label.setStyleSheet('color: blue')
        self.reg_label.mouseReleaseEvent = self.register_open
        
        self.rec_label = QLabel("Esqueceu a senha? Recupere-a!")
        self.rec_label.setStyleSheet('color: blue')
        self.rec_label.mouseReleaseEvent = self.rec_password
        
        self.user_line_edit = QLineEdit()
        self.pw_line_edit = QLineEdit()
        self.pw_line_edit.setEchoMode(QLineEdit.Password)
        
        self.login_pbutton = QPushButton('Login')
        self.login_pbutton.clicked.connect(self.login_confirm)
        
        #create grids
        self.login_grid = QGridLayout()
        self.login_grid.setSpacing(20)
        self.login_form_grid = QGridLayout()
        self.login_form_grid.setSpacing(10)
        self.qlabels_login_grid = QGridLayout()
        self.qlabels_login_grid.setSpacing(5)
        
        #adding elements to form grid
        self.login_form_grid.addWidget(self.user_label, 0,0)
        self.login_form_grid.addWidget(self.pw_label, 1,0)
        self.login_form_grid.addWidget(self.user_line_edit, 0,1)
        self.login_form_grid.addWidget(self.pw_line_edit, 1,1)
 
        #adding elements to qlabels grid
        self.qlabels_login_grid.addWidget(self.reg_label, 1,0)
        self.qlabels_login_grid.addWidget(self.rec_label, 2,0)
        
        #adding elements to login grid
        self.login_grid.addLayout(self.login_form_grid, 0,1)
        self.login_grid.addWidget(self.login_pbutton, 1,1)
        self.login_grid.addLayout(self.qlabels_login_grid, 1,0)
        
        #create widget to display layout
        self.login_widget = QWidget()
        self.login_widget.setLayout(self.login_grid)
    
    #check with the server if the login/pw matches
    def login_confirm(self, event):
        logger.debug("APP - event: {}.".format(event))
        
        quser = self.user_line_edit.text()
        qpass = self.pw_line_edit.text()
        
        query = user_psql.query_user(usess, quser, user = True, scalar = False)
        qlist = []
        
        for item in str(query).split(","):
            qlist.append(item.split("="))
        
        if query == "SQLAlchemyError":
            gerrors.serv_opt_error()
        elif query == None:
            gerrors.login_error()
        else:
            if qlist[0][1] == quser and qlist[1][1] == qpass:
                self.login_signal.emit()
                self.login_info.emit(qlist)
                logger.info("APP - {} logged.".format(quser))
                logger.debug("APP - Signal emit: {}.".format(self.login_signal))
                logger.debug("APP - Info emit: {}.".format(self.login_info))
                self.close()
            elif qlist[0][1] == quser and not qlist[1][1] == qpass:
                gerrors.userpass_error()
    
    #open the password recovery widget
    def rec_password(self, event):
        self.rec_label.setStyleSheet('color: purple')
        self.dialog = Recovery()
        self.dialog.show()
    
    #open the registration widget
    def register_open(self, event):
        self.reg_label.setStyleSheet('color: purple')
        self.dialog = Register()
        self.dialog.show()
        
#defines the recovery window
class Recovery(QDialog):
    
    def __init__(self):
        super(Recovery, self).__init__()
        #self.setFixedSize(400,150)
        self.create_rec_box()
        
        self.user_name.editingFinished.connect(self.check_db)
        self.email_ad.editingFinished.connect(self.check_db)
        
        self.rec_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.rec_buttonBox.accepted.connect(self.check_db)
        self.rec_buttonBox.rejected.connect(self.reject)
        
        recLayout = QVBoxLayout()
        recLayout.addWidget(self.rec_box)
        recLayout.addWidget(self.rec_buttonBox)
        
        self.setLayout(recLayout)
        
        self.setWindowTitle('Recuperação de Senha')
        
    def create_rec_box(self):
        self.rec_box = QGroupBox('Recuperação de Senha')
        rec_box_layout = QFormLayout()
        
        self.user_name = QLineEdit()
        rec_box_layout.addRow(QLabel('Usuário:'), self.user_name)
        
        self.or_label = QLabel('-- OU --')
        self.or_label.setAlignment(Qt.AlignLeft)
        rec_box_layout.addRow(self.or_label)
        
        self.email_ad = QLineEdit()
        rec_box_layout.addRow(QLabel('Email:'), self.email_ad)
        
        self.user_inex = QLabel('Usuário não encontrado!')
        self.user_inex.setStyleSheet('color: red')
        rec_box_layout.addRow(self.user_inex)
        self.user_inex.hide()
        
        self.email_inex = QLabel('Email não encontrado!')
        self.email_inex.setStyleSheet('color: red')
        rec_box_layout.addRow(self.email_inex)
        self.email_inex.hide()
        
        self.rec_box.setLayout(rec_box_layout)
    
    #check the provided infos and compares with the registred info
    def check_db(self):
        sender = self.sender()
        self.check_flag = False
        
        if sender == self.user_name or sender == self.rec_buttonBox:
            if user_psql.query_user(usess, self.user_name.text()):
                self.user_inex.hide()
                self.email_inex.hide()
                self.check_flag = True
            elif self.user_name.text() == "":
                pass
            else:
                self.email_inex.hide()
                self.user_inex.show()
        elif sender == self.email_ad or sender == self.rec_buttonBox:
            if user_psql.query_user(usess, self.email_ad.text()):
                self.email_inex.hide()
                self.user_inex.hide()
                self.check_flag = True
            elif self.email_ad.text() == "":
                pass
            else:
                self.user_inex.hide()
                self.email_inex.show()
            
        if sender == self.rec_buttonBox:
            if self.check_flag:
                self.confirm_rec_email()
                self.close()
            else:
                gerrors.rec_error()
    
    #send email with the new password        
    def confirm_rec_email(self):
        email = self.email_ad.text()
        user = self.user_name.text() 
        
        query = user_psql.query_user(usess, user, scalar = False)
        qlist = []
        
        for item in str(query).split(","):
            qlist.append(item.split("="))
        
        email_pass = System().sys_email()
        
        if qlist[0][1] == user or qlist[6][1] == email:
            new_pw = recmail.send_email(qlist[0][1], qlist[3][1], qlist[6][1], email_pass)
            if type(new_pw) == str:
                logger.info("RECOVERY - {} asked a new password.".format(user))
                user_psql.change_user_pw(usess, qlist[0][1], new_pw)
            else:
                gerrors.email_error()
        else:
            gerrors.rec_error()

#defines the update info window, its <almost> equal to the register window
class Update(QDialog):
     
    def __init__(self, user):
        super(Update, self).__init__()

        self.user = user
        self.update_user_box()
        
        self.nv_cb.currentTextChanged.connect(self.on_nv_cb_changed)
        
        upd_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        upd_buttonBox.accepted.connect(self.upd_confirm)
        upd_buttonBox.rejected.connect(self.reject)
        
        updLayout = QVBoxLayout()
        
        updLayout.addWidget(self.update_form_box)
        updLayout.addWidget(upd_buttonBox)
        updLayout.setSizeConstraint(3)
        
        self.setLayout(updLayout)
        self.setWindowTitle('Atualizar Cadastro')
        
    def update_user_box(self):
        self.update_form_box = QGroupBox("Atualizar Informações")
        form_layout = QFormLayout()
        
        self.p_name = QLineEdit()
        self.p_name.setText(self.user.pname)
        form_layout.addRow(QLabel('Primeiro Nome:'), self.p_name)
        
        self.sb_name = QLineEdit()
        self.sb_name.setText(self.user.sname)
        form_layout.addRow(QLabel('Sobrenome:'), self.sb_name)
        
        self.email_adress = QLineEdit()
        self.email_adress.setText(self.user.email)
        form_layout.addRow(QLabel('Email:'), self.email_adress)
        
        nv_cb_list = ['Analista', 'Técnico', 'Aluno', 'Outros']
        self.nv_cb = QComboBox()
        for item in nv_cb_list:
            self.nv_cb.addItem(item)
        nv_index = self.user.access_dict.get(self.user.nvl, 0)
        self.nv_cb.setCurrentIndex(nv_index)
        form_layout.addRow(QLabel('Nível:'), self.nv_cb)
        self.other_label = QLabel('Qual?')
        self.other_name = QLineEdit()
        
        if not nv_index == 2:
            self.other_label.hide()
            self.other_name.hide()
        
        self.other_name.setText(self.user.other)
        form_layout.addRow(self.other_label, self.other_name)
        
        self.login_name = QLineEdit()
        self.login_name.setText(self.user.login)
        form_layout.addRow(QLabel('Usuário'), self.login_name)
        
        self.pw = QLineEdit()
        self.pw.setText(self.user.pw)
        self.pw.setEchoMode(QLineEdit.Password)
        form_layout.addRow(QLabel('Senha:'), self.pw)
        
        self.update_form_box.setLayout(form_layout)
    
    #hides the other line edit if not needed
    def on_nv_cb_changed(self, value):
        if value == "Outros":
            self.other_label.show()
            self.other_name.show()
        else:
            self.other_label.hide()
            self.other_name.hide()
    
    #confirm the changes
    def upd_confirm(self):
        upd_conf = QMessageBox()
        upd_conf.setText("Salvar informações?")
        upd_conf.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        upd_conf = upd_conf.exec()
        
        if upd_conf == QMessageBox.Yes:
            self.save_form()
        else:
            self.reject()
    
    #actually send the new infos, if no badword is found, to the database
    def save_form(self):
        if self.other_name.text() == "" or self.other_name.text() == "None":
            other_name = None
        else:
            other_name = self.other_name.text()
            
        form_dict = {"login": self.login_name.text(), 
                     "password": self.pw.text(),
                     "name": self.p_name.text(),
                     "surname": self.sb_name.text(),
                     "nvl": self.nv_cb.currentText(),
                     "other_spec": other_name,
                     "email": self.email_adress.text()}
        
        for key, value in form_dict.items():
            if type(value) == str:
                form_dict[key] = value.strip()
                
        bad_flag = False
        
        for item in form_dict.values():
            if user_psql.query_user(usess, item, badword = True):
                bad_flag = True
        
        #the username var keeps track of the current login (in cases the user changes)
        username = self.user.login
        quser = user_psql.query_user(usess, form_dict["login"])
        
        if bad_flag:
            gerrors.reg_bw_error()
        elif "" in form_dict.values():
            gerrors.reg_error()
        elif not quser or form_dict["login"] == username:
            user_psql.update_user(usess, username, form_dict)
            logger.info("UPDATE - {} updated SQL entry".format(username))
            self.close()
        else:
            gerrors.reg_nf_error()

#defines the register widget - <almost identical, almost>
class Register(QDialog):
    
    def __init__(self):
        super(Register, self).__init__()
        
        self.create_form_group_box()
        
        self.nv_cb.currentTextChanged.connect(self.on_nv_cb_changed)
        
        reg_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        reg_buttonBox.accepted.connect(self.reg_confirm)
        reg_buttonBox.rejected.connect(self.reject)
        
        regLayout = QVBoxLayout()
        regLayout.addWidget(self.form_group_box)
        regLayout.addWidget(reg_buttonBox)
        regLayout.setSizeConstraint(3)
        self.setLayout(regLayout)
        
        self.setWindowTitle('Registro de Usuário')
        
    def create_form_group_box(self):
        self.form_group_box = QGroupBox('Registro de Usuário')
        form_layout = QFormLayout()
        
        self.p_name = QLineEdit()
        form_layout.addRow(QLabel('Primeiro Nome:'), self.p_name)
        
        self.sb_name = QLineEdit()
        form_layout.addRow(QLabel('Sobrenome:'), self.sb_name)
        
        self.email_adress = QLineEdit()
        form_layout.addRow(QLabel('Email:'), self.email_adress)
        
        nv_cb_list = ['Analista', 'Técnico', 'Aluno', 'Outros']
        self.nv_cb = QComboBox()
        for item in nv_cb_list:
            self.nv_cb.addItem(item)
        form_layout.addRow(QLabel('Nível:'), self.nv_cb)
        
        self.other_label = QLabel("Qual?")
        self.other_name = QLineEdit()
        form_layout.addRow(self.other_label, self.other_name)
        self.other_label.hide()
        self.other_name.hide()
        
        self.user_pass = QLineEdit()
        form_layout.addRow(QLabel('Usuário:'), self.user_pass)
        
        self.form_pass = QLineEdit()
        self.form_pass.setEchoMode(QLineEdit.Password)
        form_layout.addRow(QLabel('Senha:'), self.form_pass)
        
        self.form_group_box.setLayout(form_layout)
        
    def on_nv_cb_changed(self, value):
        if value == "Outros":
            self.other_label.show()
            self.other_name.show()
        else:
            self.other_label.hide()
            self.other_name.hide()
        
    def reg_confirm(self):
        reg_conf = QMessageBox()
        reg_conf.setText("Salvar informações?")
        reg_conf.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        reg_conf = reg_conf.exec()
        
        if reg_conf == QMessageBox.Yes:
            self.save_form()
        else:
            self.reject()
    
    def save_form(self):
        if self.other_name.text() == "" or "None":
            other_name = None
        else:
            other_name = self.other_name.text()
            
        form_dict = {"login": self.user_pass.text(), 
                     "password": self.form_pass.text(),
                     "name": self.p_name.text(),
                     "surname": self.sb_name.text(),
                     "nvl": self.nv_cb.currentText(),
                     "other_spec": other_name,
                     "email": self.email_adress.text(),
                     "date": str(datetime.now())}
        
        for key, value in form_dict.items():
            if type(value) == str:
                form_dict[key] = value.strip()
                
        bad_flag = False
        
        for item in form_dict.values():
            if user_psql.query_user(usess, item, badword = True):
                bad_flag = True
                
        if bad_flag:
            gerrors.reg_bw_error()
        elif "" in form_dict.values():
            gerrors.reg_error()
        elif not user_psql.query_user(usess, form_dict["login"]):
            logger.info("REGISTER - ({}, {}) created a new SQL entry".format(form_dict["login"], form_dict["name"]))
            user_psql.add_user(usess, form_dict)
            self.rec_sucess()
            self.close()
        else:
            gerrors.reg_nf_error()

    def rec_sucess(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Information)
        error.setText("Registro realizado com sucesso, realize o login.")
        error.setWindowTitle("Registro Realizado")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()        

class Patients(QDialog):
    def __init__(self):
        super(Patients, self).__init__()
        
        self.setWindowTitle("Banco de Pacientes")
        self.setGeometry(200, 200, 800, 500)  
        self.setMaximumSize(screen.size())

        
    def create_patientes_layout(self):
        pass
    
class Samples(QDialog):
     def __init__(self):
        super(Samples, self).__init__()
        
        self.setWindowTitle("Banco de Amostras")
        self.setGeometry(200, 200, 800, 500)  
        self.setMaximumSize(screen.size())

class Info(QDialog):
    def __init__(self):
        super(Info, self).__init__()
        
        self.setWindowTitle("BD Info")
        self.setGeometry(200, 200, 800, 250)  
        self.setMaximumSize(screen.size())
        
        self.create_info_layout()
        
        infoLayout = QVBoxLayout()
        infoLayout.addWidget(self.info_widget)
        
        self.setLayout(infoLayout)
    '''
    print("Usuários cadastrados (teste): ", upsql.row_count(usess, table="User"))
    print("Pacientes registrados: ", spsql.row_count(ssess, table="Patients"))
    print("Amostras cadastradas: ", spsql.row_count(ssess, table="Samples"))
    print("Exames cadastrados: ", spsql.row_count(ssess, table="Exams"))
    '''
        
    def create_info_layout(self):
        
        self.info_grid = QGridLayout()
        self.info_viewer = QPlainTextEdit()
        self.info_viewer.setReadOnly(True)
        
        #server_info
        sinfo = user_psql.check_db_info()
        
        #table_info
        tinfo = [user_psql.row_count(usess),
                sampat_psql.row_count(dsess, "Patients"),
                sampat_psql.row_count(dsess, "Samples"),
                sampat_psql.row_count(dsess, "Exams")]

        info = "Tabelas:\n{}\n\nDados do servidor:\n"\
        "Usuários cadastrados: {}\n"\
        "Pacientes registrados: {}\nAmostras cadastradas: {}\n"\
        "Exames cadastrados: {}".format("\n".join(sinfo[0]), *tinfo)
        
        self.info_viewer.setPlainText(info)
        
        self.info_grid.addWidget(self.info_viewer)
        
        self.info_widget = QWidget()
        self.info_widget.setLayout(self.info_grid)
        
        
class Options(QWidget):
    def __init__(self):
        super(Options, self).__init__()
        
        self.setWindowTitle("Configurações")
        self.setGeometry(200, 200, 800, 500)  
        #self.setMaximumSize(800, 500)
        self.setFixedSize(800, 500)
        
        self.create_config_layout()
        
        self.options_layout = QVBoxLayout()
        self.options_layout.addWidget(self.opt_widget)
        self.setLayout(self.options_layout)
        
        self.opt_list.currentItemChanged.connect(self.options_layout_manager)
        
    def options_layout_manager(self, new_item, old_item):
        row = self.opt_list.row(new_item)
        if row == 0:
            self.central_opt_widget.setCurrentWidget(self.server_widget)
        elif row == 1:
            self.central_opt_widget.setCurrentWidget(self.email_widget)
        elif row == 2:
            self.central_opt_widget.setCurrentWidget(self.log_widget)
        elif row == 3:
            self.central_opt_widget.setCurrentWidget(self.user_widget)
                   
    def create_config_layout(self):
        
        self.opt_list = QListWidget()
        
        opt_list = ["Servidor", "Configurações de Email",
                    "Registro de Eventos", "Permissão de Usuários"]
        self.opt_list.addItems(opt_list)
        self.opt_list.setCurrentRow(0)
        self.list_header = QLabel("Configurações:")
        self.opt_header = QLabel("Opções:")
        
        self.options_grid = QGridLayout()
        
        self.central_opt_widget = QStackedWidget()
        self.serv = self.server_opt()
        self.central_opt_widget.addWidget(self.server_widget)
        
        try:
            #TODO esconder self.user se não for admin (-1)
            self.user = self.user_opt()
            self.central_opt_widget.addWidget(self.user_widget)
        except:
            self.opt_list.takeItem(3)
            logger.debug("APP - OPTIONS - Users option error")
        
        self.email = self.email_opt()
        self.central_opt_widget.addWidget(self.email_widget)
        self.log = self.log_opt()
        self.central_opt_widget.addWidget(self.log_widget)
               
        self.spacer_header = Spacer(20, 10).spacer()
        self.spacer_option = Spacer(15, 540).spacer()
        
        self.options_grid.addWidget(self.list_header, 0, 0, 1, 1)
        self.options_grid.addWidget(self.opt_list, 1, 0, 1, 1)
        self.options_grid.addItem(self.spacer_option, 1, 1)
        self.options_grid.addWidget(self.opt_header, 0, 2, 1, 1)
        self.options_grid.addWidget(self.central_opt_widget, 1, 2, 1, 1)
        
        self.opt_list.setFixedWidth(161)
        self.options_grid.setColumnMinimumWidth(0, 161)
        self.options_grid.setColumnStretch(0, 1)
        
        self.opt_widget = QWidget()
        self.opt_widget.setLayout(self.options_grid)

### server_opt definitions block start

    def server_opt(self):
        layout = QGridLayout()
        
        uform_layout = QFormLayout()
        dform_layout = QFormLayout()
        
        #user database info
        self.userver = QLabel("Configurações do Banco de Usuário:")
        uform_layout.addRow(self.userver)
        
        self.uloginedit = QLineEdit()
        uform_layout.addRow(QLabel("Login:"), self.uloginedit)
        
        self.upasswordedit = QLineEdit()
        self.upasswordedit.setEchoMode(QLineEdit.Password)
        uform_layout.addRow(QLabel("Senha:"), self.upasswordedit)
        
        self.uhostnameedit = QLineEdit()
        uform_layout.addRow(QLabel("Hostname:"), self.uhostnameedit)
        
        self.utableedit = QLineEdit()
        uform_layout.addRow(QLabel("Tabela:"), self.utableedit)
        
        #general data database info
        self.dserver = QLabel("Configurações do Banco de Dados:")
        dform_layout.addRow(self.dserver)
        
        self.dloginedit = QLineEdit()
        dform_layout.addRow(QLabel("Login:"), self.dloginedit)
        
        self.dpasswordedit = QLineEdit()
        self.dpasswordedit.setEchoMode(QLineEdit.Password)
        dform_layout.addRow(QLabel("Senha:"), self.dpasswordedit)
        
        self.dhostnameedit = QLineEdit()
        dform_layout.addRow(QLabel("Hostname:"), self.dhostnameedit)
        
        self.dtableedit = QLineEdit()
        dform_layout.addRow(QLabel("Tabela:"), self.dtableedit)

        #setings recap
        try:
            self.serv_options_recap()
            logger.info("Loading server adress options.")
        except KeyError:
            logger.warning("No options saved to load.")
        
        #TODO: incluir botão "reiniciar" <- aparentemente está funcionando
        #save and label options
        self.save_serv_btn = QPushButton("Salvar")
        self.restart_serv_btn = QPushButton("Reiniciar")
        self.restart_serv_btn.clicked.connect(self.restart_app_btn)
        
        self.save_serv_btn.resize(100, 400)
        self.save_serv_btn.clicked.connect(self.save_serv_options)
        
        self.saved_serv_lbl = QLabel("Opções Salvas, reinicie o programa para fazer efeito.")
        self.saved_serv_lbl.setStyleSheet("color: green")
        self.saved_serv_lbl.setFont(QFont("Times", weight = QFont.Bold))
        self.saved_serv_lbl.setVisible(False)
        
        #grid adjusting
        layout.addLayout(uform_layout, 0, 0)
        layout.addItem(Spacer(350, 24).spacer(), 1, 0)
        layout.addLayout(dform_layout, 2, 0)
        layout.setRowStretch(2, 10)
        layout.addWidget(self.saved_serv_lbl, 4, 0, 1, 2, Qt.AlignLeft)
        layout.addWidget(self.restart_serv_btn, 4, 0, 1, 2, Qt.AlignRight)
        layout.addWidget(self.save_serv_btn, 4, 2, 1, 2, Qt.AlignRight)
        #layout.setHorizontalSpacing(20)
        
        self.server_widget = QWidget()
        self.server_widget.setLayout(layout)
        
    def serv_options_recap(self):
        user_db_dict = {}
        data_db_dict = {}
        
        for item in settings._keys():
            if "db_adress" in item:
                value_name = item.split("/")[1]
                value = settings.load_registry("db_adress", value_name)
                if "uentry" in value_name:
                    user_db_dict[value_name] = aux.hex_to_str(value, 4)
                elif "dentry" in value_name:
                    data_db_dict[value_name] = aux.hex_to_str(value, 3)
                else:
                    pass
        
        self.uloginedit.setText(user_db_dict["uentryl"])
        self.upasswordedit.setText(user_db_dict["uentryw"])
        self.uhostnameedit.setText(user_db_dict["uentryh"])
        self.utableedit.setText(user_db_dict["uentryt"])
        
        self.dloginedit.setText(data_db_dict["dentryl"])
        self.dpasswordedit.setText(data_db_dict["dentryw"])
        self.dhostnameedit.setText(data_db_dict["dentryh"])
        self.dtableedit.setText(data_db_dict["dentryt"])
       
    def saved_serv_timer(self, active=False):
        if active:
            self.saved_serv_lbl.setVisible(True)
        else:
            self.saved_serv_lbl.setVisible(False)

    def save_serv_options(self):
        user_db_dict = {"uentryl": self.uloginedit.text(),
                        "uentryw": self.upasswordedit.text(),
                        "uentryh": self.uhostnameedit.text(),
                        "uentryt": self.utableedit.text()}
        
        data_db_dict = {"dentryl": self.dloginedit.text(),
                        "dentryw": self.dpasswordedit.text(),
                        "dentryh": self.dhostnameedit.text(),
                        "dentryt": self.dtableedit.text()}
        
        for key, value in user_db_dict.items():
            if not value == "":
                user_db_dict[key] = aux.str_to_hex(value, 4)
            else:
                gerrors.serv_opt_error()
            
        for key, value in data_db_dict.items():
            if not value == "":
                data_db_dict[key] = aux.str_to_hex(value, 3)
            else:
                gerrors.serv_opt_error()
                
        for key, value in user_db_dict.items():
            settings.add_registry("db_adress", key, value)
            
        for key, value in data_db_dict.items():
            settings.add_registry("db_adress", key, value)
        
        logger.info("Server options saved")        
        self.saved_serv_timer(True)
        timer = QTimer()
        timer.singleShot(2000, self.saved_serv_timer)
        
### server_opt definitions block end
### user_opt definitions block start

    def user_opt(self):
        user_layout = QGridLayout()
        
        #defining table
        rows = user_psql.row_count(usess, table="User")
        ut_header = "Usuário", "Nível"
        
        self.users_list = user_psql.query_values(usess, column = "login")
        self.nvl_list = user_psql.query_values(usess, column = "nvl")
        nvl = ['Analista', 'Técnico', 'Aluno', 'Outros']
        
        self.user_table = QTableWidget(rows, 2)
        self.user_table.setHorizontalHeaderLabels(ut_header)
        self.header = self.user_table.horizontalHeader()
        self.header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.user_table.setSortingEnabled(False)
        self.changes_dict = {}
        
        for i in range(0, rows):
            self.user_table.setItem(i, 0, QTableWidgetItem(self.users_list[i][0]))
            self.nvl_combo = QComboBox()
            self.nvl_combo.addItems(nvl)
            self.nvl_combo.setProperty('row', i)
            self.nvl_combo.activated.connect(self.combo_flags)
            self.nvl_combo.currentIndexChanged.connect(self.combo_flags)
            self.user_table.setCellWidget(i, 1, self.nvl_combo)
            index = self.nvl_combo.findText(self.nvl_list[i][0], Qt.MatchExactly)
            self.nvl_combo.setCurrentIndex(index)
        self.user_table.setSortingEnabled(True)
        
        self.user_save_btn = QPushButton("Salvar")
        self.saved_user_lbl = QLabel("Níveis atualizados.")
        self.saved_user_lbl.setStyleSheet("color: green")
        self.saved_user_lbl.setFont(QFont("Times", weight = QFont.Bold))
        
        self.saved_user_timer()
        self.user_save_btn.clicked.connect(self.update_nvl)
    
        user_layout.addWidget(self.user_table, 0, 0, 3, 4)
        user_layout.addWidget(self.user_save_btn, 4, 3, 1, 1)
        user_layout.addWidget(self.saved_user_lbl, 4, 0, 1, 1)
        self.user_widget = QWidget()
        self.user_widget.setLayout(user_layout)
    
    def combo_flags(self):
        comboBox = self.sender()
        row = comboBox.property('row')
        text = comboBox.currentText()
        user = self.user_table.item(row, 0).text()
        self.changes_dict[user] = [self.nvl_list[row][0], text]        
        
    def update_nvl(self):
        logger.debug("OPTIONS - User permissions changed: {}".format(self.changes_dict))
        for key, values in self.changes_dict.items():
            user = key
            new_info = {"nvl": values[1]}
            if not values[1] == "":
                user_psql.update_user(usess, user, new_info)
            else:
                pass
        
        self.saved_user_timer(True)
        timer = QTimer()
        timer.singleShot(2000, self.saved_user_timer)

    def saved_user_timer(self, active=False):
        if active:
            self.saved_user_lbl.setVisible(True)
        else:
            self.saved_user_lbl.setVisible(False)
            
    def restart_app_btn(self, event):
        try:
            subprocess.Popen([sys.executable, absfilepath])
        except OSError:
            gerrors.res_error()
        else:
            QApplication.quit()
        
### user_opt definitions block end
### email_opt definitions block start

    def email_opt(self):
        email_layout = QGridLayout()
        email_form_layout = QFormLayout()
        
        #defining form rows
        email_form_layout.addRow(QLabel("Configurações de email:"))
        
        self.serv_email_adress = QLineEdit()
        email_form_layout.addRow(QLabel("Email do Servidor:"), self.serv_email_adress)
        
        self.serv_email_password = QLineEdit()
        self.serv_email_password.setEchoMode(QLineEdit.Password)
        email_form_layout.addRow(QLabel("Senha do email:"), self.serv_email_password)
        
        self.email_info = QLabel("(Provedores suportados: Yahoo, Gmail, Hotmail)")
        email_form_layout.addRow(self.email_info)
        
        #email options recap
        try:
            self.email_opt_recap()
            logger.info("Loading server email adress options.")
        except KeyError:
            logger.warning("No options saved to load.")
        
        #defining layout buttons
        self.save_email_btn = QPushButton("Salvar")
        self.save_email_btn.resize(100, 400)
        self.save_email_btn.clicked.connect(self.save_email_option)
        
        self.saved_email_lbl = QLabel("Opções Salvas.")
        self.saved_email_lbl.setStyleSheet("color: green")
        self.saved_email_lbl.setFont(QFont("Times", weight = QFont.Bold))
        self.saved_email_lbl.setVisible(False)
        
        email_layout.addLayout(email_form_layout, 0, 0)
        email_layout.addItem(Spacer(350, 24).spacer(), 2, 0)
        email_layout.addWidget(self.saved_email_lbl, 4, 0, 1, 2, Qt.AlignLeft)
        email_layout.addWidget(self.save_email_btn, 4, 0, 1, 2, Qt.AlignRight)

        self.email_widget = QWidget()
        self.email_widget.setLayout(email_layout)
    
    def email_opt_recap(self):
        email_dict = {}
        
        for item in settings._keys():
            if "db_adress" in item:
                value_name = item.split("/")[1]
                value = settings.load_registry("db_adress", value_name)
                email_dict[value_name] = aux.hex_to_str(value, 6)
                
        self.serv_email_adress.setText(email_dict["serv_email_adress"])
        self.serv_email_password.setText(email_dict["serv_email_pass"])
        
    def save_email_option(self):
        email_dict = {"serv_email_adress": self.serv_email_adress.text(),
                      "serv_email_pass": self.serv_email_password.text()}
        
        for key, value in email_dict.items():
            if not value == "":
                email_dict[key] = aux.str_to_hex(value, 6)
            else:
                gerrors.email_opt_error()
        
        for key, value in email_dict.items():
            settings.add_registry("db_adress", key, value)
        logger.info("Email options saved.")
        
        self.saved_email_timer(True)
        timer = QTimer()
        timer.singleShot(2000, self.saved_email_timer)
            
    def saved_email_timer(self, active=False):
        if active:
            self.saved_email_lbl.setVisible(True)
        else:
            self.saved_email_lbl.setVisible(False)
            
### emaik_opt definitions block end
### log_opt definitions block start
        
    def log_opt(self):
        #defining the layouts
        self.log_paths = {"log_path": "",
                          "config_path": "",
                          "log_file": "/GDAPP_info.log",
                          "log_config_file": "/GDAPP_conflog.conf"}
        grid_layout = QGridLayout()
        path_form_layout = QFormLayout()

        #defining a text widget to see log      
        self.log_viewer = QPlainTextEdit()
        self.log_viewer.setReadOnly(True)
        
        value = settings.load_registry("configs", "log_path")
        if not value:
            self.log_btn = QPushButton("Selecione a pasta")
        else:
            self.log_btn = QPushButton(value)
            file = self.log_paths["log_file"]
            self.log_reader(value + file)

        self.default_btn = QPushButton("Padrão")
        self.default_btn.resize(100, 200)
        
        self.log_btn.clicked.connect(self.log_file)
        self.default_btn.clicked.connect(self.default_log)

        #defining form layout

        path_form_layout.addRow(QLabel("Definição dos caminhos:"))
        path_form_layout.addRow(QLabel("Pasta com .log:"), self.log_btn)
                
        #defining grid layout
        
        grid_layout.addLayout(path_form_layout, 0, 0)
        grid_layout.addWidget(self.default_btn, 1, 0, Qt.AlignRight)
        grid_layout.addItem(Spacer(350, 24).spacer(), 2, 0)
        grid_layout.addWidget(self.log_viewer, 3, 0)
        
        self.log_widget = QWidget()
        self.log_widget.setLayout(grid_layout)
        
    def change_buttons(self):
        value = settings.load_registry("configs", "log_path")
        self.log_btn.setText(value)
        QApplication.processEvents()
        
    def default_log(self):
        default_path = os.path.dirname(os.path.realpath(__file__)) + "\logs"
        settings.add_registry("configs", "log_path", default_path)
        self.change_buttons()
        self.log_reader(default_path + self.log_paths["log_file"])
        
    def log_file(self):
        log_folder = QFileDialog()
        log_folder.setFileMode(2)
        log_folder.setOption(QFileDialog.ReadOnly)
        log_folder.setOption(QFileDialog.ShowDirsOnly)
        directory = log_folder.getExistingDirectory(self, "Selecione a pasta")

        if directory:
            self.log_paths["log_path"] = directory.replace("/","\\")
            self.log_path = self.log_paths["log_path"] + self.log_paths["log_file"]
            self.log_btn.setText(self.log_paths["log_path"])
            settings.add_registry("configs", "log_path", self.log_paths["log_path"])
            self.change_buttons()
            self.log_reader(self.log_path)
   
    def log_reader(self, log_path):
        try:
            with open(log_path, "r") as log:
                log_lines = log.readlines()
                log_len = len(log_lines)
                if log_len > 50:
                    self.log_viewer.setPlainText("".join(log_lines[-(log_len-40):]))
                elif log_len > 30:
                    self.log_viewer.setPlainText("".join(log_lines[-(log_len-20):]))
                else:
                    self.log_viewer.setPlainText("".join(log_lines[-log_len:]))
        except FileNotFoundError:
            self.log_viewer.setPlainText("Nenhum arquivo .log encontrado.\n\n" \
                                         "Caso o endereço da pasta tenha sido alterado, reabra o programa.")
### log_opt definitions block end
class System():
    
    def __init__(self):
        self.settings = Configurations()
        self.path = self.settings.load_registry("configs", "log_path") #it doesn't belong here but it needs to be here
        self.logger = _logger.logger_define(self.path)
        self.logger.propagate = False
        self.gerrors = errorex.gd_errors()
        
        
    def sys_serv_opt_recap(self):
        self.user_db_dict = {}
        self.data_db_dict = {}
        
        for item in settings._keys():
            if "db_adress" in item:
                value_name = item.split("/")[1]
                value = settings.load_registry("db_adress", value_name)
                if "uentry" in value_name:
                    self.user_db_dict[value_name] = aux.hex_to_str(value, 4)
                elif "dentry" in value_name:
                    self.data_db_dict[value_name] = aux.hex_to_str(value, 3)
                    
    def sql_user_connect(self):
        self.sys_serv_opt_recap()
        
        login = self.user_db_dict["uentryl"]
        upw = self.user_db_dict["uentryw"]
        hn = self.user_db_dict["uentryh"]
        udb = self.user_db_dict["uentryt"]
        
        try:
            user_psql, usess = sqlmng.sql_init(login, upw, hn, udb)
            return user_psql, usess
        except:
            logger.warning("Connection error.")
            raise Exception("DB ADRESS INVALID")
            
    def sql_sampat_connect(self):
        self.sys_serv_opt_recap()
        
        login = self.data_db_dict["dentryl"]
        upw = self.data_db_dict["dentryw"]
        hn = self.data_db_dict["dentryh"]
        udb = self.data_db_dict["dentryt"]
        
        try:
            sampat_psql, dsess = sqlmng.sql_init(login, upw, hn, udb)
            return sampat_psql, dsess
        except:
            logger.warning("Connection error.")
            raise Exception("DB ADRESS INVALID")
            
            
    def sys_email(self): 
        email_dict = {}
        for item in settings._keys():
            if "db_adress" in item:
                value_name = item.split("/")[1]
                if "_email_" in value_name:
                    value = settings.load_registry("db_adress", value_name)
                    email_dict[value_name] = aux.hex_to_str(value, 6)
                    
        email_pass = [email_dict["serv_email_adress"], email_dict["serv_email_pass"]]
        return email_pass
        
#the code that starts the magic

if __name__ == "__main__":
    #initializes the errors class inside the errorex module  
    settings = System().settings
    logger = System().logger
    gerrors = System().gerrors
    
    try:
        user_psql, usess = System().sql_user_connect()
    except:
        conn_error_flag = (True, "user") 
    try:
        sampat_psql, dsess = System().sql_sampat_connect()
    except:
        conn_error_flag = (True, "sampat")
        
    logger.info("__main__ - Program oppened")
    logger.info("CONFIG - Configurations initialized.")
    logger.debug("CONFIG - {}".format(settings))

    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    
    try:
        if conn_error_flag[0] == True:
            gerrors.conn_error_flag(conn_error_flag[1])
    except:
        pass
    
    ex = App()
    sys.exit(app.exec_())


    