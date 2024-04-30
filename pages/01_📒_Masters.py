#from logging import PlaceHolder
from dataclasses import field
from queue import Empty
#from matplotlib.widgets import Button
import streamlit as st
import pandas as pd
import numpy as np
import json
import ast
#import pandas_read_xml as pdx
#from pandas_read_xml import flatten, fully_flatten, auto_separate_tables
from unicodedata import normalize
import os
import urllib.parse
import requests
from sqlalchemy import create_engine,text
import pymysql
import pymssql
#from main import show_login_page,LoggedOut_Clicked
from st_aggrid import AgGrid,DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, grid_options_builder,ColumnsAutoSizeMode
#from formatter import NullFormatter

from functions import add_sampling,delete_sampling,get_unlinked_obsr_ar,get_unlinked_obsr,update_password,import_defalut_checklist,update_verification_criteria,update_risk_weights,get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit
from functions import get_dataset_sampled,get_linked_obsr,get_risk_weights_ds_vouching,create_user,check_login,assign_user_rights,create_company,get_company_names,get_risk_weights_ds
from functions import check_audit_status,get_dataset_nonsampled,delete_ar_linking,insert_ar_linking,get_linked_obsr_ar,get_obs_related_vv_summary,delete_vv_linking,insert_vv_linking,modify_audit_cheklist,add_audit_cheklist,del_checklist,get_audit_checklist,create_dataset,add_verification_criteria,get_dsname,get_entire_dataset,get_auditee_comp
import sqlite3
from PIL import Image
url="https://acecom22-my.sharepoint.com/:w:/g/personal/saurabhjog_acecomskills_in/ESLKUvAGIMJJontdPiuXk5YBTxjbcYnCkilrcBJ3oHy0ww?e=ZS4i6g"
image = Image.open('autoaudit_t.png')
st.set_page_config(page_title="AutoAudit", page_icon=":white_check_mark:", layout="wide")
#st.title(":white_check_mark: AutoAudit")
headercol1,headercol2,co3=st.columns([8,2,1])
with headercol1 : st.image(image,width=200,)
with co3: 
    link =f'[Help]({url})'
    st.markdown(link, unsafe_allow_html=True)
    #st.markdown(f'''<a href={url}><button style="padding: 5px 8px; border-radius: 5px; border: 1px solid red;">Help</button></a>''',
    #            unsafe_allow_html=True)

st.markdown("""---""")
masters=st.container()
#from st_aggrid import AgGrid
headerSection = st.container()
#masterSection = st.container()
loginSection = st.container()
logOutSection = st.container()

    
def show_login_page():
    with loginSection:
        tab1,tab2 =st.tabs(["   Existing Users  ","   Change Password   "])
        with tab1:
            
            if st.session_state['loggedIn'] == False:
                #st.session_state['username'] = ''
                st.title("Login") 
                userName = st.text_input (label="User Name", value="", placeholder="Enter your user name",key="k1")
                password = st.text_input (label="Password", value="",placeholder="Enter password", type="password",key="k2")
                #get Companies for user
                rights=get_user_rights()
                mask = rights['user'] == userName
                comp_name= rights[mask]
                #comp_name=comp_name['company_name']
                compname=st.selectbox("Select Company",comp_name['company_name'])
                mask1=comp_name['company_name']==compname
                roleds=comp_name[mask1]
                if roleds.size !=0:
                    role=roleds['role'].values[0]
                else:
                    role=""
                #st.write(compname)
                #st.write(comp_name['company_name'])
                #get Audit for company
                audits=get_audit(compname)
                audit=st.selectbox("Select Audit Name",audits,key="auit_name")
                if audit:
                    st.button ("Login", on_click=check_login, args= (userName, password,compname,role,audit))
                
        with tab2:
            with st.form("New User",clear_on_submit=True):
                
                st.title("Change Password")
                userid = st.text_input (label="User ID", value="", placeholder="Enter your user ID",key="k5")
                password = st.text_input (label="Password", value="",placeholder="Enter Current Password", type="password",key="k6")
                new_pass = st.text_input (label="New Password", value="", placeholder="Enter New Password", type="password",key="k3")
                renew_pass = st.text_input (label="New Password", value="", placeholder="ReEnter New Password", type="password",key="k4")
                submit_user =st.form_submit_button("Submit")
                if submit_user:
                    if new_pass == renew_pass:
                        #createuser=create_user(displayname,userid,password,designation)
                        newpass=update_password(userid,password,new_pass)
                        st.success(newpass)
                    else:
                        st.success('New Password and ReEntered Password not matching...')
                #st.button ("Register", on_click=Register_Clicked, args= (userid, password,designation,displayname))


def show_masters():
   
    comp_name=st.session_state['Company']
    #st.write(f"Audit ID:-{st.session_state['AuditID']}")
    #st.write(st.session_state['Audit'])
    #st.write(st.session_state['AuditID'])
    auditid=int(st.session_state['AuditID'])
    ds_names=get_dsname(int(st.session_state['AuditID']))
    ds_names.loc[-1]=['---']
    ds_names.index=ds_names.index+1
    ds_names.sort_index(inplace=True)
    with masters:
        
        def nested_csv(dataframe):
            all_columns=list(dataframe.columns)
            parent_cols=st.multiselect("To Merge Chield recorsd in single row...Keep Columns of Parent record & Remove List of Chield Columns",options=all_columns,key="nestecoloptiosexlcsv",default=all_columns,
                                        help="Chield / Nested fields are Merged in single row...eg- in Sales invoice- Stock items with units & rates")
            if parent_cols.__len__()!=all_columns.__len__():
                records=None
                j=None
                #fill forward Na values for parent
                dataframe[parent_cols]=dataframe[parent_cols].ffill(axis=0)
                #fill na
                dataframe.fillna(dataframe.dtypes.replace({'object': 'N.A.', 'float64': 0}),inplace=True)
            
                #st.dataframe(dataframe)
                chield_cols = [item for item in all_columns if item not in parent_cols]
                #st.write(chield_cols,parent_cols)
                #cmdb=st.button("try",key="try")
                j=(dataframe.groupby(parent_cols).apply(lambda x: x[chield_cols].to_dict('records')).reset_index()
                                .rename(columns={0:'Chield-Data'})
                                .to_json(orient='records'))
                    #print(json.dumps(json.loads(j), indent=2, sort_keys=True))
                dataframe= pd.read_json(j)
                #st.write(j)
                #expand nested fileds
                
                nestedcols=['Chield-Data']
                for col in nestedcols:
                #st.write(col) 
                    dataframe[col] = dataframe[col].apply(lambda x: json.dumps(x))
            #st.write(dataframe)
            else:
                if 'Chield-Data' in dataframe.columns:
                    dataframe = dataframe.drop(columns=['Chield-Data'], axis=1)
            return(dataframe)    
                       
        def fileupload(uploaded_file,ftype,table_name,addnew):
            try:
                message=""
                if uploaded_file is not None:
                    dataframe=None
                    if ftype=='CSV':
                        rb=st.radio("Select File Structure Type",options=("Simple","Nested"),key="rbxCSVl",
                                    help="Select Nested if Data has Parent & Chield records eg Sales Invoice & Stock Details for each ale Invoice",horizontal=True)       
                        
                        if rb=="Simple":dataframe = pd.read_csv(uploaded_file,encoding= 'unicode_escape',skiprows=header_row-1,skipfooter=footer_row)
                        else:
                            dataframe = pd.read_csv(uploaded_file,encoding= 'unicode_escape',skiprows=header_row-1,skipfooter=footer_row)
                            dataframe=nested_csv(dataframe)
                            
                        #st.subheader(uploaded_file)
                        #dataframe = pd.read_csv(uploaded_file,encoding='utf-8')
                        #st.dataframe(dataframe)
                        
                    elif ftype=='JSON':
                        data = json.load(uploaded_file)
                        recordspath=st.text_input("Field containing Data",key="jsonrecordpath",placeholder="This is the Field Containing Data....Keep it Blank if Data preview is correct else,Type & press Tab / Enter",
                                                  help="Check the data shown in Table below, change the name & try")
                        #nestedcols=st.text_input("Enter Column names which are Nested- seperated by ,Comma",key="nestedcolumnams")
                        if recordspath:
                            dataframe=pd.json_normalize(data,record_path=recordspath)
                            
                        else: 
                            dataframe=pd.json_normalize(data)
                            
                        nestedcolslist=list(dataframe.columns)
                        nestedcols=st.multiselect("Select All Fields which are Nested",options=nestedcolslist,key="nestecoloptios",
                                                    help="These are Chield fields ,consisting if List of records...These are shown in Round Grey background ")
                        
                        #st.write(nestedcols)
                        if nestedcols:
                            for col in nestedcols:
                                #st.write(col) 
                                dataframe[col] = dataframe[col].apply(lambda x: json.dumps(x))
                           
                    elif ftype=='SQL':
                        driver=st.selectbox("Select Database",("postgresql","mysql","mssql"),key="sbsql")
                        user=st.text_input("Enter User Name*",key="sqluser")
                        password=st.text_input("Enter password*",key="sqlpass")
                        #st.write(password)
                        if "@" in password: password = urllib.parse.quote_plus(password)
                        #st.write(password)
                        hostname=st.text_input("Enter Host Name*",key="sqlhost")
                        #hostname=urllib.parse.quote_plus(hostname)
                        port=st.text_input("Enter Port*",key="sqlport")
                        database=st.text_input("Enter Database Name*",key="sqldbname")
                        sqltext=st.text_area("Enter SQL Query*",key="tasql")
                        #sql="select * from users"
                        if driver=="postgresql": driver="postgresql+psycopg2"
                        if driver=="mssql": driver="mssql+pymssql"
                        if driver=="mysql": driver="mysql+pymysql"
                        #engine = create_engine('mysql://scott:tiger@localhost/test')
                        #engine = create_engine('postgresql://user:pass@localhost:5432/mydb')
                        

                        engintext=f"{driver}://{user}:{password}@{hostname}:{port}/{database}"
                       
                        if sqltext and user and password and hostname and port and database : 
                            
                            engine=create_engine(engintext)
                            dataframe=pd.read_sql(sql=sqltext,con=engine)
                            
                        else:
                            message="Enter All Required Fields"
                    elif ftype=='API':     
                        reqtype=st.selectbox("Request Type",("GET","POST"),key="getpost")
                        url = st.text_input("Enter URL*",key="stturl",placeholder="without single or double quotes")
                        jLoad=None
                        payloadtype=st.radio("Is Payload Text or {Dictionary}",options=("{Dictionary}","Text"),key="pods",horizontal=True)
                        payload = st.text_area("Enter Payload",key="apipayload",placeholder="IF Dictionary- text must be in { curly brackets}; IF Text- without Quotes")
                        #payload=str(payload).strip("'<>() ").replace('\'', '\"')
                        if payload: 
                            if payloadtype=="{Dictionary}":
                                #jLoad=ast.literal_eval(str(jLoad))
                                j_obj=json.loads(payload)
                                #st.success(j_obj)
                                jLoad = json.dumps(j_obj)
                                #st.success(payload)
                                #st.success(jLoad)
                            else :jLoad=payload

                        
                        header=None
                        headers = st.text_area("Enter Headers",key="apipayheader",placeholder="text must be in { curly brackets}")
                        if headers: header=ast.literal_eval(headers)
                        #if st.button("Get Data from API",key="apigetdata"):
                        if url:
                            
                            if reqtype=="GET" : 
                                
                                response = requests.request("GET", url, headers=header, data=jLoad)
                            else: 
                                response = requests.request("POST", url, headers=header, data=jLoad)
                            
                            data=response.json()
                            recordspath=st.text_input("Field Containing Data",key="jsonrecordpath2",help="Check the data shown in Table below, change the name & try")
                            if recordspath: dataframe=pd.json_normalize(data,record_path=recordspath)
                            else: dataframe=pd.json_normalize(data)
                            nestedcolslist=list(dataframe.columns)
                            nestedcols=st.multiselect("Select All Fields which are Nested",options=nestedcolslist,key="nestecoloptios1",
                                                      help="These are Chield fields ,consisting if List of records...These are shown in Round Grey background ")
                                    
                                    #st.write(nestedcols)
                            if nestedcols:
                                for col in nestedcols:
                                    #st.write(col) 
                                    dataframe[col] = dataframe[col].apply(lambda x: json.dumps(x))

                    elif ftype=='XML':
                        #xml=st.file_uploader("xml file",type='xml',key="xmlfile")
                        #read this in file
                        
                        fileformate=st.selectbox("Select encoding formate",("utf-16","utf-8"),key="utfsb")
                        #text_xml = xml.read()
                        #tags=st.text_input("Enter Tags seperated by comma",key="tags")
                        #tagslist=tags.split(",")
                        xml=uploaded_file.getvalue().decode(fileformate)
                        #st.write(xml)
                        xml=xml.strip().replace("&amp;","and")
                        xml=xml.replace("&#4","")
                        #st.write(xml)
                        #dfx = pdx.read_xml(xml, ['ENVELOPE','BODY','DATA','COLLECTION'])
                        #if len(tagslist)>1:
                            #dfx = pdx.read_xml(xml,tagslist)
                        #else: 
                        dfx = pdx.read_xml(xml)
                        #print(dfx)
                        dfx = dfx.pipe(fully_flatten)
                        #print(dfx)
                        dataframe= pd.DataFrame(dfx)
                        #st.dataframe(dataframe)
                    else:
                        #generate dataframe     
                        rb=st.radio("Select File Structure Type",options=("Simple","Nested"),key="rbxl",
                                    help="Select Nested if Data has Parent & Chield records eg Sales Invoice & Stock Details for each ale Invoice",horizontal=True)       
                        
                        if rb=="Simple": dataframe = pd.read_excel(uploaded_file,skiprows=header_row-1,skipfooter=footer_row)
                        else: 
                            dataframe = pd.read_excel(uploaded_file,skiprows=header_row-1,skipfooter=footer_row)
                            all_columns=list(dataframe.columns)
                            parent_cols=st.multiselect("To Merge Chield recorsd in single row...Keep Columns of Parent record & Remove List of Chield Columns",options=all_columns,key="nestecoloptiosexl",default=all_columns,
                                                        help="Chield / Nested fields are Merged in single row...eg- in Sales invoice- Stock items with units & rates")
                            if parent_cols.__len__()!=all_columns.__len__():
                                records=None
                                j=None
                                #fill forward Na values for parent
                                dataframe[parent_cols]=dataframe[parent_cols].ffill(axis=0)
                                #fill na
                                dataframe.fillna(dataframe.dtypes.replace({'object': 'N.A.', 'float64': 0}),inplace=True)
                            
                                #st.dataframe(dataframe)
                                chield_cols = [item for item in all_columns if item not in parent_cols]
                                #st.write(chield_cols,parent_cols)
                                #cmdb=st.button("try",key="try")
                                j=(dataframe.groupby(parent_cols).apply(lambda x: x[chield_cols].to_dict('records')).reset_index()
                                                .rename(columns={0:'Chield-Data'})
                                                .to_json(orient='records'))
                                    #print(json.dumps(json.loads(j), indent=2, sort_keys=True))
                                dataframe= pd.read_json(j)
                                #st.write(j)
                                #expand nested fileds
                                
                                nestedcols=['Chield-Data']
                                for col in nestedcols:
                                #st.write(col) 
                                    dataframe[col] = dataframe[col].apply(lambda x: json.dumps(x))
                            #st.write(dataframe)
                            else:
                                if 'Chield-Data' in dataframe.columns:
                                    dataframe = dataframe.drop(columns=['Chield-Data'], axis=1)
                            
                    
                    #try: 
                    if dataframe is not None:
                        for y in dataframe.columns:
                            #st.write(y)
                            #check if  column is Boolion type
                            if(pd.api.types.is_bool_dtype(dataframe[y])):
                                #convert to string
                                
                                dataframe[y] = dataframe[y].map({True: 'True', False: 'False'})
                                #st.write(y)
                        st.success("Preview Data...")
                        st.dataframe(dataframe)
                        
                        #check if colum name=index or Index
                        #if 'Index' in dataframe.columns or 'index' in dataframe.columns:
                        cols=['index','autoaudit_status','autoaudit_sampled']
                        if dataframe.columns.str.lower().isin(cols).any():
                            #st.error(f'Column name with "Index" or "index" not allowed...Please change colum Name')
                            message=f"Column name with - 'Index','AutoAudit_Status','AutoAudit_Sampled' -not allowed...Please change colum Name"
                        else:
                            if st.button("Create Data Set",key="b1"):
                                if table_name:
                                    if addnew=="new":
                                        message=create_dataset(dataframe,table_name,comp_name,person_responsible)
                                        st.success(message) 
                                    else:
                                        message=add_datato_ds(dataframe,ds_name,comp_name)
                                        st.success(message)      
                                else:
                                    st.success("Please enter Data Set Name")
                                    message="Please enter Data Set Name"
                                    #masters.empty()
                        #del & clear DataFrame
                        del [[dataframe]]
                        dataframe=pd.DataFrame()  
                    #except: 
                else:
                    #st.error("Upload File")
                    message="Upload File"
            except Exception as e:
                #st.error("ERROR....Invalid Input")
                message=f"{e} - ERROR....Invalid Input or Error in Import"
                pass
            return message
                

        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        
        #st.subheader("Masters")
        
        with st.sidebar.markdown("# Masters "):
            master_options = st.radio(
            'Select Option',
            ('Add New Data Set', 'Add Records to Existing Data Set','Select Sample Data for Audit','Set Verification Check List for Data Set','Update Risk Weights for Data Set','Compare Audited Dataset with Current Version','Set Audit Check List','Link Audit Checklist with Vouching, Verification & Other Remarks'))            
        if master_options=='Add New Data Set':
            #function for fileupload
            
                #return message
            #st.session_state['url']="https://www.youtube.com/watch?v=lP7IRGPp-ZM"
            st.info('**Add New Data Set**')
            ftype=st.radio("Select Data Source",options=['CSV','XLSX','JSON','SQL','API'],horizontal=True,
                           help="Import Data from file types like- CSV,XLSX,JSON or Get by- SQL Query or API",key="opcrds")
            
            if ftype=='CSV':
                new_title = f'<p style="color:Red;">1) Check that - First Row contains column Headings.<br>2) File is of - .csv type.<br>3) No column should have name - index.</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                #st.error(f"1) Check that - First Row contains column Headings..\n2) File is of - .csv type\n3) No column should have name - index")
                
            elif ftype=='JSON':
                new_title = f'<p style="color:Red;">Check the Result before Importing DataSet</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                #st.error('Check the Result before Importing DataSet')
            
            elif ftype=='XML':
                new_title = f'<p style="color:Red;">Check the Result before Importing DataSet</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                #st.error('Check the Result before Importing DataSet')
            elif ftype=='SQL':
                new_title = f'<p style="color:Red;">Check the Result before Importing DataSet</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                #st.error('Check the Result before Importing DataSet')
            
            elif ftype=='API':
                new_title = f'<p style="color:Red;">Check the Result before Importing DataSet</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                #st.error('Check the Result before Importing DataSet')    
            
            else:
                new_title = f'<p style="color:Red;">1) Check that - First Row contains column Headings.<br>2) File is of - .xlsx type.<br>3) File contains only 1 sheet.<br>4) No column should have name - index.</p>'
                st.markdown(new_title, unsafe_allow_html=True)

                #st.error(f"1) Check that - First Row contains column Headings..\n2) File is of - .xlsx type\n3) File contains only 1 sheet\n4) No column should have name - index")
            #st.warning("Check ...First Column is Primary Key / Unique")
            #st.markdown("""---""")
            auditee=get_auditee_comp()
            table_name=""
            if auditee.empty:
                st.error(f"No Auditee assigned to Current Company...\n Assign Atleast 1 user with Auditee Role")
                
            else:
                placeholder=st.empty()
                with placeholder.container():
                    message=""
                    substring=["'",'"',':','.','+','-',',',';','`','~','@','#','!','$','%','^','&','*','(',')','[',']','{','}','/','<','>','?']
                    substring1="Special Charaters except _ are not allowed; Name Must be Unique"
                    spchr=True          
                    table_name=st.text_input("Enter Name of Data Set to be Imported*",key="tablename1",placeholder=substring1,help=substring1)
                    table_name=table_name.replace(" ", "_")
                    if table_name:
                        for strn in substring:
                            if strn in table_name:
                                spchr=True
                                break
                            else:
                                message="Enter Name & then Press ENTER to move ahead"
                                spchr=False
                            
                        if spchr==True:
                            # t="Enter Name & then Press ENTER to move ahead"
                            # new_title=f'<p style="color:Red;">{t}</p>'
                            # st.markdown(new_title, unsafe_allow_html=True)
                            message=substring1
                        else:
                                st.write(f"Data Set with name- *{table_name}* will be created.")
                                c1,c2= st.columns(2)
                                with c1:
                                    person_responsible=st.selectbox("Select Auditee, who will be responsible for Queries",auditee,key="sbperson_responsibleok")
                                
                                if ftype=='CSV':
                                    c1,c2= st.columns(2)
                                    with c1:
                                        header_row=st.number_input("Row Number of Column Headers",min_value=1,value=1,key="headrerowcsv",help="Row Number for Header...from this row Data will be imported.")
                                    with c2:
                                        footer_row=st.number_input("No of Rows to skip from Bottom",min_value=0,value=0,key="footerrowcsv",help="for these rows from Bottom of Table, Data will not be imported.")
                                    uploaded_file = st.file_uploader("Upload a file",type='csv',key="uploadfile2")
                                    message=fileupload(uploaded_file,ftype,table_name,"new")                        
                                elif ftype=='JSON':
                                    uploaded_file = st.file_uploader("Upload a file",type='json',key="uploadfile3")
                                    message=fileupload(uploaded_file,ftype,table_name,"new") 
                                elif ftype=='XML':
                                    uploaded_file = st.file_uploader("Upload a file",type='xml',key="uploadfilexml3")
                                    message=fileupload(uploaded_file,ftype,table_name,"new") 
                                elif ftype=='SQL':
                                    st.info("Import using SQL Query")
                                    message=fileupload("uploaded_file",ftype,table_name,"new")
                                elif ftype=='API':
                                    st.info("Import using API")
                                    message=fileupload("uploaded_file",ftype,table_name,"new")
                                else:
                                    c1,c2= st.columns(2)
                                    with c1:
                                        header_row=st.number_input("Row Number of Column Headers",min_value=1,value=1,key="headrerow",help="Row Number for Header...from this row Data will be imported.")
                                    with c2:
                                        footer_row=st.number_input("No of Rows to skip from Bottom",min_value=0,value=0,key="xlsxrowcsv",help="for these rows from Bottom of Table, Data will be imported.")
                                    uploaded_file = st.file_uploader("Upload a file",type='xlsx',key="uploadfile1")
                                    message=fileupload(uploaded_file,ftype,table_name,"new") 
                    else: message="Enter Name & then Press ENTER to move ahead"
                if message=="Data Set Added Successfully": placeholder.empty()
                st.success(message)
                                    #st.error("Run time Error...Invalid Input or Data type Mismatch")
        
        elif master_options=='Add Records to Existing Data Set':
                #st.session_state['url']="https://docs.streamlit.io/library/api-reference/layout/st.columns"
                st.info("**Add data to Existing Data Set**")
                ftype=st.radio("Select File Type",options=['CSV','XLSX','JSON','SQL','API'],horizontal=True,
                           help="Import Data from file types like- CSV,XLSX,JSON or Get by- SQL Query or API",key="opaddcrds")
               
                mes="Check that all colums are Exactly same as per Existing Data Set, before uploading."
                original_title = f'<p style="color:Red; ">{mes}</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                #st.markdown("""---""")
                #get list of ds_name for current company
                ds_names=get_dsname(int(st.session_state['AuditID']))
                if ds_names.empty:
                    st.error(f"No Data Sets for Current Company...\n First Add Data Set in current Company.")
                else:
                    placeholder=st.empty()
                    message=""
                    with placeholder:
                        col1, col2 =st.columns(2)
                        with col1:
                            st.success("Select Data Set to add Records...")
                            ds_name=st.selectbox("Select Data Set Name...",ds_names,key="sb0")
                            st.write("**Current Data Set**")
                            dsname=f"{st.session_state['AuditID']}_{ds_name}"
                            df=get_entire_dataset(dsname)
                            df.drop(columns=['AutoAudit_Status','AutoAudit_Sampled'],inplace=True)
                            st.dataframe(df)
                        with col2:
                            st.success("Check Data to Add to Current Data Set")
                            if ftype=='CSV':
                                header_row=st.number_input("Row Number of Colum Headers",min_value=1,value=1,key="headrerowcsv11",
                                                            help="Row Number for Header...from this row Data will be imported.")
                                footer_row=st.number_input("No of Rows to skip from Bottom",min_value=0,value=0,key="footerrowcsv1",help="for these rows from Bottom of Table, Data will be imported.")
                                
                                uploaded_file = st.file_uploader("Upload a file",type='csv',key="uploadfile22")
                                
                            elif ftype=='JSON':
                                uploaded_file = st.file_uploader("Upload a file",type='JSON',key="uploadfile23")
                            elif ftype=='XML':
                                uploaded_file = st.file_uploader("Upload a file",type='xml',key="uploadfilexml")
                            elif ftype=='SQL':
                                st.info("Import using SQL Query")
                                uploaded_file="uploadfile"
                            elif ftype=='API':
                                st.info("Import using API")
                                uploaded_file="uploadfile"
                            else:
                                header_row=st.number_input("Row Number of Colum Headers",min_value=1,value=1,key="headrerow1",
                                                           help="Row Number for Header...from this row Data will be imported.")
                                footer_row=st.number_input("No of Rows to skip from Bottom",min_value=0,value=0,key="footerrowxl1",help="for these rows from Bottom of Table, Data will be imported.")
                                uploaded_file = st.file_uploader("Upload a file",type='xlsx',key="uploadfile11")
                                
                            #uploaded_file = st.file_uploader("Upload a file",type='xlsx',key="1uploadfile1")
                            
                        
                            if uploaded_file is not None:
                                    dataframe=None
                                    if ftype=='CSV':
                                        rb=st.radio("Select File Structure Type",options=("Simple","Nested"),key="rbxCSVl",
                                                        help="Select Nested if Data has Parent & Chield records eg Sales Invoice & Stock Details for each ale Invoice",horizontal=True)       
                        
                                        if rb=="Simple":dataframe = pd.read_csv(uploaded_file,encoding= 'unicode_escape',skiprows=header_row-1,skipfooter=footer_row)
                                        else:
                                            dataframe = pd.read_csv(uploaded_file,encoding= 'unicode_escape',skiprows=header_row-1,skipfooter=footer_row)
                                            dataframe=nested_csv(dataframe)
                                            
                                    elif ftype=='JSON':
                                        data = json.load(uploaded_file)
                                        recordspath=st.text_input("Field containing Data",key="jsonrecordpadd2",placeholder="This is the Field Containing Data....Keep it Blank if Data preview is correct else,Type & press Tab / Enter",
                                                                help="Check the data shown in Table below, change the name & try")
                                        #nestedcols=st.text_input("Enter Column names which are Nested- seperated by ,Comma",key="nestedcolumnams")
                                        if recordspath:
                                            dataframe=pd.json_normalize(data,record_path=recordspath)
                                        else: 
                                            dataframe=pd.json_normalize(data)
                                            
                                        nestedcolslist=list(dataframe.columns)
                                        nestedcols=st.multiselect("Select All Fields which are Nested",options=nestedcolslist,key="nestecoloptiadd2",
                                                                    help="These are Chield fields ,consisting if List of records...These are shown in Round Grey background ")
                                        
                                        #st.write(nestedcols)
                                        if nestedcols:
                                            for col in nestedcols:
                                                #st.write(col) 
                                                dataframe[col] = dataframe[col].apply(lambda x: json.dumps(x))
                                    
                                    elif ftype=='XML':
                                                        
                                        fileformate=st.selectbox("Select encoding formate",("utf-16","utf-8"),key="utfsb1")
                                        #text_xml = xml.read()
                                        tags=st.text_input("Enter Tags seperated by comma",key="tags1")
                                        tagslist=tags.split(",")
                                        xml=uploaded_file.getvalue().decode(fileformate)
                                        #st.write(xml)
                                        xml=xml.strip().replace("&amp;","and")
                                        xml=xml.replace("&#4","")
                                        #st.write(xml)
                                        #dfx = pdx.read_xml(xml, ['ENVELOPE','BODY','DATA','COLLECTION'])
                                        if len(tagslist)>1:
                                            dfx = pdx.read_xml(xml,tagslist)
                                        else: dfx = pdx.read_xml(xml)
                                        #print(dfx)
                                        dfx = dfx.pipe(fully_flatten)
                                        #print(dfx)
                                        dataframe= pd.DataFrame(dfx)
                                        
                                    elif ftype=='SQL':
                                        driver=st.selectbox("Select Database",("postgresql","mysql","mssql"),key="sbsql2")
                                        user=st.text_input("Enter User Name*",key="sqluser2")
                                        password=st.text_input("Enter passord*",key="sqlpass2")
                                        password = urllib.parse.quote_plus(password)
                                        hostname=st.text_input("Enter Host Name*",key="sqlhost2")
                                        port=st.text_input("Enter Port*",key="sqlport2")
                                        database=st.text_input("Enter Database Name*",key="sqldbname2")
                                        sqltext=st.text_area("Enter SQL Query*",key="tasql2")
                                        #sql="select * from users"
                                        if driver=="postgresql": driver="postgresql+psycopg2"
                                        if driver=="mssql": driver="mssql+pymssql"
                                        if driver=="mysql": driver="mssql+pymysql"
                                        #engine = create_engine('mysql://scott:tiger@localhost/test')
                                        #engine = create_engine('postgresql://user:pass@localhost:5432/mydb')
                                        engintext=f"{driver}://{user}:{password}@{hostname}:{port}/{database}"
                                        #st.write(engintext)
                                        if sqltext and user and password and hostname and port and database: 
                                            engine=create_engine(engintext)
                                            dataframe=pd.read_sql(sql=sqltext,con=engine)
                                        else:
                                            st.error("Enter All Required Fields")
                                    
                                    elif ftype=='API':
                                        reqtype=st.selectbox("Request Type",("GET","POST"),key="getpost3")
                                        url = st.text_input("Enter URL*",key="stturl3",placeholder="without single or double quotes")
                                        jLoad=None
                                        payloadtype=st.radio("Is Payload Text or {Dictionary}",options=("{Dictionary}","Text"),key="pods3",horizontal=True)
                                        payload = st.text_area("Enter Payload",key="apipayload3",placeholder="text must be in { curly brackets}")
                                        #payload=str(payload).strip("'<>() ").replace('\'', '\"')
                                        if payload: 
                                            if payloadtype=="{Dictionary}":
                                                #jLoad=ast.literal_eval(str(jLoad))
                                                j_obj=json.loads(payload)
                                                st.success(j_obj)
                                                jLoad = json.dumps(j_obj)
                                                st.success(payload)
                                                st.success(jLoad)
                                            else :jLoad=payload

                                        
                                        header=None
                                        headers = st.text_area("Enter Headers",key="apipayheader3",placeholder="text must be in { curly brackets}")
                                        if headers: header=ast.literal_eval(headers)
                                        #if st.button("Get Data from API",key="apigetdata"):
                                        if url:
                                            
                                            if reqtype=="GET" : 
                                                
                                                response = requests.request("GET", url, headers=header, data=jLoad)
                                            else: 
                                                response = requests.request("POST", url, headers=header, data=jLoad)
                                            
                                            data=response.json()
                                            recordspath=st.text_input("Field Containing Data",key="jsonrecordpath23",help="Check the data shown in Table below, change the name & try")
                                            if recordspath: dataframe=pd.json_normalize(data,record_path=recordspath)
                                            else: dataframe=pd.json_normalize(data)
                                            nestedcolslist=list(dataframe.columns)
                                            nestedcols=st.multiselect("Select All Fields which are Nested",options=nestedcolslist,key="nestecoloptios13",
                                                                    help="These are Chield fields ,consisting if List of records...These are shown in Round Grey background ")
                                                    
                                                    #st.write(nestedcols)
                                            if nestedcols:
                                                for col in nestedcols:
                                                    #st.write(col) 
                                                    dataframe[col] = dataframe[col].apply(lambda x: json.dumps(x))

                       
                                    else:  
                                        rb=st.radio("Select File Structure Type",options=("Simple","Nested"),key="rbxll",
                                                        help="Select Nested if Data has Parent & Chield records eg Sales Invoice & Stock Details for each ale Invoice",horizontal=True)       
                                                  
                                        if rb=="Simple":dataframe = pd.read_excel(uploaded_file,skiprows=header_row-1,skipfooter=footer_row)
                                        else:
                                            dataframe = pd.read_excel(uploaded_file,skiprows=header_row-1,skipfooter=footer_row)
                                            dataframe=nested_csv(dataframe)
                                            
                                    if dataframe is not None:  
                                        for y in dataframe.columns:
                                        #check if  column is Boolion type
                                                if(pd.api.types.is_bool_dtype(dataframe[y])):
                                                    #convert to string
                                                    dataframe[y] = dataframe[y].map({True: 'True', False: 'False'})
                                                    #st.write(y)
                                        dfmax=df['index'].max()
                                        dataframe.insert(0,"index",range(dfmax+1, dfmax+1 + len(dataframe)))
                                        dataframe.columns = dataframe.columns.astype(str)
                                        st.dataframe(dataframe)
                                        dfcol1=df.columns.tolist()
                                        dfcol2=dataframe.columns.tolist()
                                        #st.info(dfcol1)
                                        #st.info(dfcol2)
                                        if dfcol1==dfcol2: 
                                            datatype=[]
                                            for col in dfcol1:
                                                if df[col].dtype!=dataframe[col].dtype:
                                                    st.error(f"Data type Mismatch in Column - {col}: Data set Type is-{df[col].dtype} ,But Data type of this file is-{dataframe[col].dtype}")
                                                    datatype.append(False)
                                            if all(datatype):
                                                if st.button("Append to Data Set",key="b11"):
                                                    message=add_datato_ds(dataframe,ds_name,comp_name)
                                                    st.success(message)
                                                    placeholder.empty()
                                        else:
                                            st.warning("Mismatch in Colums of two Datasets...Please upload Data set with same structure.")
                                        #del & clear DataFrame
                                        #check colum datatypes
                                        
                                        
                                        del [[dataframe,df]]
                                        dataframe=pd.DataFrame()
                                        df=pd.DataFrame()  
                    st.success(message)
            
        elif master_options=='Select Sample Data for Audit':
            st.info("**Select Sample to Audit Data Set**")
            ds_name=st.selectbox("Select Data Set",ds_names,key="sb1sam")
            if ds_name=="---":
                #st.error("Select Data Set Name")
                mes="Select Data Set Name from above List"
                original_title = f'<p style="color:Red; ">{mes}</p>'
                st.markdown(original_title, unsafe_allow_html=True)
            else:
                ds_file_name=f"{(st.session_state['AuditID'])}_{ds_name}"
                optionssampl=st.radio("1",("Add Sampling","Remove Sampling"),horizontal=True,key="optionfirst",label_visibility="hidden")
                #with st.expander("Add Sampling"):
                #st.markdown("""---""")
                if optionssampl=="Add Sampling":
                    #st.markdown("""---""")
                    #st.success("Select Sampling Method")
                    #setsam=st.radio("",('Select All','Filter & Select','Random Sampling'),horizontal=True,key='strcrudassam')
                    setsam=st.selectbox("Select Sampling Method",options=('Select All','Filter & Select','Random Sampling'),key="slelctsamples")
                    if setsam=='Filter & Select':
                        #g
                        #sel_Observations=selected[0]['Criteria']
                            #st.success(sel_Observations)
                        #placeholder=st.empty()
                        #with placeholder.container():
                            
                        df_unsampled=get_dataset_nonsampled(ds_file_name)
                        st.success(f'Total Rows **Not** Sampled for Auditing - **{len(df_unsampled)}**')
                        st.subheader('Select Rows to Add to Sample Data')
                        builder = GridOptionsBuilder.from_dataframe(df_unsampled)
                        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=15)
                        builder.configure_selection(selection_mode="multiple",use_checkbox=True)
                                    #builder.configure_default_column(editable=True)
                        go = builder.build()
                                    #uses the gridOptions dictionary to configure AgGrid behavior.
                        grid_response=AgGrid(df_unsampled, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                                    #selelcted row to show in audit AGGrid
                        add_links = grid_response['selected_rows']
                        with st.form(key='frlnksam',clear_on_submit=True):
                            #col1 ,col2 =st.rows(2)
                            #with col1:                                    
                                    
                                                        
                                    addlinkb=st.form_submit_button("Add Selected >>")
                                    if addlinkb:
                                        if add_links:
                                            
                                            add_links=[d['index'] for d in add_links]
                                                #st.write(del_links)                                              
                                            dfm=add_sampling(ds_file_name,add_links)
                                            st.success(dfm)
                                            #placeholder.empty()
                                        else:
                                            st.success('Select 1 or More Rows to Add Sample Data...')
                        with st.expander("See Rows Sampled..."):
                                    
                            df_sampled=get_dataset_sampled(ds_file_name)
                            st.success(f'Rows Sampled - {len(df_sampled)}')
                                        #df_linked.drop(['id'],axis=1,inplace=True)
                            st.dataframe(df_sampled) 
                        del[[df_unsampled,df_sampled]]
                        df_sampled=pd.DataFrame()
                        df_unsampled=pd.DataFrame()
                                    
                    elif setsam=='Select All':
                        df_unsampled=get_dataset_nonsampled(ds_file_name)
                        #st.success(f'Total Rows Not yet Sampled - {len(df_unsampled)}')
                        st.success(f'Total Rows **Not** Sampled for Auditing - **{len(df_unsampled)}**')
                        if len(df_unsampled)>0:
                            st.subheader('Add All the Rows to Sample Data') 
                            placeholder=st.empty()  
                            #placeholder.text("empty container")
                            
                            with placeholder.form(key='frlnksamall',clear_on_submit=True): 
                                added=""        
                                st.dataframe(df_unsampled)
                                addall=st.form_submit_button("Add All to Sample Data")
                                #cmdadd=st.button("Add All to Sample Data",key='adalls')
                                if addall:
                                    rows=df_unsampled['index']
                                #st.write(rows)
                                    added=add_sampling(ds_file_name,rows)
                                    
                                    placeholder.empty()
                            st.success(added)
                        else:
                            st.subheader('All the Rows are already added to Sample Data')
                        del[df_unsampled]
                        #df_sampled=pd.DataFrame()
                        df_unsampled=pd.DataFrame()
                    else:
                         #col1,col2=st.columns(2)
                        #with col2:     
                                         
                        df_unsampled=get_dataset_nonsampled(ds_file_name)
                        #with col1:   
                        
                        st.success(f'Total Rows **Not** Sampled for Auditing - **{len(df_unsampled)}**')
                        st.subheader('Add Random Rows to Sample Data')
                        if len(df_unsampled)>0:
                                #st.success('Select Method')
                                randops=st.radio('Select Sampling Method',("Get Random Number of Rows"," Get % of Total Rows"),horizontal=True)
                                
                                if randops=='Get Random Number of Rows':
                                    nrow=st.number_input("How many Random Rows you want to Select...",min_value=1,max_value=len(df_unsampled),key='nrow')
                                    
                                    #addsam=st.button("Get Random Rows",key='samp1')
                                    
                                    rand=df_unsampled.sample(n=nrow,random_state=1)
                                                                                                                 
                                else:
                                    nper=st.number_input("How much % of Random Rows you want to Select...",min_value=1.00,max_value=100.00,key='nper')
                                    rand=df_unsampled.sample(frac=nper/100,random_state=1)
                                    
                                if len(rand)>0:
                                    placeholder=st.empty()
                                    added=""
                                    with placeholder.form("keyrand",clear_on_submit=True):
                                        st.write("Random Data Selected...")
                                        st.dataframe(rand)
                                        rows=rand['index'].tolist()
                                        #samp=(f'Add above {len(rand)} Rows to Sample Data-')
                                        addsam=st.form_submit_button("Add Above to Sample")
                                        if addsam:
                                            
                                            #st.write(rows)
                                            added=add_sampling(ds_file_name,rows)
                                              
                                            placeholder.empty()
                                    st.success(added)
                                else:
                                    st.success("No Data Sampled....Increase Sample Size")
                        else:
                                st.success('All the Rows are already added to Sample Data')
                        with st.expander("See Rows Not yet Sampled"):
                            df_unsampled=get_dataset_nonsampled(ds_file_name)
                            st.success(f'Total Rows Not yet Sampled - {len(df_unsampled)}')
                            st.dataframe(df_unsampled)
                        del[df_unsampled]
                        #df_sampled=pd.DataFrame()
                        df_unsampled=pd.DataFrame()           
                 
                else:       
                #with st.expander("Remove Sampling"):
                    #st.markdown("""---""")
                    st.subheader("Select Rows to Remove from Sampled Data")
                    
                    col1 ,col2 =st.columns(2)
                    with col1:
                            #st.success('Rows Sampled and not Yet Audited')
                            df_sampled=get_dataset_sampled(ds_file_name)
                            st.success(f'Rows Sampled and not Yet Audited - {len(df_sampled)}')
                            builder = GridOptionsBuilder.from_dataframe(df_sampled)
                            builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=15)
                            builder.configure_selection(selection_mode="multiple",use_checkbox=True)
                            #builder.configure_default_column(editable=True)
                            go = builder.build()
                            #uses the gridOptions dictionary to configure AgGrid behavior.
                            grid_response=AgGrid(df_sampled, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                            #selelcted row to show in audit AGGrid
                            del_links = grid_response['selected_rows']
                            with st.form(key='frlnksamd',clear_on_submit=True):                          
                                dellinkb=st.form_submit_button("Remove Selected >>")
                                if dellinkb:
                                        if del_links:
                                            #st.write(len(del_links))
                                            del_links=[d['index'] for d in del_links]
                                            #st.write(del_links)                                              
                                            dfm=delete_sampling(ds_file_name,del_links)
                                            st.success(dfm)
                                        else:
                                            st.success('Select 1 or More Rows to Remove from Sample Data...')
                    with col2:
                            #st.success('Rows Un-Sampled')
                            df_unsampled=get_dataset_nonsampled(ds_file_name)
                            st.success(f'Rows Un-Sampled - {len(df_unsampled)}')
                            #df_linked.drop(['id'],axis=1,inplace=True)
                            st.dataframe(df_unsampled) 
                
                    del[[df_unsampled,df_sampled]]
                    df_sampled=pd.DataFrame()
                    df_unsampled=pd.DataFrame()
                    
                    
        elif master_options=='Set Verification Check List for Data Set':
                st.info("**Set Audit Verification Check List**")
               
                #ds_names=get_dsname(int(st.session_state['AuditID']))
                ds_name=st.selectbox("Data Set Name",ds_names,key="sb1")
                    #if st.button("View Current check list",key="cc1"):
                        #veri_df=get_verification(ds_name,int(st.session_state['AuditID']))
                        #st.dataframe(veri_df)
                    #Chek_List=pd.DataFrame()
                if ds_name=="---":
                    mes="Select Data Set Name from above List"
                    original_title = f'<p style="color:Red; ">{mes}</p>'
                    st.markdown(original_title, unsafe_allow_html=True)
                else:
                    #placeholder=st.empty()
                    #sta=""
                    with st.form("Verification Criteria",clear_on_submit=True):
                            c1,c2 =st.columns(2)
                            with c1:
                                Crtiteria=st.text_area("Enter Verification Criteria*",key="verarea",placeholder="Required;Must be Unique; Dont Use Quotation marks")
                            with c2:
                                risk_weight=st.slider("Set Risk Weights",min_value=1,max_value=10,key='slider2',value=1)
                                
                                if risk_weight >=0 and risk_weight <=3:
                                    risk_category='Low'
                                elif risk_weight >=4 and risk_weight <=7:
                                    risk_category='Medium'
                                else:
                                    risk_category='High'
                            
                                                
                            submitted = st.form_submit_button("Submit")
                            if submitted:
                                #add above to database
                                if Crtiteria:
                                    sta=add_verification_criteria(Crtiteria,ds_name,comp_name,risk_weight,risk_category)
                                    st.success(sta)
                                else:
                                    st.error('Criteria can not be blank.')
                    #st.success(sta)
                    with st.expander("View Verification Criteria"):
                            #st.header("Verification Criteria")
                            veri_df=get_verification(ds_name,int(st.session_state['AuditID']))
                            st.dataframe(veri_df)
                                
        elif master_options=='Set Audit Check List':
            st.info("**Set Check List for Audit**")
            auditid=int(st.session_state['AuditID'])
            crud=st.radio("1",('View','Add New','Modify','Delete'),horizontal=True,key='strcrudas',label_visibility="hidden")
            df=get_audit_checklist(auditid)
            df.sort_values(by=['Audit_Area','Heading'],inplace=True)
            builder = GridOptionsBuilder.from_dataframe(df)
            builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
            builder.configure_selection(selection_mode="single",use_checkbox=True)
                        #builder.configure_default_column(editable=True)
            go = builder.build()
                        #uses the gridOptions dictionary to configure AgGrid behavior.
            grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                        #selelcted row to show in audit AGGrid
            selected = grid_response['selected_rows']
                #st.data
            if crud=='Add New':
                
                auditee=get_auditee_comp()
                if auditee.empty:
                    st.success(f"No Auditee assigned to Current Company...\n Assign Atleast 1 user with Auditee Role")
                else:
                    #st.success('Import Default Check List OR Enter details to Add New Records')
                    add_options= st.radio("1",('Import Default Check List','Import Check List from Templet', 'Add Check List Manually'),horizontal=True,key='op1',label_visibility="hidden")
                        

                    if add_options=='Import Default Check List':
                        placeholder=st.empty()
                        res=""
                        with placeholder.container():
                            chklist=st.selectbox("Choose Checklist-",("Internal Audit","Tax Audit","CARO"),key="dechlist")
                            if chklist=="Internal Audit": chfile="checklist.xlsx"
                            if chklist=="Tax Audit": chfile="taxaudit.xlsx"
                            if chklist=="CARO": chfile="caro.xlsx"
                            with st.expander("Show Default Audit Check List"):
                                showchecklist=st.button("Show Check List...",key="viedefatchk")
                                if showchecklist:
                                    df=pd.read_excel(chfile)
                                    st.dataframe(df)
                            with st.form("Import Checklist",clear_on_submit=True):
                                st.success("**Do You Want to Import Default Check List...**")
                                person_responsible=st.selectbox("Select Defalut Person Responsible...You can Modify Later.",auditee,key="sbperson_responsibleck1i")
                                impbt=st.form_submit_button("Import")
                                if impbt:
                                        df=pd.read_excel(chfile)
                                        
                                        df['Person_Responsible']=person_responsible
                                        df['Audit_id']=auditid
                                        res=import_defalut_checklist(df)
                                        placeholder.empty()
                        st.success(res)
                        
                    elif  add_options=='Import Check List from Templet': 
                        #download excel Templet
                        st.success("**Download Excel Templet**")
                        with open("templete.xlsx", 'rb') as f:
                            st.download_button('Download Templet',f,"Templet.xlsx",key="dwnldtam")    
                        
                        #upload Templet 
                        st.success("**Upload Excel Templet**")  
                        #st.error("Upload Excel Templet...****")
                        t=f"(1)Check- Do not change Number of Columns or Column Headings. (2)All Columns are required, if value is Null / Blank that row will not be imported."
                        new_title=f'<p style="color: red;">{t}</p>'
                        st.markdown(new_title, unsafe_allow_html=True)

                        person_responsible=st.selectbox("Select Defalut Person Responsible...You can Modify Later.",auditee,key="sbperson_responsibleck2")
                        uploaed_file=st.file_uploader("Upload File",type=['xlsx'],key='fileuploadxl',)
                        if uploaed_file is not None:
                            try:
                                df=pd.read_excel(uploaed_file).dropna()
                                if df.columns.tolist()==['Criteria','Audit_Area','Heading']:
                                    cmdok=st.button("Import Templet",key="imprtTemplet")
                                    if cmdok:
                                        df['Person_Responsible']=person_responsible
                                        df['Audit_id']=auditid
                                        res=import_defalut_checklist(df)
                                        st.success(res)
                                        st.success("Click checkbox of any row to Refresh Table")
                                    
                                else:                                
                                    st.error("Check Excel sheet should be Exactly as per Templet, with Columns- 'Criteria', 'Audit_Area', 'Heading'")
                            except ValueError:
                                st.error("Can not Import..Wrong Excel Format")
                                
                    else:
                        #addc=st.button('Add Check List',key='defchkli')
                        #if addc:
                        #placeholder=st.empty()
                        #res=""
                        with st.form("Add Checklist",clear_on_submit=True):
                                #st.write("*Don't Use Quotation marks*")
                                criteria=st.text_area("Enter Criteria / Checklist*",key='criteriac',placeholder="Required;Must be Unique")
                                Audit_area=st.text_input("Enter Audit Area*",key='Aarea',placeholder="Required")
                                heading=st.text_input("Enter Heading / Group*",key='Heading',placeholder="Required")
                                risk_weight=st.slider("Set Risk Weights",min_value=1,max_value=10,key='slider2rw',value=1)
                                person_responsible=st.selectbox("Select Person Responsible",auditee,key="sbperson_responsibleck")
            
                                if risk_weight >=0 and risk_weight <=3:
                                    risk_category='Low'
                                elif risk_weight >=4 and risk_weight <=7:
                                    risk_category='Medium'
                                else:
                                    risk_category='High'
                                submitted_chk = st.form_submit_button("Submit")
                                                               
                                if submitted_chk:
                                    
                                    if criteria  and Audit_area and heading:
                                        res=add_audit_cheklist(criteria,Audit_area,heading,risk_weight,
                                                                  risk_category,person_responsible,auditid)
                                        #placeholder.empty()
                                    else:
                                        st.error("Criteria, Audit Area & Headings are Mandatory fields")
                                        
                        #st.success(res)

            elif crud=='Modify':
                auditee=get_auditee_comp()
                if auditee.empty:
                    st.success(f"No Auditee assigned to Current Company... Assign Atleast 1 user with Auditee Role")
                else:
                    if selected:
                            
                            placeholder = st.empty()
                            
                            strng=""
                            with placeholder.form("Modify Checklist Doc",clear_on_submit=True):
                                st.success('Enter details to Modify Selected Record')
                                #st.write("*Don't Use Quotation marks*")
                                mcriteria=st.text_area("Update Criteria*",key='mcriteria',value=selected['Criteria'].iloc[0])
                                mauditarea=st.text_input("Update Audit Area*",key='mauditarea',value=selected['Audit_Area'].iloc[0])
                                mheading=st.text_input("Update Heading / Group*",key='mheading',value=selected['Heading'].iloc[0])
                                mrisk_weight=st.slider("Update Risk Weights",min_value=1,max_value=10,key='slider2rwm',value=selected['Risk_Weight'].iloc[0])
                                mperson_responsible=st.selectbox("Update Person Responsible",auditee,key="sbperson_responsibleckm")
                
                                if mrisk_weight >=0 and mrisk_weight <=3:
                                        mrisk_levl='Low'
                                elif mrisk_weight >=4 and mrisk_weight <=7:
                                        mrisk_levl='Medium'
                                else:
                                        mrisk_levl='High'
                                    
                                roid=selected['id'].iloc[0]
                                
                                
                                submitted_chk_mod =st.form_submit_button("Submit")
                                if submitted_chk_mod:
                                    if mcriteria  and mauditarea and mheading:
                                        strng=modify_audit_cheklist(roid,mcriteria,mrisk_weight,mrisk_levl,mauditarea,
                                                                     mheading,mperson_responsible)
                                        strng=(f"{strng}; Click on CheckBox of any Row to Refresh Table") 
                                        placeholder.empty()
                                    else:
                                        st.success("Criteria, Audit Area & Heading are Mandatory fields")
                            st.success(strng)  
                    else:
                            st.success('Select a Record to Modify ....')
                        
                    
            elif crud=='View':
                st.success('')
            else:
                if selected:
                    placeholder=st.empty()
                    res=""
                    with placeholder.container():
                        st.success('Are you sure you want to Delete Selected Record')
                        if st.button("Delete Selected Record",key='delcompdocack'):
                            rid=selected['id'].iloc[0]
                            res=del_checklist(rid)
                            placeholder.empty()
                    st.success(res)
                else:
                        st.success('Select a Record to Delete ....')

        elif master_options=='Link Audit Checklist with Vouching, Verification & Other Remarks':
            st.info("**Link Audit Checklist with Vouching, Verification & Other Remarks**")
            link_options= st.selectbox('Select to Link Audit Checklist',options=("----",'Vouching & Verification','Analytical Review & Other'),key='linkingvv')
            if link_options=="----":
                mes="Select Option from above List"
                original_title = f'<p style="color:Red; ">{mes}</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                
            elif link_options=="Vouching & Verification":
                #st.subheader('Link Vouching & Verification Criterias to Audit Checklist')
                
                crud=st.radio("1",('Add Link','Delete Link'),horizontal=True,key='linkrd',label_visibility="hidden")
                if crud=="Add Link":
                    #st.success('Select Observations to Add Link...')
                    df=get_audit_checklist(auditid)
                    builder = GridOptionsBuilder.from_dataframe(df)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                                #builder.configure_default_column(editable=True)
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                                #selelcted row to show in audit AGGrid
                    selected = grid_response['selected_rows']
                    if selected:
                        sel_Observations=selected['Criteria'].iloc[0]
                        st.success(sel_Observations)
                        
                        col1 ,col2 =st.columns(2)
                        with col1:
                            st.success('Select Vouching & Verification Criterias to Link to above Checklist Item')
                            #st.write("Check 1 or More items to add ")
                            df_unlined=get_unlinked_obsr(selected['id'].iloc[0])
                            builder = GridOptionsBuilder.from_dataframe(df_unlined)
                            builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                            builder.configure_selection(selection_mode="multiple",use_checkbox=True)
                            #builder.configure_default_column(editable=True)
                            go = builder.build()
                            #uses the gridOptions dictionary to configure AgGrid behavior.
                            grid_response=AgGrid(df_unlined, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                            #selelcted row to show in audit AGGrid
                            add_links = grid_response['selected_rows']
                            with st.form(key='frlnk',clear_on_submit=True):                    
                                addlinkb=st.form_submit_button("Add Selected >>")
                                if addlinkb:
                                    if add_links:
                                        
                                        add_links=pd.DataFrame(add_links)
                                        #st.dataframe(add_links)
                                        if '_selectedRowNodeInfo' in add_links.columns:
                                            add_links.drop(['_selectedRowNodeInfo'], axis=1,inplace=True)
                                        add_links.drop(['Criteria','DataSetName'],axis=1,inplace=True)
                                        add_links.rename(columns = {'id':'vv_id'}, inplace = True)
                                        add_links['obs_id']=selected['id'].iloc[0]
                                        #st.dataframe(add_links)
                                        
                                        dfm=insert_vv_linking(add_links)
                                        #st.success(dfm)
                                        st.success(f"{dfm}: Click on Checkbox of any Row to Refresh above Table")
                                    else:
                                        st.success('Select 1 or More Rows to Add Link...')
                        with col2:
                            st.success('Vouching & Verification Criterias Linked to Checklist')
                            df_linked=get_linked_obsr(selected['id'].iloc[0])
                            df_linked.drop(['id'],axis=1,inplace=True)
                            st.dataframe(df_linked)  
                    else:
                        st.success('Select Observations to Add Link...')    
                       
                    
                    
                else:
                    st.success('Select Observations to Delete Link...')
                    df=get_audit_checklist(auditid)
                    builder = GridOptionsBuilder.from_dataframe(df)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                                #builder.configure_default_column(editable=True)
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                                #selelcted row to show in audit AGGrid
                    selected = grid_response['selected_rows']
                    
                    if selected:
                        sel_Observations=selected['Criteria'].iloc[0]
                        st.success(sel_Observations)
                        st.success('Vouching & Verification Criterias Linked to Checklist')
                        df_linked=get_linked_obsr(selected['id'].iloc[0])
                        #df_linked.drop(['id'],axis=1,inplace=True)
                        #st.dataframe(df_linked)
                        builder = GridOptionsBuilder.from_dataframe(df_linked)
                        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                        builder.configure_selection(selection_mode="multiple",use_checkbox=True)
                                #builder.configure_default_column(editable=True)
                        go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                        grid_response=AgGrid(df_linked, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                                #selelcted row to show in audit AGGrid
                        del_links = grid_response['selected_rows']                            
                        dellinkb=st.button("Delete Selected Link >>",key='delinkb')
                        if dellinkb:
                                if del_links:
                                    #st.write(len(del_links))
                                    del_links=[d['id'] for d in del_links]
                                    
                                    
                                    dfm=delete_vv_linking(del_links)
                                    st.success(f"{dfm}: Click on Checkbox of any Row to Refresh above Table")
                                else:
                                    st.success('Select 1 or More Rows to Delete Link...')
                    else:
                        st.success('Select Observations to Delete Link...')    
                    
                    
            else:
                #st.subheader('Link Analytical Review & Other Remarks to Audit Checklist')
                
                crud=st.radio("1",('Add Link','Delete Link'),horizontal=True,key='linkrdar',label_visibility="hidden")
                if crud=="Add Link":
                    #st.success('Select Observations to Add Link...')
                    df=get_audit_checklist(auditid)
                    builder = GridOptionsBuilder.from_dataframe(df)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                                #builder.configure_default_column(editable=True)
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                                #selelcted row to show in audit AGGrid
                    selected = grid_response['selected_rows']
                    if selected:
                        sel_Observations=selected['Criteria'].iloc[0]
                        st.success(sel_Observations)
                        
                        col1 ,col2 =st.columns(2)
                        with col1:
                            st.success('Select Analytical & Other Remarks to Link to above Checklist Item')
                            df_unlined=get_unlinked_obsr_ar(selected['id'].iloc[0])
                            builder = GridOptionsBuilder.from_dataframe(df_unlined)
                            builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                            builder.configure_selection(selection_mode="multiple",use_checkbox=True)
                            #builder.configure_default_column(editable=True)
                            go = builder.build()
                            #uses the gridOptions dictionary to configure AgGrid behavior.
                            grid_response=AgGrid(df_unlined, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                            #selelcted row to show in audit AGGrid
                            add_links = grid_response['selected_rows']
                            with st.form(key='frlnkar',clear_on_submit=True):                  
                                addlinkb=st.form_submit_button("Add Selected >>")
                                if addlinkb:
                                    if add_links:
                                        
                                        add_links=pd.DataFrame(add_links)
                                        #st.dataframe(add_links)
                                        if '_selectedRowNodeInfo' in add_links.columns:
                                            add_links.drop(['_selectedRowNodeInfo'], axis=1,inplace=True)
                                        add_links.drop(['Criteria','DataSetName'],axis=1,inplace=True)
                                        add_links.rename(columns = {'Id':'ar_id'}, inplace = True)
                                        add_links['obs_id']=selected['id'].iloc[0]
                                        #st.dataframe(add_links)
                                        
                                        dfm=insert_ar_linking(add_links)
                                        #st.success(dfm)
                                        st.success(f"{dfm}: Click on Checkbox of any Row to Refresh above Table")
                                    else:
                                        st.success('Select 1 or More Rows to Add Link...')
                        with col2:
                            st.success('Remarks that are Linked')
                            df_linked=get_linked_obsr_ar(selected['id'].iloc[0])
                            df_linked.drop(['id'],axis=1,inplace=True)
                            st.dataframe(df_linked)    
                    else:
                        st.success('Select Observations to Add Link...')    
                                       
                else:
                    st.success('Select Observations to Delete Link...')
                    df=get_audit_checklist(auditid)
                    builder = GridOptionsBuilder.from_dataframe(df)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                                #builder.configure_default_column(editable=True)
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                                #selelcted row to show in audit AGGrid
                    selected = grid_response['selected_rows']
                    
                    if selected:
                        sel_Observations=selected['Criteria'].iloc[0]
                        st.success(sel_Observations)
                        st.success('Criterias that are Linked')
                        df_linked=get_linked_obsr_ar(selected['id'].iloc[0])
                        #df_linked.drop(['id'],axis=1,inplace=True)
                        #st.dataframe(df_linked)
                        builder = GridOptionsBuilder.from_dataframe(df_linked)
                        #builder.configure_column('id',hide=True)
                        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                        builder.configure_selection(selection_mode="multiple",use_checkbox=True)
                                #builder.configure_default_column(editable=True)
                        
                        go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                        grid_response=AgGrid(df_linked, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                                #selelcted row to show in audit AGGrid
                        del_links = grid_response['selected_rows']                            
                        dellinkb=st.button("Delete Selected Link >>",key='delinkbard')
                        if dellinkb:
                                if del_links:
                                    #st.write(len(del_links))
                                    del_links=[d['id'] for d in del_links]
                                    
                                    
                                    dfm=delete_ar_linking(del_links)
                                    #st.success(dfm)
                                    st.success(f"{dfm}: Click on Checkbox of any Row to Refresh above Table")
                                else:
                                    st.success('Select 1 or More Rows to Delete Link...')
                    else:
                        st.success('Select Observations to Delete Link...')    
                                      
                                                   
        elif master_options=='Update Risk Weights for Data Set':
            st.info("**Update Vouching & Verification Risk Weights**")
                #st.dataframe(Chek_List,width=1000)
            ds_names=get_dsname(int(st.session_state['AuditID']))
            #st.error('Select Data Set Name...')
            ds=st.selectbox("Select Data Set Name...",ds_names,key="sbrisk1")
            #fields=get_fields_names(f"{comp_name}_{st.session_state['AuditID']}_{ds}")
            #remove wher field is null
            
            criteria=get_risk_weights_ds_vouching(ds)
            criteria=criteria[['Criteria']]
            with st.form("Risk",clear_on_submit=True):
                    c1,c2 =st.columns(2)
                    with c1:
                        criteria_selected=st.selectbox("Select Vouching & Verification Criteria",key="sf1",options=criteria)
                    with c2:
                        risk_weight=st.slider("Set Risk Weights",min_value=0,max_value=10,key='slider2',value=1)
                        
                        if risk_weight >=0 and risk_weight <=3:
                            risk_category='Low'
                        elif risk_weight >=4 and risk_weight <=7:
                            risk_category='Medium'
                        else:
                            risk_category='High'
                       
                                        
                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        if not criteria.empty:
                            #st.write(criteria)
                            updaterisk=update_risk_weights(criteria_selected,ds,int(st.session_state['AuditID']),risk_weight,risk_category)
                            #Chek_List=add_verification_criteria(Crtiteria,ds_name,comp_name,risk_weight,risk_category)
                        else:
                            st.error('Criteria can not be blank.')
            
            #st.write(field)
            with st.expander("View Risk Weights"):
                    #st.subheader("Risk Weights")
                    riskdf=get_risk_weights_ds_vouching(ds)
                    #riskdf.reset_index(drop=True, inplace=True)
                    #st.dataframe(riskdf)
                    #st.dataframe(riskdf,index=False)
                    #veri_df=get_verification(ds_name,int(st.session_state['AuditID']))
                    riskdf = riskdf.style.set_properties(**{'background-color': 'AliceBlue', 'color': 'darkblue'})
                    
                    st.dataframe(riskdf)
                    #st.write(riskdf,unsafe_allow_html=True,)
                    
        else:
                st.info("**Compare Audited Dataset with Current Version of Dataset**")
                mes="1)Upload Current Version of Dataset"
                original_title = f'<p style="color:Red; ">{mes}</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                mes="2)Check...Data Structure is Exactly  same, with same colum names"
                original_title = f'<p style="color:Red; ">{mes}</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                #st.success("1)Upload Current Version of Dataset...\n2)Check...Data Structure is Exactly  same, with same colum names")
                #st.success("Check ...Data Structure is Exactly  same, with same colum names")
                ftype=st.radio("Select Data Source",options=['CSV','XLSX','JSON','SQL','API'],key="rdio",horizontal=True)
                
                ds_names=get_dsname(int(st.session_state['AuditID']))
                ds=st.selectbox("Select Data Set Name...",ds_names,key="sb2")
                #ds_name=ds[0]
                ds_name=f"{st.session_state['AuditID']}_{ds}"
                #st.write(ds_name)
                if ftype=='CSV':
                    header_row=st.number_input("Row Number of Colum Headers",min_value=1,value=1,key="headrerowcsv2")
                    footer_row=st.number_input("No of Rows to skip from Bottom",min_value=0,value=0,key="footerrowcsv2",help="for these rows from Bottom of Table, Data will be imported.")
                    uploaded_file = st.file_uploader("Upload a file",type='csv',key="uploadfile22")
                elif ftype=='XML':
                            uploaded_file = st.file_uploader("Upload a file",type='xml',key="uploadfilexmlcom3")
                elif ftype=='JSON':
                    uploaded_file = st.file_uploader("Upload a file",type='json',key="uploadfile23")
                elif ftype=='SQL':
                    uploaded_file="uploaded_file"

                elif ftype=='API':
                    uploaded_file="uploaded_file"
                    
                else:
                    header_row=st.number_input("Row Number of Colum Headers",min_value=1,value=1,key="headrerow2")
                    footer_row=st.number_input("No of Rows to skip from Bottom",min_value=0,value=0,key="footerrowxls2",help="for these rows from Bottom of Table, Data will be imported.")
                    uploaded_file = st.file_uploader("Upload a file",type='xlsx',key="uploadfile11")
                
                if uploaded_file is not None:
                    dataframe_new=None
                    if ftype=='CSV':
                        rb=st.radio("Select File Structure Type",options=("Simple","Nested"),key="rbxCSVl",
                                    help="Select Nested if Data has Parent & Chield records eg Sales Invoice & Stock Details for each ale Invoice",horizontal=True)       

                        if rb=="Simple":dataframe_new = pd.read_csv(uploaded_file,encoding= 'unicode_escape',skiprows=header_row-1,skipfooter=footer_row)
                        else:
                            dataframe_new = pd.read_csv(uploaded_file,encoding= 'unicode_escape',skiprows=header_row-1,skipfooter=footer_row)
                            dataframe_new=nested_csv(dataframe_new)
                    elif ftype=='JSON':
                        data = json.load(uploaded_file)
                        recordspath=st.text_input("Field containing Data",key="jsoncompare",placeholder="This is the Field Containing Data....Keep it Blank if Data preview is correct else,Type & press Tab / Enter",
                                                  help="Check the data shown in Table below, change the name & try")
                        #nestedcols=st.text_input("Enter Column names which are Nested- seperated by ,Comma",key="nestedcolumnams")
                        if recordspath:
                            dataframe_new=pd.json_normalize(data,record_path=recordspath)
                            
                        else: 
                            dataframe_new=pd.json_normalize(data)
                            
                        nestedcolslist=list(dataframe_new.columns)
                        nestedcols=st.multiselect("Select All Fields which are Nested",options=nestedcolslist,key="nestecolopcompare",
                                                    help="These are Chield fields ,consisting if List of records...These are shown in Round Grey background ")
                        
                        #st.write(nestedcols)
                        if nestedcols:
                            for col in nestedcols:
                                #st.write(col) 
                                dataframe_new[col] = dataframe_new[col].apply(lambda x: json.dumps(x))
                    
                    elif ftype=='XML':
                        fileformate=st.selectbox("Select encoding formate",("utf-16","utf-8"),key="utfsb")
                        #text_xml = xml.read()
                        tags=st.text_input("Enter Tags seperated by comma",key="tags")
                        tagslist=tags.split(",")
                        xml=uploaded_file.getvalue().decode(fileformate)
                        #st.write(xml)
                        xml=xml.strip().replace("&amp;","and")
                        xml=xml.replace("&#4","")
                        #st.write(xml)
                        #dfx = pdx.read_xml(xml, ['ENVELOPE','BODY','DATA','COLLECTION'])
                        if len(tagslist)>1:
                            dfx = pdx.read_xml(xml,tagslist)
                        else: dfx = pdx.read_xml(xml)
                        #print(dfx)
                        dfx = dfx.pipe(fully_flatten)
                        #print(dfx)
                        dataframe_new= pd.DataFrame(dfx)
                    
                    elif ftype=='SQL':
                        driver=st.selectbox("Select Database",("postgresql","mysql","mssql"),key="sbsql3")
                        user=st.text_input("Enter User Name*",key="sqluserc3")
                        password=st.text_input("Enter passord*",key="sqlpassc3")
                        password = urllib.parse.quote_plus(password)
                        hostname=st.text_input("Enter Host Name*",key="sqlhostc3")
                        port=st.text_input("Enter Port*",key="sqlportc3")
                        database=st.text_input("Enter Database Name*",key="sqldbnamec3")
                        sqltext=st.text_area("Enter SQL Query*",key="tasqlc3")
                        #sql="select * from users"
                        if driver=="postgresql": driver="postgresql+psycopg2"
                        if driver=="mssql": driver="mssql+pymssql"
                        if driver=="mysql": driver="mssql+pymysql"
                        #engine = create_engine('mysql://scott:tiger@localhost/test')
                        #engine = create_engine('postgresql://user:pass@localhost:5432/mydb')
                        engintext=f"{driver}://{user}:{password}@{hostname}:{port}/{database}"
                        #st.write(engintext)
                        if sqltext and user and password and hostname and port and database: 
                            engine=create_engine(engintext)
                            dataframe_new=pd.read_sql(sql=sqltext,con=engine)
                        else:
                            st.error("Enter All Required Fields")
                    
                    elif ftype=='API':
                        reqtype=st.selectbox("Request Type",("GET","POST"),key="getpost3com")
                        url = st.text_input("Enter URL*",key="stturl3",placeholder="without single or double quotes")
                        jLoad=None
                        payloadtype=st.radio("Is Payload Text or {Dictionary}",options=("{Dictionary}","Text"),key="pods3",horizontal=True)
                        payload = st.text_area("Enter Payload",key="apipayload3com",placeholder="text must be in { curly brackets}")
                        #payload=str(payload).strip("'<>() ").replace('\'', '\"')
                        if payload: 
                            if payloadtype=="{Dictionary}":
                                #jLoad=ast.literal_eval(str(jLoad))
                                j_obj=json.loads(payload)
                                st.success(j_obj)
                                jLoad = json.dumps(j_obj)
                                st.success(payload)
                                st.success(jLoad)
                            else :jLoad=payload

                        
                        header=None
                        headers = st.text_area("Enter Headers",key="apipayheader3com",placeholder="text must be in { curly brackets}")
                        if headers: header=ast.literal_eval(headers)
                        #if st.button("Get Data from API",key="apigetdata"):
                        if url:
                            
                            if reqtype=="GET" : 
                                
                                response = requests.request("GET", url, headers=header, data=jLoad)
                            else: 
                                response = requests.request("POST", url, headers=header, data=jLoad)
                            
                            data=response.json()
                            recordspath=st.text_input("Field Containing Data",key="jsonrecordpath23com",help="Check the data shown in Table below, change the name & try")
                            if recordspath: dataframe_new=pd.json_normalize(data,record_path=recordspath)
                            else: dataframe_new=pd.json_normalize(data)
                            nestedcolslist=list(dataframe_new.columns)
                            nestedcols=st.multiselect("Select All Fields which are Nested",options=nestedcolslist,key="nestecoloptios13",
                                                    help="These are Chield fields ,consisting if List of records...These are shown in Round Grey background ")
                                    
                                    #st.write(nestedcols)
                            if nestedcols:
                                for col in nestedcols:
                                    #st.write(col) 
                                    dataframe_new[col] = dataframe_new[col].apply(lambda x: json.dumps(x))

                    else: 
                        rb=st.radio("Select File Structure Type",options=("Simple","Nested"),key="rbxxls3",
                                    help="Select Nested if Data has Parent & Chield records eg Sales Invoice & Stock Details for each ale Invoice",horizontal=True)       

                        if rb=="Simple":dataframe_new = pd.read_excel(uploaded_file,skiprows=header_row-1,skipfooter=footer_row)
                        else:
                            dataframe_new = dataframe_new = pd.read_excel(uploaded_file,skiprows=header_row-1,skipfooter=footer_row)
                            dataframe_new=nested_csv(dataframe_new)
                    #get audited DF
                    
                    df=get_entire_dataset(ds_name)
                    #df.drop(columns=['Status','index','Sampled'],inplace=True)
                    df.drop(columns=['AutoAudit_Status','index','AutoAudit_Sampled'],inplace=True)
                    #df.sort_index(inplace=True)
                    st.success("Audited Dataset")
                    with st.expander("Expand",):
                        st.dataframe(df)
                    st.success("Current Version of Dataset")
                    if dataframe_new is not None:
                        with st.expander("Expand"):
                            st.dataframe(dataframe_new)
                    
                        #convert date or num colum headings to string
                        dataframe_new.columns = dataframe_new.columns.astype(str)
                        dfcol1=df.columns.tolist()
                        dfcol2=dataframe_new.columns.tolist()
                        #indexkey=df.columns[0]
                        #indexkey2=dataframe_new.columns[0]
                        
                        #st.info(dfcol1)
                        #st.info(dfcol2)
                        if dfcol1==dfcol2:                       
                            if st.button("Compare Data Set",key="b2"):
                                df_all = pd.concat([df, dataframe_new],axis='columns', keys=['Audited', 'Current'])
                                #df_all = pd.concat([df.set_index(indexkey), dataframe_new.set_index(indexkey)], 
                                        #axis='columns', keys=['Audited', 'Current'])
                                #st.dataframe(df_all)
                                df_final = df_all.swaplevel(axis='columns')[df.columns[0:]]
                                df_final.fillna('No Value',inplace=True)
                                #df_final=df_final.astype(str)
                                def highlight_diff(data, color='yellow'):
                                    attr = 'background-color: {}'.format(color)
                                    other = data.xs('Audited', axis='columns', level=-1)
                                    return pd.DataFrame(np.where(data.ne(other, level=0), attr, ''),index=data.index, columns=data.columns)
                                #st.write("Differences are Highlited with Yellow backgroud")
                                mes="Differences are Highlited with Yellow backgroud."
                                original_title = f'<p style="background-color:Yellow; ">{mes}</p>'
                                st.markdown(original_title, unsafe_allow_html=True)
                                st.dataframe(df_final.reset_index(drop=True).style.apply(highlight_diff, axis=None))
                                csv=df_final.to_csv().encode('utf-8')
                                st.download_button("Download csv file",csv,f"com_{ds_name}.csv")
                                del[[df_final,df_all,df,dataframe_new]]
                                df_final=pd.DataFrame()
                                df_all=pd.DataFrame()
                                df=pd.DataFrame()
                                dataframe_new=pd.DataFrame()
                                
                        else:
                            st.error("Mismatch in Colums of two Datasets...please upload Data set with same structure.")
                            del[[df,dataframe_new]]
                            df=pd.DataFrame()
                            dataframe_new=pd.DataFrame()               


def login(userName: str, password: str) -> bool:
        #this checks login & password is correct
    if (userName is None):
        return False
    else:
        if (password is None):
            return False
        else:
            if userName=="abc" and password=='abc':
                return True
            else:
                return False
 

#def show_main_page():
    #with mainSection:
        #st.write(f"User:-{st.session_state['username']}")
        
 
def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False
    loginuser=""
    
def show_logout_page():
    loginSection.empty()
    with logOutSection:
        st.sidebar.button ("Log Out", key="logout", on_click=LoggedOut_Clicked)
        


def Register_Clicked(displayname,userid ,password,designation):
    createuser=create_user(displayname,userid,password,designation)
    st.success(createuser)
    #show_login_page()
    


def show_auditee():
    st.warning("You Have Logged In as Auditee...You have no access to this Menu")



with headerSection:
    #if 'url' not in st.session_state:
        #st.session_state['url'] = ""
        
    if 'User' not in st.session_state:
        st.session_state['User'] = ""
    
    if 'Company' not in st.session_state:
        st.session_state['Company'] = ""
    
    if 'Role' not in st.session_state:
        st.session_state['Role'] = ""
    
    if 'Audit' not in st.session_state:
        st.session_state['Audit'] = ""
    
    if 'AuditID' not in st.session_state:
        st.session_state['AuditID'] = ""
    
    if 'loggedIn' not in st.session_state:
        st.session_state['loggedIn'] = False
        show_login_page()
        #st.title("Login")
    else:
        if st.session_state['loggedIn']:
            show_logout_page() 
            #if audit is closed dont show this
            auditstatus=check_audit_status()
            if auditstatus=="Open":
                if st.session_state['Role'] == "Auditee":
                        show_auditee()
                else:
                        show_masters() 
            else: st.error("Audit is Closed. you can not Access this Menu...")    
            
        else:
            #st.title("Login")
            show_login_page()

    
    