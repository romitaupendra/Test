import streamlit as st
import pandas as pd
import hashlib
import sqlite3
import services
from google.oauth2 import service_account
from google.cloud import bigquery

# Security

# passlib,hashlib,bcrypt,scrypt


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False


# DB Management

conn = sqlite3.connect('data.db')
c = conn.cursor()


# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
    conn.commit()


def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data


def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data


def main():

    st.set_page_config(
        page_title="Analysis of Stock Market using Twitter Sentiments",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Analysis of Stock Market using Twitter Sentiments")

    # Sidebar
    
    menu = ["SignUp", "Login"]
    choice = st.sidebar.selectbox(label="Menu", options=menu, index=0, help="Main Navigation Menu")

    if choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')

        if st.button("Signup"):
            create_usertable()
            add_userdata(new_user, make_hashes(new_password))
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")

    elif choice == "Login":

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login/Logout"):

            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username, check_hashes(password, hashed_pswd))
            if result:

                
                st.header("Welcome, {}!!".format(username))

                st.header(":gear: Navigation")
                menu = [ "----Select----", "Twitter Analysis", "Stock Trends"]
                choice = st.selectbox(label="Menu", options=menu, index=0, help="Main Navigation Menu")

                if choice == "Twitter Analysis" :

                    
                    company = st.selectbox("Company",
                                  ['---- Select ---',
                                  'TSLA',
                                  'APPL',
                                  'FB',
                                  'MSFT','TWTR'],
                                  index = 0
                                  )

                elif choice == "Stock Trends" :

                     company = st.selectbox("Company",
                                  ['---- Select ---',
                                  'TSLA',
                                  'APPL',
                                  'FB',
                                  'MSFT','TWTR'],
                                  index = 0
                                  )
                       
            else:
                st.sidebar.error("Incorrect Username/Password")




# Create API client.
credentials = service_account.Credentials.from_service_account_info(
st.secrets["gcp_service_account"])
client = bigquery.Client(credentials=credentials)# Perform query.# Uses st.experimental_memo to only rerun when the query changes or after 10 min.@st.experimental_memo(ttl=600)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()# Convert to list of dicts. Required for st.experimental_memo to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows

rows = run_query("SELECT word FROM `bigquery-public-data.samples.shakespeare` LIMIT 10")# Print results.
st.write("Some wise words from Shakespeare:")
for row in rows:
    st.write("✍️ " + row['word'])


if __name__ == '__main__':
    main()


