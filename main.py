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
import plotly.express as px
from langchain_community.utilities import PythonREPL
repl = PythonREPL()
# from feedback import send_feedback



# import pprint
# for model in genai.list_models():
#     pprint.pprint(model.name)

try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
except:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)
model = "models/gemini-1.5-flash-latest" 


# SYSTEM_PROMPT_INFO = """
# You are a professional information extractor. From the provided context, you have to extract these 5 information and then output them in JSON format. Each key should have an array of values with equal length.
# If date is not provided in the context, you can put None in Date. For every amount, there should be a date. Dont write anything extra. Only JSON response is required. A single JSON is required containing list of values for each key.
# {
#     "Date": ["YYYY-MM-DD", ], # The date of receiving or paying : datatype datetime
#     "Category": ["category", ], # High level category of expense : datatype string
#     "Description": ["description", ], # Description for the category : datatype string
#     "Amount": ["amount", ], # amount paid : datatype integer
#     "Type": ["type", ], # Expense or income : datatype string
# }
# CONSTRAINT: Make sure the arrays are not empty, the length of each array is equal, data types are correct and response is json. Before outputting, recheck all the array lengths.
# """

SYSTEM_PROMPT_INFO="""You are a professional information extractor. From the provided context (text or image), extract key financial information and output it in JSON format. Each key should have an array of values with equal length.

Rules:
1. Prioritize total or summary amounts over individual line items.
2. Every amount must have a corresponding date.
3. Output only the JSON response.
CRITICAL INSTRUCTION: Your entire response MUST be a valid, parseable JSON string. Do not include any text before or after the JSON.
JSON Structure:
{
    "Date": ["YYYY-MM-DD", ...],  // Type: string
    "Category": ["category", ...], // Type: string
    "Description": ["description", ...], // Type: string
    "Amount": [amount, ...],  // Type: number
    "Type": ["type", ...]    // "Expense" or "Income"; type: string
}

Guidelines for Receipts and Invoices:
1. Hierarchical Data:
   - Prioritize totals (e.g., "Total Charges") over individual items.
   - Ignore individual items if a total is available.
   - Example: Choose "Total: $50" over "Item 1: $30, Item 2: $20".

2. Key Fields:
   - Date: Use the most prominent date (usually at the top).
   - Amount: Use the "Total" or bottom-line figure.
   - Ignore "Subtotal" if "Total" is present.
   - Ignore "Balance" or "Amount Due" for this extraction.

3. Categories:
   - Infer from the business type or receipt title.
   - Common categories: "Medical", "Grocery", "Restaurant", "Retail".

4. Descriptions:
   - Use the business name or service type.
   - For medical: "Doctor's Visit", "Lab Test", "Consultation".
   - For others: "Grocery Shopping", "Dinner", etc.

5. Transaction Type:
   - Receipts and invoices usually indicate "Expense".
   - "Income" is rare (e.g., a refund receipt).

6. Multiple Totals:
   - Some receipts have multiple totals (e.g., "Subtotal", "Tax", "Total").
   - Always choose the final, all-inclusive total.

7. No Line Items:
   - Many receipts don't need line-item extraction.
   - Focus on the total amount and overall purpose.

Data Validation:
- Ensure all arrays have equal length.
- Validate data types.
- Double-check before output.

Example - Medical Receipt:
Input: Image of a clinic receipt with "Total Charges: $150"
Output:
{
    "Date": ["2024-05-13"],
    "Category": ["Medical"],
    "Description": ["Clinic Consultation"],
    "Amount": [4400],
    "Type": ["Expense"]
}

Key Changes:
1. Focus on totals, not line items.
2. Understand receipt hierarchy.
3. Infer categories from context.
4. Use business-specific descriptions."""


SYSTEM_PROMPT_RETRIEVE = """
i have a csv named {}_expense.csv with these columns: Date,Category,Description,Amount,Type. 
Write python code for this user query: {}. 
Only output python code without any quotes, special characters or extra words
"""


def extract_info(model, text=None, image_path=None, image_prompt=None):
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
            [f"Prompt: {SYSTEM_PROMPT_INFO}. Information about image: {image_prompt}", image_parts[0]]
        )
    print('extract_info - extract_info func', response.text)
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
    print('loaded_df - load_csv func', loaded_df)
    return loaded_df

def update_csv(loaded_df, curr_month, extracted_info):
    new_df = pd.DataFrame(extracted_info)
    loaded_df = pd.concat([loaded_df, new_df], ignore_index=True)
    loaded_df['Date'] = pd.to_datetime(loaded_df['Date'], errors='coerce', format='%Y-%m-%d')
    loaded_df['Date'] = loaded_df['Date'].fillna(curr_date)
    print('loaded_df - update_csv func', loaded_df)
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
        print(f"Error executing generated code: {e}")
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
    # img_prompt = st.text_input("Image Info ", value='')
    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        bytes_data = uploaded_image.getvalue()
        # print("image prompt", img_prompt)
        extracted_info = extract_info(model, image_path=uploaded_image, )
        print(extracted_info)
        loaded_df = load_csv(curr_month)
        update_csv(loaded_df, curr_month, extracted_info)
        uploaded_image.close()  

    # Preview Data Section
    prev_button = st.button(label="Preview Data",use_container_width=True, key='preview')
    if prev_button:
        loaded_df = load_csv(curr_month)
        st.dataframe(loaded_df, use_container_width=True)

        
        
    # st.session_state['feedback'] = st.text_input("Feedback",)    
    # print(st.session_state['feedback'])
    # send_button = st.button(label="Send Feedback", use_container_width=True, key='send', on_click=send_feedback, args=(str(st.session_state['feedback']),))

    
    # Display Chart
    
    loaded_df = load_csv(curr_month)
    
    # Plot categories with expenses
    only_expenses = loaded_df[loaded_df['Type'] == 'Expense']
    category_expenses = only_expenses.groupby('Category')['Amount'].sum().reset_index()
    fig1 = px.bar(category_expenses, x='Category', y='Amount', title='Categories with Expenses',)

    # Plot expenses vs income
    expense_income = loaded_df.groupby('Type')['Amount'].sum().reset_index()
    fig2 = px.bar(expense_income, x='Type', y='Amount', title='Expenses vs Income', )

    # Create two columns and display the charts side by side
    col1, col2 = st.columns(2)

    # Display the first chart in the first column
    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    # Display the second chart in the second column
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

    
    st.cache_data.clear()
    
    st.cache_data.clear()

if __name__ == "__main__":
    main()
