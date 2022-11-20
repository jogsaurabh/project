import streamlit as st
import pandas as pd
import pickle
import numpy as np
import os.path
from datetime import date,timedelta
from functions import update_password,get_active_users_created_by_me,get_comp_created_by_user,get_user_rights,get_active_users,get_audit,get_comp_by_user,creat_audit
from functions import get_user_rights_created_byMe,get_linked_obsr_ar,create_user,check_login,assign_user_rights,create_company,get_company_names
#import sqlite3
from PIL import Image
image = Image.open('autoaudit_t.png')
st.set_page_config(page_title="AutoAudit", page_icon=":white_check_mark:", layout="wide")
#st.title(":white_check_mark: AutoAudit")
st.image(image,width=250)
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
    
    
    #st.write(comp_name)
    #st.info(reply)
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
                userid = st.text_input (label="", value="", placeholder="Enter user ID",key="ck5l")
                password = "Pass123"
                designation = st.text_input (label="", value="", placeholder="Enter Designation",key="ck3l")
                displayname = st.text_input (label="", value="", placeholder="Enter Display Name",key="ck4l")
                
                exp_date=st.date_input("Set Licence Expiry Date:-",value=exp_date,key="exp_date1")
                submit_userc =st.form_submit_button("Submit")
                if submit_userc:
                    # create User with above
                    createuser=create_user(displayname,userid,password,designation)
                    st.info(createuser)
                    # add company- Test
                    ceratcomp=create_company("Test", "Test","Test",0,"test")
                    st.info(ceratcomp)
                    # add Audit- Test
                    cretaeaudit=creat_audit("Test","Test", "Test","Test")
                    st.info(cretaeaudit)
                    # add Role of Manger for this user
                    userright=assign_user_rights(userid,"Test","Manager")
                    st.info(userright)
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
            st.info(f"Licence Expiry Date is :- {exp_date}")
            if exp_date> date.today():
                    st.info("Licenec is Valid")
            else:
                st.info("Licenec has Expired")
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
            st.info ("Expiry Date is not Set")
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
            master_options = st.radio("Select",('Create Company','Create User','Assign User Rights','Add New Audit'))
        #st.sidebar.button("Assign User Rights",key="ba1",on_click=assign_user_rights_show)
        
        if master_options=="Create Company":
            #st.success("""For First Time Login- """)
            with st.form("Create New Company",clear_on_submit=True):
                        st.title("Create New Company")
                        comp_name = st.text_input (label="",value="",placeholder="Enter company Name",key="comp_name1")
                        com_address = st.text_input (label="", value="",placeholder="Enter company Address",key="com_address1")
                        com_email = st.text_input (label="", value="", placeholder="Enter email",key="com_email1")
                        #com_mobile = st.number_input("Mobile No",min_value=1111111111,max_value=9999999999,key="com_mobile1")
                        #com_person = st.text_input (label="", value="", placeholder="Enter Contact Person",key="com_person1")
                        
                        #st.write(comp_name)
                        #st.button("Submit",on_click=create_company, args= (comp_name, com_address,com_email,com_mobile,com_person))
                        #st.button("Submit",key="sub11"):
                        if st.form_submit_button("Submit"):
                            message_verify=create_company(comp_name, com_address,com_email,1234567890,'com_person')
                            st.info(message_verify)
        #elif master_options=="Home":
            #st.title("Welcome to AutoAudit")
        elif master_options=="Create User":
            with st.form("New User",clear_on_submit=True):
                
                st.title("Create User")
                userid = st.text_input (label="", value="", placeholder="Enter user ID",key="ck5")
                password = st.text_input (label="", value="",placeholder="Set password", type="password",key="ck6")
                designation = st.text_input (label="", value="", placeholder="Enter Designation",key="ck3")
                displayname = st.text_input (label="", value="", placeholder="Enter Display Name",key="ck4")
                submit_userc =st.form_submit_button("Submit")
                if submit_userc:
                    createuser=create_user(displayname,userid,password,designation)
                    st.info(createuser)
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
                    st.info(f"Only Users with Manager Role can Assign Rights...\n You are not Manager for any Company.")
                else:
                
                #if company_list.empty:
                        #st.info('You can assign rights for Company created by you.')
                        
                #else:
                        with st.form("Assign User Rights",clear_on_submit=True):
                            
                            st.title("Assign User Rights")
                            
                            company_name=st.selectbox("Select Company",companies,key="company_name")
                                    #users=get_unassigned_users(comapname)
                            user=st.selectbox("Select User",users,key="usersb")
                            role=st.selectbox("Select Role",("Manager","Auditor","Auditee"),key="usersb1")
                                               
                            submitb = st.form_submit_button("Submit")
                            if submitb:
                                message_verify=assign_user_rights(user,company_name,role)
                                st.info(message_verify)
                                
            else:
                st.info("You have not created any users....you can only assign rights to User Created by you")
                                    #assign_user_rights(user,company_name,role)
            #show user rights
            showrights=st.button("Show User Rights",key="seur")
            if showrights:
                
                userrights_df=get_user_rights_created_byMe()
                st.title("Existing User Rights")
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
                st.info(f"Only Users with Manager Role can add Audit...\n You are not Manager for any Company.")
            else:
                with st.form("Add New Audit",clear_on_submit=True):
                        st.title("Add New Audit")
                        Audit_Name = st.text_input (label="Enter Audit Name",value="",placeholder="-Max lenght 6",key="Audit_Name1")
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
                                    st.info(message_verify)
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
        st.info("Invalid user name or password")

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
                #st.write(audit.value[1])
                if audit:
                    st.button ("Login", on_click=check_login, args= (userName, password,compname,role,audit))
                    #check if licence expired for this 
                    
                elif userName=="admin" and password=="AutoAdmin":
                    st.button ("Login", on_click=check_login, args= (userName, password,compname,role,audit))
                
                    
        with tab2:
            with st.form("New User",clear_on_submit=True):
                
                st.title("Change Password")
                userid = st.text_input (label="", value="", placeholder="Enter your user ID",key="k5")
                password = st.text_input (label="", value="",placeholder="Enter Current Password", type="password",key="k6")
                new_pass = st.text_input (label="", value="", placeholder="Enter New Password", type="password",key="k3")
                renew_pass = st.text_input (label="", value="", placeholder="ReEnter New Password", type="password",key="k4")
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
            if st.session_state['Role'] == "Auditee" or st.session_state['Role'] == "Auditor":
                show_auditee()
            elif st.session_state['Role'] =="admin":
                show_admin()
            else:
                show_main_page()   
        else:
            show_login_page()
                       
                