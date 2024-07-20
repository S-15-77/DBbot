import streamlit as st
from components.data_search_keka_ui import data_search

def main():
    st.sidebar.title('DATABOT')
    page_options = {
        'Execute SQL Query': data_search,
    }
    page = st.sidebar.radio('Select Page:', list(page_options.keys()))
    page_options[page]()

if __name__ == "__main__":
    main()



    