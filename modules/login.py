# login - logout

import streamlit as st
import json

def load_users(file_path='users.json'):
    with open(file_path, 'r') as file:
        return json.load(file)

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
