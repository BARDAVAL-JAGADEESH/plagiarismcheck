import os
import sqlite3
import json
from flask import Flask, request, jsonify, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import PyPDF2  # For handling PDF files

# Initialize NLTK
nltk.download('punkt')

app = Flask(__name__)
DATABASE = 'plagiarism.db'

# Initialize SQLite database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            content TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS plagiarism_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            similarity_percentage FLOAT,
            comparison_text TEXT,
            FOREIGN KEY(document_id) REFERENCES documents(id)
        )''')
        conn.commit()

# Function to store document content in the database
def store_document(file_name, content):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO documents (file_name, content) VALUES (?, ?)', (file_name, content))
        conn.commit()

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to check plagiarism
def check_plagiarism(new_doc_text):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM documents')
        documents = c.fetchall()

    doc_contents = [doc[2] for doc in documents]  # List of existing documents' content
    doc_contents.append(new_doc_text)  # Add the new document to the list

    # Use TfidfVectorizer to calculate cosine similarity
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(doc_contents)

    # Compute cosine similarities
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    max_similarity = max(cosine_sim[0])  # Get max similarity score
    similarity_percentage = max_similarity * 100  # Convert to percentage

    # Store plagiarism result
    comparison_text = json.dumps([doc_contents[i] for i in range(len(cosine_sim[0])) if cosine_sim[0][i] > 0.1])  # Only consider relevant matches
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM documents WHERE content = ?', (new_doc_text,))
        document_id = c.lastrowid  # Get the last inserted document's ID
        c.execute('INSERT INTO plagiarism_results (document_id, similarity_percentage, comparison_text) VALUES (?, ?, ?)', 
                  (document_id, similarity_percentage, comparison_text))
        conn.commit()

    return similarity_percentage, comparison_text

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.htm')

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        # Check if the file is a PDF
        if file.filename.endswith('.pdf'):
            file_content = extract_text_from_pdf(file)
        else:
            # For other file types, assume plain text
            file_content = file.read().decode('utf-8')

        store_document(file.filename, file_content)

        # Check plagiarism for the uploaded document
        similarity_percentage, comparison_text = check_plagiarism(file_content)

        # Return plagiarism results as JSON
        return jsonify({
            'similarity_percentage': similarity_percentage,
            'comparison_text': comparison_text
        })
    return jsonify({'error': 'No file uploaded'}), 400

# Initialize the database on start
init_db()

if __name__ == '__main__':
    app.run(debug=True)
