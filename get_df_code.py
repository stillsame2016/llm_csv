from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_df_code(llm, question):
    prompt = PromptTemplate(
        template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
        We have a dataframe df with the following columns:
            Code	
            Station_ID	
            JMD_code	
            Station_Name	
            Altitude_m	
            Latitude	
            Longitude	
            Time	
            SPI

        The following is the request from a user:    
        {question}

        Generate the python code for the request as one statement st.session_state.df = ... only without any explanation.

        Answer:<|eot_id|><|start_header_id|>assistant<|end_header_id|>
        """,
        input_variables=["question"],
    )

    df_code_chain = prompt | llm | StrOutputParser()
    return df_code_chain.invoke({"question": question})

