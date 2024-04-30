#from email import message
import sqlite3
import pandas as pd
import streamlit as st
import os.path
import pickle
from datetime import date,timedelta
from datetime import datetime
import numpy as np
from os.path import join, dirname, abspath
#db_path = join(dirname(dirname(abspath(__file__))), 'autoaudit.db')
db_path='autoaudit.db'
def create_user(Name,user,password,designation):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #st.success("Done1")
        #add DS name in table
        sqlite_insert_with_param = """INSERT INTO Users
                          (Name,user,password,designation,Created_by) 
                          VALUES (?,?,?,?,?);"""
        data_tuple = (Name,user,password,designation,st.session_state['User'])
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        
        cursor.close()
        message_verify="User Created..."
    except sqlite3.Error as error:
        message_verify=error
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def get_audit_by_com(comp_name,audit):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT id from Audit where Company_name='{comp_name}' AND Audit_Name ='{audit}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        auditid = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        auditid=error
        st.error(auditid)
    except :
        auditid="Run time Error...Invalid Input or Data type Mismatch"
        st.error(auditid)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return auditid
    
    
def check_login(username,password,comp_name,role,audit) :
    try:
        sqliteConnection = sqlite3.connect(db_path)
        if username!="admin":
            #check if licence is not expired
            if os.path.isfile('file.pkl'):
                with open('file.pkl', 'rb') as file:
                            # Call load method to deserialze
                    exp_date = pickle.load(file) 
                if exp_date < date.today():  
                    st.error("Licenec has Expired...Please Contact to Renew the Licence...")     
                    return False
                    #gdruve="https://drive.google.com/file/d/18c0EASbKEC3vDXzVLJqzkeJj9mz0uPoe/view?usp=sharing"
                else:  
                    #sqliteConnection = sqlite3.connect(gdruve)
                    cursor = sqliteConnection.cursor()
                    cursor.execute(f"SELECT password from Users where user='{username}'")
                    passworddb=cursor.fetchone()
                    #print(passworddb[0])
                    cursor.close()
                    sqliteConnection.close()
                    #st.write(passworddb[0])
                    if passworddb:
                        if passworddb[0]==password:
                            st.session_state['loggedIn'] = True
                            st.session_state['User']=username
                            st.session_state['Company']=comp_name
                            st.session_state['Role']=role
                            st.session_state['Audit']=audit
                            auditid=get_audit_by_com(comp_name,audit)
                            audit_id=auditid['id'].values[0]
                            st.session_state['AuditID']=audit_id
                            #st.session_state['url']='https://google.com'
                            return True
                        else:
                            st.session_state['loggedIn'] = False
                            st.success("Invalid password")
                            return False
                    else:
                        st.session_state['loggedIn'] = False
                        st.success("Invalid user name ")
                        return False
            else:
                st.error("Licence Invalid...")
                return False
        else:   
            if password=="AutoAdmin":
                #st.success("Admin")
                st.session_state['loggedIn'] = True
                st.session_state['User']="admin"
                st.session_state['Company']=""
                st.session_state['Role']="admin"
                st.session_state['Audit']="audit"
                st.session_state['AuditID']="0"
                return True
            else:
                st.success("Invalid password")
                return False

               
    except sqlite3.Error as error:
        if sqliteConnection:
            sqliteConnection.close()
        st.error(error)
        return False
    except :
        st.error("Error...")
        return False

    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
def create_company(comp_name, com_address,com_email,com_mobile,com_person):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #st.success("Done1")
        #add DS name in table
        sqlite_insert_with_param = """INSERT INTO Company
                          (Name,Address,email,mobile,contact_person,Created_by) 
                          VALUES (?,?,?,?,?,?);"""
        data_tuple = (comp_name, com_address,com_email,com_mobile,com_person,st.session_state['User'])
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        #st.success("Company created...")
        message_verify=("Company created...")
        cursor = sqliteConnection.cursor()
        #st.success("Done1")
        #add DS name in table
        sqlite_insert_with_param = """INSERT INTO Users_Rights
                          (user,company_name,role) 
                          VALUES (?,?,?);"""
        data_tuple = (st.session_state['User'],comp_name,'Manager')
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        message_verify="Company created successfully ..."
        
    except sqlite3.Error as error:
        message_verify=error
        st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify
    
def add_datato_ds(df,table_name,comp_name):
    try:
        #ds=table_name
        table_name= f"{st.session_state['AuditID']}_{table_name}"
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        df.to_sql(table_name,sqliteConnection,if_exists='append', index=False)
        message=("Data Set Appended Successfully")
        sqliteConnection.commit()
        cursor.close()
        
    except sqlite3.Error as error:
        message=error
    except ValueError as error:
        message=error
        st.error("Values Mismatch...Data Set NOT Appended ")
    except :
        message="Run time Error...Invalid Input or Data type Mismatch"
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message

def assign_user_rights(user,company_name,role):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #st.success("Done1")
        #add DS name in table
        sqlite_insert_with_param = """INSERT INTO Users_Rights
                          (user,company_name,role) 
                          VALUES (?,?,?);"""
        data_tuple = (user,company_name,role)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        #st.success("User Rights Assigned...")
        message_verify=("User Rights Assigned...")
    except sqlite3.Error as error:
        message_verify=error
        #st.error(error)
        #st.success(company_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def create_dataset(df,table_name,comp_name,person_responsible):
    try:
        
        sqliteConnection = sqlite3.connect(db_path)
        ds=table_name
        currentime=str(datetime.now())[:19]
        table_name= f"{st.session_state['AuditID']}_{table_name}"
        cursor = sqliteConnection.cursor()
        df.to_sql(table_name,sqliteConnection,if_exists='fail', index=True)
        message=("Data Set created Successfully")
        sqliteConnection.commit()
        cursor.close()
        #add DS name in table
        cursor = sqliteConnection.cursor()
        sqlite_insert_with_param = """INSERT INTO DSName
                          (DS,company_name,person_responsible,created_by,cretaed_on,Audit_Name,Audit_id) 
                          VALUES (?,?,?,?,?,?,?);"""
        data_tuple = (ds,comp_name,person_responsible,st.session_state['User'],currentime,st.session_state['Audit'],int(st.session_state['AuditID']))
        cursor.execute(sqlite_insert_with_param,data_tuple)
        sqliteConnection.commit()
        cursor.close()
        message=("Data Set Added Successfully")
        # Alter table to add  audit status
        cursor = sqliteConnection.cursor()
        cursor.execute(f"ALTER TABLE '{table_name}' ADD AutoAudit_Status TEXT NOT NULL DEFAULT 'Unaudited'")
        sqliteConnection.commit()
        cursor.close()
        # Alter table to add  audit Sampled?
        cursor = sqliteConnection.cursor()
        cursor.execute(f"ALTER TABLE '{table_name}' ADD AutoAudit_Sampled TEXT NOT NULL DEFAULT 'No'")
        sqliteConnection.commit()
        cursor.close()
        # add default risk to risk master table
        #get list of columns in df
        sqliteConnection.close()
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        cols=list(df.columns)
        risk_df=pd.DataFrame(cols,columns=['Field'])
        risk_df=risk_df.applymap(str)
        risk_df['audit_id']=int(st.session_state['AuditID'])
        risk_df['DataSetName']=ds
        risk_df['created_by']=st.session_state['User']
        risk_df['created_on']=currentime
        #st.success(list(risk_df.columns))
        #st.dataframe(risk_df)
        #risk_df['Criteria']=f"'{risk_df['Field']}': should be Correct"
        risk_df['Criteria']=(risk_df['Field'])+': should be Correct'
        #st.dataframe(risk_df)
        risk_df.to_sql("Risk_Master",sqliteConnection,if_exists='append', index=False)
        #st.write('okkkkkk')
        sqliteConnection.commit()
        cursor.close()
    except sqlite3.Error as error:
        st.error(error)
        if "Error binding parameter" in error.__str__():
            #st.error("got it")
            sqlite_insert_with_param = f"DROP TABLE if EXISTS {table_name}"
            cursor.execute(sqlite_insert_with_param)
            sqliteConnection.commit()
            cursor.close()
            
        message="Error in Dataset Creation"
    #except ValueError:
        #DROP TABLE if EXISTS Test_1_jsontf
    #except :
        #message("Run time Error...Invalid Input or Data type Mismatch")
    finally:
        
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message

def add_verification_criteria (Criteria,DsName,comp_name,risk_weight,risk_category):
    
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #st.success("Done1")
        #add DS name in table
        
        currentime=str(datetime.now())[:19]
        sqlite_insert_with_param = """INSERT INTO DSCriteria
                          (Verification_Criteria,DSName,Risk_Weight,Risk_Category,CompanyName,created_by,created_on,Audit_Name,Audit_id) 
                          VALUES (?,?,?,?,?,?,?,?,?);"""
        data_tuple = (Criteria,DsName,risk_weight,risk_category,comp_name,st.session_state['User'],currentime,st.session_state['Audit'],int(st.session_state['AuditID']))
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        
        #Add in risk master
        sqlite_insert_with_param = """INSERT INTO Risk_Master
                          (Criteria,DataSetName,Risk_Weight,created_by,created_on,Audit_id,Risk_Category) 
                          VALUES (?,?,?,?,?,?,?);"""
        data_tuple = (Criteria,DsName,risk_weight,st.session_state['User'],currentime,int(st.session_state['AuditID']),risk_category)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        message_verify = "Criteria Added Successfully.."
        
        cursor.close()
        #st.success(message_verify)
    except sqlite3.Error as error:
        message_verify=error
        #st.write(message_verify)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def get_dsname(auditid):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT DS from DSName where Audit_id='{auditid}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        DSName = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        DSName=error
    except :
        DSName="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return DSName

def get_dsname_personresponsible(auditid,pr):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT DS from DSName where Audit_id='{auditid}' AND person_responsible='{pr}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        DSName = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        DSName=error
    except :
        DSName="Run time Error...Invalid Input or Data type Mismatch"   
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return DSName

def get_dataset(DSname):
    #this is for auditing which is samplled
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from '{DSname}' where AutoAudit_Status ='Unaudited' and AutoAudit_Sampled ='Yes'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"  
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_dataset_nonsampled(DSname):
    #this is for auditing
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from '{DSname}' where AutoAudit_Sampled ='No'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"   
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_dataset_sampled(DSname):
    #this is sampled but not audited
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from '{DSname}' where AutoAudit_Sampled ='Yes' and AutoAudit_Status ='Unaudited'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"    
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df


def get_verification(DSname,Audit_id):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT Verification_Criteria,Risk_Weight,Risk_Category from DSCriteria where DsName='{DSname}' AND Audit_id='{Audit_id}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"  
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_analytical_review (criteria,condition,cause,effect,DsName,comp_name,risk_weight,risk_category,file_name):
    
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #st.success("Done1")
        #add DS name in table
        #table_name="AR_"+DsName
        sqlite_insert_with_param = f"""INSERT INTO Audit_AR
                          (Criteria,Condition,Cause,Effect,DataSetName,CompanyName,Created_on,Risk_Weight,Risk_Category,created_by,Audit_Name,Audit_id,Review_File) 
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);"""
        #to add or less time differenceuse following code
        """currentime=datetime.now()+timedelta(minutes=150)
        currentime=str(currentime)[:19]
        currentime=str(datetime.now()+timedelta(minutes=150))[:19]
        """
        currentime=str(datetime.now())[:19]
        data_tuple = (criteria,condition,cause,effect,DsName,comp_name,currentime,risk_weight,risk_category,st.session_state['User'],st.session_state['Audit'],int(st.session_state['AuditID']),file_name)
        #st.success("Done2")
        
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        st.success("Review Inserted")
        #get list of reviews
        #query=f"SELECT Criteria,Condition,Cause,Effect,Risk_Weight,Risk_Category,Review_File from Audit_AR where DataSetName='{DsName}' and Audit_id='{int(st.session_state['AuditID'])}'"
        #st.write(query)
        #sql_query=pd.read_sql_query(query,sqliteConnection)
        #df = pd.DataFrame(sql_query)
        cursor.close()
        df='Review Inserted'
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df) 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return df

def insert_vouching(df):
     
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        df.to_sql("Audit_Queries",sqliteConnection,if_exists='append', index=False)
            
        sqliteConnection.commit()
        cursor.close()
        vouching=("Audit Vouching added Successfully")
    except sqlite3.Error as error:
        vouching=error
        #st.success(vouching)
    except :
        vouching="Run time Error...Invalid Input or Data type Mismatch"  
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return vouching


def update_audit_status(data_id,DsName):
     
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE '{DsName}' SET AutoAudit_Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus="Audit Status updated...."
    except sqlite3.Error as error:
        auditstatus=error
    except :
        auditstatus="Run time Error...Invalid Input or Data type Mismatch"  
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus

  
def get_queries(auidt_id):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Audit_Queries where Audit_id={auidt_id}"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"    
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_pending_queries(auidt_id):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Audit_Queries where Audit_id={auidt_id} AND Status='Pending' AND (Condition='No' OR Audit_Value IS NOT NULL)"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_entire_dataset(DSname):
    #this is for auditing
    try:
        sqliteConnection = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from '{DSname}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"  
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_audit_verification(df):
    try:
            sqliteConnection = sqlite3.connect(db_path)
            cursor = sqliteConnection.cursor()
            df.to_sql("Audit_Queries",sqliteConnection,if_exists='append', index=False)
            
            sqliteConnection.commit()
            cursor.close()
            message="Audit Verification added Successfully"
            
    except sqlite3.Error as error:
            message=error
    except :
            message="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                #message=("The SQLite connection is closed")
            
    return message

def get_ar(comp_name):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Audit_AR where CompanyName='{comp_name}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_ar_summary():
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"select DataSetName as 'DataSet Name',count(Criteria) as 'Total Remarks',sum(Risk_Weight) as 'Risk Weight' from Audit_AR where audit_id='{int(st.session_state['AuditID'])}' GROUP by DataSetName"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_ar_for_ds(ds_name):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT Criteria,Condition,Cause,Effect,Risk_Weight,Risk_Category,Review_File from Audit_AR where DataSetName='{ds_name}' and Audit_id='{int(st.session_state['AuditID'])}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_company_names():
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        cursor.execute(f"SELECT Name from Company")
        compnamesT=cursor.fetchall()
        #tuple to nap arry convert
        compnames=pd.DataFrame(compnamesT)
        #st.write(compnames)
        cursor.close()
    except sqlite3.Error as error:
        compnames=error
    except :
        compnames="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return compnames

def get_user_rights_created_byMe():
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Users_Rights where user in (SELECT user from Users where is_active='Yes' and Created_by='{st.session_state['User']}')"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        userrights = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        userrights=error
        st.write(userrights)
    except :
        userrights="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(userrights)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return userrights

def get_user_foraudit_task(company_name):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT user from Users_Rights WHERE company_name = '{company_name}' AND role <>'Auditee'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        userrights = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        userrights=error
        st.write(userrights)
    except :
        userrights="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(userrights)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return userrights

def get_user_rights():
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query="SELECT * from Users_Rights"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        userrights = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        userrights=error
        st.write(userrights)
    except :
        userrights="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(userrights)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return userrights

def get_active_users():
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        cursor.execute("SELECT user from Users where is_active='Yes'")
        usersT=cursor.fetchall()
        #tuple to list convert
        users=pd.DataFrame(usersT)
        #st.write(users)
        cursor.close()
    except sqlite3.Error as error:
        users=error
        st.write(users)
    except :
        users="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(users)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return users

def get_active_users_created_by_me():
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        cursor.execute(f"SELECT user from Users where is_active='Yes' and Created_by='{st.session_state['User']}'")
        usersT=cursor.fetchall()
        #tuple to list convert
        users=pd.DataFrame(usersT)
        #st.write(users)
        cursor.close()
    except sqlite3.Error as error:
        users=error
        st.write(users)
    except :
        users="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(users)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return users


def get_auditee_comp():
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT user from Users_Rights where company_name='{st.session_state['Company']}' AND role ='Auditee'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        auditee = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        auditee=error
        st.write(auditee)
    except :
        auditee="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(auditee)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return auditee

def get_audit(compname):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT Audit_Name from Audit where Company_name='{compname}' AND Status ='Open'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        audits = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        audits=error
        st.write(audits)
    except :
        audits="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(audits)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return audits

def get_comp_by_user():
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #if st.session_state['User']:
        query=f"SELECT company_name from Users_Rights where user='{st.session_state['User']}' and role='Manager'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        companies = pd.DataFrame(sql_query)
        cursor.close()

    except sqlite3.Error as error:
        companies=error
        st.write(companies)
    except :
        companies="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(companies)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return companies

def get_comp_created_by_user():
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #if st.session_state['User']:
        query=f"SELECT Name from Company where Created_by='{st.session_state['User']}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        companies = pd.DataFrame(sql_query)
        cursor.close()

    except sqlite3.Error as error:
        companies=error
        st.write(companies)
    except :
        companies="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(companies)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return companies


def creat_audit(Audit_Name,Company_name, Period,Remarks):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #st.success("Done1")
        #add DS name in table
        currentime=str(datetime.now())[:19]
        sqlite_insert_with_param = """INSERT INTO Audit
                          (Audit_Name,Company_name,Period,Remarks,Created_by,Created_on) 
                          VALUES (?,?,?,?,?,?);"""
        data_tuple = (Audit_Name,Company_name,Period,Remarks,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        #st.success("Audit created...")
        message_verify=("Audit Created...")
    except sqlite3.Error as error:
        message_verify=error
        st.error(error)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def add_query_reply(id,reply):
    
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        reply=reply.replace("'","''")
        query=f"UPDATE Audit_Queries SET Reply ='{reply}', Reply_by='{st.session_state['User']}' WHERE Id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply="Reply to Query is updated...."
    except sqlite3.Error as error:
        updatereply=error
    except :
        updatereply="Run time Error...Invalid Input or Data type Mismatch" 
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply

def update_query_status(id,reply,close):
    
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        reply=reply.replace("'","''")
        query=f"UPDATE Audit_Queries SET status_update_remarks ='{reply}',status_udate_by ='{st.session_state['User']}',Status ='{close}' WHERE Id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply="Query Status updated...."
    except sqlite3.Error as error:
        updatereply=error
    except :
        updatereply="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply


def update_query_status_ar(id,reply,close):
    
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        reply=reply.replace("'","''")
        query=f"UPDATE Audit_AR SET status_update_remarks ='{reply}',status_update_by ='{st.session_state['User']}',Status ='{close}' WHERE Id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply="Query Status updated...."
    except sqlite3.Error as error:
        updatereply=error
    except :
        updatereply="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply


def add_query_reply_AR(id,reply):
    
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        reply=reply.replace("'","''")
        query=f"UPDATE Audit_AR SET reply ='{reply}',reply_by ='{st.session_state['User']}' WHERE Id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply="Query Reply updated...."
    except sqlite3.Error as error:
        updatereply=error
    except :
        updatereply="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply


def get_risk_weights_ds_vouching(ds_name):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT Criteria,Risk_Weight,Risk_Category from Risk_Master where DataSetName='{ds_name}' and Audit_id={int(st.session_state['AuditID'])}"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #st.write(query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_task(task,details,duedate,person,auditid):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        currentime=str(datetime.now())[:19]
        sqlite_insert_with_param = """INSERT INTO Tasks
                          (Task,Details,Due_Date,Person,audit_id,Created_by,Created_on) 
                          VALUES (?,?,?,?,?,?,?);"""
        data_tuple = (task,details,duedate,person,auditid,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        #st.success("Record Added...")
        message_verify=("Record Added...To Refresh Table- Click on Check Box for any Row")
    except sqlite3.Error as error:
        message_verify=error
        #st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch" 
        #st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def get_all_tasks(auidt_id):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Tasks where audit_id={auidt_id} "
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_tasks_byuser(auidt_id,user):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Tasks where audit_id={auidt_id} and Person='{user}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_overdue_tasks(auidt_id):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Tasks where Date(Due_Date) < Date('now') AND audit_id={auidt_id} AND Status='Pending'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def del_task(id):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        
        #currentime=datetime.now()
        sqlite_insert_with_param = f"DELETE FROM Tasks WHERE id = {id}"
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        #st.success("Record Deleted...To Refresh Table- Click on Check Box for any Row")
        message_verify="Record Deleted...To Refresh Table- Click on Check Box for any Row"
    except sqlite3.Error as error:
        message_verify=error
        #st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
        #st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def update_task(Task,Details,Due_Date,Person,Status,id):
     
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        if Task : Task=Task.replace("'","''")
        if Details : Details=Details.replace("'","''")
        query=f"""UPDATE Tasks  SET Task='{Task}' , Details ='{Details}' ,Due_Date='{Due_Date}',
                Person='{Person}', Status='{Status}' WHERE id={id}"""
        #query=f"UPDATE  SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus="Task updated...."
        #st.success(auditstatus)
    except sqlite3.Error as error:
        auditstatus=error
        st.error(auditstatus)
    except :
        auditstatus="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(auditstatus)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus


def get_risk_weights_ds(ds_name):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT Criteria,Risk_Weight,Risk_Category from Risk_Master where DataSetName='{ds_name}' and Audit_id='{int(st.session_state['AuditID'])}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def update_risk_weights(criteria,DsName,auditid,risk_weight,risk_category):
     
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE Risk_Master  SET Risk_Weight={risk_weight} , Risk_Category ='{risk_category}' WHERE Criteria='{criteria}' AND audit_id ={auditid} AND DataSetName ='{DsName}'"
        #query=f"UPDATE  SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus="Risk Weights updated...."
        st.success(auditstatus)
    except sqlite3.Error as error:
        auditstatus=error
        st.error(auditstatus)
    except :
        auditstatus="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(auditstatus)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus


def update_verification_criteria(criteria,old_criteria,DsName,auditid,risk_weight,risk_category):
     
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        if criteria : criteria=criteria.replace("'","''")
        query=f"UPDATE DSCriteria SET Verification_Criteria={criteria}, Risk_Weight={risk_weight} , Risk_Category ='{risk_category}' WHERE Verification_Criteria='{old_criteria}' AND audit_id ={auditid} AND DataSetName ='{DsName}'"
        #query=f"UPDATE  SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus="Verification Criteria updated...."
        st.success(auditstatus)
    except sqlite3.Error as error:
        auditstatus=error
        #st.success(auditstatus)
        st.error(auditstatus)
    except :
        auditstatus="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(auditstatus)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus

def get_dataset_values(DSname):
    #this is for auditing
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        values={}
        #get total count of DS
        query=f"SELECT count(*) from '{DSname}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_records=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_records']=total_records
        else:
            values['total_records']=0
        #get total count of DS where status=Audited
        query=f"SELECT count(*) from '{DSname}' WHERE AutoAudit_Status= 'Audited'"
        cursor.execute(query)
        total_audited=cursor.fetchone()
        if total_audited[0]!= None:
            #st.write(total_audited)
            total_audited=int(total_audited[0])
        #st.write(total_audited)
            values['total_audited']=total_audited
        else:
            values['total_audited']=0
        #st.write(values)
        cursor.close()
    except sqlite3.Error as error:
        message=error
        st.error(message)
    except :
        message="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return values


def get_audit_values(Audit_id):
    #this is for audit queries v&v per audit
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        values={}
        #get total count of audit queries v&v
        query=f"SELECT count(*) from Audit_Queries WHERE Status= 'Pending' AND Audit_Id='{Audit_id}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_queries_vv=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_queries_vv']=total_queries_vv
        else:
            values['total_queries_vv']=0
        
        #get total count of audit queries AR
        query=f"SELECT count(*) from Audit_AR WHERE status= 'Pending' AND Audit_Id='{Audit_id}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_queries_ar=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_queries_ar']=total_queries_ar
        else:
            values['total_queries_ar']=0
       
        cursor.close()
    except sqlite3.Error as error:
        message=error
        st.error(message)
    except :
        message="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return values

def get_audit_values_byAuditee(Audit_id,userid):
    #this is for audit queries v&v per audit
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        values={}
        #get total count of audit queries v&v
        query=f"SELECT count(*) from Audit_Queries WHERE Status= 'Pending' AND Audit_Id='{Audit_id}' AND DataSetName in (SELECT DS from DSName WHERE person_responsible='{userid}')"
        #st.success(query)
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_queries_vv=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_queries_vv']=total_queries_vv
        else:
            values['total_queries_vv']=0
        
        #get total count of audit queries AR
        query=f"SELECT count(*) from Audit_AR WHERE status= 'Pending' AND Audit_Id='{Audit_id}' AND DataSetName in (SELECT DS from DSName WHERE person_responsible='{userid}')"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_queries_ar=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_queries_ar']=total_queries_ar
        else:
            values['total_queries_ar']=0
       
        cursor.close()
    except sqlite3.Error as error:
        message=error
        st.error(message)
    except :
        message="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return values

def get_values_id_dsn(Audit_id,datasetname):
    #this is for audit queries v&v- per DS
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        values={}
        #get total count of audit queries v&v
        query=f"SELECT count(*) from Audit_Queries WHERE Status= 'Pending' AND Audit_Id='{Audit_id}' AND DataSetName='{datasetname}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_queries_vv=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_queries_vv']=total_queries_vv
        else:
            values['total_queries_vv']=0
        
        #get total count of audit queries AR
        query=f"SELECT count(*) from Audit_AR WHERE status= 'Pending' AND Audit_id='{Audit_id}'AND DataSetName='{datasetname}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_queries_ar=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_queries_ar']=total_queries_ar
        else:
            values['total_queries_ar']=0
       
       #get risk score for Queries of DS
        query=f"SELECT sum (Risk_Weight) FROM queries_risk WHERE Audit_id='{Audit_id}'AND DataSetName='{datasetname}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        #st.write(total_records)
        if total_records[0]!= None:
            auditrisk_audited=int(total_records[0])
            #st.write(total_records,total_records)
            values['auditrisk_audited']=auditrisk_audited
        else:
            values['auditrisk_audited']=0
        
        #get risk score for Dataset
        query=f"SELECT sum (Risk_Weight) FROM Risk_Master WHERE Audit_id='{Audit_id}'AND DataSetName='{datasetname}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            auditrisk_total=int(total_records[0])
         #st.write(total_records,total_records)
            values['auditrisk_total']=auditrisk_total
        else:
            values['auditrisk_total']=0
        
        #total Risk for DS= Total audited records * above
        # total risk score for Dataset- AR
        query=f"SELECT sum (Risk_Weight) FROM Audit_AR WHERE Audit_id='{Audit_id}'AND DataSetName='{datasetname}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            auditrisk_total=int(total_records[0])
         #st.write(total_records,total_records)
            values['auditrisk_total_AR']=auditrisk_total
        else:
            values['auditrisk_total_AR']=0
        
        # total Audit risk score for AR pending
        query=f"SELECT sum (Risk_Weight) FROM Audit_AR WHERE Audit_id='{Audit_id}'AND DataSetName='{datasetname}' AND status='Pending'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            auditrisk_total=int(total_records[0])
         #st.write(total_records,total_records)
            values['auditrisk_pending_AR']=auditrisk_total
        else:
            values['auditrisk_pending_AR']=0
        cursor.close()
    except sqlite3.Error as error:
        message=error
        st.error(message)
    except :
        message="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return values

def get_vv_quries(DSfilename,DSName,audit_id):
    #this is for auditing
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        # """ query1=f"""
        # SELECT b.*,a.Id,a.Criteria as "Criteria ", a.Condition as "Condition ", a.Cause as "Cause ", a.Effect as "Effect ", a.Risk_Weight as "Risk_Weight ", a.Risk_Category as "Risk_Category ", a.Audited_By, a.Audited_on, a.reply, a.reply_by, a.reply_on, 
        #     a.status_udate_by,a.status_update_remarks,a.Field as "Field "
        #     FROM queries_risk a LEFT JOIN  "{DSfilename}" b ON a.Data_Id = b."index" WHERE a.DataSetName='{DSName}'
        #     AND a.audit_id ={audit_id} order by b."index";""" """
        query=f"""
        SELECT a.Id,a.Criteria, a.Condition , a.Cause , a.Effect , a.Risk_Weight , a.Risk_Category , a.Audited_By, a.Audited_on, a.reply, a.reply_by, a.reply_on, 
            a.status_udate_by,a.status_update_remarks,a.Field,b.*
            FROM queries_risk a LEFT JOIN  "{DSfilename}" b ON a.Data_Id = b."index" WHERE a.DataSetName='{DSName}'
            AND a.audit_id ={audit_id} ;"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        
        df = pd.DataFrame(sql_query)
        #st.info(df.columns[df.columns.duplicated()])
        #st.dataframe(df)
        #rename colums with audited
        cols=df.columns
        #st.info(cols)
        newcolname=[]
        baselist=['Id', 'Criteria', 'Condition', 'Cause', 'Effect', 'Risk_Weight', 'Risk_Category', 'Audited_By', 'Audited_on', 'Reply', 'Reply_by', 'Reply_on', 'status_udate_by', 'status_update_remarks', 'Field']
        #for cnum in range(0 , len(cols)-15):
        for cnum in range(15 , len(cols)):
            
            dvalue=f"{df.columns[cnum]}_Audited"
            newcolname.append(dvalue)
            #df.columns.values[cnum]=dvalue
            #df.rename(columns={list(df)[cnum]:dvalue},inplace=True)
            #st.success(f"{cnum},{df.columns.values[cnum]},{dvalue}")
        #st.success(df.columns)
        #st.info(newcolname)
        #newcols=newcolname+baselist
        newcols=baselist+newcolname
        #st.info(newcols)
        df.columns=newcols
        #st.info(df.columns[df.columns.duplicated()])
        #st.dataframe(df)
        
        #st.success(f"{cols},{len(cols)},{df.columns[1]}")
        #df.rename(columns={df.columns[1]: 'Fee', df.columns[2]: 'Duration'},inplace=True)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_all_vv_quries(DSfilename,DSName,audit_id):
    #this is for auditing
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        
        query=f"""
        SELECT a.Status,a.Id,a.Criteria, a.Condition , a.Cause , a.Effect , a.Risk_Weight , a.Risk_Category , a.Audited_By, a.Audited_on, a.reply, a.reply_by, a.reply_on, 
            a.status_udate_by,a.status_update_remarks,a.Field,b.*
            FROM queries_risk a LEFT JOIN  "{DSfilename}" b ON a.Data_Id = b."index" WHERE a.DataSetName='{DSName}'
            AND a.audit_id ={audit_id} ;"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        
        df = pd.DataFrame(sql_query)
        #st.info(df.columns[df.columns.duplicated()])
        #st.dataframe(df)
        #rename colums with audited
        cols=df.columns
        #st.info(cols)
        newcolname=[]
        baselist=['Status','Id', 'Criteria', 'Condition', 'Cause', 'Effect', 'Risk_Weight', 'Risk_Category', 'Audited_By', 'Audited_on', 'Reply', 'Reply_by', 'Reply_on', 'status_udate_by', 'status_update_remarks', 'Field']
        #for cnum in range(0 , len(cols)-15):
        for cnum in range(16 , len(cols)):
            
            dvalue=f"{df.columns[cnum]}_Audited"
            newcolname.append(dvalue)
            #df.columns.values[cnum]=dvalue
            #df.rename(columns={list(df)[cnum]:dvalue},inplace=True)
            #st.success(f"{cnum},{df.columns.values[cnum]},{dvalue}")
        #st.success(df.columns)
        #st.info(newcolname)
        #newcols=newcolname+baselist
        newcols=baselist+newcolname
        #st.info(newcols)
        df.columns=newcols
        #st.info(df.columns[df.columns.duplicated()])
        #st.dataframe(df)
        
        #st.success(f"{cols},{len(cols)},{df.columns[1]}")
        #df.rename(columns={df.columns[1]: 'Fee', df.columns[2]: 'Duration'},inplace=True)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df


def get_ar_queries(ds_name):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT Id,Criteria,Condition,Cause,Effect,Risk_Weight,Risk_Category,created_by,
        created_on,reply,reply_by,reply_on,status_update_remarks,status_update_by,Review_File 
        from Audit_AR where DataSetName='{ds_name}' and Audit_id='{int(st.session_state['AuditID'])}'
        and status='Pending'"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        #st.error(df)   
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_all_ar_queries(ds_name):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT status,Id,Criteria,Condition,Cause,Effect,Risk_Weight,Risk_Category,created_by,
        created_on,reply,reply_by,reply_on,status_update_remarks,status_update_by,Review_File 
        from Audit_AR where DataSetName='{ds_name}' and Audit_id='{int(st.session_state['AuditID'])}'
        """
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        #st.error(df)   
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df


def get_Summary_audit_values(Audit_id,ds):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
               
        query=f"SELECT Criteria,count(Criteria) as 'Total Queries' FROM queries_risk WHERE Audit_id='{Audit_id}' AND DataSetName='{ds}' GROUP BY Criteria"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #cursor.execute(query)
        
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_Summary_audit_values_comp_auditeeId(Audit_id,userid):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
               
        query=f"SELECT DataSetName as 'Data Set Name',count(Criteria) as 'Total Queries' FROM queries_risk WHERE Audit_id='{Audit_id}' AND DataSetName in (SELECT DS from DSName WHERE person_responsible='{userid}') GROUP BY DataSetName"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #cursor.execute(query)
        
        cursor.close() 
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_Summary_AR_audit_values_comp_auditeeId      (Audit_id,userid):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
               
        query=f"SELECT DataSetName as 'Data Set Name',count(Criteria) as 'Total Queries' FROM Audit_AR WHERE Audit_id='{Audit_id}' AND DataSetName in (SELECT DS from DSName WHERE person_responsible='{userid}') GROUP BY DataSetName"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #cursor.execute(query)
        
        cursor.close() 
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_Summary_audit_values_comp(Audit_id):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
               
        query=f"SELECT DataSetName as 'Data Set Name',count(Criteria) as 'Total Queries' FROM queries_risk WHERE Audit_id='{Audit_id}' GROUP BY DataSetName "
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #cursor.execute(query)
        
        cursor.close() 
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df


def get_Summary_audit_values_riskweight(Audit_id,ds):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #for V&V     
        query=f"SELECT Criteria,sum(Risk_Weight) as 'Total Risk Weight' FROM queries_risk WHERE Audit_id='{Audit_id}' AND DataSetName='{ds}' GROUP BY Criteria"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #for AR
        query=f"SELECT Criteria,sum(Risk_Weight) as 'Total Risk Weight' FROM Audit_AR WHERE Audit_id='{Audit_id}' AND DataSetName='{ds}' GROUP BY Criteria"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        dfar = pd.DataFrame(sql_query)
        cursor.close()
        #merge 2 df
        #df=df.append(dfar,ignore_index=True)
        df=pd.concat([df,dfar],ignore_index=True)
        
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_Summary_audit_values_riskweight_comp(Audit_id):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
               
        query=f"SELECT DataSetName as 'Data Set Name',sum(Risk_Weight) as 'Total Risk Weight' FROM queries_risk WHERE Audit_id='{Audit_id}'  GROUP BY DataSetName"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #cursor.execute(query)
        
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_Summary_audit_values_riskcategory(Audit_id,ds):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
               
        query=f"SELECT Criteria,Risk_Category,sum(Risk_Weight) as 'Total Risk Weight' FROM queries_risk WHERE Audit_id='{Audit_id}' AND DataSetName='{ds}' GROUP BY Criteria,Risk_Category"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #cursor.execute(query)
        
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_company_docs(comp_name):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT id,Title,Document_Type,Remarks,File_Ref,created_by,created_on from Company_File where Company='{comp_name}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_comp_doc(title,remarks,file_ref,doc_type,comp_name):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        currentime=str(datetime.now())[:19]
        sqlite_insert_with_param = """INSERT INTO Company_File
                          (Title,Remarks,File_Ref,Document_Type,Company,Created_by,Created_on) 
                          VALUES (?,?,?,?,?,?,?);"""
        data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        #st.success("Record Added...")
        message_verify="Record Added...To Refresh Table- Click on Check Box for any Row"
    except sqlite3.Error as error:
        message_verify=error
        #st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch" 
        #st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def del_comp_doc(id):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        
        #currentime=datetime.now()
        sqlite_insert_with_param = f"DELETE FROM Company_File WHERE id = {id}"
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        #st.success("Record Deleted...")
        message_verify="Record Deleted...To Refresh Table- Click on Check Box for any Row"
    except sqlite3.Error as error:
        message_verify=error
        #st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def modif_comp_doc(roid,title,remarks,file_ref,doc_type):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        if title : title=title.replace("'","''")
        if file_ref: file_ref=file_ref.replace("'","''")
        if remarks: remarks=remarks.replace("'","''")
        #update audit status
        if file_ref==None:
            query=f"""UPDATE Company_File  SET Title='{title}',Remarks ='{remarks}',Document_Type='{doc_type}'
                WHERE id={roid} """
        else:
            query=f"""UPDATE Company_File  SET Title='{title}',Remarks ='{remarks}', File_Ref='{file_ref}' , Document_Type='{doc_type}'
                WHERE id={roid} """
            
        #query=f"""UPDATE Company_File  SET Title='{title}',Remarks ='{remarks}', File_Ref='{file_ref}' , Document_Type='{doc_type}'
            #WHERE id={roid} """
        #query=f"UPDATE  SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus="Record updated...To Refresh Table- Click on Check Box for any Row"
        #st.success(auditstatus)
    except sqlite3.Error as error:
        auditstatus=( error)
        #st.success(auditstatus)
    #except :
        #auditstatus="Run time Error...Invalid Input or Data type Mismatch" 
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus

def get_audit_docs(auditid):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT id,Title,Document_Type,Remarks,File_Ref,created_by,created_on from Audit_File where Audit_id='{auditid}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch" 
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_audit_doc(title,remarks,file_ref,doc_type,audit_id):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        
        currentime=str(datetime.now())[:19]
        #currentime=str(currentime[:19])
        sqlite_insert_with_param = """INSERT INTO Audit_File
                          (Title,Remarks,File_Ref,Document_Type,Audit_id,Created_by,Created_on) 
                          VALUES (?,?,?,?,?,?,?);"""
        data_tuple = (title,remarks,file_ref,doc_type,audit_id,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        st.success("Record Added...To Refresh Table- Click on Check Box for any Row")
        message_verify="Record Added...To Refresh Table- Click on Check Box for any Row"
    except sqlite3.Error as error:
        message_verify=error
        st.error(message_verify)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
        st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def del_audit_doc(id):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        
        #currentime=datetime.now()
        sqlite_insert_with_param = f"DELETE FROM Audit_File WHERE id = {id}"
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        #st.success("Record Deleted...To Refresh Table- Click on Check Box for any Row")
        message_verify="Record Deleted...To Refresh Table- Click on Check Box for any Row"
    except sqlite3.Error as error:
        message_verify=error
        #st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
        #st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def modif_audit_doc(roid,title,remarks,file_ref,doc_type):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        if title : title=title.replace("'","''")
        if file_ref: file_ref=file_ref.replace("'","''")
        if remarks: remarks=remarks.replace("'","''")
        #update audit status
        if file_ref==None:
            query=f"""UPDATE Audit_File  SET Title='{title}',Remarks ='{remarks}',Document_Type='{doc_type}'
                WHERE id={roid} """
        else:
            query=f"""UPDATE Audit_File  SET Title='{title}',Remarks ='{remarks}', File_Ref='{file_ref}' , Document_Type='{doc_type}'
                WHERE id={roid} """
            
        #query=f"""UPDATE Company_File  SET Title='{title}',Remarks ='{remarks}', File_Ref='{file_ref}' , Document_Type='{doc_type}'
            #WHERE id={roid} """
        #query=f"UPDATE  SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus="Record updated...To Refresh Table- Click on Check Box for any Row"
        #st.success(auditstatus)
    except sqlite3.Error as error:
        auditstatus=error
        #st.success(auditstatus)
    except :
        auditstatus="Run time Error...Invalid Input or Data type Mismatch"
        #st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus

def get_audit_checklist(auditid):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT id,Criteria,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,created_by,created_on,audit_id from Audit_Observations where Audit_id={auditid}"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def del_checklist(id):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        
        #currentime=datetime.now()
        sqlite_insert_with_param = f"DELETE FROM Audit_Observations WHERE id = {id}"
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        st.success("Record Deleted...")
        message_verify="Record Deleted..."
    except sqlite3.Error as error:
        message_verify=error
        st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
        st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def add_audit_cheklist(criteria,Audit_area,heading,risk_weight,risk_category,person_responsible,auditid):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        
        currentime=str(datetime.now())[:19]
        sqlite_insert_with_param = """INSERT INTO Audit_Observations
                          (Criteria,Risk_Weight,Risk_Level,Audit_Area,Heading,Person_Responsible,created_by,created_on,audit_id) 
                          VALUES (?,?,?,?,?,?,?,?,?);"""
        data_tuple = (criteria,risk_weight,risk_category,Audit_area,heading,person_responsible,st.session_state['User'],currentime,auditid)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        st.success("Record Added...")
        message_verify="Record Added..."
    except sqlite3.Error as error:
        message_verify=error
        st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
        st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify


def modify_audit_cheklist(roid,Criteria,Risk_Weight,Risk_Level,Audit_Area,Heading,Person_Responsible):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        if Criteria : Criteria=Criteria.replace("'","''")
        if Audit_Area : Audit_Area=Audit_Area.replace("'","''")
        if Heading : Heading=Heading.replace("'","''")
        query=f"""UPDATE Audit_Observations SET Criteria='{Criteria}', Risk_Weight ={Risk_Weight}, Risk_Level='{Risk_Level}' , Audit_Area='{Audit_Area}',
            Heading ='{Heading}', Person_Responsible='{Person_Responsible}' WHERE id={roid} """
            
        #query=f"""UPDATE Company_File  SET Title='{title}',Remarks ='{remarks}', File_Ref='{file_ref}' , Document_Type='{doc_type}'
            #WHERE id={roid} """
        #query=f"UPDATE  SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        status="Record updated...."
        st.success(status)
    except sqlite3.Error as error:
        status=error
        st.error(status)
    except :
        status="Run time Error...Invalid Input or Data type Mismatch"
        st.error(status)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return status

def import_defalut_checklist(df):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        df.to_sql("Audit_Observations",sqliteConnection,if_exists='append', index=False)
        
        sqliteConnection.commit()
        cursor.close()
        #vouching=("Audit Vouching added Successfully")
        vouching='CheckList Imported...You can Modify Later.'
        st.dataframe(df)
    except sqlite3.Error as err:
        st.error(err)
        #st.success("err")
        #if e=="UNIQUE constraint failed":
        #vouching="Audit Criteria MUST be UNIQUE...if Existing Audit Criteria is in Defalut CheckList, Can not Import file."
        #else:
        vouching=err
    except :
        vouching="Run time Error...Invalid Input or Data type Mismatch"
    #     #st.error(status)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return vouching

def get_audit_observations(auditid):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,DeadLine,Risk_Weight,Risk_Level,Compliance_Status,Audit_Area,Heading,person_responsible,Management_Comments,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid}"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df= error
        st.error(error)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def modify_audit_observation(roid,Condition,Cause,Effect,Conclusion,Impact,Recomendation,Corrective_Action_Plan,Is_Adverse_Remark,DeadLine,file_name):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        if Condition : Condition=Condition.replace("'","''")
        if Cause : Cause=Cause.replace("'","''")
        if Effect : Effect=Effect.replace("'","''")
        if Conclusion : Conclusion=Conclusion.replace("'","''")
        if Impact : Impact=Impact.replace("'","''")
        if Recomendation : Recomendation=Recomendation.replace("'","''")
        if Corrective_Action_Plan : Corrective_Action_Plan=Corrective_Action_Plan.replace("'","''")
        currentime=str(datetime.now())[:19]
        if file_name==None:
            query=f"""UPDATE Audit_Observations  SET Condition='{Condition}',Cause ='{Cause}',Effect='{Effect}', 
                Conclusion='{Conclusion}',Impact='{Impact}',Recomendation='{Recomendation}',Corrective_Action_Plan='{Corrective_Action_Plan}' 
                ,Is_Adverse_Remark='{Is_Adverse_Remark}',DeadLine='{DeadLine}',Observation_by='{st.session_state['User']}', 
                Observation_on='{currentime}' WHERE id={roid} """
        else:
            query=f"""UPDATE Audit_Observations  SET Condition='{Condition}',Cause ='{Cause}', Effect='{Effect}' , 
                Conclusion='{Conclusion}',Impact='{Impact}',Recomendation='{Recomendation}',Corrective_Action_Plan='{Corrective_Action_Plan}' 
                ,Is_Adverse_Remark='{Is_Adverse_Remark}',DeadLine='{DeadLine}',Observation_by='{st.session_state['User']}',
                Observation_on='{currentime}',Annexure='{file_name}' WHERE id={roid} """
        
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus=("Record updated....")
        st.success(auditstatus)
    except sqlite3.Error as error:
        auditstatus=error
        st.error(error)
    except :
        auditstatus="Run time Error...Invalid Input or Data type Mismatch"
        st.error(auditstatus)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus

def get_Audit_summ(auditid):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Observation,Risk_Weight,Risk_Level,Impact,Area,Need_for_Management_Intervention,created_by,created_on,Audit_id from Audit_Summary where Audit_id={auditid}"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        st.error(error)
        df=error
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_audit_summ(auditid,Observation,risk_weight,risk_category,Impact,
                            Area,Need_for_Management_Intervention):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        
        currentime=str(datetime.now())[:19]
        sqlite_insert_with_param = """INSERT INTO Audit_Summary
                          (Observation,Risk_Weight,Risk_Level,Impact,Area,Need_for_Management_Intervention,Audit_id,Created_by,Created_on) 
                          VALUES (?,?,?,?,?,?,?,?,?);"""
        data_tuple = (Observation,risk_weight,risk_category,Impact,Area,Need_for_Management_Intervention,auditid,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        st.success("Record Added....Click on Checkbox for any row to Refresh Table")
        message_verify="Record Added..."
    except sqlite3.Error as error:
        st.error(error)
        message_verify=error
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
        st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def modify_audit_summ(roid,Observation,Impact,Area,Need_for_Management_Intervention,risk_weight,risk_category):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        if Observation : Observation=Observation.replace("'","''")
        if Impact : Impact=Impact.replace("'","''")
        if Area : Area=Area.replace("'","''")
        if Need_for_Management_Intervention : Need_for_Management_Intervention=Need_for_Management_Intervention.replace("'","''")
        query=f"""UPDATE Audit_Summary SET Observation='{Observation}', Impact ='{Impact}', Area='{Area}' , Need_for_Management_Intervention='{Need_for_Management_Intervention}',
            Risk_Weight ={risk_weight}, Risk_Level='{risk_category}' WHERE id={roid} """
         
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        status=("Record updated....Click on Checkbox for any row to Refresh Table")
        #st.success(status)
    except sqlite3.Error as error:
        status=error
        #st.success(status)
    except :
        status="Run time Error...Invalid Input or Data type Mismatch"
        #st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return status

def del_audit_sum(id):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        
        #currentime=datetime.now()
        sqlite_insert_with_param = f"DELETE FROM Audit_Summary WHERE id = {id}"
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        st.success("Record Deleted....Click on Checkbox for any row to Refresh Table")
        message_verify=("Record Deleted...")
    except sqlite3.Error as error:
        message_verify=error
        st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
        st.error(error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def get_pending_obser(auditid):   
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,DeadLine,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,Management_Comments,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid} and Compliance_Status='Open'"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df


def get_pending_obser_for_auditee(auditid,auditee):   
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,Compliance_Remarks,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,DeadLine,Risk_Weight,Action_Remarks,Risk_Level,Audit_Area,Heading,person_responsible,Management_Comments,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid} and Person_Responsible='{auditee}' and Compliance_Status='Open'"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df


def get_pending_advere_obser(auditid):   
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,DeadLine,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,Management_Comments,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid} and Compliance_Status='Open' and Is_Adverse_Remark = 'Yes' """
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df
def get_all_obser(auditid):   
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT * from Audit_Observations where Audit_id={auditid}"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def update_mgt_comm(id,reply):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        if reply : reply=reply.replace("'","''")
        
        query=f"UPDATE Audit_Observations SET Management_Comments ='{reply}' WHERE id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply=("Management_Comments updated....")
    except sqlite3.Error as error:
        updatereply=error
    except :
        updatereply="Run time Error...Invalid Input or Data type Mismatch"
        #st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply

def get_pending_Corrective(auditid):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,DeadLine,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,
                    Management_Comments,Action_Remarks,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid} and Compliance_Status='Open'"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_pending_Corrective_forauditee(auditid,auditee):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,Action_Remarks,DeadLine,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,
                    Management_Comments,Compliance_Remarks,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid} and Person_Responsible=='{auditee}' and Compliance_Status='Open'"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df
    
def update_corre_action(id,reply):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        if reply : reply=reply.replace("'","''")
        query=f"UPDATE Audit_Observations SET Action_Remarks ='{reply}' WHERE id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply="Action_Remarks updated...."
    except sqlite3.Error as error:
        updatereply=error
    except :
        updatereply="Run time Error...Invalid Input or Data type Mismatch"
        #st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply

def get_pending_Compliance(auditid): 
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,DeadLine,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,
                    Management_Comments,Action_Remarks,Compliance_Status,Compliance_Remarks,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid} and Compliance_Status='Open'"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df
       
def update_compliance_remarks(id,reply,status):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        if reply : reply=reply.replace("'","''")
        query=f"UPDATE Audit_Observations SET Compliance_Remarks ='{reply}', Compliance_Status='{status}' WHERE id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply="Compliance_Remarks updated...."
    except sqlite3.Error as error:
        updatereply=error
    except :
        updatereply="Run time Error...Invalid Input or Data type Mismatch"
        #st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply

def closed_audit(auditid):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE Audit SET Status ='Closed' WHERE id = {auditid}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply="Audit Closed...."
    except sqlite3.Error as error:
        updatereply=error
    except :
        updatereply="Run time Error...Invalid Input or Data type Mismatch"
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply

def update_password(usrid,oldpass,newpass):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        #check if user id & password is correct
        cursor.execute(f"SELECT password from Users where user='{usrid}'")
        passworddb=cursor.fetchone()
        #print(passworddb[0])
        cursor.close()
        #sqliteConnection.close()
        #st.write(passworddb[0])
        if newpass : newpass=newpass.replace("'","''")
        if passworddb:
            if passworddb[0]==oldpass:
                cursor = sqliteConnection.cursor()
                query=f"UPDATE Users SET password ='{newpass}' WHERE user = '{usrid}'"
                cursor.execute(query)
                sqliteConnection.commit()
                cursor.close()
                        
                        # update with new password
               
                updatereply="Password Changed...."
            else:
                
                updatereply="Invalid Password"
        else:
            #st.session_state['loggedIn'] = False
            updatereply="Invalid user name "
                
    except sqlite3.Error as error:
        updatereply=error
    except :
        updatereply="Run time Error...Invalid Input or Data type Mismatch"
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply

def get_unlinked_obsr(obr_id):
    try:
        auditid=int(st.session_state['AuditID'])
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT id,Criteria,DataSetName FROM Risk_Master WHERE audit_id={auditid} AND id NOT in (SELECT vv_id FROM Link_vv WHERE obs_id={obr_id})"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
            df=error
            st.error(df)
    except :
            df="Run time Error...Invalid Input or Data type Mismatch"
            st.error(df)
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                #message=("The SQLite connection is closed")
            
    return df

def get_linked_obsr(obr_id):
    try:
        #auditid=int(st.session_state['AuditID'])
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT id,vv_id as 'Criteria id',Criteria, DataSetName from linking_vv WHERE obs_id={obr_id}"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
            df=error
            st.error(df)
    except :
            df="Run time Error...Invalid Input or Data type Mismatch"
            st.error(df)
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                #message=("The SQLite connection is closed")
            
    return df

def insert_vv_linking(df):
     
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        df.to_sql("Link_vv",sqliteConnection,if_exists='append', index=False)
            
        sqliteConnection.commit()
        cursor.close()
        vouching=("Added Successfully")
    except sqlite3.Error as error:
        vouching=error
        #st.success(vouching)
    except :
        vouching="Run time Error...Invalid Input or Data type Mismatch"
            
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return vouching

def delete_vv_linking(del_links):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        listvalues=','.join([str(i) for i in del_links])
        #currentime=datetime.now()
        sqlite_insert_with_param = f"Delete FROM Link_vv WHERE id in({listvalues})"
        #st.write(sqlite_insert_with_param)
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        #st.success("Record Deleted...")
        message_verify="Record Deleted..."
    except sqlite3.Error as error:
        message_verify=error
        st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
        st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def get_obs_related_vv(obr_id):
    try:
        #auditid=int(st.session_state['AuditID'])
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT DataSetName,Criteria,Condition,Cause,Effect,reply,status_update_remarks,Risk_Weight FROM queries_risk WHERE risk_id in (SELECT risk_id from linking_vv WHERE obs_id={obr_id})"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
            df=error
            st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                #message=("The SQLite connection is closed")
            
    return df

def get_obs_related_vv_summary(obr_id):
    try:
        #auditid=int(st.session_state['AuditID'])
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT DataSetName,Criteria, count(Criteria)as 'Total Queries',sum(Risk_Weight) as 'Total Risk Weight' FROM queries_risk WHERE risk_id in (SELECT risk_id from linking_vv where obs_id={obr_id}) group by DataSetName,Criteria"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
            df=error
            st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                #message=("The SQLite connection is closed")
            
    return df

def get_unlinked_obsr_ar(obr_id):
    try:
        auditid=int(st.session_state['AuditID'])
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT id,Criteria,DataSetName FROM Audit_AR WHERE audit_id={auditid} AND id NOT in (SELECT ar_id FROM Link_ar WHERE obs_id={obr_id})"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
            df=error
            st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                #message=("The SQLite connection is closed")
            
    return df

def get_linked_obsr_ar(obr_id):
    try:
        #auditid=int(st.session_state['AuditID'])
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT id,ar_id as 'Criteria id',Criteria, DataSetName from linking_ar WHERE obs_id={obr_id}"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
            df=error
            st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                #message=("The SQLite connection is closed")
            
    return df

def insert_ar_linking(df):
     
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        df.to_sql("Link_ar",sqliteConnection,if_exists='append', index=False)
            
        sqliteConnection.commit()
        cursor.close()
        vouching=("Added Successfully")
    except sqlite3.Error as error:
        vouching=error
        #st.success(vouching)
    except :
        vouching="Run time Error...Invalid Input or Data type Mismatch"
        #st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return vouching

def delete_ar_linking(del_links):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        listvalues=','.join([str(i) for i in del_links])
        #currentime=datetime.now()
        sqlite_insert_with_param = f"Delete FROM Link_ar WHERE id in({listvalues})"
        #st.write(sqlite_insert_with_param)
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        #st.success("Record Deleted...")
        message_verify="Record Deleted..."
    except sqlite3.Error as error:
        message_verify=error
        st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
        st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def get_obs_related_ar(obr_id):
    try:
        #auditid=int(st.session_state['AuditID'])
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT DataSetName,Criteria,Condition,Cause,Effect,reply,status_update_remarks,Risk_Weight FROM Audit_AR WHERE Id in (SELECT ar_id from linking_ar WHERE obs_id={obr_id})"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
            df=error
            st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                #message=("The SQLite connection is closed")
            
    return df


def get_obs_related_ar_summary(obr_id):
    try:
        #auditid=int(st.session_state['AuditID'])
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"SELECT DataSetName,Criteria, count(Criteria)as 'Total Queries',sum(Risk_Weight) as 'Total Risk Weight' FROM Audit_AR WHERE Id in (SELECT ar_id from linking_ar where obs_id={obr_id}) group by DataSetName,Criteria"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
            df=error
            st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                #message=("The SQLite connection is closed")
            
    return df

def delete_sampling(dsfilename,del_links):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        listvalues=','.join([str(i) for i in del_links])
        #currentime=datetime.now()
        sqlite_insert_with_param = f"update '{dsfilename}' SET AutoAudit_Sampled='No' WHERE `index` in ({listvalues})"
        #st.write(sqlite_insert_with_param)
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        #st.success("Record Deleted...")
        message_verify="Record Deleted..."
    except sqlite3.Error as error:
        message_verify=error
        st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
        st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def add_sampling(dsfilename,del_links):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        listvalues=','.join([str(i) for i in del_links])
        #currentime=datetime.now()
        sqlite_insert_with_param = f"update '{dsfilename}' SET AutoAudit_Sampled='Yes' WHERE `index` in ({listvalues})"
        #st.write(sqlite_insert_with_param)
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.success("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        #st.success("Record Deleted...")
        message_verify="Records added for Sampling..."
    except sqlite3.Error as error:
        message_verify=error
        st.error(error)
        #st.success(comp_name)
    except :
        message_verify="Run time Error...Invalid Input or Data type Mismatch"
        st.error(message_verify)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def check_audit_status():
    try:
        auditid=int(st.session_state['AuditID'])
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        query=f"""SELECT Status from Audit where id={auditid}"""
        cursor.execute(query)
        
        sql_query=cursor.fetchone()
        df = sql_query[0]
        #st.write(df)
        cursor.close()
    except sqlite3.Error as error:
        df=error
        st.error(df)
    except :
        df="Run time Error...Invalid Input or Data type Mismatch"
        st.error(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df
