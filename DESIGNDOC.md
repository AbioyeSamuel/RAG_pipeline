**Design Document: Role-Based Knowledge Access Control System for the RAG Pipeline**

**1. Introduction**
This document outlines the design and implementation of a Role-Based Knowledge Access Control (RBAC) System integrated with a Retrieval-Augmented Generation (RAG) pipeline. The system ensures that only authorized users can access certain documents, thereby enhancing security and maintaining controlled knowledge access. The design also supports detailed logging of document accesses for auditing purposes.

**2. System Overview**
The RBAC system is designed to work in tandem with a RAG pipeline that retrieves relevant context from a document repository (stored using FAISS) and generates responses via an LLM. The RBAC component restricts document retrieval based on user roles, ensuring that users see only the documents they are permitted to access.

Key Components:
User Authentication & Role Management:
Users are authenticated and assigned a role (e.g., admin, researcher, student). Their role determines the access permissions for document retrieval.

Document Repository & FAISS Indexing:
Documents (text and PDF) are processed, chunked, and embedded using the text-embedding-ada-002 model. These embeddings are stored in a FAISS index for fast similarity search.

Role-Based Filtering:
Retrieved documents are filtered based on the user's role using data from a permissions table in an SQLite database.

Access Logging:
Document accesses are logged into an access_logs table for auditing purposes.

**3. Database Schema**
The system uses an SQLite database (rbac.db) located in the data/ folder. The schema consists of the following tables:

3.1 Users Table (users)
Stores user credentials and their assigned role.

id: INTEGER, PRIMARY KEY, AUTOINCREMENT
username: TEXT, UNIQUE, NOT NULL
password_hash: TEXT, NOT NULL
role_id: INTEGER, NOT NULL, FOREIGN KEY referencing roles(id)
3.2 Roles Table (roles)
Defines user roles.

id: INTEGER, PRIMARY KEY, AUTOINCREMENT
name: TEXT, UNIQUE, NOT NULL
3.3 Permissions Table (permissions)
Maps roles to allowed document categories.

id: INTEGER, PRIMARY KEY, AUTOINCREMENT
role_id: INTEGER, NOT NULL, FOREIGN KEY referencing roles(id)
document_category: TEXT, NOT NULL
For example, the "admin" role might have permission "all", while "researcher" might have "research", and "student" might have "general".
3.4 Documents Table (documents)
Stores metadata about each document.

id: INTEGER, PRIMARY KEY, AUTOINCREMENT
file_path: TEXT, UNIQUE, NOT NULL
category: TEXT, NOT NULL
This category is used by the RBAC filter to restrict access.
3.5 Access Logs Table (access_logs)
Records each document access attempt for auditing.

id: INTEGER, PRIMARY KEY, AUTOINCREMENT
user_id: INTEGER, NOT NULL, FOREIGN KEY referencing users(id)
doc_id: INTEGER, NOT NULL, FOREIGN KEY referencing documents(id)
access_time: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
access_status: TEXT, NOT NULL
Example status: "GRANTED", "DENIED"

**4. System Architecture and Workflow**
4.1 User Authentication & Dynamic Role Assignment
Authentication:
Users log in via the auth.py module, which verifies credentials using bcrypt (or SHA-256 in our simplified version) and returns both user_id and role_id.

Role Assignment:
The returned role_id is used by the system to dynamically filter document retrieval, replacing any hard-coded role values.

4.2 Document Processing and FAISS Indexing
Document Loading:
The system processes all documents in the data/ folder (both .txt and .pdf formats) using the TextLoader and PyPDFLoader modules.

Chunking:
Documents are split into smaller chunks using RecursiveCharacterTextSplitter to improve retrieval accuracy.

Embedding:
Each chunk is embedded using the OpenAI text-embedding-ada-002 model. These embeddings are stored in a FAISS index, which is saved to disk (using pickle) for faster future retrieval.

4.3 Role-Based Access Control and Retrieval
Filtering Mechanism:
When a query is processed, the FAISS index retrieves the top K relevant document chunks.
The access_control.py module then filters these documents based on the user’s role (by checking the allowed document categories in the permissions table).

Query Handling:
The filtered documents are passed to the language model to generate a response. Document accesses are logged for auditing.

4.4 Response Generation
Language Model Integration:
The system uses GPT-4o-mini (or a similar LLM) for response generation.
Contextual Prompts:
The generated response is based on the retrieved and role-filtered documents, ensuring that only authorized content is used to generate answers.

**5. Rationale Behind Design Choices**
5.1 SQLite
Portability & Simplicity:
SQLite is lightweight, serverless, and easy to set up, making it ideal for prototyping and small to medium-scale deployments.
5.2 FAISS
Performance:
FAISS is highly efficient for vector similarity searches and scales well even with large document collections.
5.3 Role-Based Access Control (RBAC)
Security:
RBAC ensures that sensitive information is accessible only to authorized users, a crucial feature for knowledge-based systems.

Flexibility:
The system can easily be extended to support additional roles and permissions, making it future-proof.

5.4 Design Integration with RAG Pipeline
Seamless Integration:
The RBAC layer integrates directly into the RAG pipeline by filtering retrieved documents before passing them to the language model, ensuring that responses are both relevant and secure.

Auditability:
Logging document accesses provides a trail for auditing and troubleshooting, enhancing system transparency.

**6. Security Considerations**
Authentication:
Secure user authentication using hashed passwords (bcrypt) protects against unauthorized access.

Role Enforcement:
The RBAC system ensures that users only retrieve documents that match their role's permissions.

Logging:
Access logs enable continuous monitoring and auditing of document access, ensuring accountability.

**7. Conclusion**
The proposed design provides a robust, scalable, and secure role-based knowledge access control system for a RAG-based model. By leveraging SQLite for a lightweight, portable database solution and FAISS for efficient document retrieval, the system meets the requirements for controlled and auditable access to a knowledge base. The design is flexible enough to allow further enhancements, such as additional roles, fine-tuning of document indexing, or integration with enterprise-level databases if needed.