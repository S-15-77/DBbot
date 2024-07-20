# DBbot
Databot:  virtual assistant for seamless natural language to SQL query translation. With Databot, interact with databases effortlessly, bridging the gap between human language and database commands. Harnessing the capabilities of OpenAI's language models, Databot ensures accuracy and efficiency in your database operations.
## How to set up
- Create a virtual environment
  ```bash
  python -m venv env
  ```
- Activate the Virtual Environment
  ``` bash
  env/Scripts/activate
  ```
- Run the Requirement.txt file to download all the packages
  ```bash
  pip install -r requirement.txt       
  ```
- Create a .env file and add the data as mentioned

    ```
    OPENAI_API_KEY=<INSERT_OPENAI_API_KEY_HERE>
    OPENAI_CHAT_MODEL='gpt-35-turbo-16k'
    ```
## Running the project 

### Routing to Keka folder
```bash
cd keka
```
### What's in main.py

- main.py file containes the main function which is used to execute the streamlit application 

### Running in streamlit app 
```bash
streamlit run main.py
```

### What's in Component folder

- component folder contains the UI for the databot which is scripted using the streamlit application

- **How result Displays:**
  ```
   if len(results) > 0:
      with st.chat_message("DataBot"):
          response1 = st.write_stream(response_delay(results))
      st.session_state.messages.append({"role": "Databot", "content": response1})
      # st.download_button("Download PDF", pdf_data, "results.pdf", "pdf")
      # st.set_option('deprecation.showPyplotGlobalUse', False)
      streamlit_feedback(feedback_type="thumbs")

      
    else:
      with st.chat_message("DataBot"):
          st.write_stream(response_delay('No results found.'))
      st.session_state.messages.append({"role": "Databot", "content": "No Results Found"})
      streamlit_feedback(feedback_type="thumbs")
  ```

### What's in the Fuction folder
- **data_search.py :** The connect_db() function is designed to establish a connection to a specific database. 
- **Prompt template:** Change the Template based on the db 
```
template = '''
    Act as a SQL specialist and try to find the correct relation between the question and the SQL query.  
    Use only the given tables and join them if necessary. Do not add any other columns or table that are not present in the database.
    When presented with an input question, begin by crafting a syntactically accurate {dialect} statement.  
    When it mentioed any name make it Capitalize.
    Try to use LIKE and wildcard operators to compare similar names and prevent duplication while retaining all relevant data.
    If the data is asked for month don't use numeric values, instead use the joins from the d_date table to extract the month name. 
    If the data is asked about the employee details, use the joins from the d_employee table to extract the employee details.
    If the data is asked about the location details, use the joins from the d_location table to extract the location details.
    Use Aggregation whenever possible and avoid duplication.
    Filter out irrelevant data and retain only the necessary information.
    Also, follow up on the history of the data and use the most recent data when only asked.
    Utilize all available tables and incorporate joins as required. 
    Ensure comparison of similar names using wildcard operators.
    Use only the nessary columns and avoid using *.
    Try to minimize the null or missing values in the result.
    Finally, return only the syntactically correct query.
    If the SQL query required a LIKE operator, always use it at last and add "collate" as "tr-TR-x-icu".
    If using LIKE, always add "collate" as "tr-TR-x-icu".

    Template Details:
    {table_info}

    Question: {input}
    Top_k: {top_k}

    Example Output:

    '''
    prompt = PromptTemplate.from_template(template)
  ```

  - **Create a SQL Chain**: 
  ```
  generate_query = create_sql_query_chain(llm, db,k=100,prompt=prompt)
  ```
  - **Chain to generate SQL Query**
  ```
  execute_query = QuerySQLDataBaseTool(db=db,return_direct=True)
  query = generate_query.invoke({"question": question})
  ```
  - **Printing Query**
  ```
  generate_query.get_prompts()[0].pretty_print()
  print(query)
  ```
 - **Executing the Query in the DB environment:** These line of code is used to run the generated SQL query and return the SQL output
  ```
  chain = generate_query | execute_query
  result = chain.invoke({"question": question})
  print(result)
  ```

  - **Chat completion of the Generated SQL Result**
```
answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )
ans = answer_prompt | llm | StrOutputParser()
chain_ans = (RunnablePassthrough.assign(query=generate_query).assign(result=itemgetter("query") | execute_query) | ans)
results = chain_ans.invoke({"question": question})
print(results)
```
- **Chart For the SQL Output and the Chat Result:**
  ```
  chart_prompt = PromptTemplate.from_template('''
        You are a data visualization specialist. and you have been given a SQL result. 
        Import all the required packages if required.  
        Import datetime, pandas, and matplotlib.pyplot as plt           
        Given the following user question, corresponding SQL query, and SQL result, Write only a python code to Construct a chart using the SQL result if possible else say can't able to build as a python code.
        Try to use different types of charts like bar, pie, line, etc. based on the data if possible.
        Must use labels and titles to make the chart more informative.
        Try to use different colors for different data points.
        Use only one chart type for the given SQL result.
        If the data is not enough to create a chart, mention that it is not possible to create a chart as python print statement.
        Do not try to create a new data or modify the existing data.
                                                
        Question : {question}
        SQL Result : {result}
        Answer : ''')
    answer_chart = chart_prompt | llm | StrOutputParser()
    chain_chart = (
    RunnablePassthrough.assign(query=generate_query).assign(
    result=itemgetter("query") | execute_query
    )
    | answer_chart
    )
    print("="*20)
    code = chain_chart.invoke({"question": question})
    code =  code.replace("python", "").replace("`", "")
    print(code)

    return results,exec(code)
  ```

### Additional
- **Code to generate as a pdf file(Report Generator):** Add this code in **data_search_keka.py** 
 ```
  class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Query Results', 0, 1, 'C')

    def table(self, data):
        self.set_font('Arial', '', 12)
        for row in data:
            for item in row:
                self.cell(40, 10, str(item), 1)
            self.ln(10)
  ```

```
def to_pdf(result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, result)
    return pdf.output(dest='S').encode('latin1')
```

- **./component/data_search_keka_ui.py**
```
pdf_data = to_pdf(results)
st.download_button("Download PDF", pdf_data, "results.pdf", "pdf")
```

- **token_helper.py :** Used to count the no of token sent and receieved (for gpt-3.5-turbo-16k model)
- **response_delay.py:** Used to delay the output
