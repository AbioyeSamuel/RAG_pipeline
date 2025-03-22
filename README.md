RAG pipeline - Context Retrieval and Response Generation

This project enables efficient document retrieval and query answering using FAISS and OpenAI's GPT-4o-mini. Documents are embedded into a FAISS index, and queries are processed to retrieve relevant chunks before generating responses using OpenAI's API.

Prerequisites
Ensure you have the following installed:

Python 3.8+
pip package manager
OpenAI API key
SQLite (bundled with Python)
bcrypt library for secure password hashing (installed via requirements.txt)

Installation and Setup
Step 1: Clone the Repository
git clone https://github.com/AbioyeSamuel/RAG_pipeline.git
cd Rag_Pipeline
Step 2. Install Required Dependencies
pip install -r requirements.txt
Step 3. Open the .env file for Environment Variables
Add your OpenAI API key:
OPENAI_API_KEY=your-api-key-here
Step 4: Set Up the RBAC Database
python db_setup.py


Running the Solution
Step 1: Process Documents and Build FAISS Index
Run the script from the src directory: 
cd src
python main.py

This script will:

Load and process documents
Split them into chunks
Create or load a FAISS index
Process queries and retrieve relevant documents
Generate responses using GPT-4o
Save results to data/results.json

Step 2: View the Results
Once the script runs successfully, open the data/results.json file to see the output:

cat data/results.json  # On macOS/Linux
type data\results.json  # On Windows

Results are stored in data/results.json.
The RBAC system filters retrieved documents based on user roles and logs each access attempt.
For further testing of the authentication and RBAC functionality, refer to the tests in tests/test_auth.py.

User Authentication and Role-Based Access Control
Before processing queries, the main script will prompt you for your username and password. Ensure that you have registered users in the system using the provided auth.py module or by running tests in tests/test_auth.py.

Additional Notes
Results: All results are stored in data/results.json.
RBAC Enforcement: The system filters retrieved documents based on the authenticated user's role and logs each access attempt.
Testing: For further testing of the authentication and RBAC functionality, refer to the tests in tests/test_auth.py.

cd tests
python test_auth.py