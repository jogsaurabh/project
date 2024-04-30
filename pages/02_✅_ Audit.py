#from cgitb import enable
#from distutils.command.build import build
#from sys import audit
#from turtle import onclick
import os
from functions import check_audit_status
from queue import Empty
import numpy as np
import pygwalker as pyg
from pygwalker.api.streamlit import StreamlitRenderer

from jinja2 import Environment, FileSystemLoader
#from email.policy import default
#from operator import index
#from sys import audit
#from tkinter import HORIZONTAL
#from matplotlib.cbook import report_memory
import streamlit as st
#from streamlit import caching
from datetime import datetime
from docx import Document
from htmldocx import HtmlToDocx
from functions import get_obs_related_vv,update_password,get_ar_queries,modify_audit_summ,add_audit_summ,get_Audit_summ,get_audit_observations,del_audit_doc,modif_comp_doc,get_company_docs,get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit,add_audit_verification
from functions import get_obs_related_ar,closed_audit,create_user,check_login,get_dsname_personresponsible,assign_user_rights,create_company,get_company_names,get_pending_queries
from functions import del_comp_doc,add_comp_doc,create_dataset,add_verification_criteria,get_dsname,get_entire_dataset,get_auditee_comp
from functions import get_obs_related_ar_summary,get_obs_related_vv_summary,get_pending_Compliance,del_audit_sum,modify_audit_observation,modif_audit_doc,add_audit_doc,get_audit_docs,get_dataset,add_analytical_review,insert_vouching,update_audit_status,get_ar_for_ds,add_query_reply
import pandas as pd
from functions import del_task,get_overdue_tasks,get_user_foraudit_task,add_task,get_all_tasks,update_task,get_tasks_byuser

from PIL import Image
image = Image.open('autoaudit_t.png')
from st_aggrid import AgGrid,DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, grid_options_builder,ColumnsAutoSizeMode
#from pandas_profiling import ProfileReport
#import pandas_profiling
#from streamlit_pandas_profiling import st_profile_report
import sqlite3
url="https://acecom22-my.sharepoint.com/:w:/g/personal/saurabhjog_acecomskills_in/ESLKUvAGIMJJontdPiuXk5YBTxjbcYnCkilrcBJ3oHy0ww?e=ZS4i6g"
st.set_page_config(page_title="AutoAudit", page_icon=":white_check_mark:", layout="wide")

headercol1,headercol2,co3=st.columns([8,2,1])
with headercol1 : st.image(image,width=200,)
with co3: 
    link =f'[Help]({url})'
    st.markdown(link, unsafe_allow_html=True)
    #st.markdown(f'''<a href={url}><button style="padding: 5px 8px; border-radius: 5px; border: 1px solid red;">Help</button></a>''',
    #            unsafe_allow_html=True)
st.markdown("""---""")

audit_container=st.container()
updatecontainer=st.container()
cont_observation=st.container()
cont_oaudit_summary=st.container()
con_show_audit=st.container()
#st.write(f"User:-{st.session_state['username']}")
#comp_name=st.session_state['Company']
@st.cache_resource
def gen_walk(df):

      #pyg.walk(df, env='Streamlit', dark='light')
    #df = pd.read_csv("./bike_sharing_dc.csv")
    # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
    return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")

def show_Audit_observations():
    with cont_observation:
        st.info("**Observations for Audit Check List**")
        crud=st.radio("1",('Show Observations','Update Audit Observations'),horizontal=True,key='strcrudas',label_visibility="hidden")
        auditid=int(st.session_state['AuditID'])
        df=get_audit_observations(auditid)
        df.sort_values(by=['Audit_Area','Heading'],inplace=True)
        if crud=='Update Audit Observations':
            #st.success('Update Audit Observations...')
            #auditid=int(st.session_state['AuditID'])
            #df=get_audit_observations(auditid)
            builder = GridOptionsBuilder.from_dataframe(df)
            builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
            builder.configure_selection(selection_mode="single",use_checkbox=True)
                            #builder.configure_default_column(editable=True)
            #builder.configure_default_column(groupable=True)
            go = builder.build()
                            #uses the gridOptions dictionary to configure AgGrid behavior.
            grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                            #selelcted row to show in audit AGGrid
            selected = grid_response['selected_rows']
            #csv=df.to_csv().encode('utf-8')
            #st.download_button("Download CSV file",csv,f"Audit_Obs.csv")
            if selected:
                st.success(f"""Criteria:- \n{selected['Criteria'].iloc[0]}""")
                
                filename=selected['Annexure'].iloc[0]
                rev_filename=f"{auditid}_{filename}"
                                    
                if filename:
                                        
                    with open(os.path.join("obsev_docs",rev_filename), 'rb') as f:
                        st.download_button('Download Attachment', f, file_name=filename,key="reveiewdld")    
                with st.expander('See Related Queries of Vouching & Verification'):
                    st.success('Vouching & Verification Queries...TO REFRESH - Close & Expande This Expander')
                    col1,col2 = st.columns(2)
                    
                    with col2:
                        st.subheader('Related Queries')
                        vvqueries=get_obs_related_vv(selected['id'].iloc[0])
                        vvqueries.sort_values("DataSetName",inplace=True)
                        builder = GridOptionsBuilder.from_dataframe(vvqueries)
                        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                        go = builder.build()
                        AgGrid(vvqueries, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),key="Query1",columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
            
                        #st.dataframe(vvqueries)
                    with col1:
                        st.subheader('Summary')
                        vvsummary=get_obs_related_vv_summary(selected['id'].iloc[0])
                        #st.dataframe(vvsummary)
                        builder = GridOptionsBuilder.from_dataframe(vvsummary)
                        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                        go = builder.build()
                        AgGrid(vvsummary, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),key="sum1",columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
            
                with st.expander('See Related Analytical Review & Other Remarks'):
                    st.success('Analytical Review & Other Remarks...TO REFRESH - Close & Expande This Expander')
                    col1,col2 = st.columns(2)
                    
                    with col2:
                        st.subheader('Queries')
                        vvqueries=get_obs_related_ar(selected['id'].iloc[0])
                        vvqueries.sort_values("DataSetName",inplace=True)
                        #st.dataframe(vvqueries)
                        builder = GridOptionsBuilder.from_dataframe(vvqueries)
                        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                        go = builder.build()
                        AgGrid(vvqueries, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),key="query2",columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
            
                    with col1:
                        st.subheader('Summary')
                        vvsummary=get_obs_related_ar_summary(selected['id'].iloc[0])
                        #st.dataframe(vvsummary)
                        builder = GridOptionsBuilder.from_dataframe(vvsummary)
                        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                        go = builder.build()
                        AgGrid(vvsummary, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),key="sum2",columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
            
                        
                st.markdown("""---""")    
                if selected['Compliance_Status'].iloc[0]=="Open":
                    with st.expander("Update Observations..."): 
                        with st.form("Modify Observation Doc",clear_on_submit=True):
                            cond=""
                            if selected['Condition'].iloc[0]!=None: cond = selected['Condition'].iloc[0]
                            Condition=st.text_area("Update Condition",key='condition',value=cond)
                            cause_v=""
                            if selected['Cause'].iloc[0]!=None: cause_v = selected['Cause'].iloc[0]
                            Cause=st.text_area("Update Cause",key='Cause',value=cause_v)
                            effect_v=""
                            if selected['Effect'].iloc[0]!=None: effect_v = selected['Effect'].iloc[0]
                            Effect=st.text_area("Update Effect",key='Effect',value=effect_v)
                            conclusion_v=""
                            if selected['Conclusion'].iloc[0]!=None: conclusion_v = selected['Conclusion'].iloc[0]
                            Conclusion=st.text_area("Update Conclusion",key='Conclusion1',value=conclusion_v)
                            impact_v=""
                            if selected['Impact'].iloc[0]!=None: impact_v = selected['Impact'].iloc[0]
                            Impact=st.text_area("Update Impact",key='Impact',value=impact_v)
                            reconmendation_v=""
                            if selected['Recomendation'].iloc[0]!=None: reconmendation_v = selected['Recomendation'].iloc[0]
                            Recomendation=st.text_area("Update Recomendation",key='Recomendation',value=reconmendation_v)
                            cor_act_pln_v=""
                            if selected['Corrective_Action_Plan'].iloc[0]!=None: cor_act_pln_v = selected['Corrective_Action_Plan'].iloc[0]
                            Corrective_Action_Plan=st.text_area("Update Corrective_Action_Plan",key='Corrective_Action_Plan',value=cor_act_pln_v)
                            Is_Adverse_Remark=st.selectbox("Update Is_Adverse_Remark",key='isactive',options=("Yes","No"))
                            #Is_Adverse_Remark=st.text_input("Update Is_Adverse_Remark",key='Is_Adverse_Remark',value=selected[0]['Is_Adverse_Remark'])
                            if selected['DeadLine'].iloc[0]!=None:
                                DeadLine=st.date_input('Update DeadLine',key='DeadLine',value=datetime.strptime(selected['DeadLine'].iloc[0], '%Y-%m-%d').date())
                            else: DeadLine=st.date_input('Update DeadLine',key='DeadLinee') 
                            Annexure=st.file_uploader("Upload File",type=['pdf','xlsx','docx'],key='Annexure')
                            file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilname')
                            
                                            
                            roid=selected['id'].iloc[0]
                                            
                                            
                            submitted_Obsr_mod =st.form_submit_button("Submit")
                            if submitted_Obsr_mod:
                                if Is_Adverse_Remark=="Yes" or Is_Adverse_Remark=="No":
                                    
                                    if Annexure is not None:
                                                            #st.write(f'again-{file_name}')
                                        if file_name:
                                            if Annexure.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                                extn="docx"
                                            elif Annexure.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                                extn='xlsx'
                                            else :
                                                extn='pdf'
                                                                #if st.button("Upload file",key='uf1'):
                                            comp_filename=f"{auditid}_{file_name}.{extn}"
                                            file_name=f"{file_name}.{extn}"
                                            with open(os.path.join("obsev_docs",comp_filename),"wb") as f: 
                                                f.write(Annexure.getbuffer())
                                                                
                                            updatobr=modify_audit_observation(roid,Condition,Cause,Effect,Conclusion,Impact,Recomendation,Corrective_Action_Plan,Is_Adverse_Remark,DeadLine,file_name)                                        
                                        else:
                                            st.success("Enter File Name")    
                                    else:
                                                        #st.write(f'befor-{file_name}')
                                        file_name=None
                                                        #st.write(f'then-{file_name}')
                                                            #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                        updatobr=modify_audit_observation(roid,Condition,Cause,Effect,Conclusion,Impact,Recomendation,Corrective_Action_Plan,Is_Adverse_Remark,DeadLine,file_name)                                        
                                                
                                else: 
                                    st.success('Is_Adverse_Remark can either be Yes or No') 
                else:
                    st.success("Can Not Modify....Audit Observation is CLOSED")     
            else:
                st.success('Select a Record to Update ....')
        else:
            #show summary
            #table = pd.pivot_table(df, values='Risk_Weight', index=['Audit_Area', 'Heading','Criteria'],
                     #aggfunc=np.sum) 
            #table=df.groupby(['Audit_Area', 'Heading','Criteria','Condition','Cause','Effect'])['Risk_Weight'].sum()  
            #table.drop_duplicates("Audit_Area",keep='first',inplace=True)  
            #st.dataframe(table)            
            builder = GridOptionsBuilder.from_dataframe(df)
            builder.configure_default_column(groupable=True)
            #builder.configure_columns(column_names=['Audit_Area', 'Heading','Criteria'])
            builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
            builder.configure_selection(selection_mode="single",use_checkbox=True)
                            #builder.configure_default_column(editable=True)
            #builder.configure_columns(['Audit_Area'],columnDefs={'field': 'Audit_Area', 'rowGroup': 'true', 'hide': 'true' })
            #gridOptionsset = {'columnDefs': {'field': 'Audit_Area', 'rowGroup': 'true', 'hide': 'true' }}
            #builder.configure_grid_options(gridOptionsset)
            go = builder.build()
                            #uses the gridOptions dictionary to configure AgGrid behavior.
            
            grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),key="sum3",columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
            selected = grid_response['selected_rows']
                        #download file option
            if selected:
                            filename=selected['Annexure'].iloc[0]
                            com_filename=f"{(st.session_state['AuditID'])}_{filename}"
                            #com_filename=f"{st.session_state['Company']}_{filename}"
                                   
                            if filename:
                                        
                                with open(os.path.join("obsev_docs",com_filename), 'rb') as f:
                                    st.download_button('Download Attachment', f, file_name=filename,key="dlcompfile")    
                    
            st.success(f"""Use Options to Group Report by Mutiple Levels. 
                       Right Click to Export Report to Excel""")
        del[df]
        df=pd.DataFrame()
        
def show_planning():
    with  con_show_audit:
        st.info('**Audit Planning & Task Management**')
        crud=st.radio("1",('View','Add New','Modify','Delete'),horizontal=True,key='strcrudpl',label_visibility="hidden")
        auditid=int(st.session_state['AuditID'])
        df=get_all_tasks(auditid)
        builder = GridOptionsBuilder.from_dataframe(df)
        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
        builder.configure_selection(selection_mode="single",use_checkbox=True)
                        #builder.configure_default_column(editable=True)
        go = builder.build()
                        #uses the gridOptions dictionary to configure AgGrid behavior.
        grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                        #selelcted row to show in audit AGGrid
        selected = grid_response['selected_rows']
        users=get_user_foraudit_task(st.session_state['Company'])    
        if crud=='Add New':
                    st.success("Enter details to Add New Record.")
                    
                    with st.form("tasks",clear_on_submit=True):
                        task=st.text_input("Enter Task*",key="taskti")
                        details=st.text_area("Enter Task Details",key="taskdti")
                        person=st.selectbox("Select Person Responsible",options=users,key="seusers")
                        duedate=st.date_input("Select Due Date for Task",key="duetask")
                        submitted = st.form_submit_button("Submit")
                        if submitted:
                            if task:
                                addtask=add_task(task,details,duedate,person,auditid)
                                st.success(addtask)
                            else:
                                st.error("Task can not be Blank")

        elif crud=='Modify':
                           
            if selected:
                if st.session_state['Role']=="Manager" or st.session_state['User']==selected['created_by'].iloc[0]:
                    
                    st.success("Enter details to Modify Selected Record...")
                    with st.form("tasksupdateta",clear_on_submit=True):
                        roid=selected['id'].iloc[0]
                        task=st.text_input("Update Task*",key="tasktiu",value=selected['Task'].iloc[0])
                        details=st.text_area("Update Task Details",key="taskdtiu",value=selected['Details'].iloc[0])
                        person=st.selectbox("Update Person Responsible",options=users,key="seusersu")
                        if selected['Due_Date'].iloc[0]!=None:
                            duedate=st.date_input('Update Due_Date',key='Due_Date',value=datetime.strptime(selected['Due_Date'].iloc[0], '%Y-%m-%d').date())
                        else: duedate=st.date_input('Update DeadLine',key='Due_Datee') 
                        #duedate=st.date_input("Update Due Date for Task",key="duetasku")
                        staus=st.selectbox("Update Status",options=("Pending","Completed"),key="seusersu1")
                        submitted = st.form_submit_button("Submit")
                        if submitted:
                            if task:
                                updatet=update_task(task,details,duedate,person,staus,roid)
                                st.success(updatet)
                            else:
                                st.error("Task can not be Blank")
                else:
                    st.error("Only Manager can Modify or Delete the Task or you can Modify or Delete Task created by you only.")        
            else:
                st.success('Select a Record to Modify ....')
                    
        elif crud=='View':
            st.success('Right Click to Export Report to Excel')
        else:
            #for delet
            if st.session_state['Role']=="Manager" or st.session_state['User']==selected['created_by'].iloc[0]:
                if selected:
                        st.success('Are you sure you want to Delete Selected Record')
                        if st.button("Delete Selected Record",key='delcompdocackst'):
                            rid=selected['id'].iloc[0]
                            rdel=del_task(rid)
                            st.success(rdel)
                else:
                        st.success('Select a Record to Delete ....')
            else:
                    st.error("Only Manager can Modify or Delete the Task or you can Modify or Delete Task created by you only.")        
           



def show_audit():
    
    with audit_container:
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        
        #st.subheader("Audit")
        with st.sidebar.markdown("# Audit"):
            sel_option= st.radio("Select Option",('Audit- Vouching, Verification, Review','Planning','Documents & Info.','Observations for Audit Check List','Close Audit'),key='raiodmainop')
        if sel_option=='Documents & Info.':
            st.info("**Audit Documentation**")
            docs_ops=st.selectbox('Audit File Type',options=('-----','Company Audit File','Audit Working Papers'))
            if docs_ops=="-----":
                t="Select type of Audit File from above..."
                new_title=f'<p style="color: red;">{t}</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                #st.success("Select type of Audit File from above...")
            elif docs_ops=="Company Audit File":
                
                #st. success(docs_ops)
                #st.markdown("""---""")
                crud=st.radio("Company Audit File Documents",('View','Add New','Modify','Delete'),horizontal=True,key='strcrud')
                df=get_company_docs(st.session_state['Company'])
                builder = GridOptionsBuilder.from_dataframe(df)
                builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                builder.configure_selection(selection_mode="single",use_checkbox=True)
                        #builder.configure_default_column(editable=True)
                
                go = builder.build()
                        #uses the gridOptions dictionary to configure AgGrid behavior.
                grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                        #selelcted row to show in audit AGGrid
                selected = grid_response['selected_rows']
                #st.dataframe(selected)
                                
                if crud=='Add New':
                    st.success('Enter details to Add New Record')
                    with st.form("Add Comp docs",clear_on_submit=True):
                        dtitle=st.text_input("Enter Title (Title should not be Duplicate)",key='dtitle',placeholder="Required")
                        dremarks=st.text_input("Enter Remarks",key='dremarks')
                        c1,c2 =st.columns(2)
                        with c1:
                            ddoctype=st.selectbox("Select Docuement / Information Type",('Other','Appointment','Communications','Legal','Organisation Details','Registrations'),key='sbadd')
                        with c2:
                            compfile=st.file_uploader("Upload File",type=['pdf','xlsx','docx'],key='compfile')
                            
                            file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilname',placeholder="Required")
                        submitted_com = st.form_submit_button("Submit")
                        if submitted_com:
                            if dtitle:
                                if compfile is not None:
                                        if file_name:
                                            if compfile.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                                extn="docx"
                                            elif compfile.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                                extn='xlsx'
                                            else :
                                                extn='pdf'
                                            #if st.button("Upload file",key='uf1'):
                                            comp_filename=f"{st.session_state['Company']}_{file_name}.{extn}"
                                            file_name=f"{file_name}.{extn}"
                                            with open(os.path.join("comp_docs",comp_filename),"wb") as f: 
                                                f.write(compfile.getbuffer())
                                            Reveiew=add_comp_doc(dtitle,dremarks,file_name,ddoctype,st.session_state['Company'])                                        
                                            st.success(Reveiew)
                                        else:
                                            st.success("Enter File Name")    
                                else:
                                    file_name=None
                                    st.error("Upload File...")
                                        #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                    #Reveiew=add_comp_doc(dtitle,dremarks,file_name,ddoctype,st.session_state['Company'])                                        
                            else:
                                st.error("Please Enter -Title. It is Mandatory field")

                           
                elif crud=='Modify':
                    if selected:
                        placeholder=st.empty()
                        Reveiew=""
                        with placeholder.container():
                            st.success('Enter details to Modify Selected Record')
                            with placeholder.form("Mdify Comp Doc",clear_on_submit=True):
                                dtitle=st.text_input("Enter New Title (Title should not be Duplicate)",key='dtitlem',value=selected['Title'].iloc[0])
                                dremarks=st.text_input("Enter New Remarsk",key='dremarksm',value=selected['Remarks'].iloc[0])
                                roid=selected['id'].iloc[0]
                                c1,c2 =st.columns(2)
                                with c1:
                                    ddoctype=st.selectbox("Select Docuement / Information Type",('Other','Appointment','Communications','Legal','Organisation Details','Registrations'),key='sbmodif')
                                with c2:
                                    compfile=st.file_uploader("Upload File",type=['pdf','xlsx','docx'],key='compfilem')
                                    st.write(f"Uploaded filename: {selected['File_Ref'].iloc[0]}")
                                    #if selected[0]['File_Ref']:
                                        #file_name=selected[0]['File_Ref']
                                        #st.write(f"Uploaded filename: {file_name}")
                                    file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilnamem')
                                    #else: 
                                        #file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilnamem2')
                                submitted_com_mod =st.form_submit_button("Submit")
                                if submitted_com_mod:
                                    #st.write(file_name)
                                    if dtitle:
                                        
                                        if compfile is not None:
                                                #st.write(f'again-{file_name}')
                                                if file_name:
                                                    if compfile.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                                        extn="docx"
                                                    elif compfile.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                                        extn='xlsx'
                                                    else :
                                                        extn='pdf'
                                                    #if st.button("Upload file",key='uf1'):
                                                    comp_filename=f"{st.session_state['Company']}_{file_name}.{extn}"
                                                    file_name=f"{file_name}.{extn}"
                                                    with open(os.path.join("comp_docs",comp_filename),"wb") as f: 
                                                        f.write(compfile.getbuffer())
                                                    
                                                    Reveiew=modif_comp_doc(roid,dtitle,dremarks,file_name,ddoctype)                                        
                                                    st.success(Reveiew)
                                                    placeholder.empty()
                                                else:
                                                    st.success("Enter File Name")    
                                        else:
                                            #st.write(f'befor-{file_name}')
                                            file_name=None
                                            #st.write(f'then-{file_name}')
                                                #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                            Reveiew=modif_comp_doc(roid,dtitle,dremarks,file_name,ddoctype)                                        
                                            st.success(Reveiew)
                                            placeholder.empty()
                                    else:
                                        st.success("Please Enter -Title. It is Mandatory field")

                        st.success(Reveiew)
                    else:
                        st.success('Select a Record to Modify ....')
                        
                elif crud=='View':
                    #st.markdown("""---""")
                    if selected:
                        filename=selected['File_Ref'].iloc[0]
                        com_filename=f"{st.session_state['Company']}_{filename}"
                                    
                        if filename:
                                        
                            with open(os.path.join("comp_docs",com_filename), 'rb') as f:
                                st.download_button('Download Attachment', f, file_name=filename,key="dlcompfile")    
                    
                else:
                    if selected:
                        placeholder=st.empty()
                        Reveiew=""
                        with placeholder.container():
                            st.success('Are you sure you want to Delete Selected Record')
                            if st.button("Delete Selected Record",key='delcompdoc'):
                                rid=selected['id'].iloc[0]
                                Reveiew=del_comp_doc(rid)
                                placeholder.empty()
                        st.success(Reveiew)
                    else:
                        st.success('Select a Record to Delete ....')

                del[df]
                df=pd.DataFrame()
                
                with st.expander("Download Sample Documents ..."):
                    doc=st.selectbox("Select from list below",('Proposal for Internal Audit Services','Engagement Letter','Organization Background','Industry Research'),key='docsample')
                    if doc:
                            com_filename=f"{doc}.docx"
                            with open(os.path.join("samples",com_filename), 'rb') as f:
                                st.download_button('Download Sample File', f, file_name=com_filename,key="sampledownload")    
                
            else:
                
                #st. success(docs_ops)
                #st.markdown("""---""")
                auditid=int(st.session_state['AuditID'])
                crud=st.radio("Audit Working Papers",('View','Add New','Modify','Delete'),horizontal=True,key='strcruda')
                df=get_audit_docs(st.session_state['AuditID'])
                builder = GridOptionsBuilder.from_dataframe(df)
                builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                builder.configure_selection(selection_mode="single",use_checkbox=True)
                        #builder.configure_default_column(editable=True)
                go = builder.build()
                        #uses the gridOptions dictionary to configure AgGrid behavior.
                grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                        #selelcted row to show in audit AGGrid
                selected = grid_response['selected_rows']
                #st.dataframe(selected)
                           
                if crud=='Add New':
                    st.success('Enter details to Add New Record')
                    #st.write(st.session_state['AuditID'])
                    with st.form("Add Audit docs",clear_on_submit=True):
                        dtitle=st.text_input("Enter Title*",key='dtitlea',placeholder="Required, Title should not be Duplicate")
                        dremarks=st.text_input("Enter Remarks",key='dremarksa')
                        c1,c2 =st.columns(2)
                        with c1:
                            ddoctype=st.selectbox("Select Docuement / Information Type",('Other','Scope & Objective','Organisation Background','Minutes of Meetings',
                                                                                         'Interviews','Risk Analysis','Management Represenatations','Process Walk Through'),key='sbadda')
                        with c2:
                            compfile=st.file_uploader("Upload File",type=['pdf','xlsx','docx'],key='compfilea')
                            
                            file_name=st.text_input("Enter File Name without extention*",key='comfilnamea',placeholder="Required...Name should be Unique")
                        submitted_coma = st.form_submit_button("Submit")
                        if submitted_coma:
                            if dtitle:
                                if compfile is not None:
                                        if file_name:
                                            if compfile.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                                extn="docx"
                                            elif compfile.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                                extn='xlsx'
                                            else :
                                                extn='pdf'
                                            #if st.button("Upload file",key='uf1'):
                                            #comp_filename=f"{auditid}_{file_name}.{extn}"
                                            comp_filename=f"{st.session_state['Company']}_{file_name}.{extn}"
                                            file_name=f"{file_name}.{extn}"
                                            with open(os.path.join("audit_docs",comp_filename),"wb") as f: 
                                                f.write(compfile.getbuffer())
                                            Reveiew=add_audit_doc(dtitle,dremarks,file_name,ddoctype,auditid)                                        
                                        else:
                                            st.success("Enter File Name")    
                                else:
                                    file_name=None
                                    st.error("Upload File...") 
                                        #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                    #Reveiew=add_audit_doc(dtitle,dremarks,file_name,ddoctype,auditid)                                        
                            else:
                                st.error("Please Enter -Title. It is Mandatory field")

                           
                elif crud=='Modify':
                    if selected:
                        placeholder=st.empty()
                        Reveiew=""
                        with placeholder.container():
                            st.success('Enter details to Modify Selected Record')
                            with st.form("Modify Audit Doc",clear_on_submit=True):
                                dtitle=st.text_input("Enter New Title* (Title should not be Duplicate)",key='dtitlema',value=selected['Title'].iloc[0])
                                dremarks=st.text_input("Enter New Remarsk",key='dremarksma',value=selected['Remarks'].iloc[0])
                                roid=selected['id'].iloc[0]
                                c1,c2 =st.columns(2)
                                with c1:
                                    ddoctype=st.selectbox("Select Docuement / Information Type",('Other','Scope & Objective','Organisation Background','Minutes of Meetings',
                                                                                            'Interviews','Risk Analysis','Management Represenatations','Process Walk Through'),key='sbadda')
                    
                                with c2:
                                    compfile=st.file_uploader("Upload File",type=['pdf','xlsx','docx'],key='compfilema')
                                    st.write(f"Uploaded filename: {selected['File_Ref'].iloc[0]}")
                                    #if selected[0]['File_Ref']:
                                        #file_name=selected[0]['File_Ref']
                                        #st.write(f"Uploaded filename: {file_name}")
                                    file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilnamema')
                                    #else: 
                                        #file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilnamem2')
                                submitted_com_moda =st.form_submit_button("Submit")
                                if submitted_com_moda:
                                    #st.write(file_name)
                                    if dtitle:
                                        
                                        if compfile is not None:
                                                #st.write(f'again-{file_name}')
                                                if file_name:
                                                    if compfile.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                                        extn="docx"
                                                    elif compfile.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                                        extn='xlsx'
                                                    else :
                                                        extn='pdf'
                                                    #if st.button("Upload file",key='uf1'):
                                                    comp_filename=f"{st.session_state['Company']}_{file_name}.{extn}"
                                                    file_name=f"{file_name}.{extn}"
                                                    with open(os.path.join("audit_docs",comp_filename),"wb") as f: 
                                                        f.write(compfile.getbuffer())
                                                    
                                                    Reveiew=modif_audit_doc(roid,dtitle,dremarks,file_name,ddoctype)                                        
                                                    placeholder.empty()
                                                else:
                                                    st.success("Enter File Name")    
                                        else:
                                            #st.write(f'befor-{file_name}')
                                            file_name=None
                                            #st.write(f'then-{file_name}')
                                                #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                            Reveiew=modif_audit_doc(roid,dtitle,dremarks,file_name,ddoctype)                                        
                                            placeholder.empty()
                                    else:
                                        st.success("Please Enter -Title. It is Mandatory field")
                        st.success(Reveiew)
                                
                            
                    else:
                        st.success('Select a Record to Modify ....')
                        
                elif crud=='View':
                    #st.markdown("""---""")
                    if selected:
                        filename=selected['File_Ref'].iloc[0]
                        #com_filename=f"{auditid}_{filename}"
                        com_filename=f"{st.session_state['Company']}_{filename}"          
                        if filename:
                                        
                            with open(os.path.join("audit_docs",com_filename), 'rb') as f:
                                st.download_button('Download Attachment', f, file_name=filename,key="dlcompfilea")    
                    
                else:
                    if selected:
                        placeholder=st.empty()
                        Reveiew=""
                        with placeholder.container():
                            st.success('Are you sure you want to Delete Selected Record')
                            if st.button("Delete Selected Record",key='delcompdoca'):
                                rid=selected['id'].iloc[0]
                                Reveiew=del_audit_doc(rid)
                                placeholder.empty()
                        st.success(Reveiew)
                                
                    else:
                        st.success('Select a Record to Delete ....')

                del[df]
                df=pd.DataFrame()
                with st.expander("Download Sample Documents ..."):
                    doc=st.selectbox("Select from list below",('Scope and Objective Statement','Overall Planning','Risk Analysis',
                                               'Opening Meeting Control Statement','General Process Understanding','Data Needs Identification and Collection',
                                               'Data Analysis and Summaries Preparation','Previous Audit Report Analysis',
                                               'Brain Storming Sessions','Selection of Samples','Walk Through Tracking',
                                               'Documentation of Walk Through','Planning and Execution of Audit Programme',
                                               'Quality Checklist of Evidence Collection','Final Report Release Checklist',
                                               'Overall Closure Checklist','Agenda for the Meeting',
                                               'Minutes of Meeting'),key='docsample1')
                    if doc:
                            com_filename=f"{doc}.docx"
                            with open(os.path.join("samples",com_filename), 'rb') as f:
                                st.download_button('Download Sample File', f, file_name=com_filename,key="sampledownloadwp")    
                
                
        elif sel_option=='Planning':
            show_planning()
        elif sel_option=='Observations for Audit Check List':
            #st.success('Update Audit Observations...')
            show_Audit_observations()
        
        elif sel_option=='Close Audit':
            st.info("**Close Audit**")
            auditid=int(st.session_state['AuditID'])
            pending_qs=get_pending_Compliance(auditid)
            if len(pending_qs)==0:
                st.success("All Audit Observations are Closed ; so Now You can Close this Audit. ")
                if st.button("Close Audit",key='closeauit'):
                    cl=closed_audit(auditid)
                    st.success(cl)
                    st.success("Login Again")
                    st.session_state['loggedIn'] = False
                    loginuser=""
            else:
                st.error("Following are Open Audit Observations, First Close all the Open Items & then you can Close Audit.")
                st.dataframe(pending_qs)
                
        else:
            #do V&V
            st.info("**Audit Dataset**")
            optionsdf=get_dsname(int(st.session_state['AuditID']))
            #add blank row at begining of list
            optionsdf.loc[-1]=['---']
            optionsdf.index=optionsdf.index+1
            optionsdf.sort_index(inplace=True)  
            d_sname=st.selectbox("Select Data Set to Audit",optionsdf,key="selectdsname")
            ds_name=f"{(st.session_state['AuditID'])}_{d_sname}"
            #select dataset 
        
               
            if d_sname=="---":
                t="Select Data Set to Audit from above..."
                new_title=f'<p style="color: red;">{t}</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                #st.success("Select Data Set to Audit from above...")
            else:
                
                df=get_dataset(ds_name)
                df.drop(['AutoAudit_Status', 'AutoAudit_Sampled'], axis=1,inplace=True)
                optionssampl=st.radio("1",("Vouching & Verification","Analyse Dataset","Analytical Review & Other Remarks"),horizontal=True,key="optionfirstaudit",label_visibility="hidden")
                
                #tab1,tab2 =st.tabs(["   Vouching & Verification  ","   Analytical Review & Other Remarks   "])
                #with tab1:
                if optionssampl=="Vouching & Verification":
                    
                    #st.write(f"**{d_sname}**")
                    st.success("**Select a Row for Voching & Verification**")
                    
                    #st.dataframe(df)
                        #builds a gridOptions dictionary using a GridOptionsBuilder instance.
                    builder = GridOptionsBuilder.from_dataframe(df)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                        #builder.configure_default_column(editable=True)
                    go = builder.build()
                        #uses the gridOptions dictionary to configure AgGrid behavior.
                    #st.success("aggrid is jow")
                    grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                        #selelcted row to show in audit AGGrid
                    selected = grid_response['selected_rows']
                    if selected:
                        #st.success("selected")
                        placeholder=st.empty()
                        res=""
                        vouching=""
                        very=""
                        update_audit=""
                        #imp=st.button('View Default Check List',key='defchkli')
                        with placeholder.container():
                            with st.form("Auditing",clear_on_submit=True):
                                                        
                                #colum1,colum2 =st.columns(2)
                                #with colum1:
                                    #selected = grid_response['data']
                                    selected_df = pd.DataFrame(selected)
                                    
                                    #rowinedx if added delet
                                    if '_selectedRowNodeInfo' in selected_df.columns:
                                        selected_df.drop(['_selectedRowNodeInfo'], axis=1,inplace=True)
                                    #st.dataframe(selected_df)
                                    data_id=int(selected_df.iloc[0,0])
                                    #st.write(data_id)
                                    #st.dataframe(selected_df.describe())
                                    #st.write(selected_df.info())
                                    #delet index colum
                                    selected_df = selected_df.drop(['index'], axis=1, errors='ignore')
                                    selected_df=selected_df.applymap(str)
                                    selected_df=selected_df.transpose()
                                    selected_df["Field"]=selected_df.index
                                    selected_df.rename(columns={0:'Value'},inplace=True)
                                    selected_df['Audit_Value']=selected_df['Value']
                                    selected_df["Cause"]=''
                                    selected_df["Effect"]=''
                                    selected_df=selected_df[['Field','Value','Audit_Value','Cause','Effect']]
                                    #selected_df.reset_index()
                                    #selected_df=selected_df.rename(columns={'0':'Value'},inplace=True)
                                    #st.dataframe(selected_df)  
                                    #show Vouching AGGrid
                                    builder_Audit=GridOptionsBuilder.from_dataframe(selected_df)
                                    #builder_Audit.configure_default_column(editable=True)
                                    builder_Audit.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                                    builder_Audit.configure_columns((['Audit_Value','Cause','Effect']),editable=True,autoHeight=True,wrapText=True)
                                    builder_Audit.configure_columns(['Audit_Value','Cause','Effect'],cellStyle={'color': 'red'})
                                    builder_Audit.configure_columns(['Value'],autoHeight=True,wrapText=True)
                                    #builder_Audit.configure_column(field='Audit_Value',wrapText=True)
                                    go_audit = builder_Audit.build()
                                    st.success("**Vouching-** If values are wrong...**Double click** on **Audit Value** to enter correct value & **press ENTER**.")
                                    #audited=AgGrid(selected_df, gridOptions=go_audit,update_mode= GridUpdateMode.VALUE_CHANGED,height = 80)
                                    audited=AgGrid(selected_df, gridOptions=go_audit,update_mode=(GridUpdateMode.VALUE_CHANGED|GridUpdateMode.SELECTION_CHANGED))
                                    #st.write(veri
                                    audited_data=audited['data']
                                    #df_audited_data=pd.DataFrame(audited_data)
                                    #aud_df=pd.DataFrame(audited_data)
                                    #st.dataframe(df_audited_data)
                                    #st.write(audited_data)
                                #with colum2:
                                    currentime=str(datetime.now())[:19]
                                    #Verification
                                    st.success("**Verification**- if Criteria is met... **Tick Check Box**, else keep Unchecked.")
                                    df_verif=get_verification(d_sname,int(st.session_state['AuditID']))
                                    df_verif["Cause"]=''
                                    df_verif["Effect"]=''
                                    df_verif.drop(['Risk_Weight','Risk_Category'], axis=1,inplace=True)
                                    
                                    builder_verif=GridOptionsBuilder.from_dataframe(df_verif)
                                    builder_verif.configure_selection(selection_mode="multiple",use_checkbox=True)
                                    builder_verif.configure_columns((['Cause','Effect']),editable=True)
                                    builder_verif.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                                    go_verif=builder_verif.build()
                                    verif=AgGrid(df_verif, gridOptions=go_verif,update_mode=(GridUpdateMode.VALUE_CHANGED|GridUpdateMode.SELECTION_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                                    #st.write(verif)
                                    all_verif=verif["data"]
                                    df_all_verif=pd.DataFrame(all_verif)
                                    #st.dataframe(df_all_verif)
                                    if '_selectedRowNodeInfo' in df_all_verif.columns:
                                        df_all_verif.drop(['_selectedRowNodeInfo'], axis=1,inplace=True)
                                    #get DF for selected
                                    selected_verif=verif["selected_rows"]
                                    df_selected_ver=pd.DataFrame(selected_verif)
                                    #st.dataframe(df_selected_ver)
                                    if '_selectedRowNodeInfo' in df_selected_ver.columns:
                                        df_selected_ver.drop(['_selectedRowNodeInfo'], axis=1,inplace=True)
                                    
                                    #get df for not selected
                                    df_unselected_ver=pd.concat([df_all_verif,df_selected_ver]).drop_duplicates(keep=False).reset_index(drop=True)
                                    #st.dataframe(df_all_verif)
                                    #st.dataframe(df_unselected_ver)
                                    #add colums to selected    
                                    df_selected_ver.rename(columns={'Verification_Criteria':'Criteria'},inplace=True)
                                    df_selected_ver['DataSetName']=d_sname
                                    df_selected_ver['CompanyName']=st.session_state['Company']
                                    df_selected_ver['Condition']="Yes"
                                    
                                        
                                    #add colums to Unselected    
                                    df_unselected_ver.rename(columns={'Verification_Criteria':'Criteria'},inplace=True)
                                    df_unselected_ver['DataSetName']=d_sname
                                    df_unselected_ver['CompanyName']=st.session_state['Company']
                                    df_unselected_ver['Condition']="No"  
                                    if 'rowIndex' in df_unselected_ver.columns:
                                        df_unselected_ver.drop(['rowIndex'], axis=1,inplace=True)
                                        
                                    #st.dataframe(df_selected_ver)   
                                    #st.dataframe(df_unselected_ver)  
                                    Submit_audit= st.form_submit_button("Submit")
                                    if Submit_audit:
                                        if  audited_data.empty:
                                            st.success("Select row to Audit")
                                        else:
                                            #add  in database####new code required
                                            #data_id=int(audited_data.iloc[0,0])
                                            
                                            audited_data = audited_data[audited_data['Value'] != audited_data['Audit_Value']]
                                            audited_data['DataSetName']=d_sname
                                            audited_data['CompanyName']=st.session_state['Company']
                                            audited_data['Data_Id']=data_id
                                            audited_data['Audited_on']=currentime
                                            audited_data['Audited_By']=st.session_state['User']
                                            audited_data['Audit_Name']=st.session_state['Audit']
                                            audited_data['Audit_id']=int(st.session_state['AuditID'])
                                            audited_data['Condition']=audited_data['Field']+': Value asper Records is- '+audited_data['Value']+'; but as per Audit is-'+audited_data['Audit_Value']
                                            audited_data['Criteria']=audited_data['Field']+': should be Correct'
                                            del audited_data['Value'] 
                                                                
                                            #st.dataframe(audited_data)
                                            vouching=insert_vouching(audited_data)
                                            #st.success(vouching)
                                                    
                                            
                                            #for verification =yes insert in Audit_queries
                                            df_selected_ver['Data_Id']=data_id
                                            df_selected_ver['Condition']="Yes"
                                            df_selected_ver['Audited_on']=currentime
                                            df_selected_ver['Audited_By']=st.session_state['User']
                                            df_selected_ver['Audit_Name']=st.session_state['Audit']
                                            df_selected_ver['Audit_id']=int(st.session_state['AuditID'])
                                            df_selected_ver['Status']="Closed"
                                            very=add_audit_verification(df_selected_ver)
                                            
                                            
                                            #for verification =No insert in Audit_queries
                                            df_unselected_ver['Data_Id']=data_id
                                            df_unselected_ver['Condition']="No"
                                            df_unselected_ver['Audited_on']=currentime
                                            df_unselected_ver['Audited_By']=st.session_state['User']
                                            df_unselected_ver['Audit_Name']=st.session_state['Audit']
                                            df_unselected_ver['Audit_id']=int(st.session_state['AuditID'])
                                            very=add_audit_verification(df_unselected_ver)
                                            #st.success(very)
                                            #st.dataframe(df_unselected_ver)
                                            #update audit status
                                            update_audit=update_audit_status(data_id,ds_name)
                                            #refresh AGGrid-update_mode=GridUpdateMode.MODEL_CHANGED also added with OR
                                            #df = df.drop([0],inplace=True)
                                            #st.success(update_audit)
                                            #del & clear DataFrame
                                            del [[df_verif,df_unselected_ver,df_selected_ver,audited_data,selected_df,df_all_verif]]
                                            df_all_verif=pd.DataFrame()
                                            df_unselected_ver=pd.DataFrame()
                                            df_selected_ver=pd.DataFrame()
                                            audited_data=pd.DataFrame()
                                            selected_df=pd.DataFrame()
                                            df_verif=pd.DataFrame()
                                            placeholder.empty()
                                            res="To Refresh Table- Click on Check Box for any Row"
                        
                        st.write(f"{vouching} ")
                        st.write(f"{very} ")
                        st.write(f"{update_audit} ")
                        st.success(res)
                                        #auditnext()
                    
                                           
                elif optionssampl=="Analytical Review & Other Remarks":
                #with tab2:
                    #st.subheader(d_sname)
                    #add Reveiew Remark
                    #show in DF
                    st.success("**Add Analytical Review & Other Comments for Data Set...**")
                    # add verification list
                    #st.markdown("""---""")
                    Reveiew=get_ar_for_ds(d_sname)  
                    #st.header("Add Comments")
                    with st.form("Analytical Review & Other Comments",clear_on_submit=True):
                        criteria=st.text_input("Criteria*",key='t1',placeholder="Required; Must be Unique")
                        condition=st.text_input("Condition*",key='t2',placeholder="Required")
                        cause=st.text_input("Cause",key='t3')
                        effect=st.text_input("Effect",key='t4')
                        #reviewfile=st.file_uploader("Upload Remarks/ Calculation File",type=['pdf','xlsx','docx'],key='reviewfile11')
                        
                                        
                                        #with open(os.path.join("rev_files",rev_filename), 'rb') as f:
                                            #st.download_button('Download File', f, file_name=rev_filename)    
                        c1,c2 =st.columns(2)
                        with c1:
                            risk_weight=st.slider("Risk Weights",min_value=1,max_value=10,key='slider1',value=1)
                                                            
                            if risk_weight >=1 and risk_weight <=3:
                                risk_category='Low'
                            elif risk_weight >=4 and risk_weight <=7:
                                risk_category='Medium'
                            else:
                                risk_category='High'
                        with c2:
                            #file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='stfn1')
                            reviewfile=st.file_uploader("Upload Remarks/ Calculation File",type=['pdf','xlsx','docx'],key='reviewfile1')
                            #if reviewfile is not None:
                                #st.write("file_name")
                                #file_name=st.text_input("Enter File Name...Name should be Unique",key='stfn')                
                        #reviewfile=st.file_uploader("Upload Remarks/ Calculation File",type=['pdf','xlsx','docx'],key='reviewfile1')
                            #if reviewfile is not None:
                            file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='stfn')
                        submitted = st.form_submit_button("Submit")                   
                        #submitted = st.button("Submit",key="sumbitform1")
                        if submitted:
                            if criteria and condition:
                                if reviewfile is not None:
                                    if file_name:
                                        if reviewfile.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                            extn="docx"
                                        elif reviewfile.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                            extn='xlsx'
                                        else :
                                            extn='pdf'
                                        #if st.button("Upload file",key='uf1'):
                                        rev_filename=f"{(st.session_state['AuditID'])}{d_sname}_{file_name}.{extn}"
                                        file_name=f"{file_name}.{extn}"
                                        with open(os.path.join("rev_files",rev_filename),"wb") as f: 
                                            f.write(reviewfile.getbuffer()) 
                                        
                                        #with open(rev_filename, 'rb') as f:
                                        Reveiew=add_analytical_review(criteria,condition,cause,effect,d_sname,st.session_state['Company'],risk_weight,risk_category,file_name)
                                    else:
                                        st.success("Enter File Name")    
                                else:
                                    file_name=None
                                    #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                    Reveiew=add_analytical_review(criteria,condition,cause,effect,d_sname,st.session_state['Company'],risk_weight,risk_category,file_name)
                            else:
                                st.success("Criteria & Condition are Mandatory fields")

                        
                    
                    with st.expander("View Analytical Review & Other Comments"):
                        st.success(f"Analytical Review & Other Comments for:- {d_sname}")
                        Reveiew=get_ar_queries(d_sname)
                        #st.dataframe(Reveiew)
                        #show Aggrid
                        builder = GridOptionsBuilder.from_dataframe(Reveiew)
                        #.loc[:, ['DataSetName','Field','Data_Id','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                        builder.configure_pagination(enabled=True,paginationPageSize=10,paginationAutoPageSize=False)
                        builder.configure_selection(selection_mode="single",use_checkbox=True)
                                    #builder.configure_default_column(editable=True)
                        #cc=JsCode("return{color: 'red'}")
                        #builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                        go = builder.build()
                                    #uses the gridOptions dictionary to configure AgGrid behavior.
                        #grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),theme="blue")
                        grid_response=AgGrid(Reveiew, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),key="sum10")
                        selected = grid_response['selected_rows']
                        #download file option
                        if selected:
                            filename=selected['Review_File'].iloc[0]
                            com_filename=f"{(st.session_state['AuditID'])}{d_sname}_{filename}"
                            #com_filename=f"{st.session_state['Company']}_{filename}"
                                   
                            if filename:
                                        
                                with open(os.path.join("rev_files",com_filename), 'rb') as f:
                                    st.download_button('Download Attachment', f, file_name=filename,key="dlcompfile")    
                    
                        #reviws_table=st.table(Reveiew)
                    
                    del Reveiew       
                    Reveiew=pd.DataFrame()
                    

                else:
                    st.success("**Review & Analyse Data Set...**")
                    ds=get_entire_dataset(ds_name)
                    with st.expander('Visualise Data Set'):
                         st.write(f"Data Set :- {d_sname}")
                         st.success(f"""Generate Chats for easy Analysis""")
                         renderer=gen_walk(ds)
                         renderer.explorer()
                    with st.expander('Analyse Data Set'):
                        st.write(f"Data Set :- {d_sname}")
                        st.dataframe(ds)
                    with st.expander("View Statistical Summary"):
                        st.success(f"Stats Summary for:- {d_sname}")
                        st.dataframe(ds.describe(include='all').transpose())
                    del ds
                    ds=pd.DataFrame()
                     
                    
                    
                        
headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
logOutSection = st.container()
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
 

def show_main_page():
    with mainSection:
        st.write(f"User:-{st.session_state['username']}")
        
 
def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False
    loginuser=""
    
def show_logout_page():
    loginSection.empty()
    with logOutSection:
        st.sidebar.button ("Log Out", key="logout", on_click=LoggedOut_Clicked)


def LoggedIn_Clicked(userName, password):
    if login(userName, password):
        st.session_state['loggedIn'] = True
        st.session_state['username']=userName
        loginuser=userName
    else:
        st.session_state['loggedIn'] = False
        st.success("Invalid user name or password")

def Register_Clicked(userid, password,designation,displayname):
    createuser=create_user(displayname,userid,password,designation)
    st.success(createuser)
    #show_login_page()
   
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
                password = st.text_input (label="Current Password", value="",placeholder="Enter Current Password", type="password",key="k6")
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
                #st.form_submit_button("Submit",on_click=Register_Clicked, args= (userid, password,designation,displayname))
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
                #if audit is closed dont show this
                auditstatus=check_audit_status()
                if auditstatus=="Open":
                    if st.session_state['Role'] == "Auditee":
                        show_auditee()
                    else:                     
                        show_audit()  
                else: st.error("Audit is Closed. you can not Access this Menu...")
                    
            else:
                #st.title("Login")
                show_login_page()
        