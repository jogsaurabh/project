#from logging import PlaceHolder
from dataclasses import field
from queue import Empty
import streamlit as st
import pandas as pd
import numpy as np
import json
#from main import show_login_page,LoggedOut_Clicked
from st_aggrid import AgGrid,DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, grid_options_builder
#from formatter import NullFormatter

from functions import import_defalut_checklist,update_verification_criteria,update_risk_weights,get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit
from functions import get_risk_weights_ds_vouching,create_user,check_login,assign_user_rights,create_company,get_company_names,get_risk_weights_ds
from functions import modify_audit_cheklist,add_audit_cheklist,del_checklist,get_audit_checklist,create_dataset,add_verification_criteria,get_dsname,get_entire_dataset,get_auditee_comp
import sqlite3
from PIL import Image
image = Image.open('autoaudit_t.png')
st.set_page_config(page_title="AutoAudit", page_icon=":white_check_mark:", layout="wide")
#st.title(":white_check_mark: AutoAudit")
st.image(image,width=250)
st.markdown("""---""")
masters=st.container()
#from st_aggrid import AgGrid
headerSection = st.container()
#masterSection = st.container()
loginSection = st.container()
logOutSection = st.container()

def show_masters():
    comp_name=st.session_state['Company']
    with masters:
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        
        st.title("Masters")
        with st.sidebar.markdown("# Masters "):
            master_options = st.radio(
            'Masters- Dataset',
            ('Add New Data Set', 'Add Records to Data Set','Set Check List','Verification Check List','Set Risk Weights for Data Set','Compare with Audited Dataset'))            
        if master_options=='Add New Data Set':
            
            st.header("Add New Data Set")
            ftype=st.radio("Select File Type",options=['CSV','XLSX','JSON'])
            if ftype=='CSV':
                st.success(f"1) Check that - First Row contains column Headings..\n2) File is of - .csv type\n3) No column should have name - index")
            elif ftype=='JSON':
                st.success('Check the Result before Importing DataSet')
                
            else:
                st.success(f"1) Check that - First Row contains column Headings..\n2) File is of - .xlsx type\n3) File contains only 1 sheet\n4) No column should have name - index")
            
            #st.success(f"1) Check that - First Row contains column Headings..\n2) File is of - .xlsx type\n3) File contains only 1 sheet")
            #with st.form("New Dataset",clear_on_submit=True):
            #st.warning("Check ...First Column is Primary Key / Unique")
            auditee=get_auditee_comp()
            if auditee.empty:
                st.info(f"No Auditee assigned to Current Company...\n Assign Atleast 1 user with Auditee Role")
                
            else:
                table_name=st.text_input("Enter Name of Data Set",key="tablename1")
                person_responsible=st.selectbox("Select Auditee, who will answer Queries",auditee,key="sbperson_responsible")
                if ftype=='CSV':
                    uploaded_file = st.file_uploader("Upload a file",type='csv',key="uploadfile2")
                elif ftype=='JSON':
                    uploaded_file = st.file_uploader("Upload a file",type='json',key="uploadfile3")
                else:
                    uploaded_file = st.file_uploader("Upload a file",type='xlsx',key="uploadfile1")
                if uploaded_file is not None:
                        #st.write(uploaded_file.name)
                        filename=uploaded_file.name
                        if ftype=='CSV':
                            dataframe = pd.read_csv(uploaded_file,encoding= 'unicode_escape')
                            for y in dataframe.columns:
                                #check if  column is Boolion type
                                if(pd.api.types.is_bool_dtype(dataframe[y])):
                                    #convert to string
                                    dataframe[y] = dataframe[y].map({True: 'True', False: 'False'})
                                    #st.write(y)
                        elif ftype=='JSON':
                            data = json.load(uploaded_file)
                            dataframe=pd.json_normalize(data)
                            for y in dataframe.columns:
                                #check if  column is Boolion type
                                if(pd.api.types.is_bool_dtype(dataframe[y])):
                                    #convert to string
                                    dataframe[y] = dataframe[y].map({True: 'True', False: 'False'})
                                    #st.write(y)
                        else:                            
                            dataframe = pd.read_excel(uploaded_file)
                            
                            for y in dataframe.columns:
                                #st.write(y)
                                #check if  column is Boolion type
                                if(pd.api.types.is_bool_dtype(dataframe[y])):
                                    #convert to string
                                    
                                    dataframe[y] = dataframe[y].map({True: 'True', False: 'False'})
                                    #st.write(y)
                            
                        st.dataframe(dataframe)
                        #st.table(dataframe.info())
                        #check if colum name=index or Index
                        if 'Index' in dataframe.columns or 'index' in dataframe.columns:
                            st.info(f'Column name with "Index" or "index" not allowed...Please change colum Name')
                        else:
                            if st.button("Create Data Set",key="b1"):
                                if table_name:
                                    message=create_dataset(dataframe,table_name,comp_name,person_responsible)
                                    st.success(message) 
                                    #masters.empty()       
                                else:
                                    st.info("Please enter Data Set Name")
                                    #masters.empty()
                        #del & clear DataFrame
                        del [[dataframe]]
                        dataframe=pd.DataFrame()   
        elif master_options=='Add Records to Data Set':
                st.header("Add data to Existing Data Set")
                ftype=st.radio("Select File Type",options=['CSV','XLSX','JSON'])
                
                st.info("Check that all colums are Exactly same as per Existing Data Set, before uploading.")
                #get list of ds_name for current company
                ds_names=get_dsname(int(st.session_state['AuditID']))
                if ds_names.empty:
                    st.info(f"No Data Sets for Current Company...\n First Add Data Set in current Company.")
                else:
                    col1, col2 =st.columns(2)
                    with col1:
                        st.success("Select Data Set to add Records...")
                        ds_name=st.selectbox("Select Data Set Name...",ds_names,key="sb0")
                        st.write("Current Data Set")
                        dsname=f"{comp_name}_{st.session_state['AuditID']}_{ds_name}"
                        df=get_entire_dataset(dsname)
                        df.drop(columns=['Status','Sampled'],inplace=True)
                        st.dataframe(df)
                    with col2:
                        st.success("Check Data to Add to Current Data Set")
                        if ftype=='CSV':
                            uploaded_file = st.file_uploader("Upload a file",type='csv',key="uploadfile22")
                        elif ftype=='JSON':
                            uploaded_file = st.file_uploader("Upload a file",type='JSON',key="uploadfile23")
                        else:
                            uploaded_file = st.file_uploader("Upload a file",type='xlsx',key="uploadfile11")
                
                        #uploaded_file = st.file_uploader("Upload a file",type='xlsx',key="1uploadfile1")
                        
                    
                        if uploaded_file is not None:
                                #st.write("Data to Add ")
                                #filename=uploaded_file.name
                                #dataframe = pd.read_excel(uploaded_file,)
                                if ftype=='CSV':
                                    dataframe = pd.read_csv(uploaded_file,encoding= 'unicode_escape')
                                    for y in dataframe.columns:
                                #check if  column is Boolion type
                                        if(pd.api.types.is_bool_dtype(dataframe[y])):
                                            #convert to string
                                            dataframe[y] = dataframe[y].map({True: 'True', False: 'False'})
                                            #st.write(y)
                                elif ftype=='JSON':
                                    data = json.load(uploaded_file)
                                    dataframe=pd.json_normalize(data)
                                    for y in dataframe.columns:
                                        #check if  column is Boolion type
                                        if(pd.api.types.is_bool_dtype(dataframe[y])):
                                            #convert to string
                                            dataframe[y] = dataframe[y].map({True: 'True', False: 'False'})
                                    
                                else:                            
                                    dataframe = pd.read_excel(uploaded_file)
                                    for y in dataframe.columns:
                                #check if  column is Boolion type
                                        if(pd.api.types.is_bool_dtype(dataframe[y])):
                                            #convert to string
                                            dataframe[y] = dataframe[y].map({True: 'True', False: 'False'})
                                            #st.write(y)
                                dfmax=df['index'].max()
                                dataframe.insert(0,"index",range(dfmax+1, dfmax+1 + len(dataframe)))
                                st.dataframe(dataframe)
                                dfcol1=df.columns.tolist()
                                dfcol2=dataframe.columns.tolist()
                                if dfcol1==dfcol2: 
                                    if st.button("Append to Data Set",key="b11"):
                                        message=add_datato_ds(dataframe,ds_name,comp_name)
                                        st.success(message)
                                else:
                                    st.warning("Mismatch in Colums of two Datasets...please upload Data set with same structure.")
                                #del & clear DataFrame
                                del [[dataframe,df]]
                                dataframe=pd.DataFrame()
                                df=pd.DataFrame()  
                
        elif master_options=='Verification Check List':
                st.header("Add Verification Check List")

                st.success("Select Data Set Name")
                ds_names=get_dsname(int(st.session_state['AuditID']))
                ds_name=st.selectbox("",ds_names,key="sb1")
                    #if st.button("View Current check list",key="cc1"):
                        #veri_df=get_verification(ds_name,int(st.session_state['AuditID']))
                        #st.dataframe(veri_df)
                    #Chek_List=pd.DataFrame()
                with st.form("Verification Criteria",clear_on_submit=True):
                        c1,c2 =st.columns(2)
                        with c1:
                            Crtiteria=st.text_area("Enter Verification Criteria")
                        with c2:
                            risk_weight=st.slider("Set Risk Weights",min_value=1,max_value=10,key='slider2')
                            
                            if risk_weight >=1 and risk_weight <=3:
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
                                
                            else:
                                st.write('Criteria can not be blank.')
                        
                with st.expander("View Verification Criteria"):
                        st.header("Verification Criteria")
                        veri_df=get_verification(ds_name,int(st.session_state['AuditID']))
                        st.dataframe(veri_df)
                            
        elif master_options=='Set Check List':
            st.header("Set Check List")
            auditid=int(st.session_state['AuditID'])
            crud=st.radio("",('View','Add New','Modify','Delete'),horizontal=True,key='strcrudas')
            df=get_audit_checklist(auditid)
            builder = GridOptionsBuilder.from_dataframe(df)
            builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=15)
            builder.configure_selection(selection_mode="single",use_checkbox=True)
                        #builder.configure_default_column(editable=True)
            go = builder.build()
                        #uses the gridOptions dictionary to configure AgGrid behavior.
            grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                        #selelcted row to show in audit AGGrid
            selected = grid_response['selected_rows']
                #st.data
            if crud=='Add New':
                st.success('Enter details to Add New Record')
                auditee=get_auditee_comp()
                if auditee.empty:
                    st.info(f"No Auditee assigned to Current Company...\n Assign Atleast 1 user with Auditee Role")
                else:
                    
                    add_options= st.radio("",('Import Default Check List', 'Add Check List'),horizontal=True,key='op1')
                    if add_options=='Import Default Check List':
                        #imp=st.button('View Default Check List',key='defchkli')
                        person_responsible=st.selectbox("Select Defalut Person Responsible...You can Modify Later.",auditee,key="sbperson_responsibleck1i")
                        impbt=st.button("Import",key='impchklist')
                        if impbt:
                                df=pd.read_excel('checklist.xlsx')
                                
                                df['Person_Responsible']=person_responsible
                                df['Audit_id']=auditid
                                res=import_defalut_checklist(df)
                                st.success(res)
                                
                                
                            
                            
                    else:
                        #addc=st.button('Add Check List',key='defchkli')
                        #if addc:
                            with st.form("Add Checklist",clear_on_submit=True):
                                criteria=st.text_area("Enter Criteria / Checklist",key='criteriac')
                                Audit_area=st.text_input("Enter Audit Area",key='Aarea')
                                heading=st.text_input("Enter Heading / Group",key='Heading')
                                risk_weight=st.slider("Set Risk Weights",min_value=1,max_value=10,key='slider2rw')
                                person_responsible=st.selectbox("Select Person Responsible",auditee,key="sbperson_responsibleck")
            
                                if risk_weight >=1 and risk_weight <=3:
                                    risk_category='Low'
                                elif risk_weight >=4 and risk_weight <=7:
                                    risk_category='Medium'
                                else:
                                    risk_category='High'
                                submitted_chk = st.form_submit_button("Submit")
                                                               
                                if submitted_chk:
                                    
                                    if criteria  and Audit_area :
                                        addchk=add_audit_cheklist(criteria,Audit_area,heading,risk_weight,
                                                                  risk_category,person_responsible,auditid)
                                    else:
                                        st.info("Criteria & Audit Area are Mandatory fields")
                            

            elif crud=='Modify':
                auditee=get_auditee_comp()
                if auditee.empty:
                    st.info(f"No Auditee assigned to Current Company...\n Assign Atleast 1 user with Auditee Role")
                else:
                    if selected:
                            st.success('Enter details to Modify Selected Record')
                            with st.form("Mdify Checklist Doc",clear_on_submit=True):
                                mcriteria=st.text_area("Update Criteria",key='mcriteria',value=selected[0]['Criteria'])
                                mauditarea=st.text_input("Update Audit Area",key='mauditarea',value=selected[0]['Audit_Area'])
                                mheading=st.text_input("Update Heading / Group",key='mheading',value=selected[0]['Heading'])
                                mrisk_weight=st.slider("Update Risk Weights",min_value=1,max_value=10,key='slider2rwm')
                                mperson_responsible=st.selectbox("Update Person Responsible",auditee,key="sbperson_responsibleckm")
                
                                if mrisk_weight >=1 and mrisk_weight <=3:
                                        mrisk_levl='Low'
                                elif mrisk_weight >=4 and mrisk_weight <=7:
                                        mrisk_levl='Medium'
                                else:
                                        mrisk_levl='High'
                                    
                                roid=selected[0]['id']
                                
                                
                                submitted_chk_mod =st.form_submit_button("Submit")
                                if submitted_chk_mod:
                                    if mcriteria  and mauditarea :
                                        addchk=modify_audit_cheklist(roid,mcriteria,mrisk_weight,mrisk_levl,mauditarea,
                                                                     mheading,mperson_responsible)
                                    else:
                                        st.info("Criteria & Audit Area are Mandatory fields")
                            
                    else:
                            st.info('Select a Record to Modify ....')
                        
                    
            elif crud=='View':
                st.success('')
            else:
                if selected:
                        st.success('Are you sure you want to Delete Selected Record')
                        if st.button("Delete Selected Record",key='delcompdocack'):
                            rid=selected[0]['id']
                            rdel=del_checklist(rid)
                else:
                        st.info('Select a Record to Delete ....')

                       
                                                   
        elif master_options=='Set Risk Weights for Data Set':
            st.header("Update Risk Weights for each Field")
                #st.dataframe(Chek_List,width=1000)
            ds_names=get_dsname(int(st.session_state['AuditID']))
            st.success('Select Data Set Name...')
            ds=st.selectbox("",ds_names,key="sbrisk1")
            #fields=get_fields_names(f"{comp_name}_{st.session_state['AuditID']}_{ds}")
            #remove wher field is null
            
            criteria=get_risk_weights_ds_vouching(ds)
            criteria=criteria[['Criteria']]
            with st.form("Risk",clear_on_submit=True):
                    c1,c2 =st.columns(2)
                    with c1:
                        criteria_selected=st.selectbox("Select Criteria",key="sf1",options=criteria)
                    with c2:
                        risk_weight=st.slider("Set Risk Weights",min_value=1,max_value=10,key='slider2')
                        
                        if risk_weight >=1 and risk_weight <=3:
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
                            st.info('Criteria can not be blank.')
            
            #st.write(field)
            with st.expander("View Risk Weights"):
                    st.header("Risk Weights")
                    riskdf=get_risk_weights_ds_vouching(ds)
                    #veri_df=get_verification(ds_name,int(st.session_state['AuditID']))
                    st.dataframe(riskdf)
        else:
                st.header("Compare Audited Dataset with Current Version of Dataset")
                st.success("1)Upload Current Version of Dataset...\n2)Check...Data Structure is Excatly same, with same colum names")
                #st.info("Check ...Data Structure is Excatly same, with same colum names")
                ftype=st.radio("Select File Type",options=['CSV','XLSX','JSON'])
                
                ds_names=get_dsname(int(st.session_state['AuditID']))
                ds=st.selectbox("Select Data Set Name...",ds_names,key="sb2")
                #ds_name=ds[0]
                ds_name=f"{comp_name}_{st.session_state['AuditID']}_{ds}"
                #st.write(ds_name)
                if ftype=='CSV':
                    uploaded_file = st.file_uploader("Upload a file",type='csv',key="uploadfile22")
                elif ftype=='JSON':
                    uploaded_file = st.file_uploader("Upload a file",type='json',key="uploadfile23")
                else:
                    uploaded_file = st.file_uploader("Upload a file",type='xlsx',key="uploadfile11")
                
                #uploaded_file = st.file_uploader("Upload a xlsx file",type='xlsx',key="uploadfile2")

                if uploaded_file is not None:
                    #st.write(uploaded_file.name)
                    #filename=uploaded_file.name
                    if ftype=='CSV':
                        dataframe_new = pd.read_csv(uploaded_file,encoding= 'unicode_escape')
                    elif ftype=='JSON':
                        data = json.load(uploaded_file)
                        dataframe_new=pd.json_normalize(data)
                    else:                            
                        dataframe_new = pd.read_excel(uploaded_file)
                    #dataframe_new = pd.read_excel(uploaded_file)
                    #dataframe_new=dataframe_new.index.name = 'id'
                    #get audited DF
                    df=get_entire_dataset(ds_name)
                    #df.drop(columns=['Status','index','Sampled'],inplace=True)
                    df.drop(columns=['Status','index','Sampled'],inplace=True)
                    #df.sort_index(inplace=True)
                    st.success("Audited Dataset")
                    with st.expander(""):
                        st.dataframe(df)
                    st.success("Current Version of Dataset")
                    with st.expander(""):
                        st.dataframe(dataframe_new)
                    dfcol1=df.columns.tolist()
                    dfcol2=dataframe_new.columns.tolist()
                    #indexkey=df.columns[0]
                    #indexkey2=dataframe_new.columns[0]
                    if dfcol1==dfcol2:                       
                        if st.button("Compare Data Set",key="b2"):
                            df_all = pd.concat([df, dataframe_new],axis='columns', keys=['Audited', 'Current'])
                            #df_all = pd.concat([df.set_index(indexkey), dataframe_new.set_index(indexkey)], 
                                    #axis='columns', keys=['Audited', 'Current'])
                            #st.dataframe(df_all)
                            df_final = df_all.swaplevel(axis='columns')[df.columns[0:]]
                            df_final.fillna('No Value',inplace=True)
                            df_final=df_final.astype(str)
                            def highlight_diff(data, color='yellow'):
                                attr = 'background-color: {}'.format(color)
                                other = data.xs('Audited', axis='columns', level=-1)
                                return pd.DataFrame(np.where(data.ne(other, level=0), attr, ''),index=data.index, columns=data.columns)
                                
                            st.dataframe(df_final.reset_index(drop=True).style.apply(highlight_diff, axis=None))
                            csv=df_final.to_csv().encode('utf-8')
                            st.download_button("Download csv file",csv,f"com_{ds_name}.csv")
                    else:
                        st.warning("Mismatch in Colums of two Datasets...please upload Data set with same structure.")
                                            


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


def Register_Clicked(userid, password,designation,displayname):
    createuser=create_user(displayname,userid,password,designation)
    st.info(createuser)
    #show_login_page()
    

    
def show_login_page():
    with loginSection:
        tab1,tab2 =st.tabs(["   Existing Users  ","   New Users   "])
        with tab1:
            
            if st.session_state['loggedIn'] == False:
                #st.session_state['username'] = ''
                st.title("Login") 
                userName = st.text_input (label="", value="", placeholder="Enter your user name",key="k1")
                password = st.text_input (label="", value="",placeholder="Enter password", type="password",key="k2")
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
                
                st.title("Register")
                userid = st.text_input (label="", value="", placeholder="Enter your user ID",key="k5")
                password = st.text_input (label="", value="",placeholder="Set password", type="password",key="k6")
                designation = st.text_input (label="", value="", placeholder="Enter your Designation",key="k3")
                displayname = st.text_input (label="", value="", placeholder="Enter your Display Name",key="k4")
                st.form_submit_button("Submit",on_click=Register_Clicked, args= (userid, password,designation,displayname))
                #st.button ("Register", on_click=Register_Clicked, args= (userid, password,designation,displayname))

def show_auditee():
    st.warning("You Have Logged In as Auditee...You have no access to this Menu")



with headerSection:
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
            if st.session_state['Role'] == "Auditee":
                    show_auditee()
            else:
                    show_masters()     
            
        else:
            #st.title("Login")
            show_login_page()

    
    