#from turtle import color
#from re import X
from docx import Document
from htmldocx import HtmlToDocx
from PIL import Image
import json
import numpy as np
#import streamlit.components.v1 as components
#import plotly.io as pio
from jinja2 import Environment, FileSystemLoader
image = Image.open('autoaudit_t.png')
import pandas as pd  # pip install pandas openpyxl
#import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
from st_aggrid import AgGrid,DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, grid_options_builder,ColumnsAutoSizeMode
from functions import get_pending_obser,get_all_obser,update_password,get_pending_advere_obser,get_Summary_audit_values,get_ar_queries,get_all_ar_queries,get_all_vv_quries,get_vv_quries,get_values_id_dsn,get_audit_values,get_queries,get_ar,get_pending_queries,get_dataset_values
from functions import get_Summary_audit_values_riskweight_comp,get_Summary_audit_values_riskcategory,get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit
from functions import get_Audit_summ,get_ar_summary,get_audit_observations,get_Summary_audit_values_comp,get_Summary_audit_values_riskweight,create_user,check_login,assign_user_rights,create_company,get_company_names
from functions import del_audit_sum,modify_audit_summ,add_audit_summ,create_dataset,add_verification_criteria,get_dsname,get_entire_dataset,get_auditee_comp
st.set_page_config(page_title="Audit Dashboard", page_icon=":bar_chart:", layout="wide")
#st.title(":bar_chart: Audit Dashboard")
#import streamlit.components.v1 as components


url="https://acecom22-my.sharepoint.com/:w:/g/personal/saurabhjog_acecomskills_in/ESLKUvAGIMJJontdPiuXk5YBTxjbcYnCkilrcBJ3oHy0ww?e=ZS4i6g"
headercol1,headercol2,co3=st.columns([8,2,1])
with headercol1 : st.image(image,width=200)
with co3: 
    link =f'[Help]({url})'
    st.markdown(link, unsafe_allow_html=True)
    #st.markdown(f'''<a href={url}><button style="padding: 5px 8px; border-radius: 5px; border: 1px solid red;">Help</button></a>''',
    #            unsafe_allow_html=True)
st.markdown("""---""")
# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/


report_container=st.container()
cont_oaudit_summary=st.container()
        
def show_Audit_summary():
    with cont_oaudit_summary:
        st.info('**Summary of Audit Report**')
        crud=st.radio("1",('View','Add New','Modify','Delete'),horizontal=True,key='strcrud',label_visibility="hidden")
        auditid=int(st.session_state['AuditID'])
        df=get_Audit_summ(auditid)
        builder = GridOptionsBuilder.from_dataframe(df)
        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=15)
        builder.configure_selection(selection_mode="single",use_checkbox=True)
                        #builder.configure_default_column(editable=True)
        go = builder.build()
                        #uses the gridOptions dictionary to configure AgGrid behavior.
        grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                        #selelcted row to show in audit AGGrid
        selected = grid_response['selected_rows']
        #col1,col2,c3,c4 =st.columns(4)
        #with col1:
            #csv=df.to_csv().encode('utf-8')
            #st.download_button("Download CSV file",csv,f"Audit_Summ.csv")
        #report in word
        #with col2:
        
        
        
        if crud=='Add New':
                    #st.success("Enter details to Add New Record...Single quotes ' not allowed")
                    with st.form("Add AduSumm docs",clear_on_submit=True):
                        Observation=st.text_input("Enter Observation*",key='Observation',placeholder="Required")
                        Impact=st.text_input("Enter Impact",key='Impact')
                        Area=st.text_input("Enter Area",key='Area')
                        Need_for_Management_Intervention=st.text_input("Need_for_Management_Intervention",key='Need_for_Management_Intervention',value='Yes')
                        risk_weight=st.slider("Set Risk Weights",min_value=1,max_value=10,key='slider2rws')
                        if risk_weight >=1 and risk_weight <=3:
                                    risk_category='Low'
                        elif risk_weight >=4 and risk_weight <=7:
                                    risk_category='Medium'
                        else:
                                    risk_category='High'
                        submitted_com_sum = st.form_submit_button("Submit")
                        if submitted_com_sum:
                            if Observation:
                                audsum=add_audit_summ(auditid,Observation,risk_weight,risk_category,Impact,
                                                       Area,Need_for_Management_Intervention)                                        
                            else:
                                st.success("Please Enter -Observation. It is Mandatory field")
        elif crud=='Modify':
                           
            if selected:
                st.success("Enter details to Modify Selected Record...Single quotes ' not allowed")
                with st.form("Mdify Summ",clear_on_submit=True):
                                    
                        roid=selected['id'].iloc[0]
                        Observation=st.text_input("Update Observation",key='Observationm',value=selected['Observation'].iloc[0])
                        Impact=st.text_input("Update Impact",key='Impact',value=selected['Impact'].iloc[0])
                        Area=st.text_input("Update Area",key='Aream',value=selected['Impact'].iloc[0])
                        Need_for_Management_Intervention=st.text_input("Need_for_Management_Intervention",key='Need_for_Management_Interventionm',value=selected['Need_for_Management_Intervention'].iloc[0])
                        risk_weight=st.slider("Set Risk Weights",min_value=1,max_value=10,key='slider2rwsm',value=selected['Risk_Weight'].iloc[0])
                        if risk_weight >=1 and risk_weight <=3:
                                    risk_category='Low'
                        elif risk_weight >=4 and risk_weight <=7:
                                    risk_category='Medium'
                        else:
                                    risk_category='High'
                        submitted_com_summ = st.form_submit_button("Submit")
                        if submitted_com_summ:
                            if Observation:
                                audsum=modify_audit_summ(roid,Observation,Impact,Area,
                                                         Need_for_Management_Intervention,risk_weight,risk_category)                                        
                                st.success(audsum)
                            else:
                                st.success("Please Enter - Observation. It is Mandatory field")
                            
            else:
                st.success('Select a Record to Modify ....')
                        
                    
        elif crud=='View':
            if len(df) !=0:
                st.success("Download Report in Word")
                flist=df.columns
                fileds=st.multiselect("Select Fields to be shown in Report", options=flist,key="fiedsinreport1",default=flist.to_list())
                    
                if fileds:
                    wordrep=st.button("Generate & Download Report",key="wrodrep1")
                    if wordrep:
                        df=df[fileds]
                        st.dataframe(df)
                        jsondf=df.to_dict('records')
                        
                        # 2. Create a template Environment
                        env = Environment(loader=FileSystemLoader('templates'))
                        # 3. Load the template from the Environment
                        template = env.get_template('auditreport.html')
                        html3 = template.render(logo='logosmall1.png', jsondf = jsondf,companyname=st.session_state['Company'],auditname=st.session_state['Audit'])
                        #docx to rport
                        document = Document()
                        new_parser = HtmlToDocx()
                        document=new_parser.parse_html_string(html3)
                        document.save('report.docx')
                        #st.markdown(html1, unsafe_allow_html=True)
                        #components.html(html1, width=800, height=400,scrolling=True)
                        with open('report.docx','rb') as f:
                            st.download_button('Download Report',f,'report.docx')
                        df=pd.DataFrame()
                        del (df)
                
        else:
                if selected:
                        st.success('Are you sure you want to Delete Selected Record')
                        if st.button("Delete Selected Record",key='delcompdocacks'):
                            rid=selected['id'].iloc[0]
                            rdel=del_audit_sum(rid)
                else:
                        st.success('Select a Record to Delete ....')

def show_report():
    comp_name=st.session_state['Company']
    with report_container:
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        # ---- SIDEBAR ----
        with st.sidebar.markdown("# Select..."):
            sta_opts=st.radio('Reports',('Vouching, Verification, Review','Observations by Audit Checklist','Audit Report Summary'),key='ropcompr')
        
        audit_id=int(st.session_state['AuditID'])
        if sta_opts=='Vouching, Verification, Review': 
            st.info("**Audit Reports - Vouching, Verification & other Remarks**") 
            #with st.sidebar.markdown("# Reports"):
            optionsdf=get_dsname(int(st.session_state['AuditID']))
            #add blank row at begining of list
            optionsdf.loc[-1]=['---']
            optionsdf.index=optionsdf.index+1
            optionsdf.sort_index(inplace=True)
            ds=st.selectbox("Select Data Set ",optionsdf,key="1selectdsname")
                #ds_name=f"{st.session_state['Company']}_{(st.session_state['AuditID'])}_{d_sname}"
                #select dataset 
            
            if ds=="---":
                t="Select Data Set from above list"
                new_title=f'<p style="color: red;">{t}</p>'
                st.markdown(new_title, unsafe_allow_html=True)

            else:
                
                reports=st.radio("1",("Reports by Data Set ","Query List"),horizontal=True,key='strcrudasreport',label_visibility="hidden")
                #tab1,tab2,tab3 =st.tabs(["Reports by Data Set ","   Summary Report for Audit  ","Query List"])
                #with tab1:
                    #st.header(f"Audit Summary for {ds}")
                    #get queries for selected Dataset
                if reports=="Reports by Data Set ":
                    audit_id=int(st.session_state['AuditID'])
                    st.success(f"**Audit Summary for {ds}**")
                    #st.markdown("""---""")
                    #df=get_dataset(ds_name)
                    values=get_dataset_values(f"{st.session_state['AuditID']}_{ds}")
                    totalrecords= values['total_records']
                    totalaudit=values['total_audited']
                    #st.success(totalrecords)
                    #st.success(totalaudit)
                    #dsvalues=get_audit_values(int(st.session_state['AuditID']))
                    auditvalues=get_values_id_dsn(int(st.session_state['AuditID']),ds)
                    #st.success(dsvalues)
                    #st.success(auditvalues)
                    total_queries=auditvalues['total_queries_vv'] + auditvalues['total_queries_ar']
                    totalrisk=(auditvalues['auditrisk_total']*totalaudit)+auditvalues['auditrisk_total_AR']
                    auditrisk=auditvalues['auditrisk_audited']+auditvalues['auditrisk_pending_AR']
                    if totalrisk==0:
                        riskpercent='0.00 %'
                    else:
                        riskpercent='{percent:.2%}'.format(percent=auditrisk/totalrisk)
                    #show KPIs
                    col1,col2,col3= st.columns(3)
                    with col1:
                        new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Total Transactions:</p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                            #st.markdown('<style>p{color:red;}</style>"Total Transactions:"',unsafe_allow_html=True)
                        st.subheader(f"{totalrecords}")
                        new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Total Risk Score:</p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                        st.subheader(f"{totalrisk}")
                    with col2:
                        new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Transactions Audited:</p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                            #st.subheader("Transactions Audited:")
                        st.subheader(f"{totalaudit}")
                        new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Audited Risk Score:</p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                        st.subheader(f"{auditrisk}")
                    with col3:
                        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 20px;">Total Queries:</p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                            #st.subheader("Total Queries:")
                        new_title = f'<p style="font-family:sans-serif;font-weight: bold; color:Red; font-size: 27px;">{total_queries}</p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                        #st.subheader(f"{total_queries}")
                        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 20px;">Risk Percentage:</p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                        #st.subheader(f"{riskpercent}")
                        new_title = f'<p style="font-family:sans-serif;font-weight: bold; color:Red; font-size: 27px;">{riskpercent}</p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                    #st.markdown("""---""")
                    #charts for V&V
                    
                    st.success(f"**Queries Summary for {ds}**")
                    #get DF for vouching & verification
                    auditdf_1=get_Summary_audit_values(int(st.session_state['AuditID']),ds)
                    dict={'Criteria':'Analytical Review & Other','Total Queries':auditvalues['total_queries_ar']}
                    #st.write(dict)
                    #auditdf_1=auditdf_1.append(dict,ignore_index=True)
                    dict = {k:[v] for k,v in dict.items()}
                    dict_df=pd.DataFrame(dict)
                    #st.dataframe(dict_df)
                    auditdf_1=pd.concat([auditdf_1,dict_df],ignore_index=True)
                    col1, col2= st.columns(2)
                    with col1:
                        st.bar_chart(auditdf_1,x='Criteria',y='Total Queries')
                    with col2:
                        st.dataframe(auditdf_1)
                        #st.bar_chart(auditdf,x='Criteria',y='Total Queries')
                    st.success(f"**Risk Based Audit Summary for {ds}**")
                    auditdf_r=get_Summary_audit_values_riskweight(int(st.session_state['AuditID']),ds)
                    #st.dataframe(auditdf_r)
                    col1, col2= st.columns(2)
                    with col1:
                    
                        st.bar_chart(auditdf_r,x='Criteria',y='Total Risk Weight')
                    with col2:
                        st.dataframe(auditdf_r)
                    #by Risk Category
                    #auditdf=get_Summary_audit_values_riskcategory(int(st.session_state['AuditID']),ds)
                    
                    #col1, col2= st.columns(2)
                    #with col1:
                    
                        #st.bar_chart(auditdf,x=['Criteria','Risk_Category'],y='Total Risk Weight')
                    #with col2:
                        
                        #st.dataframe(auditdf)
                    #st.markdown("""---""")
               
                    
                else:
                    st.success(f"**View / Download - Query List for {ds}...**")
                    with st.expander("Voching & Verification Queries"):
                       
                        queriesdf=get_all_vv_quries(f"{st.session_state['AuditID']}_{ds}",ds,int(st.session_state['AuditID']))
                        #st.dataframe(queriesdf)
                        st.success(f"""Use Options to Group Report by Mutiple Levels.
                                        Right Click to Export Report to Excel""")
                        builder = GridOptionsBuilder.from_dataframe(queriesdf)
                        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                        #builder.configure_selection(selection_mode="single",use_checkbox=True)
                        jscode = JsCode("""
                        function(params) {
                            if (params.data.Status === 'Pending') {
                                return {
                                    'color': 'red',
                                    
                                }
                            } 
                            else {
                                return {
                                    'color': 'blue',
                                    
                                }
                            }
                        };
                        """)
                        
                        #builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                        builder.configure_default_column(groupable=True)
                        go = builder.build()
                        go['getRowStyle'] = jscode
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                        #AgGrid(queriesdf, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                                                                                        #'Risk_Category'])
                        AgGrid(queriesdf, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,allow_unsafe_jscode=True)
                                             
                        #csv=queries_df.to_csv().encode('utf-8')
                        #st.download_button("Download csv file",csv,f"{ds}.csv")
                #get AR queries lit
                    #st.success("Query List of Analytical Reviw & Other Remarks...")
                    with st.expander("Analytical Reviw & Other Remarks"):
                        queries_ar=get_all_ar_queries(ds)
                        
                        st.success(f"""Use Options to Group Report by Mutiple Levels.
                                            Right Click to Export Report to Excel""")
                        jscode = JsCode("""
                        function(params) {
                            if (params.data.status === 'Pending') {
                                return {
                                    'color': 'red',
                                    
                                }
                            } 
                            else {
                                return {
                                    'color': 'blue',
                                    
                                }
                            }
                        };
                        """)
                        builder = GridOptionsBuilder.from_dataframe(queries_ar)
                        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                            #builder.configure_selection(selection_mode="single",use_checkbox=True)
                        #builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                        builder.configure_default_column(groupable=True)
                        go = builder.build()
                        go['getRowStyle'] = jscode
                                    #uses the gridOptions dictionary to configure AgGrid behavior.
                        AgGrid(queries_ar, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,allow_unsafe_jscode=True)
                    
                    #generate report
                              
        elif sta_opts=='Audit Report Summary':
            show_Audit_summary()
        
        else:
            st.info("**Detailed Audit Observations**")
            
            df_allObservations=get_all_obser(audit_id)
            df_pendingObservations=get_pending_obser(audit_id)
            
            if not df_allObservations.empty:
                reports2=st.radio("1",("Observations Summary ","Observations List"),horizontal=True,key='obsvrb',label_visibility="hidden")
                if reports2=="Observations Summary ":
                    st.info("**Open Audit Observations**")
                    st.success("**Risk Based Audit Summary**")
                    #st.dataframe(df_allObservations)
                    #df_summ=pd.pivot_table(df_allObservations, values='Risk_Weight', index=['Audit_Area', 'Heading'],
                                #aggfunc=np.sum)
                    df_summ=df_pendingObservations.groupby('Audit_Area',as_index=False)['Risk_Weight'].sum()
                    
                    col1, col2= st.columns(2)
                    st.success("**Risk Based Audit Summary- for Audit Area**")
                    selected_area = st.selectbox("Choose Audit Area for Details", df_summ.Audit_Area, 0)
                    with col1:
                                st.bar_chart(df_summ,x='Audit_Area',y='Risk_Weight')
                                
                    with col2:
                                
                                st.dataframe(df_summ)
                                
                    c1,c2 =st.columns(2)
                    with c1:
                                #st.write(selected_area)
                                
                                df_head=df_pendingObservations.loc[df_pendingObservations['Audit_Area'] == selected_area]
                                
                                df_head=df_head.groupby('Heading',as_index=False)['Risk_Weight'].sum()
                                st.bar_chart(df_head,x='Heading',y='Risk_Weight')
                    with c2:
                        st.dataframe(df_head)
                else:              
                #with st.expander("View All Audit Observations"):
                    st.success("**View All Audit Observations**")
                    df_allObservations=get_all_obser(audit_id)
                    jscode = JsCode("""
                        function(params) {
                            if (params.data.Compliance_Status === 'Open') {
                                return {
                                    'color': 'red',
                                    
                                }
                            } 
                            else {
                                return {
                                    'color': 'blue',
                                    
                                }
                            }
                        };
                        """)
                    builder = GridOptionsBuilder.from_dataframe(df_allObservations)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=15)
                                    #builder.configure_selection(selection_mode="single",use_checkbox=True)
                    #builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                    builder.configure_default_column(groupable=True)
                    go = builder.build()
                    go['getRowStyle'] = jscode
                                            #uses the gridOptions dictionary to configure AgGrid behavior.
                    AgGrid(df_allObservations, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),key="sum14",columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,allow_unsafe_jscode=True)
                    st.success(f"""Use Options to Group Report by Mutiple Levels.
                                                    Right Click to Export Report to Excel""")
                    st.info("**Download Report in Word**")
                    dict_df=df_allObservations.groupby(['Audit_Area','Heading']).apply(lambda x: x.to_json(orient='records')).reset_index().rename(columns={0:'Zchild'})
                    # st.write(dict_df.to_dict('records'))
                    # st.dataframe(dict_df)
                    flist=df_allObservations.columns
                    headings=['Audit_Area','Heading','id']
                    flist=[item for item in flist if item not in headings]
                    #st.write(flist.to_list())
                    fileds=st.multiselect("Select Fields to be shown in Report", options=flist,key="fiedsinreport",default=flist)
                    
                    if fileds:
                        wordrep=st.button("Generate & Download Report",key="wrodrep")
                        if wordrep:
                            finallist=headings+fileds
                            df_allObservations=df_allObservations[finallist]
                            st.dataframe(df_allObservations)
                            #jsondf=df_allObservations.to_dict('records')
                            dict_df=df_allObservations.sort_values(by="id").groupby(['Audit_Area','Heading']).apply(lambda x: x.to_dict('records')).reset_index().rename(columns={0:'Zchild'})
                            #st.dataframe(dict_df)
                            df_allObservations=df_allObservations.groupby(['Audit_Area','Heading'])['id'].min().reset_index()
                            #st.dataframe(df_allObservations)
                            dict_df=dict_df.merge(df_allObservations[['Audit_Area','Heading','id']],how='left',left_on=['Audit_Area','Heading'],right_on=['Audit_Area','Heading'])
                            dict_df.sort_values(by="id",inplace=True)
                            #st.dataframe(dict_df)
                            jsondf=dict_df.to_dict('records')
                            # r = json.dumps(jsondf)
                            # loaded_r = json.loads(r)
                            # print(loaded_r)
                            # 2. Create a template Environment
                            env = Environment(loader=FileSystemLoader('templates'))
                            # 3. Load the template from the Environment
                            template = env.get_template('observations.html')
                            html2 = template.render(logo='logosmall1.png', jsondf = jsondf,companyname=st.session_state['Company'],auditname=st.session_state['Audit'])
                            #components.html(html2)
                            #docx to rport
                            document = Document()
                            new_parser = HtmlToDocx()
                            document=new_parser.parse_html_string(html2)
                            document.save('report.docx')
                            
                            #components.html(html1, width=800, height=400,scrolling=True)
                            with open('report.docx','rb') as f:
                                st.download_button('Download Report',f,'report.docx')
                    df_allObservations=pd.DataFrame()
                    dict_df=pd.DataFrame()
                    del (df_allObservations)
                    del (dict_df)
            else:
                st.info(" No Observations...")                                            
                

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
                userid = st.text_input (label="User Id", value="", placeholder="Enter your user ID",key="k5")
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
                if st.session_state['Role'] == "Auditee":
                    show_auditee()
                else:
                    show_report()    
            else:
                #st.title("Login")
                show_login_page()
        