**Smart Finance Manager**

![image](https://github.com/ShahjahanMirza/Smart-Finance-Manager-Project/assets/103453568/a6594a76-167f-49ba-a2d7-91698fc54464)


<p>Smart Finance Manager is a powerful web application built using Streamlit, a Python library for creating interactive data applications. This project aims to simplify the process of managing your finances by providing an intuitive interface for adding expenses, tracking income, and retrieving valuable insights from your financial data.</p>

**Features**

<li>Add Expenses: Easily add your expenses by providing a text description or uploading an image. The application will intelligently extract relevant information such as date, category, description, amount, and type (expense or income).</li>
<li>Ask Questions: Interact with the application by asking questions about your financial data. The application will generate Python code based on your query and provide the desired information.</li>
<li>Preview Data: View your financial data in a tabular format, allowing you to easily analyze and understand your spending patterns.</li>
<li>Automatic Data Storage: Your financial data is automatically stored in a CSV file, ensuring that your information is always available for future reference.</li>


**Getting Started**

To run the Smart Finance Manager project locally, follow these steps:

Clone the repository:
> git clone `https://github.com/ShahjahanMirza/Smart-Finance-Manager-Project.git`

Navigate to the project directory:
> cd smart-finance-manager

Install the required dependencies:
> pip install -r requirements.txt

Set up the required environment variables:
> GOOGLE_API_KEY: Obtain an API key from the Google Cloud Console for the Generative AI API.

Run the Streamlit application:
> streamlit run main.py

The application will open in your default web browser. If not, you can access it by visiting the URL provided in the terminal.

**Deployed Application**

You can also access the deployed version of the Smart Finance Manager application by clicking the following link: [Smart Finance Manager](https://smart-finance-manager.streamlit.app/)

**Usage**

Adding Expenses:

Enter a text description of your expense or income in the "Add" input field.
Click the "Submit" button to extract the relevant information and add it to your financial data.
Uploading Images:

Click the "Upload Image" button to select an image file containing expense or income information.
The application will extract the relevant information from the image and add it to your financial data.
Asking Questions:

Enter your query in the "Ask" input field.
Click the "Ask" button to generate Python code based on your query and retrieve the desired information.
Previewing Data:

Click the "Preview Data" button to view your financial data in a tabular format.
