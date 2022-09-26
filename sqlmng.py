# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 11:07:24 2018

SQL Management Module

@author: Jullian
"""
'''This module focus is to create methods derived from sqlalchemy to be used in
the main app, the methods names are self explanatory'''

from errorex import gd_errors
import psycopg2
from sqlalchemy import (MetaData, Table, create_engine, Column, Integer, String, Date,
                        exists, Boolean, Float, exc, func, ForeignKey, select, text,
                        or_, and_, literal, schema, inspect, DateTime)
from sqlalchemy.engine import reflection
from sqlalchemy.orm import sessionmaker, relationship, mapper
from sqlalchemy.sql.expression import false
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.dialects import postgresql
# import data_import as itapi
import pandas as pd
import logging
import datetime

logger = logging.getLogger(__name__)
Base = declarative_base()
gerrors = gd_errors()
# todo: update user info

class SQL(object):
    """[manages sessions, connections and other database metainfo]

    Args:
        object ([object]): [parent object]
    """
    default_tables = ["users_table", "patients_table", "samples_table", "exams_table"]
    # the init's parameters will be used to create the engine, it will be set in the main app

    def __init__(self, server_login, server_pw, hostname, database):
        """[init the sql class]

        Args:
            server_login ([string]): [server login]
            server_pw ([string]): [server password]
            hostname ([string]): [hostname]
            database ([string]): [target database]
        """
        self.server_login = server_login
        self.server_pw = server_pw
        self.hostname = hostname
        self.database = database
        logger.info("SQLMNG - Postgress instance initialized.")

    # create the sqlalchemy engine using postgress and psycopg2 (the module)
    # the other infos comes from the SQL init class method
    def set_engine(self):
        """[set database engine]

        Returns:
            [engine]: [database engine]
        """
        db_adress = 'postgresql+psycopg2://{}:{}@{}/{}'.format(self.server_login,
                                                               self.server_pw,
                                                               self.hostname,
                                                               self.database)

        self.engine = create_engine(db_adress)
        if database_exists(self.engine.url) is False:
            logger.warn("SQLMNG - DB not found, creating new DB")
            logger.debug("SQLMNG - DB {} created".format(self.engine.url))
            create_database(self.engine.url)
        logger.info("SQLMNG - DB found, connecting.")
        logger.debug(self.engine.url)
        self.metadata = MetaData(self.engine)
        return self.engine

    # this method sets the session using the engine defined previously
    def set_session(self, engine):
        """[define session from engine]

        Args:
            engine ([engine]): [sql engine]

        Returns:
            [session]: [database session from engine]
        """
        Session = sessionmaker(bind=engine)
        self.session = Session()
        logger.debug(self.session)
        logger.info("SQLMNG - Session created.")
        return self.session

    def check_db_info(self):
        """[get database information]

        Returns:
            [list]: [list with database metadata]
        """
        info_list = [list(Base.metadata.tables.keys()), self.metadata]
        return info_list

    '''
    def _create_default_user_db(self):
        ###
        #May use in future
        ###
        users_dict = {"login": String, "password": String,
                      "name": String, "surname": String,
                      "nvl": String, "other_spec": String,
                      "email": String, "date": Date}
        badwords_dict = {"badwords": String}
        self._create_db_table("db_user_schema", "users", **users_dict)
        self._create_db_table("db_user_schema", "badwords", **badwords_dict)
        self.commit_new_tables()
        self.check_db_info()
    '''

    def _create_db_table(self, schema, tablename, **table_info):
        """[create table on schema.tablename with table_info]

        Args:
            schema ([string]): [schema name]
            tablename ([string]): [table name]
        """
        ###
        # May use in future
        ###
        self.table = Table(tablename, self.metadata,
                           Column('id', Integer, primary_key=True),
                           *(Column(key, value) for key, value in table_info.items()),
                           schema=schema)
        # self.commit_new_tables()
        # self.class_mapper(schema, tablename)

    def commit_new_table(self, schema, table):
        """[commit table creation]

        Args:
            schema ([string]): [schema name]
            tablename ([string]): [table name]
        """
        print("sqlmng: ", schema, table)
        table = str_to_table(schema, table)
        table.__table__.create(self.engine)

    def schema_exists(self, schema_name, create=False):
        """[check if schema already exist]

        Args:
            schema_name ([string]): [schema name]
            create (bool, optional): [create table if not exist]. Defaults to False.

        Returns:
            [bool]: [True if schema exists]
        """
        ret = self.engine.dialect.has_schema(self.engine, schema_name)
        if not ret:
            if create is True:
                self.engine.execute(schema.CreateSchema(schema_name))
        return ret

    def table_exists(self, name, schema=None):
        """[check if table name exist]

        Args:
            name ([string]): [table name]
            schema ([string], optional): [schema name]. Defaults to None.

        Returns:
            [bool]: [True if table name exist]
        """
        ret = inspect(self.engine).has_table(name, schema)
        return ret

    def class_mapper(self, schema, tablename):
        """[dynamically creates tables, not in use]

        Args:
            schema ([string]): [schema name]
            tablename ([string]): [table name]
        """
        if tablename == "users":
            mydict = {'__table__': '{}.{}'.format(schema, tablename),
                      '__table_args__': ({'autoload': True, 'autoload_with': self.engine},)}
        elif tablename == "badwords":
            mydict = {'__table__': '{}.{}'.format(schema, tablename),
                      '__table_args__': ({'autoload': True, 'autoload_with': self.engine},)}
        else:
            mydict = {'__table__': '{}.{}'.format(schema, tablename),
                      '__table_args__': ({'autoload': True, 'autoload_with': self.engine},)}

        cls = type('{}'.format(tablename), (Base,), mydict)
        mapper(cls, self.table)

    def detect_schema(self, schema, create_schema=False):
        """[Another implementation to check if schema exist on database]

        Args:
            schema ([string]): [schema name]
            create_schema (bool, optional): [if schema should be created]. Defaults to False.

        Returns:
            [bool]: [True if exists]
        """
        fix_schema = str(schema)
        print("schema: ", fix_schema)

        flag = exists(select([(text("schema_name"))]).select_from(text("information_schema.schemata"))
                                                     .where(text("schema_name = '{}'".format(fix_schema))))
        if self.session.query(flag).scalar():
            return True
        # self.engine.execute("SHOW CREATE SCHEMA {}".format(fix_schema)).scalar()

    # create the user on the database, the user_info should be a dict containing
    # login, pw, name, surname, email and datetime

    def add_user(self, session, user_info):
        """[summary]

        Args:
            session ([session]): [connection session]
            user_info ([list]): [list with info to add to server table]
        """
        new_user = User(**user_info)
        session.add(new_user)
        session.commit()
        logger.info("SQLMNG - User added and changes commited.")

    # this method finds the target username and change the pw on the database for
    # the new one, the pw parameter
    def change_user_pw(self, session, username, pw):
        """[change user password on table]

        Args:
            session ([session]): [connection session]
            username ([string]): [username]
            pw ([string]): [password]
        """
        session.query(User).filter_by(login=username).update({"password": pw})
        session.commit()
        logging.info("SQLMNG - {} changed password.".format(username))

    # this one deletes the target (id/login) entry from the database
    # the ident params change if the code searchs for id or login

    def delete_user(self, session, target, ident=True):
        """[delete user on table]

        Args:
            session ([session]): [connection session]
            target ([string]): [user to be deleted]
            ident (bool, optional): [if should be queried by id or login column]. Defaults to True.
        """
        if ident:
            ident = session.query(User).filter_by(id=target).delete()
        else:
            ident = session.query(User).filter_by(login=target).delete()
        session.commit()
        logging.info("SQLMNG - {} deleted and changes commited.".format(target))

    def query_values(self, session, column=None, schema="db_user_schema",
                     target=None, table="users", _type="all", _pd=False):
        """[query values from table]

        Args:
            session ([session]): [connection session]
            column ([list or string], optional): [description]. Defaults to None.
            schema (str, optional): [schema name]. Defaults to "db_user_schema".
            target ([string], optional): [what should be queried]. Defaults to None.
            table (str, optional): [table to look into]. Defaults to "users".
            _type (str, optional): [query with .all(), .last(), .first(), .scalar() or .one()]. Defaults to "all".
            _pd (bool, optional): [guide the flow of the method]. Defaults to False.

        Raises:
            ValueError: [In case the column name doesn't exist]

        Returns:
            [object]: [return the query result]
        """
        logging.debug("SQLMNG - {}".format(":".join(str(x) for x in [session,
                      column, table, _type])))

        table_name = str_to_table(schema, table)
        base_query = self.session.query(table_name)

        if table == "users":
            col = str_to_column(table_name, column)
            return self.session.query(col).all()

        if _pd is True:
            if column is not None and target is not None:
                try:
                    col_obj = str_to_column(table_name, column)
                    q = pd.read_sql(self.session.query(table_name).filter(col_obj == target).statement, self.session.bind)
                    return q
                except:
                    return pd.read_sql(self.session.query(table_name).statement, self.session.bind)
            elif column is not None:
                if _type is None:
                    try:
                        col_obj = str_to_column(table_name, column)
                        q = pd.read_sql(self.session.query(table_name).order_by(column.asc()).statement, self.session.bind)
                        return q
                    except:
                        return pd.read_sql(self.session.query(table_name).statement, self.session.bind)
                elif _type == "last":
                    try:
                        col_obj = str_to_column(table_name, column)
                        q = pd.read_sql(self.session.query(table_name).order_by(column.ID.asc()).limit(20).statement, self.session.bind)
                        return q
                    except:
                        return pd.read_sql(self.session.query(table_name).statement, self.session.bind)
            else:
                return pd.read_sql(self.session.query(table_name).statement, self.session.bind)

        if column:
            if type(column) == str:
                col_obj = str_to_column(table_name, column)
                col_query = base_query.filter(col_obj == target)
                if _type == "first":
                    return base_query.filter(col_obj == target).first()
            elif type(column) == list:
                col_obj_list = [str_to_column(table_name, col) for col in column]
                col_query = base_query.with_entities(*col_obj_list).filter(text(target))
            else:
                raise ValueError("Column must be either str or list")

            if _type == "all":
                query = col_query.all()
            elif _type == "first":
                query = col_query.first()
            # #TODO next two elifs will not work with multiple columns, fix it
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

    # the query method makes query (on the user table) based on the target param
    # if the badword param is set to true the query will be made in the badword tables
    # if the user is set to true it will look for the login column, otherwise it will look at the email column
    # if scalar is set to true the output will be either True or False
    def query_user(self, session, target, badword=False, user=True, scalar=True):
        """[summary]

        Args:
            session ([session]): [connection session]
            target ([string]): [target to be queried for]
            badword (bool, optional): [look in badword table or not]. Defaults to False.
            user (bool, optional): [return the query result as a list]. Defaults to True.
            scalar (bool, optional): [return the query result as a bool]. Defaults to True.

        Returns:
            [object]: [query]
        """
        if badword is True:
            query = session.query(exists().where(Badwords.badword == target)).scalar()
            if target:
                logging.info("SQLMNG - Badword {} queried.".format(
                             target.replace(target, "*" * len(target))))
            return query

        try:
            if scalar:
                query = session.query(exists().where(User.login == target)).scalar()
            else:
                if user:
                    query = session.query(User).filter_by(login=target).first()
                else:
                    query = session.query(User).filter_by(email=target).first()
            logging.info("SQLMNG - {} queried.".format(target))
            return query
        except exc.SQLAlchemyError:
            return exc.SQLAlchemyError.__name__

    # similar to the add_user and change password, it looks for the username and
    # update the row with the information inside new_info dict
    def update_user(self, session, username, new_info):
        """[update user in table users with new info]

        Args:
            session ([session]): [connection session]
            username ([string]): [user username to be updated]
            new_info ([dict]): [info to be updated]
        """
        session.query(User).filter_by(login=username).update(new_info)
        session.commit()
        logging.debug("SQLMNG - Update <{}> requested.".format(new_info))
        logging.info("SQLMNG - Update commited.")

    def upsert(self, schema, table_name, records={}):
        """[summary]

        Args:
            schema ([string]): [schema name]
            table_name ([string]): [table name]
            records (dict, optional): [records to be update]. Defaults to {}.

        Returns:
            [execute]: [return the execution of the upsert]
        """
        metadata = MetaData(schema=schema)
        metadata.bind = self.engine

        table = Table(table_name, metadata, schema=schema, autoload=True)

        # get list of fields making up primary key
        primary_keys = [key.name for key in inspect(table).primary_key]

        # assemble base statement
        stmt = postgresql.insert(table).values(records)

        # define dict of non-primary keys for updating
        update_dict = {
            c.name: c
            for c in stmt.excluded
            if not c.primary_key
        }

        # assemble new statement with 'on conflict do update' clause
        update_stmt = stmt.on_conflict_do_update(
            index_elements=primary_keys,
            set_=update_dict,
        )

        # execute
        with self.engine.connect() as conn:
            try:
                result = conn.execute(update_stmt)
                return result
            except exc.IntegrityError:
                return gerrors.fk_error()

    def add_rows_sampat(self, session, rows_info, schema, table):
        """[summary]

        Args:
            session ([session]): [connection session]
            rows_info ([dict]): [rows info to be added]
            schema ([string]): [schema name]
            table ([string]): [table name]

        Raises:
            ValueError: [In case the rows_info keyu doesn't match the table]
        """
        table = str_to_table(schema, table)
        new_row = table(**rows_info)
        session.add(new_row)
        try:
            session.commit()
        except exc.ProgrammingError:
            raise ValueError
        logger.info("SQLMNG - {} rows added to {} table.".format(len(rows_info), table))

    def delete_entry(self, session, schema, table, target):
        """[delete target entry from the table schema.table ]

        Args:
            session ([session]): [connection session]
            schema ([string]): [schema name]
            table ([string]): [table name]
            target ([string]): [id to be queried]
        """
        true_table = str_to_table(schema, table)
        true_col = str_to_column(true_table, 'ID')
        print(true_col)
        session.query(true_table).filter(true_col == target).delete()
        session.commit()

    def update_table(self, session, schema, table, column, target, new_entry):
        """[update table with new entry]

        Args:
            session ([session]): [connection session]
            schema ([string]): [schema name]
            table ([string]): [table name]
            column ([string]): [column to query the target]
            target ([string]): [which to be queried]
            new_entry ([dict]): [dict with info to be updated]
        """
        true_table = str_to_table(schema, table)
        true_col = str_to_column(true_table, column)
        session.query(true_table).filter(true_col == target).update(new_entry)
        session.commit()

    def update_rows_sampat(self, session, rows_info, schema, table):
        """[summary]

        Args:
            session ([session]): [connection session]
            schema ([string]): [schema name]
            table ([string]): [table name]
            rows_info ([dict]): [dict with info to be updated]
        """
        table_obj = str_to_table(schema, table)
        new_row = table_obj(**rows_info)
        session.merge(new_row)
        session.commit()
        logging.info('SQLMNG - Update commited')

    def pat_flow(self, rows_info, schema, table, verbose=False):
        """[specific flow to add entries into patients table]

        Args:
            rows_info ([dict]): [dict with info to be updated]
            schema ([string]): [schema name]
            table ([string]): [table name]
            verbose (bool, optional): [to print or not the content of rows_info]. Defaults to False.

        Raises:
            ValueError: [In case the entry weren't added to the database]
        """
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

    def samp_flow(self, rows_info, schema, table, verbose=False):
        """[specific flow to add entries into samples table]

        Args:
            rows_info ([dict]): [dict with info to be updated]
            schema ([string]): [schema name]
            table ([string]): [table name]
            verbose (bool, optional): [to print or not the content of rows_info]. Defaults to False.

        Raises:
            ValueError: [In case the entry weren't added to the database]
        """
        for entry in rows_info:
            target = int(entry["samp_serial"])
            old_id = int(entry["old_id"])
            part = True if not entry["sample_group"] == "G" else False

            query = self.session.query(Patient).filter(Patient.old_id == old_id,
                                                       Patient.particular == part)
            check = self.query_values(self.session, target=target,
                                      column='samp_serial', schema=schema,
                                      table=table, _type="scalar")

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

    def exams_flow(self, rows_info, schema, table, verbose=False):
        """[specific flow to add entries into exams table]

        Args:
            rows_info ([dict]): [dict with info to be updated]
            schema ([string]): [schema name]
            table ([string]): [table name]
            verbose (bool, optional): [to print or not the content of rows_info]. Defaults to False.

        Raises:
            ValueError: [In case the entry weren't added to the database]
        """
        for entry in rows_info:
            target = int(entry["exam_serial"])
            old_id = int(entry["old_id"])
            part = entry["sample_group"]

            query = self.session.query(Samples).filter(Samples.old_id == old_id,
                                                       Samples.sample_group == part)

            check = self.query_values(self.session, target=target,
                                      column='exam_serial', schema=schema,
                                      table=table, _type="scalar")
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

    def row_count(self, session, table="users_table"):
        """[get row count of table table]

        Args:
            session ([session]): [connection session]
            table (str, optional): [table name]. Defaults to "users_table".

        Returns:
            [int]: [row number]
        """
        if table == "users_table":
            rows = session.query(func.count(User.ID)).scalar()
        elif table == "Badword":
            rows = session.query(func.count(Badwords.ID)).scalar()
        elif table == "samples_table":
            rows = session.query(func.count(Samples.ID)).scalar()
        elif table == "patients_table":
            rows = session.query(func.count(Patient.ID)).scalar()
        elif table == "exams_table":
            rows = session.query(func.count(Exams.ID)).scalar()
        elif table == "projects_table":
            rows = session.query(func.count(Projects.ID)).scalar()
        return rows

    def col_info(self, session, schema="db_sampat_schema", table="patients_table"):
        """[get columns info from table]

        Args:
            session ([session]): [connection session]
            schema (str, optional): [schema name]. Defaults to "db_sampat_schema".
            table (str, optional): [table name]. Defaults to "patients_table".

        Returns:
            [list]: [columns from table]
        """
        insp = reflection.Inspector.from_engine(self.engine)
        col_info = insp.get_columns(table, schema)
        return col_info

    # back-end method used to add entries to the badword table, it accepts both lists and strings
    def populate_badword(self, session, badword):
        """[add badwords to table badwords]

        Args:
            session ([session]): [connection session]
            badword ([list, str]): [badword to be added]
        """
        if type(badword) == list:
            for item in badword:
                new_bad = Badwords(badword=item)
                session.add(new_bad)
        else:
            print(badword)
            new_bad = Badwords(badword=badword)
            session.add(new_bad)
        session.commit()

    def close_conn(self, session):
        """[close the session]

        Args:
            session ([session]): [connection session]
        """
        logging.info("SQL Session closed.")
        session.close()

# class that defines the User table in the database, it follows the sqlalchemy guidelines
class User(Base):
    """[define User table on database]
    """
    __tablename__ = 'users_table'
    __table_args__ = {'schema': "db_user_schema"}

    ID = Column('ID', Integer, primary_key=True)
    login = Column('Login', String)
    password = Column('Senha', String)
    name = Column('Nome', String)
    surname = Column('Sobrenome', String)
    nvl = Column('Nível', String)
    other_spec = Column('Outros', String)
    email = Column('E-Mail', String)
    date = Column('Data', Date)

    def __repr__(self):
        return "login={},password={},name={},surname={},nvl={},"\
               "other_spec={},email={},date={}".format(self.login, self.password, self.name,
                                                       self.surname, self.nvl, self.other_spec,
                                                       self.email, self.date)

# class that defines the Badword table in the database, it follows the sqlalchemy guidelines
class Badwords(Base):
    """[define Badwords table on database]
    """
    __tablename__ = 'badwords'
    __table_args__ = {'schema': "db_user_schema"}

    id = Column(Integer, primary_key=True)
    badword = Column(String)

    def __repr__(self):
        return "badword={}".format(self.badword)

# class that defines the main db in the server, it follows the sqlalchemy guidelines
class Patient(Base):
    """[define Patient table on database]
    """
    __tablename__ = 'patients_table'
    __table_args__ = {'schema': "db_sampat_schema"}

    ID = Column('ID', Integer, primary_key=True, unique=True, nullable=False)
    # old_id = Column("barcode", Integer, unique=False)
    samples = relationship("Samples", backref='sample_owner')
    particular = Column('Particular?', Boolean, default=False, unique=False, nullable=False)
    first_name = Column('Primeiro Nome', String, default=None)
    #second_name = Column(, String, default=None)
    surname = Column('Sobrenome', String, default=None)
    rn = Column('RN?', Boolean, default=False, unique=False)
    nt = Column('NT?', Boolean, default=False, unique=False)
    rg = Column('Documento', String, default=None)
    registry = Column('Registro', String, default=None)
    birth_date = Column('Data Nasc.', Date, default=None)
    register_date = Column('Data de Registro', Date, default=None)
    pat_origin = Column('Origem Paciente', String, default=None)
    doctor = Column('Médico Resp.', String, default=None)
    parent_type = Column('Parentesco', String, default=None)
    parent = Column('Parente', String, default=None)
    lib = Column('Liberado?', Boolean, default=False, unique=False, nullable=False)
    diag_hipt = Column('Hipótese Diagn.', String, default=None)
    term = Column('Termo de Cons.', Boolean, default=False, unique=False, nullable=False)
    gen = Column('Genótipo', String, default=None)
    karyotype = Column('Cariótipo', String, default=None)
    obs = Column('Observações', String, default=None)
    updated = Column(DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return rep_gen(self)

class Samples(Base):
    """[define Samples table on database]
    """
    __tablename__ = 'samples_table'
    __table_args__ = {'schema': "db_sampat_schema"}

    ID = Column('ID', Integer, primary_key=True, unique=True, nullable=False)
    barcode = Column('Cod. Barras', Integer, default=None, unique=True)
    # old_id = Column(Integer, unique=False)
    sample_group = Column('Grupo de Amostras', String, default=None)
    samp_serial = Column('Sequencial de Amostra', Integer, default=None, unique=True)
    patient_id = Column('ID Paciente', Integer, ForeignKey('db_sampat_schema.patients_table.ID'), nullable=False)
    exams = relationship('Exams', backref='master_sample')
    sample_orign = Column('Origem da Amostra', String, default=None)
    cap_color = Column('Tubo/Tampa', String, default=None)
    material_type = Column('Tipo de Material', String, default=None)
    material_volume = Column('Volume', Float, default=None)
    main_tube = Column('Tubo Mãe', Boolean, default=False, unique=False, nullable=False)
    aliquot = Column('Alíquota?', Boolean, default=False, unique=False, nullable=False)
    aliquot_id = Column('ID Alíquota', Integer, default=None, nullable=True)
    extracted = Column('Extraído?', Boolean, default=False, unique=False, nullable=False)
    processed = Column('Processado', Boolean, default=False, unique=False, nullable=False)
    arquived = Column('Arquivado?', Boolean, default=False, unique=False, nullable=False)
    arquiv_date = Column('Data de Arquivamento', Date, default=None, nullable=True)
    arq_position = Column('Posição Arquivada', String, default=None)
    sample_register_date = Column('Data de Cadastro', Date, default=None)
    sample_extraction_date = Column('Data de Extração', Date, default=None)
    sample_process_date = Column('Data de Processamento', Date, default=None)
    sample_aliquot_date = Column('Data da Alíquota', Date, default=None)
    sample_dna_concentration = Column('Concentração', Float, default=None)
    sample_dna_quality = Column('Pureza', Float, default=None)
    recall = Column('Recoleta?', Boolean, default=False, nullable=False)
    recall_date = Column('Data de Recoleta', Date, default=None, nullable=True)
    #recall_sample_id = Column(Integer, default=None, nullable=True)
    #recall_register_date = Column(Date, default=None, nullable=True)
    lib_date = Column('Data de Liberação', Date, default=None)
    lib = Column('Liberado?', Boolean, default=False, unique=False, nullable=False)
    obs = Column('Observações', String, default=None)
    updated = Column(DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return rep_gen(self)

class Exams(Base):
    """[define Exams table on database]
    """
    __tablename__ = 'exams_table'
    __table_args__ = {'schema': "db_sampat_schema"}

    ID = Column('ID', Integer, primary_key=True, unique=True, nullable=False)
    sample_id = Column('ID Amostra', Integer, ForeignKey('db_sampat_schema.samples_table.ID'), nullable=False, unique=True)
    exam_serial = Column('Sequencial', Integer, default=None, unique=True)
    sample_exam = Column('Exame', String, default=None)
    run_number = Column('Núm. Rotina', Integer, default=None)
    #seq_number = Column(Integer, default=None)
    run_letter = Column('ID da Rotina', String, default=None, unique=False)
    kit = Column('Kit', String, default=None)
    kit_lot = Column('Lote do Kit', String, default=None)
    platform = Column('Plataforma', String, default=None)
    results = Column('Resultados', String, default=None)
    lib_date = Column('Data de Liberação', Date, default=None)
    lib = Column('Liberado?', Boolean, default=False, unique=False, nullable=False)
    obs = Column('Observações', String, default=None)
    updated = Column(DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return rep_gen(self)

class Projects(Base):
    """[define Projects table on database]
    """
    __tablename__ = 'projects_table'
    __table_args__ = {'schema': "db_sampat_schema"}

    ID = Column('ID', Integer, primary_key=True, unique=True, nullable=False)
    project_name = Column('Nome do Projeto', String, default=None, unique=True)
    short_descriptor = Column('Descrição Simples', String, default=None)
    lead_researcher = Column('Pesquisador Chefe', String, default=None)
    coord = Column('Orientação/Coord.', String, default=None)
    institution = Column('Instituição', String, default=None)
    fund = Column('Fomento?', Boolean, default=False, unique=False)
    fund_name = Column('Agência de Fomento', String, default=None)
    fund_id = Column('Registro do Fomento', String, default=None)
    long_descriptor = Column('Descrição do Projeto', String, default=None)
    obs = Column('Observações', String, default=None)
    updated = Column(DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return rep_gen(self)

# a plain function that initialize the SQL class and outputs the instance and session
def str_to_table(schema, table):
    """[transform string table into class object table]

    Args:
        schema ([string]): [schema name]
        table ([string]): [table name]

    Returns:
        [object]: [table object]
    """
    '''# for item in Base._decl_class_registry.values():
    # if hasattr(item, '__table__') and item.__table__.fullname == "{}.{}".format(schema, table):
        return item'''
    for item in Base.registry.mappers:
        if item.class_.__tablename__ == table.lower():
            return item.class_

def str_to_column(table, column):
    """[transform string column into class object table.column]

    Args:
        table ([string]): [table name]
        column ([string]): [column name]

    Returns:
        [object]: [column object]
    """
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
    """[method to generate how the table classes generate its __repr__ method]

    Args:
        ncls ([list]): [class keys]

    Raises:
        NameError: [In case the class doesn't exist]

    Returns:
        [string]: [__repr__ string]
    """
    try:
        if type(ncls) == str:
            _cls = eval(ncls)
        else:
            _cls = ncls
    except:
        raise NameError("Class not found")
    cl_keys = [key for key in _cls.__dict__.keys() if not "_" in key]
    repr_str = "={},".join(cl_keys) + "={}"
    cls_attr = [getattr(_cls, key) for key in cl_keys]
    return repr_str.format(*cls_attr)
