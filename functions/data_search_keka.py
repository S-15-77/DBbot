from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
import functions.token_helper as token_helper

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from langchain.prompts.chat import ChatPromptTemplate

from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_core.prompts.chat import MessagesPlaceholder

from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

from dotenv import load_dotenv
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io
import contextlib

from io import BytesIO
from fpdf import FPDF

load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name='gpt-3.5-turbo')

def connect_db():
    db = SQLDatabase.from_uri("<DB>")
    return db

def generate_query(db,question):
    # Prompt for SQL

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
    #used to generate the SQL query
    generate_query = create_sql_query_chain(llm, db,k=100,prompt=prompt)
    #runs qurey on db and give op 
    execute_query = QuerySQLDataBaseTool(db=db,return_direct=True)
    query = generate_query.invoke({"question": question})
    print("="*80)
    generate_query.get_prompts()[0].pretty_print()
    print(query)
    print("="*20)
    # query = query.replace("sql", "").replace("`", "")
    # result = execute_query.invoke(query)
    chain = generate_query | execute_query
    result = chain.invoke({"question": question})
    print(result)
    #Used to generate the answer based the SQL query and SQL result and the user question.
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )
    ans = answer_prompt | llm | StrOutputParser()
    chain_ans = (RunnablePassthrough.assign(query=generate_query).assign(
        result=itemgetter("query") | execute_query
    ) | ans)
    print("="*20)
    results = chain_ans.invoke({"question": question})
    print(results)

    #Prompt to generate the chart based on the SQL result
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
    
    #Creation of the chain to generate the chart
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
    # execute_and_save_plot(code, "output.pdf")

    return results,exec(code)




# def execute_and_save_plot(code: str, output_pdf: str):
#     # Redirect the standard output to capture print statements
#     with contextlib.redirect_stdout(io.StringIO()) as f:
#         # Execute the provided code
#         exec(code)
    
#     # Save the plot to a PDF file
#     with PdfPages(output_pdf) as pdf:
#         pdf.savefig()
    
#     # Close the plot to free up resources
#     plt.close()

def generate_query2(db,question):
    # llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name='gpt-3.5-turbo')
    # Prompt for SQL

    template = '''
    Act as a SQL specialist and try to find the correct relation between the question and the SQL query.  
    Use only the given tables and join them if necessary. Do not add any other columns or table that are not present in the database.
    When presented with an input question, begin by crafting a syntactically accurate {dialect} statement.  
    When it mentioed any name make it Capitalize.
    Try to use LIKE and wildcard operators to compare similar names and prevent duplication while retaining all relevant data.
    Use Aggregation whenever possible and avoid duplication.
    Filter out irrelevant data and retain only the necessary information.
    Also, follow up on the history of the data and use the most recent data when only asked.
    Utilize all available tables and incorporate joins as required. 
    Ensure comparison of similar names using wildcard operators.
    Use only the nessary columns and avoid using *.
    Try to minimize the null or missing values in the result.
    Finally, return only the syntactically correct query.
    No need to use collation in the query.
    if collation is used in the query remove it.

    Template Details:
    {table_info}

    Question: {input}
    Top_k: {top_k}

    Example Output:

    '''
    prompt = PromptTemplate.from_template(template)
    # generate_query = create_sql_query_chain(llm, db,k=1000)
    generate_query = create_sql_query_chain(llm, db,k=100,prompt=prompt)
    #runs qurey on db and give op 
    
    execute_query = QuerySQLDataBaseTool(db=db,return_direct=True)
    query = generate_query.invoke({"question": question})
    print("="*80)
    generate_query.get_prompts()[0].pretty_print()
    print("="*80)
    print(query)
    print("="*20)
    # query = query.replace("sql", "").replace("`", "")
    # result = execute_query.invoke(query)
    chain = generate_query | execute_query
    result = chain.invoke({"question": question})
    print(result)
    print(chain)
    
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )
    ans = answer_prompt | llm | StrOutputParser()
    chain_ans = (RunnablePassthrough.assign(query=generate_query).assign(
        result=itemgetter("query") | execute_query
    ) | ans)
    print("="*20)
    # print(chain_ans.invoke({"question": question}))
    results = chain_ans.invoke({"question": question})
    print(results)

    
    return results


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

def to_pdf(result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, result)
    return pdf.output(dest='S').encode('latin1')
