import time
import pandas as pd
import streamlit as st
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static
from langchain_groq import ChatGroq
from get_df_code import get_df_code

title = "Jordan Standardized Precipitation Index"
st.set_page_config(layout="wide", page_title=title)
st.markdown(f"### {title}")

# Set up LLM
Groq_KEY = st.secrets["Groq_KEY"]
llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", api_key=Groq_KEY)

# Add a Chat history object to Streamlit session state
if "chat" not in st.session_state:
    st.session_state.chat = []

# Create a Kepler map
map1 = KeplerGl(height=400)

config = {
    "version": "v1",
    "config": {
        "mapState": {
            "bearing": 0,
            "latitude": 32.24,
            "longitude": 35.35,
            "pitch": 0,
            "zoom": 6,
        },
        "visState": {
          'layerBlending': "additive",
        }
    },
}
map1.config = config

# Load CSV file
df = pd.read_csv('Jordan Standardized Precipitation Index.csv')
df['Time'] = pd.to_datetime(df['Time'], format='%m/%d/%y')
df['Time'] = df['Time'].dt.strftime('%Y-%m-%d')
df['Time'] = df['Time'].fillna('')

if "df" in st.session_state:
    map1.add_data(data=st.session_state.df, name=title)
else:
    map1.add_data(data=df, name=title)

# Set up two columns for the map and chat interface
col1, col2 = st.columns([3, 2])

with col1:
    keplergl_static(map1)

# Set up the chat interface
with col2:
    # Create a container for the chat messages
    chat_container = st.container(height=355)

    # Show the chat history
    for message in st.session_state.chat:
        with chat_container:
            with st.chat_message(message['role']):
                st.markdown(message['content'])

    # Get user input
    user_input = st.chat_input("What can I help you with?")
    if user_input:
        with chat_container:
            st.chat_message("user").markdown(user_input)
            st.session_state.chat.append({"role": "user", "content": user_input})

            with st.chat_message("assistant"):
                with st.spinner("We are in the process of your request"):
                    try:
                        result = get_df_code(llm, user_input)
                        if result['category'] == 'Other':
                            response = result['answer']
                        else:
                            exec(result['answer'])
                            if isinstance(st.session_state.df, pd.Series):
                                st.session_state.df = st.session_state.df.to_frame().T
                            response = f"""
                                        Your request has been processed. {st.session_state.df.shape[0]}
                                        { "rows are" if st.session_state.df.shape[0] > 1 else "row is"}
                                        found and displayed.
                                        """
                    except Exception as e:
                        traceback.print_exc()
                        response = f"We are not able to process your request. Please refine your request and try again."
                    st.session_state.chat.append({"role": "assistant", "content": response})
                    st.rerun()

if "df" in st.session_state:
    st.dataframe(st.session_state.df)
else:
    st.dataframe(df)

