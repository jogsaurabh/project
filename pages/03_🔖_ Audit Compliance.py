from datetime import datetime
from functions import get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit,add_audit_verification
from functions import create_user,check_login,get_dsname_personresponsible,assign_user_rights,create_company,get_company_names,get_pending_queries
from functions import get_Summary_audit_values_comp_auditeeId,get_pending_obser_for_auditee,update_mgt_comm,update_query_status_ar,get_ar_queries,get_vv_quries,create_dataset,add_verification_criteria,get_dsname,get_entire_dataset,get_auditee_comp
from functions import check_audit_status,get_Summary_AR_audit_values_comp_auditeeId,get_audit_values_byAuditee,get_Summary_audit_values_comp,get_audit_values,get_pending_Corrective_forauditee,update_password,update_compliance_remarks,get_pending_Compliance,update_corre_action,get_pending_Corrective,get_pending_obser,add_query_reply_AR,get_dataset,update_query_status,add_analytical_review,insert_vouching,update_audit_status,get_ar_for_ds,add_query_reply
import pandas as pd
import os
import streamlit as st
from PIL import Image
image = Image.open('autoaudit_t.png')
from st_aggrid import AgGrid,DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, grid_options_builder,ColumnsAutoSizeMode
import sqlite3

st.set_page_config(page_title="AutoAudit", page_icon=":white_check_mark:", layout="wide")
url="https://acecom22-my.sharepoint.com/:w:/g/personal/saurabhjog_acecomskills_in/ESLKUvAGIMJJontdPiuXk5YBTxjbcYnCkilrcBJ3oHy0ww?e=ZS4i6g"
headercol1,headercol2,co3=st.columns([8,2,1])
with headercol1 : st.image(image,width=200,)
with co3: 
    link =f'[Help]({url})'
    st.markdown(link, unsafe_allow_html=True)
    #st.markdown(f'''<a href={url}><button style="padding: 5px 8px; border-radius: 5px; border: 1px solid red;">Help</button></a>''',
    #            unsafe_allow_html=True)

st.markdown("""---""")
cont_audit_status=st.container()
cont_queryupdate=st.container()

def show_update_audit_status():
    with cont_audit_status:
        auditid=int(st.session_state['AuditID'])
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        #get pending queries for DS current Audit
        #pending=get_pending_queries(auditid)
        
        #st.markdown("""---""")
        with st.sidebar.markdown("# Select Data Set"):
            sta_opts=st.comp_opps=st.radio('Audit Compliance',('Update Query Status','Update Audit Compliance Status'),key='opcompr')
            
        if sta_opts=='Update Query Status':
                st.info("**Update Status of Audit Queries**")
                optionsdf=get_dsname(int(st.session_state['AuditID']))
                #add blank row at begining of list
                optionsdf.loc[-1]=['---']
                optionsdf.index=optionsdf.index+1
                optionsdf.sort_index(inplace=True)
                d_sname=st.selectbox("Select Data Set to Audit",optionsdf,key="selectdsname")
                ds_name=f"{(st.session_state['AuditID'])}_{d_sname}"
                #select dataset 
            
                if d_sname=="---":
                    mes="Select Data Set to Update Audit Status."
                    original_title = f'<p style="color:Red; ">{mes}</p>'
                    st.markdown(original_title, unsafe_allow_html=True)
                else:
                    st.success(f"Update Remarks for {d_sname} Queries")
                    with st.expander("Vouching & Verification Queries"):
                        
                        pending=get_vv_quries(f"{st.session_state['AuditID']}_{d_sname}",d_sname,int(st.session_state['AuditID']))
                        #st.dataframe(pending)
                        
                        builder = GridOptionsBuilder.from_dataframe(pending)
                        #.loc[:, ['DataSetName','Field','Data_Id','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                        builder.configure_pagination(enabled=True,paginationPageSize=10,paginationAutoPageSize=False)
                        builder.configure_selection(selection_mode="single",use_checkbox=True)
                                    #builder.configure_default_column(editable=True)
                        #cc=JsCode("return{color: 'red'}")
                        builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                        go = builder.build()
                                    #uses the gridOptions dictionary to configure AgGrid behavior.
                        #grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),theme="blue")
                        grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

                                    #selelcted row to show in audit AGGrid
                        #csv=pending.to_csv().encode('utf-8')
                        #st.download_button("Download csv file",csv,f"{d_sname}.csv")
                        selected = grid_response['selected_rows']
                        #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                        st.write(selected)
                        if selected is not None:
                            #st.write(selected)
                            placeholder=st.empty()
                            updatereply=""
                            res=""
                            with placeholder.container():
                                currentremark=selected['status_update_remarks'].iloc[0]
                                currentquryreply=selected['Reply'].iloc[0]
                                one ,two= st.columns(2)
                                with one:
                                    "Auditee Reply:-"
                                    st.warning(currentquryreply)
                                    "Current Remarks:-"
                                    st.warning(currentremark)
                                
                                with two:
                                    reply=st.text_area("Add Status Update Remarks to Selected Query",key="ta",placeholder=f"Required\n Single Quote ' not allowed")
                                    close=st.selectbox("Close / Pending",["Pending","Closed"],key="cq")
                                submit=st.button("Submit",key="submitquery")
                                if submit:
                                        currentime=str(datetime.now())[:19]
                                        id=int(selected['Id'].iloc[0])
                                        #currentremark=selected[0]['status_update_remarks']
                                        if currentremark is None:
                                            currentremark=""
                                            reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                        else:
                                            reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                        #st.text(reply)
                                        #st.text(id)
                                        #update remark
                                        updatereply=update_query_status(id,reply,close)
                                        placeholder.empty()
                                        res="To Refresh Table- Click on Check Box for any Row"
                            st.success(f"{updatereply} {res}")
                        else:
                            st.info("Selected a Row to Update Query Status")
                    st.markdown("""---""")
                    with st.expander("Analytical Review & Other Queries"):
                            
                                pending=get_ar_queries(d_sname)
                                #st.dataframe(pending)
                                builder = GridOptionsBuilder.from_dataframe(pending)
                                #.loc[:, ['DataSetName','Field','Data_Id','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                                builder.configure_pagination(enabled=True,paginationPageSize=10,paginationAutoPageSize=False)
                                builder.configure_selection(selection_mode="single",use_checkbox=True)
                                            #builder.configure_default_column(editable=True)
                                #cc=JsCode("return{color: 'red'}")
                                builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                                go = builder.build()
                                            #uses the gridOptions dictionary to configure AgGrid behavior.
                                #grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),theme="blue")
                                grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

                                            #selelcted row to show in audit AGGrid
                                #csv=pending.to_csv().encode('utf-8')
                                #st.download_button("Download csv file",csv,f"{d_sname}.csv")
                                selected = grid_response['selected_rows']
                                #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                                
                                if selected is not None:
                                    #st.write(selected)
                                    placeholder=st.empty()
                                    updatereply=""
                                    res=""
                                    with placeholder.container():
                                        currentremark=selected['status_update_remarks'].iloc[0]
                                        currentquryreply=selected['reply'].iloc[0]
                                        filename=selected['Review_File'].iloc[0]
                                        rev_filename=f"{(st.session_state['AuditID'])}{d_sname}_{filename}"
                                        
                                        if filename:
                                            
                                            with open(os.path.join("rev_files",rev_filename), 'rb') as f:
                                                st.download_button('Download Attachment', f, file_name=filename,key="reveiewdl")    
                        
                                        one ,two= st.columns(2)
                                        
                                        with one:
                                            "Auditee Reply:-"
                                            st.warning(currentquryreply)
                                            "Current Remarks:-"
                                            st.warning(currentremark)
                                        with two:
                                            reply=st.text_area("Add Status Update Remarks to Selected Query",key="ta1",placeholder=f"Required\n Single Quote ' not allowed")
                                            close=st.selectbox("Close / Pending",["Pending","Closed"],key="cq2")
                                        submit=st.button("Submit",key="submitquery2")
                                        if submit:
                                                currentime=str(datetime.now())[:19]
                                                id=int(selected['Id'].iloc[0])
                                                #currentremark=selected[0]['status_update_remarks']
                                                if currentremark is None:
                                                    currentremark=""
                                                    reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                                else:
                                                    reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                                #st.text(reply)
                                                #st.text(id)
                                                #update remark
                                                updatereply=update_query_status_ar(id,reply,close)
                                                res="To Refresh Table- Click on Check Box for any Row"
                                                placeholder.empty()
                                    st.success(f"{updatereply} {res}")
                                else:
                                    st.info("Selected a Row to Update Query Status")
        else:
                    st.info("**Update Audit Compliance**")
                    auditid=int(st.session_state['AuditID'])
                    pending_qs=get_pending_Compliance(auditid)   
                    builder = GridOptionsBuilder.from_dataframe(pending_qs)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                    builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(pending_qs, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                                #selelcted row to show in audit AGGrid
                    #csv=pending_ob.to_csv().encode('utf-8')
                    #st.download_button("Download csv file",csv,f"{d_sname}.csv")
                    selected = grid_response['selected_rows']
                    #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                    
                    if selected is not None:
                        #st.write(selected)
                        placeholder=st.empty()
                        mgt_comments=""
                        res=""
                        with placeholder.container():
                            actionremarks=selected['Action_Remarks'].iloc[0]
                            c_Corrective_Action_Plan=selected['Corrective_Action_Plan'].iloc[0]
                                                    
                            co1,co2,co3 =st.columns(3)
                            with co1:
                                "Corrective_Action_Plan:-"
                                st.warning(c_Corrective_Action_Plan)
                                #st.write(selected)
                            with co2:
                                "Current Action_Remarks:-"
                                st.warning(actionremarks)
                            with co3:
                                "Mangement Comments:-"
                                st.warning(selected['Management_Comments'].iloc[0])
                            
                            "Current Compliance_Remarks:-"
                            st.warning(selected['Compliance_Remarks'].iloc[0])
                            reply=st.text_area("Add Compliance Remarks",key="taocc",placeholder=f"Required\nSingle Quote ' not allowed")
                            status=st.selectbox("Update Status of Audit Observation",('Open','Close'),key='ocu')
                            submit=st.button("Submit",key="submitqueryocc")
                            if submit:
                                if not reply:
                                    st.warning("Comments can not be Blank")
                                else:
                                    currentime=str(datetime.now())[:19]
                                    id=int(selected['id'].iloc[0])
                                    currentremark=selected['Compliance_Remarks'].iloc[0]
                                    if currentremark is None:
                                        currentremark=""
                                        reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                    else:
                                        reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                    #st.text(reply)
                                    #st.text(id)
                                    #update remark
                                    mgt_comments=update_compliance_remarks(id,reply,status)
                                    res="To Refresh Table- Click on Check Box for any Row"
                                    placeholder.empty()
                        st.success(f"{mgt_comments} {res}")
                    else:
                        if len(pending_qs)>0:
                            st.error("Selected a Row to Update Compliance Remarks")
                
        

headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
logOutSection = st.container()
 
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
                userid = st.text_input (label="User Id", value="", placeholder="Enter your user ID",key="k5")
                password = st.text_input (label="Password", value="",placeholder="Enter Current Password", type="password",key="k6")
                new_pass = st.text_input (label="New Password", value="", placeholder="Enter New Password", type="password",key="k3")
                renew_pass = st.text_input (label="New Password", value="", placeholder="ReEnter New Password", type="password",key="k4")
                submit_user =st.form_submit_button("Submit")
                if submit_user:
                    if new_pass == renew_pass:
                        #createuser=create_user(displayname,userid,password,designation)
                        newpass=update_password(userid,password,new_pass)
                        st.info(newpass)
                    else:
                        st.info('New Password and ReEntered Password not matching...')
                #st.form_submit_button("Submit",on_click=Register_Clicked, args= (userid, password,designation,displayname))
                #st.button ("Register", on_click=Register_Clicked, args= (userid, password,designation,displayname))

def show_auditee():
    with cont_queryupdate:
        auditid=int(st.session_state['AuditID'])
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        #get pending queries for DS current Audit
        audit_id=int(st.session_state['AuditID'])
        #pending=get_pending_queries(auditid)
        #st.markdown("""---""")
        pr=st.session_state['User']
        with st.sidebar.markdown(" Select Data Set."):
            comp_opps=st.radio('Audit Compliance',('Pending Queries','Reply to Queries','Update Corrective Actions','Update Management Comments'),key='opcomp')
        if comp_opps=='Pending Queries':
            comp_name=st.session_state['Company']
            st.info(f"**Audit Summary for {comp_name} -{st.session_state['Audit']}**")
            auditvalues=get_audit_values_byAuditee(int(st.session_state['AuditID']),st.session_state['User'])
            totalvvqueries=auditvalues['total_queries_vv']
            totalarqueries=auditvalues['total_queries_ar']
            col1,col2= st.columns(2)
            with col1:
                new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Vouching & Verification Queries:</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                    #st.markdown('<style>p{color:red;}</style>"Total Transactions:"',unsafe_allow_html=True)
                new_title = f'<p style="font-family:sans-serif; color:Red; font-size: 27px;">{totalvvqueries}</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                
            with col2:
                new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Analytical Review & Other Queries:</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                    #st.subheader("Transactions Audited:")
                new_title = f'<p style="font-family:sans-serif;color:Red; font-size: 27px;">{totalarqueries}</p>'
                st.markdown(new_title, unsafe_allow_html=True)
            #charts for V&V
            
            st.success("Vouching & Verification - Queries Summary by Dataset")
            #get DF for vouching & verification
            auditdf=get_Summary_audit_values_comp_auditeeId(int(st.session_state['AuditID']),st.session_state['User'])
            col1, col2= st.columns(2)
            with col1:
                st.bar_chart(auditdf,x='Data Set Name',y='Total Queries')
            with col2:
                st.dataframe(auditdf)
                #st.bar_chart(auditdf,x='Criteria',y='Total Queries')
            
            st.success("Analytical & Other Remarks - Summary by Dataset")
            #get DF for vouching & verification
            auditdf=get_Summary_AR_audit_values_comp_auditeeId(int(st.session_state['AuditID']),st.session_state['User'])
            col1, col2= st.columns(2)
            with col1:
                st.bar_chart(auditdf,x='Data Set Name',y='Total Queries')
            with col2:
                st.dataframe(auditdf)
                #st.bar_chart(auditdf,x='Criteria',y='Total Queries')
    
        elif comp_opps=='Reply to Queries':
            st.info("**Reply to Audit Queries**")                
            #optionsdf=get_dsname(int(st.session_state['AuditID']))
            optionsdf=get_dsname_personresponsible(auditid,pr)
            #st.dataframe(optionsdf)
            #add blank row at begining of list
            optionsdf.loc[-1]=['---']
            optionsdf.index=optionsdf.index+1
            optionsdf.sort_index(inplace=True)
            d_sname=st.selectbox("Select Data Set to Reply Audit Queries",optionsdf,key="selectdsname")
            ds_name=f"{(st.session_state['AuditID'])}_{d_sname}"
            #select dataset 
            if d_sname=="---":
                t="Select Data Set from above List to Reply Audit Queries"
                new_title=f'<p style="color: red;">{t}</p>'
                st.markdown(new_title, unsafe_allow_html=True)

            else:
                st.success(f"Reply for {d_sname} Queries")
                with st.expander("Vouching & Verification Queries"):
                    pending=get_vv_quries(f"{st.session_state['AuditID']}_{d_sname}",d_sname,int(st.session_state['AuditID']))   
                    builder = GridOptionsBuilder.from_dataframe(pending)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                    builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                    
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                                #selelcted row to show in audit AGGrid
                    #csv=pending.to_csv().encode('utf-8')
                    #st.download_button("Download csv file",csv,f"{d_sname}.csv")
                    selected = grid_response['selected_rows']
                    #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                    
                    if selected is not None:
                        #st.write(selected)
                        placeholder=st.empty()
                        updatereply="" 
                        res=""
                        with placeholder.container():
                            currentremark=selected['Reply'].iloc[0]
                            replyremarks=selected['status_update_remarks'].iloc[0]
                            
                            co1,co2 =st.columns(2)
                            with co1:
                                "Current Auditee Reply:-"
                                st.warning(currentremark)
                                #st.write(selected)
                            with co2:
                                "Auditors Remarks for Reply:-"
                                st.warning(replyremarks)
                            reply=st.text_area("Add Reply to Selected Query",key="ta",placeholder=f"Required\n Single Quote ' not allowed")
                            submit=st.button("Submit",key="submitquery")
                            if submit:
                                if not reply:
                                    st.warning("Reply can not be Blank")
                                else:
                                    currentime=str(datetime.now())[:19]
                                    id=int(selected['Id'].iloc[0])
                                    currentremark=selected['Reply'].iloc[0]
                                    if currentremark is None:
                                        currentremark=""
                                        reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                    else:
                                        reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                    #st.text(reply)
                                    #st.text(id)
                                    #update remark
                                    updatereply=add_query_reply(id,reply)
                                    res="To Refresh Table- Click on Check Box for any Row"
                                    placeholder.empty()
                        st.success(f"{updatereply} {res}")
                    else:
                        st.info("Selected a Row to Reply the Query")
                st.markdown("""---""")
                with st.expander("Analytical Review & Other Queries"):
                    pending=get_ar_queries(d_sname)
                    builder = GridOptionsBuilder.from_dataframe(pending)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                    builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                                #selelcted row to show in audit AGGrid
                    #csv=pending.to_csv().encode('utf-8')
                    #st.download_button("Download csv file",csv,f"{d_sname}.csv")
                    selected = grid_response['selected_rows']
                    #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                    
                    if selected is not None:
                        placeholder=st.empty()
                        updatereply="" 
                        res=""
                        with placeholder.container():
                            currentremark=selected['reply'].iloc[0]
                            replyremarks=selected['status_update_remarks'].iloc[0]
                            filename=selected['Review_File'].iloc[0]
                            rev_filename=f"{(st.session_state['AuditID'])}{d_sname}_{filename}"
                                        
                            if filename:
                                            
                                with open(os.path.join("rev_files",rev_filename), 'rb') as f:
                                    st.download_button('Download Attachment', f, file_name=filename,key="auditeedl")    
                            
                            co1,co2 =st.columns(2)
                            with co1:
                                "Current Auditee Reply:-"
                                st.warning(currentremark)
                                #st.write(selected)
                            with co2:
                                "Auditors Remarks for Reply:-"
                                st.warning(replyremarks)
                                #st.write(selected)
                            reply=st.text_area("Add Reply to Selected Query",key="ta1",placeholder=f"Required\n Single Quote ' not allowed")
                            submit=st.button("Submit",key="submitquery111")
                            if submit:
                                if not reply:
                                    st.warning("Reply can not be Blank")
                                else:
                                    currentime=str(datetime.now())[:19]
                                    id=int(selected['Id'].iloc[0])
                                    #currentremark=selected[0]['reply']
                                    if currentremark is None:
                                        currentremark=""
                                        reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                    else:
                                        reply=f"{currentremark} :\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                    #st.text(reply)
                                    #st.text(id)
                                    #update remark
                                    updatereply=add_query_reply_AR(id,reply)
                                    res="To Refresh Table- Click on Check Box for any Row"
                                    placeholder.empty()
                        st.success(f"{updatereply} {res}")
                    else:
                        st.info("Selected a Row to Reply the Query")
        
                
        elif comp_opps=='Update Corrective Actions':
                    auditid=int(st.session_state['AuditID'])
                    pending_ob=get_pending_Corrective_forauditee(auditid,st.session_state['User'])   
                    #place Dash Board
                    st.info("**Update Corrective Actions**")
                    with st.expander("Pending Audit Observations Summary"):
                    
                        st.success("Pending Audit Observations")
                        #df_allObservations=get_all_obser(audit_id)
                        #df_pendingObservations=get_pending_obser(audit_id)
                        if not pending_ob.empty:
                            
                            df_summ=pending_ob.groupby('Audit_Area',as_index=False)['Criteria'].count()
                            df_summ.rename(columns={'Criteria':'Count'},inplace=True)
                            col1, col2= st.columns(2)
                            with col1:
                                st.bar_chart(df_summ,x='Audit_Area',y='Count')
                                
                                
                                #st.dataframe(df_head.filter(lambda x: x['Audit_Area']==selected_area)['Risk_Weight'].sum())
                            with col2:
                                
                                st.dataframe(df_summ)
                        #place aggrid
                    builder = GridOptionsBuilder.from_dataframe(pending_ob)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                    builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(pending_ob, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                                #selelcted row to show in audit AGGrid
                    #csv=pending_ob.to_csv().encode('utf-8')
                    #st.download_button("Download csv file",csv,f"{d_sname}.csv")
                    selected = grid_response['selected_rows']
                    #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                    
                    if selected is not None:
                        #st.write(selected)
                        placeholder=st.empty()
                        mgt_comments=""
                        res=""
                        with placeholder.container():
                            actionremarks=selected['Action_Remarks'].iloc[0]
                            c_Corrective_Action_Plan=selected['Corrective_Action_Plan'].iloc[0]
                            filename=selected['Annexure'].iloc[0]
                            rev_filename=f"{(st.session_state['AuditID'])}_{filename}"
                                        
                            if filename:
                                            
                                with open(os.path.join("obsev_docs",rev_filename), 'rb') as f:
                                    st.download_button('Download Attachment', f, file_name=filename,key="auditeedl")    
                            
                            
                            co1,co2 =st.columns(2)
                            with co1:
                                "Corrective_Action_Plan:-"
                                st.warning(c_Corrective_Action_Plan)
                                #st.write(selected)
                                "Compliance Remarks:-"
                                st.warning(selected['Compliance_Remarks'].iloc[0])
                            with co2:
                                "Current Action_Remarks:-"
                                st.warning(actionremarks)
                                "Maagement Comments:-"
                                st.warning(selected['Management_Comments'].iloc[0])
                            reply=st.text_area("Add Comments to Selected Action_Plan",key="taoc",placeholder=f"Required\nSingle Quote ' not allowed")
                            submit=st.button("Submit",key="submitqueryoc")
                            if submit:
                                if not reply:
                                    st.warning("Comments can not be Blank")
                                else:
                                    currentime=str(datetime.now())[:19]
                                    id=int(selected['id'].iloc[0])
                                    currentremark=selected['Action_Remarks'].iloc[0]
                                    if currentremark is None:
                                        currentremark=""
                                        reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                    else:
                                        reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                    #st.text(reply)
                                    #st.text(id)
                                    #update remark
                                    mgt_comments=update_corre_action(id,reply)
                                    res="To Refresh Table- Click on Check Box for any Row"
                                    placeholder.empty()
                        st.success(f"{mgt_comments} {res}")
                    else:
                        st.success("Selected a Row to Reply the Audit Observation")
                
            
        else:
                    st.info("**Update Management Comments**")
                    auditid=int(st.session_state['AuditID'])
                    #pending_ob=get_pending_obser(auditid) 
                    pending_ob=get_pending_obser_for_auditee(auditid,st.session_state['User']) 
                    builder = GridOptionsBuilder.from_dataframe(pending_ob)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                    builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(pending_ob, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                                #selelcted row to show in audit AGGrid
                    #csv=pending_ob.to_csv().encode('utf-8')
                    #st.download_button("Download csv file",csv,f"{d_sname}.csv")
                    selected = grid_response['selected_rows']
                    #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                    
                    if selected is not None:
                        #st.write(selected)
                        placeholder=st.empty()
                        mgt_comments=""
                        res=""
                        with placeholder.container():
                            recomendarions=selected['Recomendation'].iloc[0]
                            #c_Management_Comments=selected[0]['Management_Comments']
                            filename=selected['Annexure'].iloc[0]
                            rev_filename=f"{(st.session_state['AuditID'])}_{filename}"
                                        
                            if filename:
                                            
                                with open(os.path.join("obsev_docs",rev_filename), 'rb') as f:
                                    st.download_button('Download Attachment', f, file_name=filename,key="auditeedl")    
                            
                            
                            co1,co2 =st.columns(2)
                            with co1:
                                "Audit Recomendations:-"
                                st.warning(recomendarions)
                                #st.write(selected)"Compliance Remarks:-"
                                "Corrective Action Plan:-"
                                st.warning(selected['Corrective_Action_Plan'].iloc[0])
                            with co2:
                                "Current Compliance Remarks:-"
                                st.warning(selected['Compliance_Remarks'].iloc[0])
                                "Current Action Remarks:-"
                                st.warning(selected['Action_Remarks'].iloc[0])
                                
                            "Current Management Comments:-"
                            st.warning(selected['Management_Comments'].iloc[0])
                            reply=st.text_area("Add Management Comments to Selected Observation",key="tao",placeholder=f"Required\nSingle Quote ' not allowed")
                            submit=st.button("Submit",key="submitqueryo")
                            if submit:
                                if not reply:
                                    st.warning("Comments can not be Blank")
                                else:
                                    currentime=str(datetime.now())[:19]
                                    id=int(selected['id'].iloc[0])
                                    currentremark=selected['Management_Comments'].iloc[0]
                                    if currentremark is None:
                                        currentremark=""
                                        reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                    else:
                                        reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                    #st.text(reply)
                                    #st.text(id)
                                    #update remark
                                    mgt_comments=update_mgt_comm(id,reply)
                                    res="To Refresh Table- Click on Check Box for any Row"
                                    placeholder.empty()
                        st.success(f"{mgt_comments} {res}")
                    else:
                        st.success("Selected a Row to Reply the Audit Observation")
                
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
                        show_update_audit_status()  
                else: st.error("Audit is Closed. you can not Access this Menu...")
            else:
                #st.title("Login")
                show_login_page()
        
