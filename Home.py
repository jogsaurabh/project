import streamlit as st
import pandas as pd
import pickle
import numpy as np
import os.path
from datetime import date,timedelta
from functions import get_all_tasks,get_pending_obser,get_Summary_audit_values_comp,get_audit_values,update_password,get_active_users_created_by_me,get_comp_created_by_user,get_user_rights,get_active_users,get_audit,get_comp_by_user,creat_audit
from functions import get_overdue_tasks,get_ar_summary,get_Summary_audit_values_riskweight_comp,get_user_rights_created_byMe,get_linked_obsr_ar,create_user,check_login,assign_user_rights,create_company,get_company_names
#import sqlite3
from PIL import Image
st.set_page_config(page_title="AutoAudit", page_icon=":white_check_mark:", layout="wide")
url="https://acecom22-my.sharepoint.com/:w:/g/personal/saurabhjog_acecomskills_in/ESLKUvAGIMJJontdPiuXk5YBTxjbcYnCkilrcBJ3oHy0ww?e=ZS4i6g"
image = Image.open('autoaudit_t.png')

#st.title(":white_check_mark: AutoAudit")
headercol1,headercol2,co3=st.columns([8,2,1])
with headercol1 : st.image(image,width=200,)
with co3: 
    link =f'[Help]({url})'
    st.markdown(link, unsafe_allow_html=True)
    #st.button('Open link', on_click=open_page(url))
    #st.markdown(f'''<a href={url}><button style="padding: 5px 8px; border-radius: 5px; border: 1px solid red;">Help</button></a>''',
   #             unsafe_allow_html=True)

st.markdown("""---""")
#get list of companies

#st.write(company_list.__str__())
headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
createcompanysection=st.container()
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
 
#def create_company_show():
    #with createcompanysection:
        #st.title("Create New Company")

def show_dashboard():
    #st.subheader(f"Audit Dashboard")
    st.markdown(f'<h4 style="color:DarkBlue;font-size:32px;">{"Audit Dashboard"}</h4>', unsafe_allow_html=True)
    with st.expander("Vouching, Verification & Analytical Remarks",expanded=True):
        #st.success(f"Audit Summary for- {st.session_state['Company']} - {st.session_state['Audit']}")
        auditvalues=get_audit_values(int(st.session_state['AuditID']))
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
        #st.markdown("---")
        st.write("**Vouching & Verification - Queries Summary by Dataset**")
        auditdf=get_Summary_audit_values_comp(int(st.session_state['AuditID']))
        
        if not auditdf.empty:
            col1, col2= st.columns(2)
            with col1:
                st.success("Vouching & Verification- Count")
                st.bar_chart(auditdf,x='Data Set Name',y='Total Queries')
                
            with col2:
                st.success("Vouching & Verification- Risk Weight")
                auditdf=get_Summary_audit_values_riskweight_comp(int(st.session_state['AuditID']))
                st.bar_chart(auditdf,x='Data Set Name',y='Total Risk Weight')
        else: st.write("Report is empty")
        #AR & Other Remarks
        st.write("**Analytical & Other Remarks Summary by Dataset**")
        #get DF for vouching & verification
        ardf=get_ar_summary()
        if not ardf.empty:
            col1, col2= st.columns(2)
            with col1:
                st.success("Analytical & Other Remarks- Count")
                st.bar_chart(ardf,x='DataSet Name',y='Total Remarks')
            with col2:
                st.success("Analytical & Other Remarks- Risk Weight")
                st.bar_chart(ardf,x='DataSet Name',y='Risk Weight')
        else: st.write("Report is empty")
    with st.expander("Pending Audit Observations as per Checklist",expanded=True):
        df_pendingObservations=get_pending_obser(int(st.session_state['AuditID']))
        if not df_pendingObservations.empty:
            df_summ=df_pendingObservations.groupby('Audit_Area',as_index=False).agg(Pending_Observations=('Criteria','count'))
            #['Criteria'].count()
            col1, col2= st.columns(2)
            with col1:
                st.success("Number of Pending Observations")
                st.bar_chart(df_summ,x='Audit_Area',y='Pending_Observations')
                        
            with col2:
                df_summ=df_pendingObservations.groupby('Audit_Area',as_index=False)['Risk_Weight'].sum()
                st.success("Risk Weight for Pending Observations")
                st.bar_chart(df_summ,x='Audit_Area',y='Risk_Weight')
        else: st.write("Report is empty")
    with st.expander("Audit Tasks Stautus",expanded=True):
        dfpending=get_all_tasks(int(st.session_state['AuditID']))
                
        if not dfpending.empty:
            
            mask = dfpending['Status'] == 'Pending'
            df_summ=get_overdue_tasks(int(st.session_state['AuditID']))
            totaltask=len(dfpending)
            dfpending=dfpending[mask]
            pendintask=len(dfpending)
            overduetask=len(df_summ)
            #show numbers
            c1,c2,c3 = st.columns(3)
            with c1:
                new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Total Tasks:</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                    #st.markdown('<style>p{color:red;}</style>"Total Transactions:"',unsafe_allow_html=True)
                new_title = f'<p style="font-family:sans-serif; color:Blue; font-size: 27px;">{totaltask}</p>'
                st.markdown(new_title, unsafe_allow_html=True)
            
            with c2:
                new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Pending Tasks:</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                    #st.subheader("Transactions Audited:")
                new_title = f'<p style="font-family:sans-serif;color:Red; font-size: 27px;">{pendintask}</p>'
                st.markdown(new_title, unsafe_allow_html=True)
            with c3:
                new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Overdue Tasks:</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                    #st.subheader("Transactions Audited:")
                new_title = f'<p style="font-family:sans-serif;color:Red; font-size: 27px;">{overduetask}</p>'
                st.markdown(new_title, unsafe_allow_html=True)
            #show charts
            col1, col2= st.columns(2)
            with col1:
                
                dfpending=dfpending[mask].groupby('Person',as_index=False)['Task'].count()
                st.success("Pending Tasks by Person")
                st.bar_chart(dfpending,x='Person',y='Task')
                        
            with col2:
                
                df_summ=df_summ.groupby('Person',as_index=False)['Task'].count()
                st.success("Overdue Tasks by Person")
                st.bar_chart(df_summ,x='Person',y='Task')
        else: st.write("Report is empty")
    df_summ=pd.DataFrame()
    del[[auditdf,ardf,df_pendingObservations,df_summ,dfpending]]
    auditdf=pd.DataFrame()
    ardf=pd.DataFrame()
    df_pendingObservations=pd.DataFrame()
    
    dfpending=pd.DataFrame()
    
def show_admin():
    st.title("Admin") 
    st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
    
    with st.sidebar.markdown("# Masters "):
        master_options = st.radio("Select",('Create User','Update Licence'))
    exp_date=date.today()+timedelta(days=365)
    if  master_options=="Create User":
        with st.form("New User-Manger",clear_on_submit=True):
                
                st.title("Create User-Manager for New Licence")
                userid = st.text_input (label="User Id", value="manager", placeholder="Enter user ID",key="ck5l")
                password = "Pass123"
                designation = st.text_input (label="Designation", value="", placeholder="Enter Designation",key="ck3l")
                displayname = st.text_input (label="Display Name", value="", placeholder="Enter Display Name",key="ck4l")
                
                exp_date=st.date_input("Set Licence Expiry Date:-",value=exp_date,key="exp_date1")
                submit_userc =st.form_submit_button("Submit")
                if submit_userc:
                    # create User with above
                    createuser=create_user(displayname,userid,password,designation)
                    st.success(createuser)
                    # add company- Test
                    ceratcomp=create_company("Test", "Test","Test",0,"test")
                    st.success(ceratcomp)
                    # add Audit- Test
                    cretaeaudit=creat_audit("Test","Test", "Test","Test")
                    st.success(cretaeaudit)
                    # add Role of Manger for this user
                    userright=assign_user_rights(userid,"Test","Manager")
                    st.success(userright)
                    #set Licence Expiry date
                    with open('file.pkl', 'wb') as file:
      
                        # A new file will be created
                        pickle.dump(exp_date, file)
                    
                    st.success(f"Licence Expiry Date Set to :- {exp_date}")
                                 
    else:
        #"Set Licence Expiry"     
        if os.path.isfile('file.pkl'):
            
            with open('file.pkl', 'rb') as file:
                        # Call load method to deserialze
                exp_date = pickle.load(file)     
            st.success(f"Licence Expiry Date is :- {exp_date}")
            if exp_date> date.today():
                    st.success("Licenec is Valid")
            else:
                st.success("Licenec has Expired")
            exp_date=st.date_input("Set Licence Expiry Date:-",value=exp_date,key="exp_date")

            setexpdt=st.button("Set Licence Expiry Date",key="setlexb")
            if setexpdt:
                
                with open('file.pkl', 'wb') as file:
            
                    # A new file will be created
                    pickle.dump(exp_date, file)
                with open('file.pkl', 'rb') as file:                
                    # Call load method to deserialze
                    exp_date = pickle.load(file)
                st.success(f"Licence Expiry Date Set to :- {exp_date}")
                
        else:
            st.success ("Expiry Date is not Set")
            exp_date=st.date_input("Set Licence Expiry Date:-",value=exp_date,key="exp_date2")

            setexpdt=st.button("Set Licence Expiry Date",key="setlexb2")
            if setexpdt:
                
                with open('file.pkl', 'wb') as file:
            
                    # A new file will be created
                    pickle.dump(exp_date, file)
                with open('file.pkl', 'rb') as file:                
                    # Call load method to deserialze
                    exp_date = pickle.load(file)
                st.success(f"Licence Expiry Date Set to :- {exp_date}")
        # Open & Read  the file in binary mode
def show_auditer():
    st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
    show_dashboard()
def assign_user_rights_show():
    st.title("Assign User")
    
def show_main_page():
    company_list=get_company_names()
    with mainSection:
        #st.success(f"{st.session_state['Company']}_{st.session_state['AuditID']}_filename")
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        #st.write(f"Audit Id:-{st.session_state['AuditID']}")
        with st.sidebar.markdown("# Masters "):
            master_options = st.radio("Select",('DashBoard','Create Company','Create User','Assign User Rights','Add New Audit'))
        #st.sidebar.button("Assign User Rights",key="ba1",on_click=assign_user_rights_show)
        if master_options=="DashBoard":
            show_dashboard()
        elif master_options=="Create Company":
            #st.success("""For First Time Login- """)
            with st.form("Create New Company",clear_on_submit=True):
                        #st.subheader("Create New Company")
                        st.markdown(f'<h5 style="color:DarkBlue;font-size:30px;">{"Create New Company"}</h5>', unsafe_allow_html=True)
                        comp_name = st.text_input (label="Enter Company Name*",value="",placeholder="Company Name Required",key="comp_name1",)
                        com_address = st.text_input (label="Enter Company Address", value="",placeholder="Company Address",key="com_address1")
                        com_email = st.text_input (label="Enter email", value="", placeholder="email",key="com_email1")
                        #com_mobile = st.number_input("Mobile No",min_value=1111111111,max_value=9999999999,key="com_mobile1")
                        #com_person = st.text_input (label="", value="", placeholder="Enter Contact Person",key="com_person1")
                        
                        #st.write(comp_name)
                        #st.button("Submit",on_click=create_company, args= (comp_name, com_address,com_email,com_mobile,com_person))
                        #st.button("Submit",key="sub11"):
                        if st.form_submit_button("Submit"):
                            if comp_name:
                                message_verify=create_company(comp_name, com_address,com_email,1234567890,'com_person')
                                st.success(message_verify)
                            else:
                                st.error("Enter Company Name")
        #elif master_options=="Home":
            #st.title("Welcome to AutoAudit")
        elif master_options=="Create User":
            with st.form("New User",clear_on_submit=True):
                
                #st.subheader("Create User")
                st.markdown(f'<h5 style="color:DarkBlue;font-size:30px;">{"Create User"}</h5>', unsafe_allow_html=True)
                userid = st.text_input (label="Enter user ID*", value="", placeholder="User ID Must be UNIQUE",key="ck5")
                password = st.text_input (label="Set password*", value="",placeholder="password Required", type="password",key="ck6")
                designation = st.text_input (label="Enter Designation", value="", placeholder="Designation",key="ck3")
                #displayname = st.text_input (label="", value="", placeholder="Enter Display Name",key="ck4")
                submit_userc =st.form_submit_button("Submit")
                if submit_userc:
                    createuser=create_user(userid,userid,password,designation)
                    st.success(createuser)
                #st.form_submit_button("Submit",on_click=Register_Clicked, args= (userid, password,designation,displayname))
                #st.button ("Register", on_click=Register_Clicked, args= (userid, password,designation,displayname))
            
                            
        elif master_options=="Assign User Rights":
            
            users=get_active_users_created_by_me()
            #if users created by me then only do following
            if not users.empty:
                if st.session_state['User']=='admin':
                    companies=get_company_names()
                else:                
                    companies=get_comp_by_user()
                    #com1=get_comp_created_by_user()
                    #com1.rename(columns={"Name":""})
                    #st.dataframe(com1)
                    #st.dataframe(companies)
                    #companies.append(com1, ignore_index = True)
                if companies.empty:
                    st.success(f"Only Users with Manager Role can Assign Rights...\n You are not Manager for any Company.")
                else:
                
                #if company_list.empty:
                        #st.success('You can assign rights for Company created by you.')
                        
                #else:
                        with st.form("Assign User Rights",clear_on_submit=True):
                            
                            #st.subheader("Assign User Rights")
                            st.markdown(f'<h5 style="color:DarkBlue;font-size:30px;">{"Assign User Rights"}</h5>', unsafe_allow_html=True)
                
                            company_name=st.selectbox("Select Company",companies,key="company_name")
                                    #users=get_unassigned_users(comapname)
                            user=st.selectbox("Select User",users,key="usersb")
                            role=st.selectbox("Select Role",("Manager","Auditor","Auditee"),key="usersb1")
                                               
                            submitb = st.form_submit_button("Submit")
                            if submitb:
                                message_verify=assign_user_rights(user,company_name,role)
                                st.success(message_verify)
                                
            else:
                st.success("You have not created any users....you can only assign rights to User Created by you")
                                    #assign_user_rights(user,company_name,role)
            #show user rights
            showrights=st.button("Show User Rights",key="seur")
            if showrights:
                
                userrights_df=get_user_rights_created_byMe()
                st.subheader("Existing User Rights")
                st.dataframe(userrights_df)
                
                del(userrights_df)
                userrights_df=pd.DataFrame()
        #add new Audit
        else:
            if st.session_state['User']=='admin':
                companies=get_company_names()
            else:
                
                companies=get_comp_by_user()
            if companies.empty:
                st.success(f"Only Users with Manager Role can add Audit...\n You are not Manager for any Company.")
            else:
                with st.form("Add New Audit",clear_on_submit=True):
                        #st.subheader("Add New Audit")
                        st.markdown(f'<h5 style="color:DarkBlue;font-size:30px;">{"Add New Audit"}</h5>', unsafe_allow_html=True)
                
                        Audit_Name = st.text_input (label="Enter Audit Name*",value="",placeholder="Rquired & Must be Unique",key="Audit_Name1")
                        #companies=get_comp_by_user()
                        Company_name = st.selectbox("Select Company",companies,key="Company_name1")
                        Period = st.text_input (label="Enter Period", value="", placeholder="Audit Period",key="Period1")
                        Remarks = st.text_input (label="Enter Remarks", value="", placeholder="Remarks",key="Remarks1")
                        #st.write(comp_name)
                        
                        #st.button("Submit",on_click=create_company, args= (comp_name, com_address,com_email,com_mobile,com_person))
                        #st.button("Submit",key="sub11"):
                        
                        if st.form_submit_button("Submit"):
                            if Audit_Name:
                                    message_verify=creat_audit(Audit_Name,Company_name,Period,Remarks)
                                    st.success(message_verify)
                            else:
                                st.success("Audit Name is Required")
    
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
                #st.write(audit.value[1])
                if audit:
                    st.button ("Login", on_click=check_login, args= (userName, password,compname,role,audit))
                    #check if licence expired for this 
                    
                elif userName=="admin" and password=="AutoAdmin":
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
    st.warning(f"You Have Logged In as {st.session_state['Role']}...You have no access to this Menu")


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
                
    else:
        if st.session_state['loggedIn']:
            show_logout_page()   
            if st.session_state['Role'] == "Auditee":
                show_auditee()
            elif st.session_state['Role'] == "Auditor":
                show_auditer()
            elif st.session_state['Role'] =="admin":
                show_admin()
            else:
                show_main_page()   
        else:
            show_login_page()
                       
                