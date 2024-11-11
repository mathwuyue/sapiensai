import streamlit as st
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import datetime
from db import get_user, add_user
import os
import dotenv

dotenv.load_dotenv()
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')


def create_jwt_token(payload):
    exp_time = datetime.datetime.now() + datetime.timedelta(days=3)
    payload['exp'] = exp_time
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token):
    try:
        # Decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        st.session_state["username"] = decoded_token["username"]
        return True  # Token is valid
    except ExpiredSignatureError:
        print('expired')
        return False, "Token expired"  # Token has expired
    except InvalidTokenError:
        print('invalid')
        return False  # Token is invalid or expired


def login_page():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            user = get_user(username)
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                token = create_jwt_token({"username": username})
                st.session_state["token"] = token
                st.session_state["username"] = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with col2:
        if st.button("Register"):
            if username and password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                try:
                    add_user(username, hashed_password)
                    st.success("User registered successfully!")
                except:
                    st.error("Username already exists")
            else:
                st.error("Please enter both username and password")