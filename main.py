import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import google.generativeai as genai
from PIL import Image
import io
import os
from dotenv import load_dotenv
load_dotenv()
import json
import streamlit as st
from langchain_community.utilities import PythonREPL
repl = PythonREPL()

# import pprint
# for model in genai.list_models():
#     pprint.pprint(model.name)

try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
except:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)
model = "models/gemini-1.5-flash-latest" 


SYSTEM_PROMPT_INFO = """
You are a professional information extractor. From the provided context, you have to extract these 5 information and then output 
them in JSON format. If date is not provided in the context, you can put None in Date. For every amount, there should be a date. Dont write anything extra. Only JSON response is required. A single JSON is required containing list of values for each key.
{
    "Date": ["YYYY-MM-DD", ], # The date of receiving or paying : datatype datetime
    "Category": ["category", ], # High level category of expense : datatype string
    "Description": ["description", ], # Description for the category : datatype string
    "Amount": ["amount", ], # amount paid : datatype integer
    "Type": ["type", ], # Expense or income : datatype string
}
CONSTRAINT: Make sure the arrays are not empty, the length of each array is equal, data types are correct and response is json.
"""

SYSTEM_PROMPT_RETRIEVE = """
i have a csv named {}_expense.csv with these columns: Date,Category,Description,Amount,Type. 
Write python code for this user query: {}. 
Only output python code without any quotes, special characters or extra words
"""


def extract_info(model, text=None, image_path=None, docs=None):
    model = genai.GenerativeModel(model)
    
    if text != None:
        response = model.generate_content(
        [f"{SYSTEM_PROMPT_INFO} CONTEXT: {text}"]
    )
        
    elif image_path != None:
        image = Image.open(image_path)
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        image_parts = [
            {
                "mime_type": 'image/png',
                "data":   image_bytes.read()
            }
            ]
        response = model.generate_content(
            [f"{SYSTEM_PROMPT_INFO}", image_parts[0]]
        )
    # print('extract_info - extract_info func', response.text)
    return json.loads(response.text)
    
curr_date = datetime.now().strftime("%Y-%m-%d")
curr_month = datetime.now().strftime("%B").lower()    


def load_csv(curr_month):
    try:
        loaded_df = pd.read_csv(f'{curr_month}_expense.csv')
    except Exception as e:
        loaded_df = pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount', 'Type'])
        loaded_df.to_csv(f'{curr_month}_expense.csv', index=False)
    finally:
        loaded_df = pd.read_csv(f'{curr_month}_expense.csv')
    # print('loaded_df - load_csv func', loaded_df)
    return loaded_df

def update_csv(loaded_df, curr_month, extracted_info):
    new_df = pd.DataFrame(extracted_info)
    loaded_df = pd.concat([loaded_df, new_df], ignore_index=True)
    loaded_df['Date'] = pd.to_datetime(loaded_df['Date'], errors='coerce', format='%Y-%m-%d')
    loaded_df['Date'] = loaded_df['Date'].fillna(curr_date)
    # print('loaded_df - update_csv func', loaded_df)
    loaded_df.to_csv(curr_month+'_expense.csv', index=False)


def retrieve_info(model, SYSTEM_PROMPT_RETRIEVE=SYSTEM_PROMPT_RETRIEVE, text=None, ):
    model = genai.GenerativeModel(model)
    response = model.generate_content(SYSTEM_PROMPT_RETRIEVE.format(curr_month,text))
    code = response.text.replace("```","").replace('python','')
    print("Generated Code:")
    print(code)
    repl = PythonREPL()
    try:
        query_result = repl.run(code)
    except Exception as e:
        # print(f"Error executing generated code: {e}")
        return None
    return query_result


#                                                              For TEXT
# extracted_info = extract_info(model, text="bought 10 apples for 5 dollars and paid 10 dollars to my friend")
# loaded_df = load_csv(curr_month) 
# update_csv(loaded_df, curr_month, extracted_info) 
    
#                                                              For IMAGE
# extracted_info = extract_info(model, image_path="G:\\Smart Finance Manager Project\\expense_img.jpg")
# loaded_df = load_csv(curr_month)  # Call the function and get the DataFrame
# update_csv(loaded_df, curr_month, extracted_info)  # Pass the DataFrame to update_csv

#                                                              Retrieve Info
# out = retrieve_info(model, text="create a dashboard of my expenses and incomes")
# print(out)


def main():
    st.title("Smart Finance Manager")
    
    # Adding Expenses Section
    query = st.text_input("Add ")
    submit_button = st.button("Submit",use_container_width=True, key='submit')
    
    if submit_button:
        extracted_info = extract_info(model, text=query)
        loaded_df = load_csv(curr_month) 
        update_csv(loaded_df, curr_month, extracted_info)
        st.session_state['query'] = ""
    
    # Retrieve Information Section
    ask = st.text_input("Ask ")
    ask_button = st.button("Ask",use_container_width=True, key='ask')
    
    if ask_button:
        out = retrieve_info(model, text=ask)
        st.write(out, unsafe_allow_html =True)
    
    # Upload Image
    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if uploaded_image is not None:
        bytes_data = uploaded_image.getvalue()
        extracted_info = extract_info(model, image_path=uploaded_image)
        # print(extracted_info)
        loaded_df = load_csv(curr_month)
        update_csv(loaded_df, curr_month, extracted_info)
        uploaded_image.close()  

    # Preview Data Section
    prev_button = st.button(label="Preview Data",use_container_width=True, key='preview')
    if prev_button:
        loaded_df = load_csv(curr_month)
        st.dataframe(loaded_df, use_container_width=True)
    
if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    main()
    
>>>>>>> e54f99a1325bd0743f3b7dde983b029147a30357
