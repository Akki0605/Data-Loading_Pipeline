import schedule
import time
from datetime import datetime
import requests
import gzip
import xml.etree.ElementTree as ET
import io
import psycopg2
from Bio.SeqUtils import molecular_weight

# URLs of the gzipped XML files in the public S3 buckets
file_url_1 = 'ProteinSequence1.xml'
file_url_2 = 'ProteinSequence2.xml'

# Database parameters
db_params = {
    'host': 'db',
    'port': '5432',
    'database': 'Database Name',
    'user': 'User',
    'password': 'default'
    }

# Function to download, extract, and parse XML file
def parse_xml_from_s3(file_url):
    response = requests.get(file_url)
    with gzip.GzipFile(fileobj=io.BytesIO(response.content), mode='rb') as f:
        xml_data = f.read().decode('utf-8')
    root = ET.fromstring(xml_data)
    sequences = {}
    for entry in root.findall('.//{http://uniprot.org/uniref}entry'):
        unique_id = entry.get('id').replace('UniRef50_', '')
        sequence = entry.find('.//{http://uniprot.org/uniref}sequence').text
        if sequence and 'X' not in sequence and "'" not in sequence:
            mw = molecular_weight(sequence, "protein")
            sequences[unique_id] = {
                'sequence': sequence,
                'molweight': mw
            }
    return sequences

# Parse XML data from the first and second bucket
sequences_1 = parse_xml_from_s3(file_url_1)
sequences_2 = parse_xml_from_s3(file_url_2)

# Find changed sequences and count
changed_sequences = {key: sequences_2[key] for key in sequences_2 if key in sequences_1 and sequences_1[key]['sequence'] != sequences_2[key]['sequence']}
changed_sequences_count = len(changed_sequences)

# Connect to the database and update the table
def update_database():
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            # Create table if not exists
            cur.execute('''
                CREATE TABLE IF NOT EXISTS Entry (
                    unique_id VARCHAR(255) PRIMARY KEY,
                    current_sequence TEXT,
                    current_molweight FLOAT,
                    last_sequence TEXT,
                    last_molweight FLOAT
                )
            ''')
            # Insert unchanged sequences from the first file into the table
            for unique_id, sequence_info in sequences_1.items():
                cur.execute('''
                    INSERT INTO Entry (unique_id, current_sequence, current_molweight, last_sequence, last_molweight)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (unique_id) DO NOTHING
                ''', (unique_id, sequence_info['sequence'], sequence_info['molweight'], None, None))
            # Insert changed sequences from the second file into the table
            for unique_id, sequence_info in changed_sequences.items():
                # Get the old values from the database
                cur.execute('SELECT current_sequence, current_molweight FROM Entry WHERE unique_id = %s;', (unique_id,))
                old_sequence, old_molweight = cur.fetchone()

                # Update current_sequence and current_molweight columns with old values
                cur.execute('''
                    UPDATE Entry
                    SET current_sequence = %s, current_molweight = %s
                    WHERE unique_id = %s
                ''', (old_sequence, old_molweight, unique_id))

                # Update last_sequence and last_molweight columns with new values
                cur.execute('''
                    UPDATE Entry
                    SET last_sequence = %s, last_molweight = %s
                    WHERE unique_id = %s
                ''', (sequence_info['sequence'], sequence_info['molweight'], unique_id))

    print("Database updated successfully.")

def job():
    print("Job started at", datetime.now())
    update_database()

# Schedule the job to run every 30 days
schedule.every(30).days.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)