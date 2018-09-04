# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 11:07:24 2018

SQL Management Module

@author: Jullian
"""
'''This module focus is to create methods derived from sqlalchemy to be used in
the main app, the methods names are self explanatory'''

import psycopg2 # analysis:ignore
from sqlalchemy import (MetaData, Table, create_engine, Column, Integer, String, Date, # analysis:ignore
                        exists, Boolean, Float, exc, func, ForeignKey, select, text, # analysis:ignore
                        or_, and_, literal) # analysis:ignore
from sqlalchemy.orm import sessionmaker, relationship, mapper # analysis:ignore
from sqlalchemy.sql.expression import false
from sqlalchemy.ext.declarative import declarative_base # analysis:ignore
from sqlalchemy_utils import create_database, database_exists
import data_import as itapi

#from sqlalchemy.ext.automap import automap_base
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

# todo: update user info
class SQL(object):

    #the init's parameters will be used to create the engine, it will be set in the main app
    def __init__(self, server_login, server_pw, hostname, database):
        self.server_login = server_login
        self.server_pw = server_pw
        self.hostname = hostname
        self.database = database
        logger.info("SQLMNG - Postgress instance initialized.")
        
    #create the sqlalchemy engine using postgress and psycopg2 (the module)
    #the other infos comes from the SQL init class method
    def set_engine(self):
        db_adress = 'postgresql+psycopg2://{}:{}@{}/{}'.format(self.server_login,
                                    self.server_pw, self.hostname, self.database)
        self.engine = create_engine(db_adress)
        if not database_exists(self.engine.url):
            logger.warn("SQLMNG - DB not found, creating new DB")
            logger.debug("SQLMNG - DB {} created".format(self.engine.url))
            create_database(self.engine.url)
        logger.info("SQLMNG - DB found, connecting.")
        logger.debug(self.engine.url)
        self.metadata = MetaData(self.engine)
        return self.engine
    
    #this method sets the session using the engine defined previously
    def set_session(self, engine):
        Session = sessionmaker(bind=engine)
        self.session = Session()
        logger.debug(self.session)
        logger.info("SQLMNG - Session created.")
        return self.session
    
    def check_db_info(self):
        info_list = [list(Base.metadata.tables.keys()), self.metadata]
        return info_list
    
    def _create_default_user_db(self):
        '''
        May use in future
        '''
        users_dict = {"login": String, "password": String,
                      "name": String, "surname": String,
                      "nvl": String, "other_spec": String,
                      "email": String, "date": Date}
        
        badwords_dict = {"badwords": String}
        
        self.create_db_table("db_user_schema", "users", **users_dict)
        self.create_db_table("db_user_schema", "badwords", **badwords_dict)
        self.commit_new_table()
        self.check_db_info()
        
    def _create_db_table(self, schema, tablename, **table_info):
        '''
        May use in future
        '''
        self.table = Table(tablename, self.metadata, 
              Column('id', Integer, primary_key = True),
              *(Column(key, value) for key, value in table_info.items()),
              schema = schema)
        self.commit_new_tables()
        #self.class_mapper(schema, tablename)
        
    def commit_new_tables(self, schema, table):
        table = str_to_table(schema, table)
        table.__table__.create(self.engine)    
        
    def class_mapper(self, schema, tablename):
        '''
        May use in the future
        '''
        if tablename == "users":
            mydict = {'__table__': '{}.{}'.format(schema, tablename), 
                  '__table_args__':({'autoload': True, 'autoload_with':self.engine},)}
        elif tablename == "badwords":
            mydict = {'__table__': '{}.{}'.format(schema, tablename), 
                  '__table_args__':({'autoload': True, 'autoload_with':self.engine},)}
        else:
            mydict = {'__table__': '{}.{}'.format(schema, tablename), 
                  '__table_args__':({'autoload': True, 'autoload_with':self.engine},)}
            
        cls = type('{}'.format(tablename), (Base,), mydict)
        mapper(cls, self.table)
        
    def detect_schema(self, schema, create_schema = False):
        fix_schema = str(schema)
        print("schema: ",   fix_schema)
        
        flag = exists(select([(text("schema_name"))]).select_from(text("information_schema.schemata"))
                                            .where(text("schema_name = '{}'".format(fix_schema))))
        if self.session.query(flag).scalar():
            return True
        #self.engine.execute("SHOW CREATE SCHEMA {}".format(fix_schema)).scalar()

    #create the user on the database, the user_info should be a dict containing
    #login, pw, name, surname, email and datetime
    def add_user(self, session, user_info):
        new_user = User(**user_info)
        session.add(new_user)
        session.commit()
        logger.info("SQLMNG - User added and changes commited.")
    
    #this method finds the target username and change the pw on the database for
    #the new one, the pw parameter
    def change_user_pw(self, session, username, pw):
        session.query(User).filter_by(login=username).update({"password": pw})
        session.commit()
        logging.info("SQLMNG - {} changed password.".format(username))
        
    #this one deletes the target (id/login) entry from the database
    #the ident params change if the code searchs for id or login
    def delete_user(self, session, target, ident=True):
        if ident:
            ident = session.query(User).filter_by(id=target).delete()
        else:
            ident = session.query(User).filter_by(login=target).delete()
        session.commit()
        logging.info("SQLMNG - {} deleted and changes commited.".format(target))
        
    def query_values(self, session, column = None, schema = "db_user_schema", 
                     target = None, table = "users", _type = "all"):
        
        logging.debug("SQLMNG - {}".format(":".join(str(x) for x in [session, 
                      column, table, _type])))
        
        table_name = str_to_table(schema, table)
        base_query = self.session.query(table_name)
        
        if table == "users":
            col = str_to_column(table_name, column)
            return self.session.query(col).all()
        
        if column:
            if type(column) == str:
                col_obj = str_to_column(table_name, column)
                col_query = base_query.filter(col_obj == target)
            elif type(column) == list:
                col_obj_list = [str_to_column(table_name, col) for col in column]
                col_query = base_query.with_entities(*col_obj_list)
            else:
                raise ValueError("Column must be either str or list")
                
            if _type == "all":
                query = col_query.all()
            elif _type == "first":
                query = col_query.first()
            #TODO next two elifs will not work with multiple columns, fix it
            elif _type == "scalar":
                query = base_query.filter(col_obj == target).first() is not None
            elif _type == "one":
                query = col_query.one()
            return query
        
        else:
            if _type == "all":
                query = base_query.all()
            elif _type == "first":
                query = base_query.first()
            else:
                query = base_query.first()
            return query

    #the query method makes query (on the user table) based on the target param
    #if the badword param is set to true the query will be made in the badword tables
    #if the user is set to true it will look for the login column, otherwise it will look at the email column
    #if scalar is set to true the output will be either True or False
    def query_user(self, session, target, badword = False, user = True, scalar=True):
        if badword == True:
            query = session.query(exists().where(Badwords.badword==target)).scalar()
            if target:
                logging.info("SQLMNG - Badword {} queried.".format(
                target.replace(target, "*"*len(target))))
            return query
        
        try:
            if scalar:
                query = session.query(exists().where(User.login==target)).scalar()
            else:
                if user:
                    query = session.query(User).filter_by(login=target).first()
                else:
                    query = session.query(User).filter_by(email=target).first()
            logging.info("SQLMNG - {} queried.".format(target))
            return query
        except exc.SQLAlchemyError:
            return exc.SQLAlchemyError.__name__
    
    #similar to the add_user and change password, it looks for the username and
    #update the row with the information inside new_info dict
    def update_user(self, session, username, new_info):
        session.query(User).filter_by(login=username).update(new_info)
        session.commit()
        logging.debug("SQLMNG - Update <{}> requested.".format(new_info))
        logging.info("SQLMNG - Update commited.")
        
    def add_rows_sampat(self, session, rows_info, schema, table):
        
        table = str_to_table(schema, table)
        new_row = table(**rows_info)
        session.add(new_row)
        session.commit()
        logger.info("SQLMNG - {} rows added to {} table.".format(len(rows_info), table))    
        
    def update_rows_sampat(self, session, rows_info, schema, table):
        table = str_to_table(schema, table)
        new_row = table(**rows_info)
        session.merge(new_row)
        session.commit()
        logging.info('SQLMNG - Update commited')
            
    def pat_flow(self, rows_info, schema, table, verbose = False):
        #TODO lidar com duplicatas
        logging.debug("SQLMNG - Insert entry <{}> requested.".format(rows_info))

        for entry in rows_info:          
            target = int(entry["old_id"])
            part = entry["particular"]
            
            check = self.session.query(Patient).filter(Patient.old_id == target,
                                                       Patient.particular == part)
            check_bool = check.first() is not None
            
            if not check_bool:
                if verbose:
                    print(entry)
                try:
                    self.add_rows_sampat(self.session, entry, schema, table)
                except:
                    logging.info('SQLMNG - Entry not added')
                    raise ValueError("New entrys not inserted on DB")
            else:
                pass
    
    def samp_flow(self, rows_info, schema, table, verbose = False):
        for entry in rows_info:
            target = int(entry["samp_serial"])
            old_id = int(entry["old_id"])
            part = True if not entry["sample_group"] == "G" else False
            
            query = self.session.query(Patient).filter(Patient.old_id == old_id,
                                                       Patient.particular == part)
            check = self.query_values(self.session, target = target, 
                                      column = 'samp_serial', schema = schema, 
                                      table = table, _type = "scalar")
            
            if not check:               
                entry["sample_owner"] = query.first()
                if verbose:
                    print(entry)
                try:
                    self.add_rows_sampat(self.session, entry, schema, table)
                
                except:
                    logging.info('SQLMNG - Entry not added')
                    raise ValueError("New entrys not inserted on DB")
            else:
                pass
            
    def exams_flow(self, rows_info, schema, table, verbose = False):
        for entry in rows_info:
            target = int(entry["exam_serial"])
            old_id = int(entry["old_id"])
            part = entry["sample_group"]
            
            query = self.session.query(Samples).filter(Samples.old_id == old_id,
                                                       Samples.sample_group == part)
            
            check = self.query_values(self.session, target = target, 
                                      column = 'exam_serial', schema = schema, 
                                      table = table, _type = "scalar")
            if not check:               
                entry["master_sample"] = query.first()
                entry.pop("sample_group", None)
                entry.pop("old_id", None)
                if verbose:
                    print(entry)
                try:
                    self.add_rows_sampat(self.session, entry, schema, table)
                    
                except:
                    logging.info('SQLMNG - Entry not added')
                    raise ValueError("New entrys not inserted on DB")
            else:
                pass
                    
    def row_count(self, session, table="User"):
        if table == "User":
            rows = session.query(func.count(User.id)).scalar()
        elif table == "Badword":
            rows = session.query(func.count(Badwords.id)).scalar()
        elif table == "Samples":
            rows = session.query(func.count(Samples.id)).scalar()
        elif table == "Patients":
            rows = session.query(func.count(Patient.id)).scalar()
        elif table == "Exams":
            rows = session.query(func.count(Exams.id)).scalar()
        return rows

    #back-end method used to add entries to the badword table, it accepts both lists and strings
    def populate_badword(self, session, badword):
        if type(badword) == list:
            for item in badword:
                new_bad = Badwords(badword = item)
                session.add(new_bad)
        else:
            print(badword)
            new_bad = Badwords(badword = badword)
            session.add(new_bad)
        session.commit()   
    def close_conn(self, session):
        logging.info("SQL Session closed.")
        session.close()

#class that defines the User table in the database, it follows the sqlalchemy guidelines
class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': "db_user_schema"}
    
    id = Column(Integer, primary_key = True)
    login = Column(String)
    password = Column(String)
    name = Column(String)
    surname = Column(String)
    nvl = Column(String)
    other_spec = Column(String)
    email = Column(String)
    date = Column(Date)
    
    def __repr__(self):
        return "login={},password={},name={},surname={},nvl={},"\
        "other_spec={},email={},date={}".format(self.login, self.password, self.name,
                    self.surname, self.nvl, self.other_spec, self.email, self.date)

#class that defines the Badword table in the database, it follows the sqlalchemy guidelines
class Badwords(Base):
    __tablename__ = 'badwords'
    __table_args__ = {'schema': "db_user_schema"}
    
    id = Column(Integer, primary_key = True)
    badword = Column(String)

    def __repr__(self):
        return "badword={}".format(self.badword)
    
#class that defines the main db in the server, it follows the sqlalchemy guidelines
class Patient(Base):
    __tablename__ = 'patients_table'
    __table_args__ = {'schema': "public"}

    id = Column(Integer, primary_key=True, unique = True)
    old_id = Column("barcode", Integer, unique = False)
    samples = relationship("Samples", backref = 'sample_owner')
    particular = Column(Boolean, default = False, unique = False, nullable = False)
    first_name = Column(String, default = None)
    second_name = Column(String, default = None)
    surname = Column(String, default = None)
    rn = Column(Boolean, default = False, unique = False)
    nt = Column(Boolean, default = False, unique = False)
    rg = Column(String, default = None)
    registry = Column(String, default = None)
    birth_date = Column(Date, default = None)
    register_date = Column(Date, default = None)
    pat_origin = Column(String, default = None)
    doctor = Column(String, default = None)
    parent_type = Column(String, default = None)
    parent = Column(String, default = None)
    lib = Column(Boolean, default = False, unique = False, nullable = False)
    diag_hipt = Column(String, default = None)
    term = Column(Boolean, default = False, unique = False, nullable = False)
    gen = Column(String, default = None)
    karyotype = Column(String, default = None)
    obs = Column(String, default = None)
    
    def __repr__(self):
        return rep_gen(self)
    
class Samples(Base):
    __tablename__ = 'samples_table'
    __table_args__ = {'schema': "public"}

    id = Column(Integer, primary_key=True)
    old_id = Column("old_id", Integer, unique = False)
    sample_group = Column(String, default = None)
    samp_serial = Column(Integer, default = None, unique = True)
    patient_id = Column(Integer, ForeignKey('public.patients_table.id'), nullable = False)
    exams = relationship('Exams', backref = 'master_sample')
    sample_orign = Column(String, default = None)
    cap_color = Column(String, default = None)
    material_type = Column(String, default = None)
    material_details = Column(String, default = None)
    material_quantity = Column(Float, default = None)   
    main_tube = Column(Boolean, default = False, unique = False, nullable = False)
    aliquot = Column(Boolean, default = False, unique = False, nullable = False)
    aliquot_id = Column(Integer, default = None, nullable = True)
    extracted = Column(Boolean, default = False, unique = False, nullable = False)
    processed = Column(Boolean, default = False, unique = False, nullable = False)
    arquived = Column(Boolean, default = False, unique = False, nullable = False)
    arquiv_date = Column(Date, default = None, nullable = True)
    arq_position = Column(String, default = None)
    sample_register_date = Column(Date, default = None)
    sample_extraction_date = Column(Date, default = None)
    sample_process_date = Column(Date, default = None)
    sample_aliquot_date = Column(Date, default = None)
    sample_dna_concentration = Column(Float, default = None)
    sample_dna_quality = Column(Float, default = None)
    recall = Column(Boolean, default = False, nullable = False)
    recall_date = Column(Date, default = None, nullable = True)
    recall_sample_id = Column(Integer, default = None, nullable = True)
    recall_register_date = Column(Date, default = None, nullable = True)
    lib_date = Column(Date, default = None)
    lib = Column(Boolean, default = False, unique = False, nullable = False)
    obs = Column(String, default = None)
    
    def __repr__(self):
        return rep_gen(self)

class Exams(Base):
    __tablename__ = 'exams_table'
    __table_args__ = {'schema': "public"}

    id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey('public.samples_table.id'), nullable = False)
    exam_serial = Column(Integer, default = None, unique = True)
    sample_exam = Column(String, default = None)
    run_number = Column(Integer, default = None)
    seq_number = Column(Integer, default = None)
    run_letter = Column(String, default = None, unique = False)
    kit = Column(String, default = None)
    kit_lot = Column(String, default = None)
    platform = Column(String, default = None)
    results = Column(String, default = None)
    lib_date = Column(Date, default = None)
    lib = Column(Boolean, default = False, unique = False, nullable = False)
    obs = Column(String, default = None)
    
    def __repr__(self):
        return rep_gen(self)
    
#a plain function that initialize the SQL class and outputs the instance and session
def str_to_table(schema, table):
    for item in Base._decl_class_registry.values():
        if hasattr(item, '__table__') and item.__table__.fullname == "{}.{}".format(schema, table):
            return item
        
def str_to_column(table, column):
    return getattr(table, column)

def sql_init(login, upw, hn, db):
    psql = SQL(login, upw, hn, db)
    try:
        engine = psql.set_engine()
    except TimeoutError as TE_ERROR:
        return TE_ERROR
    finally:
        sess = psql.set_session(engine)
        return psql, sess

def rep_gen(ncls):
    try:
        if type(ncls) == str:
            _cls = eval(ncls)
        else:
            _cls = ncls
    except:
        raise NameError("Class not found")
    cl_keys = [key for key in _cls.__dict__.keys() if not "_" in key]
    repr_str = "={},".join(cl_keys) + "={}"
    cls_attr = [getattr(_cls,key) for key in cl_keys]    
    return repr_str.format(*cls_attr)


login = "citogenomica"
spw = "telomero46"
hn = "citogenomica.phcnet.usp.br"
udb = "user_database"
ptdb = "sampat_database"


#print("#UPSQL")
upsql, usess = sql_init(login, spw, hn, udb)
spsql, ssess = sql_init(login, spw, hn, ptdb)

'''
#upsql.commit_new_tables()
upsql.check_db_info()

#upsql.class_mapper("db_user_schema", "users")
print("#SPSQL")
'''  


#pat_dict = itapi.create_dict(itapi.remodel_pat_table(itapi.filecsv, sep = ";"))
#pat_dict2 = itapi.dict_popper(pat_dict, ["Teste", "sample_register_date", "sample_group", "Ficha clínica"])

#samp_dict = itapi.create_dict(itapi.remodel_samp_table(itapi.filecsv, sep = ";"))
#exams_dict = itapi.create_dict(itapi.remodel_exams_table(itapi.filecsv, sep = ";"))

#spsql.commit_new_tables("public", "patients_table")
#spsql.commit_new_tables("public", "samples_table")
#spsql.commit_new_tables("public", "exams_table")

#spsql.pat_flow(pat_dict2, "public", "patients_table", verbose = True)
#spsql.samp_flow(samp_dict, "public", "samples_table", verbose = True)
#spsql.exams_flow(exams_dict, "public", "exams_table", verbose = True)
'''
print("Usuários cadastrados (teste): ", upsql.row_count(usess, table="User"))
print("Pacientes registrados: ", spsql.row_count(ssess, table="Patients"))
print("Amostras cadastradas: ", spsql.row_count(ssess, table="Samples"))
print("Exames cadastrados: ", spsql.row_count(ssess, table="Exams"))
'''
#print(upsql.query_values(usess, column="login", _type = "all"))
#print(upsql.query_values(usess, column="nvl", _type = "all"))
'''
spsql.check_db_info()


df_dict = itapi.create_dict(itapi.remodel_pat_table(itapi.filecsv, ";"))
#df_dict.pop('Ficha clínica', None)
#df_dict.pop('sample_register_date', None)
#df_dict.pop('sample_group', None)

#Patient.query.filter(Patient.barcode == 1).delete()


#query = upsql.query_values(usess, column="login", _all = True)
#print("query", query.login)

#query2 = ssess.query(Patient).with_entities(Patient.id, Patient.rn).group_by(Patient.id).having(Patient.id == 2).all()
#query2 = ssess.query(Patient).filter_by(rn = False).all()

query2 = spsql.query_values(ssess, target = ', column = "particular", schema = "public", table = "patients_table", _scalar = True)

if not type(query2) == list:
    print(query2)
else:    
    for item in query2:
        print("query", item)
'''

    
#print(User)
#badwords = ["where", "in", "'", "*", "AND", "OR", "AND blabla WHERE blabla",
#            '"', "''", '""', "%", "@", "!", "select", "insert", "delete",
#            "ALL", "AS", "ANY", "ADD", "ALTER", "UPDATE", "BACKUP", "CLOSE",
#            "email", " ", "name", "surname", "nome", "adm", "administrador",
#            "logon", "CLOSE", "admin", "ADMIN", "4DM1N", "adm1n", "4dmin", "login",
#            "user", "email", " ", "\\t", "\\n"]
#upsql.populate_badword(usess, badwords)
#query = psql.query_user(sess, "admin")
#print(str(query).split(","))
#psql.delete_user(sess, 29, ident=True)
#ret = sess.query(exists().where(User.login=="sdas")).scalar()
#print(ret)
#Badwords.__table__
#engine = psql.set_engine()
#Base.metadata.create_all(engine)
#sess.query(Badwords).all()
#psql.change_user_pw(sess, "admin", "admin")
#rows = psql.row_count(sess)
#cols = ["nvl"]
#print(User.__table_args__)