# login - logout

import streamlit as st

def load_users():
        return st.secrets['users']

def login_user(users, username, password):
    if username in users and password == users[username]:
        st.session_state.user_state['username'] = username
        st.session_state.user_state['password'] = password
        st.session_state.user_state['logged_in'] = True
        return True
    else:
        return False

def logout_user():
    st.session_state.user_state = {
        'username': '',
        'password': '',
        'logged_in': False
    }
