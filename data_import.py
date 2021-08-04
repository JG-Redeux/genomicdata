# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 14:30:46 2018

Code created to modify the main source of data for the database into an uniform model
and send to the database.

@author: Jullian G. Damasceno
"""

# flake8: noqa

import os
import pandas as pd
import logging
import re
import numpy as np

logger = logging.getLogger(__name__)

path = "D:/Trabalho/codpython/Project GD/planilhas/"
filexlsx = path + "_DNAteca particular 2017-08-31.xlsx"
filecsv = path + "pat_toda_dnateca_projpart.csv"
filetxt = path + "subset_dnateca.txt"
filesamp = path + "samp_subset.csv"
filesamp2 = path + "samp_toda_dnateca_projpart.csv"

def path_checker(path):
    """[Check if path is valid]

    Args:
        path ([string]): [path]

    Raises:
        Exception: [In case path does not exist]

    Returns:
        [string]: [path]
    """
    if "\\" in path:
        path.replace("\\", "/")
        return path
        
    if os.path.exists(path):
        return path
    else:
        raise Exception("Path does not exist")

def file_size(file):
    """[Check file size]

    Args:
        file ([string]): [file path]

    Returns:
        [int]: [file size]
    """
    return os.stat(file).st_size

#TODO fix xlsx import table
def import_table(file, sep = ","):
    """[Import table (csv or xlsx) into memory]

    Args:
        file ([string]): [file path]
        sep (str, optional): [separator character that should be used]. Defaults to ",".

    Returns:
        [dataframe]: [the table imported]
    """
    file_path = path_checker(file)
    fsize = file_size(file_path)
    chunk = fsize//100
    file_ext = file_path.split(".")[1]
    
    gen = True if fsize > 2*(10**8) else False
    
    if file_ext.lower() == "csv":
        try:
            if not gen:
                df = pd.read_csv(file_path, sep = sep, encoding = "ISO-8859-1",
                                 na_values = np.NaN)
            else:
                df = pd.read_csv(file_path, sep = sep, encoding = "ISO-8859-1", 
                                 na_values = False, iterator = True, chunksize = chunk)
            logger.info("ITAPI - csv imported: {}".format(file_path))
        except:
            try:
                if not gen:
                    df = pd.read_csv(file_path, sep = sep, na_values = False)
                else:
                    df = pd.read_csv(file_path, sep = sep, na_values = False, 
                                 iterator = True, chunksize = chunk)
                logger.info("ITAPI - csv imported: {}".format(file_path))
            except UnicodeDecodeError as UDE_ERROR:
                logger.warning("ITAPI - CSV import error")
                return UDE_ERROR  
    elif file_ext.lower() == "xlsx":
        try:
            if not gen:
                df = pd.read_excel(file_path, converters={"Date": pd.NaT.date()}, na_values = np.NaN)
            else:
                df = pd.read_excel(file_path, converters={"Date": pd.NaT.date()}, na_values = np.NaN, 
                                   iterator = True, chuncksize = chunk)
                df[df.columns[4]].dt.strftime('%d-%m-%Y')
                
            logger.info("ITAPI - xlsx imported: {}".format(file_path))
        except:
            logger.warning("ITAPI - xlsx import error")
            #raise Exception("ITAPI - xlsx import error")
    elif file_ext.lower() == "txt":
        try:
            if not gen:
                df = pd.read_table(file_path, encoding = "ISO-8859-1", na_values = np.NaN)
            else:
                df = pd.read_table(file_path, encoding = "ISO-8859-1", na_values = np.NaN,
                                   iterator = True, chunsize = chunk)
        except:
            try:
                if not gen:
                    df = pd.read_table(file_path, na_values = np.NaN)
                else:
                    df = pd.read_table(file_path, iterator = True, chunksize = chunk,
                                       na_values = np.NaN)
            except UnicodeDecodeError as UDE_ERROR:
                logger.warning("ITAPI - CSV import error")
                return UDE_ERROR 
        logger.info("ITAPI - txt imported: {}".format(file_path))
    
    df.dropna(how="all", axis = 0, inplace = True)
    df.dropna(how="all", axis = 1, inplace = True)
        
    return df

def normalize_reg(df, col = 1):
    """[Normalize columns]

    Args:
        df ([dataframe]): [dataframe to normalize]
        col (int, optional): [the columns which to normalize]. Defaults to 1.

    Returns:
        [dataframe]: [dataframe with normalized col column]
    """
    try:
        df_sep = pd.DataFrame(df[df.columns[col]].astype(str).str.split(' ', 1).tolist(),
                                columns = ['real', 'fake'])
        df_sep.drop("fake", axis=1, inplace=True)
        df_sep2 = pd.DataFrame(df_sep['real'].str.split('-', 1).tolist(),
                               columns = ['sample_group', 'old_id'])
        return df_sep2
    except:
        pass
        
    df_sep2 = pd.DataFrame(df[df.columns[col]].str.split('-', 1).tolist(),
                               columns = ['sample_group', 'old_id'])
    return df_sep2

def normalize_names(df):
    """[Normalize columns]

    Args:
        df ([dataframe]): [dataframe to normalize]

    Returns:
        [dict]: [dict of normalized names]
    """
    fname = []
    #TODO mname está errado
    mname = []
    sname = []
    
    pat = 'd[\w]+'
    
    df_names = df["Nome"].str.split(' ', 3).tolist()
    for name in df_names:
        if str(name) == "nan":
            fname.append(None)
        else:
            nindex = [nindex for nindex in range(len(name)) if re.match(pat, name[nindex])]
            nlen = len(nindex)
            if nlen == 0:
                fname.append(name[0])
                try:
                    mname.append(name[1])
                except IndexError:
                    pass
                if len(name) > 2:
                    sname.append(" ".join(name[2:]))
                else:
                    sname.append(np.NaN)
            else:
                fname.append(name[0])
                if nindex[0] == 1:
                    mname.append(" ".join([name[1], name[2]]))
                    sname.append(" ".join(name[3:]))
                else:
                    mname.append(name[1])
                    sname.append(" ".join(name[2:]))
        
    for i in range(len(fname)):
        try:
            mname[i]
        except IndexError:
            mname.append(np.NaN)
        
        try:
            sname[i]
        except IndexError:
            sname.append(np.NaN)
    return {"first_name": fname, "second_name": mname, "surname": sname}
    
def normalize_parents(df):
    """[Normalize columns]

    Args:
        df ([dataframe]): [dataframe to normalize]

    Returns:
        [dataframe]: [normalized dataframe]
    """
    df_prt = pd.DataFrame(df[df.columns[8]], dtype = str)
    df_prt = pd.DataFrame(df_prt[df_prt.columns[0]].
                             str.replace(' de ', ' '))
    
    df_prt2 = pd.DataFrame(df_prt['Parentesco'].str.split(' ', 1).tolist(),
                           columns = ['parent_type', 'parent'], dtype = str)
    return df_prt2

def normalize_dates(df, table):
    """[Normalize columns]

    Args:
        df ([dataframe]): [dataframe to normalize]
        table ([type]): [table that should guide the normalization method]

    Raises:
        ValueError: [in case table doesn't exist or isn't as expected]

    Returns:
        [dict, dataframe]: [dict with normalized dates and column dataframe with dates]
    """
    if table == "patients":
        
        df_date = pd.DataFrame(df[df.columns[4]].astype(str).str.split(' e ', 1).tolist(),
                              columns = ["date", "drop"])
        df_date["date"].replace("nan", pd.Timestamp('01/01/1900'), inplace = True)
        df_date.drop(df_date.columns[1], axis = 1, inplace = True)
        return df_date.astype('datetime64[ns]')
    elif table == "samples":
        df_date = pd.DataFrame(df[df.columns[5]].astype(str).str.split(' e ', 3).tolist())
        date_dict = {}
        for i in range(len(df_date)):
            row = df_date.iloc[i,:].tolist()
            date = []
            for j in row:
                if j:
                    date.append(j)
            date_dict[i] = date
        return date_dict, df_date
    else:
        raise ValueError("Table must be 'patients' or 'samples'")

def df_to_dict(df, orient=None):
    """[lazy function to write the pandas method in another way, why? reasons]

    Args:
        df ([dataframe]): [dataframe to be converted to dict]
        orient ([string]): [the way the dict should be created]

    Returns:
        [dict]: [dict converted dataframe]
    """
    if type:
        return df.to_dict(orient=type)
    else:
        return df.to_dict()

def drop_columns(df, default, label, *columns):
    """[function to drop specified columns in dataframe]

    Args:
        df ([dataframe]): [dataframe to drop columns]
        default ([boolean]): [guide the way columns should be dropped]
        label ([boolean]): [guide the way columns should be dropped]

    Returns:
        [type]: [description]
    """
    columns = list(columns)
    if default:
        dfdrop = df.drop(df.columns[list(range(12,37)) + 
                                    list(range(39, 41)) +
                                    list(range(41, 44)) +
                                    list(range(45, len(df.columns))) +
                                    [1, 3, 4, 5, 7, 8]], axis = 1, inplace = False)
    else:
        if label:
            dfdrop = df.drop(df[columns], axis = 1, inplace = False)
        else:
            dfdrop = df.drop(df.columns[columns], axis = 1, inplace = False)
    return dfdrop

def create_default_cols(df):
    """[create dict with col info from df]

    Args:
        df ([dataframe]): [dataframe to create columns]

    Returns:
        [dict]: [dict with specified normalized info from dataframe]
    """
    col_dict = {}
        
    rn_index = df.loc[df["Nome"].str.contains("rn", case = False, na = False)].index
    rn_list = [False if not i in rn_index else True for i in range(0, len(df))]
    col_dict["rn"] = rn_list
    return col_dict

def add_missing_cols(*cols_dict):
    """[create dataframe from columns information from cols_dict]

    Returns:
        [dataframe]: [dataframe with column infos]
    """
    new_cols = [pd.DataFrame(x) for x in list(cols_dict)]
    new_df = pd.concat(new_cols, axis = 1, join = "inner")
    return new_df

def exam_col_divider(df):
    """[change df and append into list]

    Args:
        df ([dataframe]): [dataframe]

    Returns:
        [list]: [list with dataframes]
    """
    df_lists = []
    kit_cols = list(range(2,25,2))
    for ind in kit_cols:
        ndf = df.iloc[:,[0, 1, -1, -2, -3] + list(range(ind, ind+2))]
        df_lists.append(ndf.copy())
    return df_lists

def exam_col_concat(df_list, nreg_df):
    """[merge dataframes from df_list and output a list with merged dataframes]

    Args:
        df_list ([list]): [list of dataframes]
        nreg_df ([dataframe]): [dataframe to merge into]

    Returns:
        [type]: [description]
    """
    ndf_list = []
    for df in df_list:
        kit_list = ["P064", "P036", "P070", "P250", "P356", "P029", 
                    "P095", "P245", "P201", "P060", "P034", "P035"]
        df["kit"] = kit_list[len(ndf_list)]
        ndf_list.append(pd.concat([df, nreg_df], axis = 1))
    return ndf_list

def exam_fix_tables(df_list):
    """[get dataframes from df_list and fix come columns data]

    Args:
        df_list ([list]): [list with dataframes]

    Returns:
        [dataframe]: [merged dataframe]
    """
    fixed_dfs = []
    for df in df_list:
        df.rename(columns = {"Teste":"sample_exam", "Nº da corrida":"run_number",
                                "Outros Laudos": "other_reports",
                                "Laudo P250 e P356":"P250_P356_rep",
                                "P036 e P070": "P036_P070_rep",
                                df.columns[5]: "kit_lot", df.columns[6]: "results"}, inplace = True)
        ndf = df[pd.notnull(df.iloc[:, -4])]
        fixed_dfs.append(ndf)
    
    cat_df = pd.concat(fixed_dfs, axis = 0)
    return cat_df

def norm_run_number(df):
    """[normalize columns]

    Args:
        df ([dataframe]): [dataframe to normalize]

    Returns:
        [dataframe]: [normalized dataframe]
    """
    df["run_letter"] = df["run_number"].str.extract(r'(\D)', expand = True)
    df["run_number"] = df["run_number"].str.extract(r'(\d)', expand = True)
    return df

def remodel_pat_table(file, sep = None):
    """[import table and remodel into the patients dataframe]

    Args:
        file ([string]): [csv or xlsx file path]
        sep ([string], optional): [separator to be used when importing dataframe]. Defaults to None.

    Returns:
        [dataframe]: [remodeled and reindexed dataframe]
    """
    if type(file) == str:
        df = import_table(file, sep = sep)
    else:
        df = file
        
    nreg_dict = df_to_dict(normalize_reg(df))
    nprt_dict = df_to_dict(normalize_parents(df))
    nnames_dict = normalize_names(df)
    date_dict = normalize_dates(df, "patients")
    dft_dict = create_default_cols(df)
    dropdf = drop_columns(df, True, False)
    df_final = add_missing_cols(dropdf, nreg_dict, nprt_dict, nnames_dict,
                                dft_dict, date_dict)
    df_final.rename(index = str, 
                    columns = {"Procedência": "pat_origin", "date": "register_date",
                     "Data da coleta": "sample_register_date", 
                     "Remetente": "doctor", "RG": "rg", "DN": "birth_date",
                     "Citogenética": "karyotype", "TC": "term","Observação": "obs",
                     "RGHC": "registry"}, 
                    inplace = True)
    
    #df_final.replace(np.nan, "NULL", inplace = True)
    df_final["term"] = df_final["term"].map({"sim": True, "não": False})
    df_final.fillna(value = False, inplace = True)
    df_final["birth_date"].replace(False, pd.Timestamp('01/01/1900'), inplace = True)
    return df_final.reindex()

def remodel_samp_table(file, sep = None):
    """[import table and remodel into the samples dataframe]

    Args:
        file ([string]): [csv or xlsx file path]
        sep ([string], optional): [separator to be used when importing dataframe]. Defaults to None.

    Returns:
        [dataframe]: [remodeled and reindexed dataframe]
    """
    #TODO função
    if type(file) == str:
        df = import_table(file, sep = sep)
    else:
        df = file
        
    date_dict, sdates = normalize_dates(df, "samples")  
    new_dates = pd.concat([sdates, df[df.columns[1]]], axis = 1)
    
    new_dates_melt = new_dates.melt(id_vars = "n° genética", var_name = "Value",
                         value_name = "sample_register_date")
    new_dates_melt.sort_values(by=["n° genética"]).reset_index(drop=True)
    new_dates_melt.dropna(inplace = True)
    
    ndm_df = pd.concat([new_dates_melt, normalize_reg(new_dates_melt, 0)], axis = 1).dropna()
    
    df_final = drop_columns(ndm_df, False, False, [0, 1])
    df_final.sort_values(by=["old_id"])
    df_final["samp_serial"] = np.arange(df_final.shape[0])
    df_final["sample_register_date"].replace("nan", pd.Timestamp('01/01/1900'), inplace = True)
    return df_final.reindex()

def remodel_exams_table(file, sep = None):
    """[import table and remodel into the exams dataframe]

    Args:
        file ([string]): [csv or xlsx file path]
        sep ([string], optional): [separator to be used when importing dataframe]. Defaults to None.

    Returns:
        [dataframe]: [remodeled and reindexed dataframe]
    """
    
    if type(file) == str:
        df = import_table(file, sep = sep)
    else:
        df = file
        
    drop_list = [0, 1, 2, 37, 38, 39, 40] + list(range(4,12)) + list(range(44, len(df.columns)))
    nreg_df = normalize_reg(df)
    ndf = drop_columns(df, False, False, drop_list)
   
    df_list = exam_col_divider(ndf)
    col_df_list = exam_col_concat(df_list, nreg_df)
    
    fdf = exam_fix_tables(col_df_list)
    fdf = norm_run_number(fdf)
    fdf.fillna(value = False, inplace = True)
    
    fdf["lib"] = fdf["other_reports"].map(bool) | fdf["P250_P356_rep"].map(bool) | fdf["P036_P070_rep"].map(bool)
    fdf["lib_date"] = fdf["other_reports"].map(str) + fdf["P250_P356_rep"].map(str) + fdf["P036_P070_rep"].map(str)
    fdf['lib_date'] = fdf["lib_date"].str.extract(r'(\d+/\d+/\d+)', expand = True)
    fdf["lib_date"] = fdf["lib_date"].astype(str)
    fdf["lib_date"].replace("nan", pd.Timestamp('01/01/1900'), inplace = True)
    fdf["exam_serial"] = np.arange(fdf.shape[0])
    fdf["kit_lot"] = fdf["kit_lot"].astype(str)
    fdf["run_number"].replace(False, 0, inplace = True)
    final_df = drop_columns(fdf, False, False, [2, 3, 4])
    return final_df.reindex()

def dict_popper(dicty, pop_target):
    """[pop pop_targets from dict dicty, cool names yeah?]

    Args:
        dicty ([dict]): [dict to pop keys]
        pop_target ([list]): [list with keys to pop]

    Returns:
        [type]: [description]
    """
    for item in dicty:
        for col in pop_target:
            item.pop(col, None)
     
        for k, v in item.items():
            if v == "nan":
                item[k] = False          
    return dicty

#patdf = remodel_pat_table(filecsv, sep = ";")
#sampdf = remodel_samp_table(filecsv, sep = ";")
#examdf = remodel_exams_table(filecsv, sep = ";")

#df = import_table(filecsv, sep = ";")
#dfn = normalize_dates(df, "patients")
