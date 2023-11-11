Data Loading Pipeline 

Introduction
This project aimed to develop a robust data loading pipeline for synchronizing protein data from the Uniref50 database into a custom SQL database. The pipeline involves tasks such as populating the database with data from XML files, computing molecular weights, and updating the database with new XML files as they are released.

Architecture
The project utilizes a containerized cluster with the following components:
<img width="1371" alt="Screenshot 2023-11-10 at 5 47 37 PM" src="https://github.com/Akki0605/Data-Loading_Pipeline/assets/106899639/291f093e-213f-4485-ad15-98dfcafdb47f">


SQL Database Container:
Uses the official PostgreSQL Docker image.
Backend storage for protein data.
Data Loader Container:
Custom-built container for populating the database and computing molecular weights.
Web Client Container:
Includes a web client (e.g., SQLPad) for querying the database.
Data Architecture Diagram
SQL Data Model
Proposed Data Model:

sql
Copy code
Table Name: Entry
Columns:
- unique_id: Unique identifier for a protein entry.
- sequence: Current amino acid sequence.
- mw: Current molecular weight of the protein.
Description: This model is suitable for scenarios where only the latest information is required, and no historical values need to be preserved.

Actual Data Model:

sql
Copy code
Table Name: Entry
Columns:
- unique_id VARCHAR(255) PRIMARY KEY: Primary key for each protein entry.
- current_sequence TEXT: Current amino acid sequence.
- current_molweight FLOAT: Current molecular weight of the protein.
- last_sequence TEXT: Historical amino acid sequence.
- last_molweight FLOAT: Historical molecular weight of the protein.
Description: In response to the requirement of maintaining historical values, this model introduces additional columns for preserving the last known amino acid sequence and molecular weight.

Implementation
Populating the Database from XML Files:
Developed a data loading script to extract relevant information from Uniref50 XML files and efficiently populate the SQL database.
Computing Molecular Weights:
The data loader script computes molecular weights for each entry using Biopython and parsing protein sequences.
Removing the "X" Amino Acid Sequence:
Ambiguous "X" amino acid sequences are filtered out to ensure data integrity.
Updating the Database with New XML Files:
The data loader script detects new Uniref50 XML files, fetches them, and updates corresponding entries in the database.
Containerization
Docker Compose YAML was employed to manage the containerized cluster, including configurations for the SQL database, data loader, and web client containers. This setup enables easy deployment, scalability, and isolation of components.

Docker Compose.yaml

docker-compose up --build 

Purpose: The Docker Compose configuration streamlines the deployment and orchestration of a backend system for a data-driven application. The setup addresses specific needs, ensuring reliable data storage, automated data loading, and a user-friendly interface for querying and interacting with the stored data.

requirements.txt

The requirements.txt file outlines Python dependencies and versions for the project, promoting a reproducible development environment.

plaintext

Best Practices:

Regularly update the requirements.txt file.

Include only necessary dependencies.

Clearly specify version constraints for compatibility.

By incorporating these elements, the project establishes a comprehensive and scalable solution for managing protein data from Uniref50.
