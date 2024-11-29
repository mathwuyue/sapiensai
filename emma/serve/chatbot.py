import streamlit as st
import time

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Dummy user credentials (in real app, use secure database)
VALID_USERNAME = "user"
VALID_PASSWORD = "password"

def check_login(username, password):
    return username == VALID_USERNAME and password == VALID_PASSWORD

def login_page():
    st.title("Chat App Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.success("Login successful!")
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

def chat_page():
    st.title("Chat Room")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()
    
    # Chat interface
    for message in st.session_state.messages:
        st.text(f"{message['user']}: {message['text']}")
    
    # Message input
    message = st.text_input("Type your message")
    if st.button("Send"):
        if message:
            st.session_state.messages.append({
                "user": "You",
                "text": message
            })
            # Simulate response (replace with actual chat functionality)
            st.session_state.messages.append({
                "user": "Bot",
                "text": f"You said: {message}"
            })
            st.experimental_rerun()

def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()