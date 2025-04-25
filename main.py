import streamlit as st
import streamlit_authenticator as stauth
from dependencies import (
    add_username, 
    get_username_by_username, 
    get_all_usernames, 
    create_table, 
    update_password)
from time import sleep
import re

COOKIE_EXPIRY_DAYS = 30 

def main():
    # Attempt to read data; if it fails, create the table
    try:
        get_all_usernames()
    except:
        create_table()

    db_query = get_all_usernames()
    credentials = {'usernames': {}}
    for data in db_query:
        credentials['usernames'][data[1]] = {'name': data[0], 'mail': data[1], 'password': data[3]}

    authenticator = stauth.Authenticate(
        credentials,
        'random_cookie_name',
        'random_signature_key',
        COOKIE_EXPIRY_DAYS,
    )

    if 'clicked_register' not in st.session_state:
        st.session_state['clicked_register'] = False
    if 'clicked_forgot' not in st.session_state:
        st.session_state['clicked_forgot'] = False

    if st.session_state['clicked_register']:
        register_form()
    elif st.session_state['clicked_forgot']:
        forgot_password_form()
    else:
        login_form(authenticator=authenticator)

def login_form(authenticator):
    name, authentication_status, username = authenticator.login('Login')
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.title("Dashboard Area")
        st.write(f'*{name} is logged in!*')
    elif authentication_status is False:
        st.error('Incorrect username or password.')
        register_btn()
    elif authentication_status is None:
        st.warning("Please enter a username and password")
        register_btn()
    
def register_btn():
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Register"):
            st.session_state['clicked_register'] = True
            st.rerun()
    with col2:
        if st.button("Forgot Password"):
            st.session_state['clicked_forgot'] = True
            st.rerun()

def confirm_msg():
    hashed_password = stauth.Hasher([st.session_state.pswrd]).generate()
    valid_email, email_warning = validate_email(st.session_state.mail)
        
    if not st.session_state.name:
        st.warning("Name is empty")
        sleep(3)
    elif not st.session_state.username:
        st.warning("Username is empty")
        sleep(3)
    elif get_username_by_username(st.session_state.username):
        st.warning("Username already exists")
        sleep(3)
    elif not valid_email:
        st.warning(email_warning)
        sleep(3)
    elif not st.session_state.pswrd:
        st.warning("Password is empty")
        sleep(3)
    elif st.session_state.pswrd != st.session_state.confirm_pswrd:
        st.warning("Passwords do not match")
        sleep(3)
    else:
        add_username(st.session_state.name, st.session_state.username, st.session_state.mail, hashed_password[0])
        st.success("Registration successful")
        sleep(3)

def register_form():
    with st.form(key='registration_form', clear_on_submit=True):
        name = st.text_input("Name", key="name")
        username = st.text_input("Username", key="username")
        mail = st.text_input("Email", key="mail")
        password = st.text_input("Password", key="pswrd", type="password")
        confirm_password = st.text_input("Confirm Password", key="confirm_pswrd", type="password")
        submit = st.form_submit_button("Save", on_click=confirm_msg)

    clicked_login = st.button("Go to login")
    if clicked_login:
        st.session_state['clicked_register'] = False
        st.rerun()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Please enter a valid email address"
    return True, ""

def forgot_password_form():
    with st.form("reset_password_form"):
        username = st.text_input("Enter your username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Reset Password")
        if submitted:
            if new_password != confirm_password:
                st.warning("Passwords do not match")
            elif not get_username_by_username(username):
                st.warning("Username not found")
            else:
                hashed_pw = stauth.Hasher([new_password]).generate()[0]
                update_password(username, hashed_pw)
                st.success("Password updated successfully")
                sleep(3)
                st.session_state['clicked_forgot'] = False
                st.rerun()

    if st.button("Back to login"):
        st.session_state['clicked_forgot'] = False
        st.rerun()

if __name__ == "__main__":
    main()
