import streamlit as st
from streamlit_feedback import streamlit_feedback
from functions.data_search_keka import connect_db, generate_query,generate_plot,generate_answers, generate_query2,to_pdf
from functions.response_delay import response_delay

def data_search():
    st.title('DATABOT')
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
   
    
    # Execute query button
    if qns := st.chat_input("What is up?"):
        
        try:
            with st.chat_message("user"):
                st.markdown(qns)
            st.session_state.messages.append({"role": "user", "content": qns})
            #connect to the database
            db = connect_db()
            #generate the query
            
            # results,code = generate_query(db,qns)
            results = generate_query2(db,qns)
            print("_-_"*20)
            pdf_data = to_pdf(results)
            # results = generate_answers(db,qns)

            # Execute SQL query
            # results = execute_query(sql_query)
            # Display results
            if len(results) > 0:
                # st.write('Query Results:')
                # st.write(results)
                with st.chat_message("DataBot"):
                    # response = st.write_stream(response_delay(results))
                    response1 = st.write_stream(response_delay(results))
                    # response2 = st.pyplot(code,use_container_width=True)
                st.session_state.messages.append({"role": "Databot", "content": response1})
                # st.session_state.messages.append({"role": "Databot", "content": response2})
                st.download_button("Download PDF", pdf_data, "results.pdf", "pdf")
                st.set_option('deprecation.showPyplotGlobalUse', False)
                streamlit_feedback(feedback_type="thumbs")

                # for row in results:
                #     st.write(row)
            else:
                with st.chat_message("DataBot"):
                    st.write_stream(response_delay('No results found.'))
                st.session_state.messages.append({"role": "Databot", "content": "No Results Found"})
                streamlit_feedback(feedback_type="thumbs")
        except Exception as e:
            with st.chat_message("DataBot"):
                    st.write_stream(response_delay(f'Error executing query: {str(e)}'))
            st.session_state.messages.append({"role": "Databot", "content": "No Results Found"})
            # st.error(f'Error executing query: {str(e)}')
            print(e)

