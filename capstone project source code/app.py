import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import sqlite3
from streamlit_option_menu import option_menu
import hashlib
from datetime import datetime
import re

# Set up SQLite for user authentication
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

def men_css():
 st.markdown("""
    <style>
        .st-emotion-cache-1vt4y43 {
            background-color: #ff6347 ;
        }
        .st-emotion-cache-1whx7iy.e1nzilvr4 p {
            font-size: 18px;
            font-weight: bold;
            color: #000000;  /* Black label text */
        }

        .stTextInput label, .stDateInput label, .stButton button {
            font-size: 18px;
            font-weight: bold;
            color: black;
        }
        .stTextInput input, .stDateInput input {
            background-color: white;
            color: black;
            border-radius: 8px;
            border: 1px solid black;
            padding: 10px;
        }
        
        .stAlert p {
            font-size: 16px;
            color: #ffffff;
        }
        .stAlert div[role="alert"] {
            background-color: #444444;
            border-radius: 8px;
            padding: 10px;
        }
        .stHeader h2 {
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 20px;
        }
        [data-testid="stSelectbox"] {
    background-color:#50C878 ;
    color: white;
    border: 1px solid #007BA7;
    padding: 10px;
    border-radius: 5px;
    font-family: 'Arial', sans-serif;
    font-size: 16px;
}

[data-testid="stSelectbox"] option {
    background-color: white;
    color: black;
}        
         div[data-testid="stButton"] button {
            background-color: #ff6347;
            color: white;
            border-radius: 8px;
            border: none;
            font-size: 18px;
            padding: 10px 20px;
        }
        .stAlert div[role="alert"][class*="success"] {
            background-color: #28a745;  /* Green background for success */
            color: white;
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
        }

        /* Custom style for student details */
          
    </style>
    """, unsafe_allow_html=True)

def load_css():
    CUSTOM_CSS = """
    [data-testid="stSidebar"] {
        background-color: #50C878; /* Set the sidebar background to blue */
        color: white;
        padding: 20px;
    }

    [data-testid="stSidebar"] .css-1d391kg {
        background-color: rgba(0, 0, 0, 0.5);  /* Adjust opacity */
    }

    [data-testid="stAppViewContainer"] {
        background-image: url("https://i.postimg.cc/D0Q5xRzj/background.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        background-attachment: fixed;
    }
    [data-testid="stAppViewContainer"]::before {
        content: "";
        display: block;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0);
        z-index: 0;
    }

    
    [data-testid="stMarkdownContainer"] {
        color: white;
    }
    [data-testid="stTable"] {
        color: white;
    }
     
    
    .st-emotion-cache-187vdiz p {
        font-size: 18px;  /* Increase font size for radio buttons */
        font-weight: bold;
    }
     .profile-pic {
        display: block;
        margin-left: auto;
        margin-right: auto;
        border-radius: 50%;
        width: 150px;
        height: 150px;
    }
    .profile-details {
        text-align: center;
        color: white;
    }
    [data-testid="stMarkdownContainer"] {
    color: black;
}
    
    [data-testid="stHeader"] {
        background-color: #50C878;
        padding: 20px;
        border-bottom: 2px solid #ff6347;
        text-align: center;
        color: white ;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        font-size: 24px ;
    }
    [data-testid="stHeader"]::after {
        content: "Weather Forecast App";
        position: absolute;
        left: 40%;
        transform: translateX(-50%);
        top: 50%;
        transform: translateY(-50%);
    }
    
    """
    st.markdown(f'<style>{CUSTOM_CSS}</style>', unsafe_allow_html=True)

# Function to create users table if it doesn't exist
def create_users_table():
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                mobile_number TEXT,
                email TEXT,
                occupation TEXT,
                dob DATE,
                username TEXT UNIQUE,
                password TEXT)''')
    conn.commit()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to add new user
def add_user(first_name, last_name, mobile_number, email, occupation, dob, username, password):
    c.execute('''INSERT INTO users (first_name, last_name, mobile_number, email, occupation, dob, username, password)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (first_name, last_name, mobile_number, email, occupation, dob, username, hash_password(password)))
    conn.commit()

# Function to authenticate login
def authenticate_user(username, password):
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, hash_password(password)))
    return c.fetchone()

# Function to get weather data from OpenWeatherMap API
def get_weather_data(city, api_key):
    base_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(base_url)
    return response.json()

# Function to extract and process weather data
def process_weather_data(data):
    forecast_list = data['list']
    dates = []
    temps = []
    descriptions = []
    
    for forecast in forecast_list:
        date = forecast['dt_txt']
        temp = forecast['main']['temp']
        description = forecast['weather'][0]['description']
        dates.append(date)
        temps.append(temp)
        descriptions.append(description)

    weather_df = pd.DataFrame({
        'Date': pd.to_datetime(dates),
        'Temperature (°C)': temps,
        'Description': descriptions,
    })

    return weather_df
def reset_login_form():
    st.session_state['username'] = ""
    st.session_state['password'] = ""

def username_exists(username):
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    return c.fetchone() is not None
# Function to display sign-up page
def sign_up_page():
    load_css()
    men_css()
    st.title("Sign Up")

    # Input fields for user data
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    mobile_number = st.text_input("Mobile Number")
    email = st.text_input("Email")
    occupation = st.text_input("Occupation")
    
    min_date = datetime(1900, 1, 1)
    max_date = datetime.now()
    date_of_birth = st.date_input("Date of Birth", min_value=min_date, max_value=max_date)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    # Function to validate email and phone number
    def validate_email(email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email)

    def validate_mobile_number(mobile):
        mobile_regex = r'^[0-9]{10}$'  # Check if the mobile number is exactly 10 digits
        return re.match(mobile_regex, mobile)

    if st.button("Sign Up"):
        # Check if all fields are filled
        if not first_name or not last_name or not mobile_number or not email or not occupation or not username or not password or not confirm_password:
            st.error("All fields are required. Please fill in all the details.")
        
        # Check if email is valid
        elif not validate_email(email):
            st.error("Invalid email address. Please enter a valid email.")
        
        # Check if mobile number is valid
        elif not validate_mobile_number(mobile_number):
            st.error("Invalid mobile number. It should be exactly 10 digits.")
        
        # Check if passwords match
        elif password != confirm_password:
            st.error("Passwords do not match. Please make sure both passwords are the same.")
        
        # Check if username already exists
        elif username_exists(username):
            st.error("Username already exists. Please choose a different username.")
        
        else:
            # Add user to the database
            add_user(first_name, last_name, mobile_number, email, occupation, date_of_birth, username, password)
            st.success("Account created successfully. You can now log in.")
            reset_login_form()
            st.session_state.show_signup = False
            st.rerun()
    if st.button("Back"):
        st.session_state.logged_in = False
        st.session_state.show_signup = False
        st.rerun()

def navigation_menu():
    load_css()
    men_css()
    with st.sidebar:
        selected = option_menu(
            menu_title=None,
            options=["Home","Weather Forecast", "Compare Cities"],
            icons=["house","cloud", "kanban"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical"
        )
    return selected
# Function to display login page
def login_page():
    load_css()
    men_css()
    
    st.markdown("<h1 style='text-align: center;'>Login</h1>", unsafe_allow_html=True)

    # Initialize session state for username and password
    if 'username' not in st.session_state:
        st.session_state['username'] = ""
    if 'password' not in st.session_state:
        st.session_state['password'] = ""

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form(key='login_form'):
                username = st.text_input('Username', key='username')
                password = st.text_input('Password', type='password', key='password')

                col_login, col_signup = st.columns(2)

                with col_login:
                    submit_button = st.form_submit_button(label='Login')
                with col_signup:
                    signup_button = st.form_submit_button(label='Sign Up')

                if submit_button:
                    if username and password:
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.show_signup = False
                        else:
                            st.error('Invalid username or password.')
                    else:
                        st.error('Please enter both username and password.')

                if signup_button:
                    st.session_state.show_signup = True
                    st.session_state.logged_in = False
                    st.rerun()

def home_page():
    st.title("Welcome to the Weather Forecast App!")
    st.markdown("""
        <div style='color:black;'>
            <h2 style='margin-top: 20px;'>About This Project:</h2>
            <p style='font-size: 16px;'>
                This application allows users to check weather forecasts for different cities and compare the weather trends between multiple locations.
            </p>
            <h4 style='margin-top: 10px;'>Key Features:</h4>
            <ul style='font-size: 16px; line-height: 1.6;'>
                <li><b>Weather Forecast:</b> Get a 5-day weather forecast for any city worldwide.</li>
                <li><b>Compare Cities:</b> Compare the weather forecasts of two cities side by side.</li>
                <li><b>Real-Time Data:</b> All data is fetched in real-time using the OpenWeatherMap API.</li>
            </ul>
            <h4 style='margin-top: 20px;'>Get Started:</h4>
            <p style='font-size: 16px;'>
                Use the sidebar to navigate between the features and explore weather data for cities across the globe.
            </p>
        </div>
    """, unsafe_allow_html=True)
# Function to display weather forecast app
def main_app():
    
    load_css()
    men_css()
    st.title("Weather Forecast App")

    selected = navigation_menu()
    api_key = '92ccf35f6ff24822135281cc734d6d84'
    
    if selected == "Home":
        home_page()
    elif selected == "Weather Forecast":
        city = st.text_input("Enter City (e.g., 'New York'):")
        country_code = st.text_input("Enter Country Code (optional, e.g., 'US'):")

        location = f"{city},{country_code}" if city and country_code else city

        if city:
            data = get_weather_data(location, api_key)
            if data['cod'] == '200':
                weather_df = process_weather_data(data)
                st.write(f"## 5-Day Weather Forecast for {city.capitalize()}")
                st.dataframe(weather_df[['Date', 'Temperature (°C)', 'Description']])
                fig = px.line(weather_df, x='Date', y='Temperature (°C)', title=f"Temperature Trend in {city.capitalize()}")
                st.plotly_chart(fig)
            else:
                st.error(f"Error: {data['message']}")

    elif selected == "Compare Cities":
        city1 = st.text_input("Enter First City (e.g., 'New York'):", key='city1')
        country_code1 = st.text_input("Enter Country Code for First City (optional, e.g., 'US'):", key='country_code1')
        city2 = st.text_input("Enter Second City (e.g., 'Los Angeles'):", key='city2')
        country_code2 = st.text_input("Enter Country Code for Second City (optional, e.g., 'US'):", key='country_code2')

        location1 = f"{city1},{country_code1}" if city1 and country_code1 else city1
        location2 = f"{city2},{country_code2}" if city2 and country_code2 else city2

        if city1 and city2:
            data1 = get_weather_data(location1, api_key)
            data2 = get_weather_data(location2, api_key)

            if data1['cod'] == '200' and data2['cod'] == '200':
                weather_df1 = process_weather_data(data1)
                weather_df2 = process_weather_data(data2)

                weather_df1['City'] = city1.capitalize()
                weather_df2['City'] = city2.capitalize()

                combined_df = pd.concat([weather_df1, weather_df2])

                st.write(f"## 5-Day Weather Forecast Comparison")
                st.dataframe(combined_df[['Date', 'City', 'Temperature (°C)', 'Description']])

                fig = px.line(combined_df, x='Date', y='Temperature (°C)', color='City', 
                              title=f"Temperature Trend Comparison: {city1.capitalize()} vs {city2.capitalize()}")
                st.plotly_chart(fig)
            else:
                st.error(f"Error: {data1.get('message', 'Unable to fetch data for the first city')} or {data2.get('message', 'Unable to fetch data for the second city')}")


# Main App Logic
create_users_table()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False

if st.session_state.show_signup:
    sign_up_page()
elif not st.session_state.logged_in:
    login_page()
else:
    main_app()