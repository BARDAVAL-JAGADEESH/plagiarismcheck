import os
import sqlite3
import json
from flask import Flask, request, jsonify, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import PyPDF2  # For handling PDF files

# Initializing the NLTK
nltk.download('punkt')

app = Flask(__name__)
DATABASE = 'plagiarism.db'

# This function is about Initializing database 
def initializing_database():
    with sqlite3.connect(DATABASE) as connection:
        c = connection.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            content TEXT,
            uploaddate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS plagiarismresults (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            documentid INTEGER,
            similaritypercentage FLOAT,
            comparisontext TEXT,
            FOREIGN KEY(document_id) REFERENCES documents(id)
        )''')
        connection.commit()

# Thi function to store all the document content in to the database
def store_document(filename, content):
    with sqlite3.connect(DATABASE) as connection:
        c = connection.cursor()
        c.execute('INSERT INTO documents (file_name, content) VALUES (?, ?)', (filename, content))
        connection.commit()

# This function will help extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# This function will  to check plagiarism 
def check_plagiarism(new_doc_text):
    with sqlite3.connect(DATABASE) as connection:
        c = connection.cursor()
        c.execute('SELECT * FROM documents')
        documents = c.fetchall()

    doc_contents = [doc[2] for doc in documents]  
    doc_contents.append(new_doc_text)  

    # this will Use TfidfVectorizer to calculate  similarity in content 
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(doc_contents)

    # this will count similarity
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    max_similarity = max(cosine_sim[0])  
    similarity_percentage = max_similarity * 100  # this will Convert into percentage

    # this will Store plagiarism result
    comparison_text = json.dumps([doc_contents[i] for i in range(len(cosine_sim[0])) if cosine_sim[0][i] > 0.1])  # Only consider relevant matches
    with sqlite3.connect(DATABASE) as connection:
        c = connection.cursor()
        c.execute('SELECT id FROM documents WHERE content = ?', (new_doc_text,))
        document_id = c.lastrowid  
        c.execute('INSERT INTO plagiarism_results (document_id, similarity_percentage, comparison_text) VALUES (?, ?, ?)', 
                  (document_id, similarity_percentage, comparison_text))
        connection.commit()

    return similarity_percentage, comparison_text

# This function is home page 
@app.route('/')
def index():
    return render_template('index.htm')

#this will function will help to upload 
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        # this will Check if the file is a PDF or 
        if file.filename.endswith('.pdf'):
            file_content = extract_text_from_pdf(file)
        else:
            # For other file types, assume plain text
            file_content = file.read().decode('utf-8')

        store_document(file.filename, file_content)

        # This will check plagiarism for the uploaded document
        similarity_percentage, comparison_text = check_plagiarism(file_content)

        # This will return plagiarism results in the form of  JSON
        return jsonify({
            'similarity_percentage': similarity_percentage,
            'comparison_text': comparison_text
        })
    return jsonify({'error': 'No file uploaded'}), 400


initializing_database()

if __name__ == '__main__':
    app.run(debug=True)
