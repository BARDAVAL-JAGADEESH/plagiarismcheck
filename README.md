# Plagiarism Checker Application

This is a Flask-based plagiarism checker that supports uploading documents, extracting text (PDF supported), and checking for similarities with previously uploaded documents. The app stores documents and their plagiarism check results in an SQLite database.

## Features
- Upload a text file or PDF file.
- Extracts text from PDF files.
- Check the similarity between uploaded documents using cosine similarity.
- Store documents and plagiarism results in an SQLite database.
- Display plagiarism results including similarity percentage and comparison details.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.x
- Flask
- SQLite (comes pre-installed with Python)
- NLTK library (Natural Language Toolkit for text processing)
- scikit-learn (for text vectorization and cosine similarity)
- PyPDF2 (for extracting text from PDF files)

### Install Dependencies

You can install the required Python libraries using pip. Create a virtual environment (optional) and then run:

```bash
pip install -r requirements.txt
 pip install flask scikit-learn nltk PyPDF2




