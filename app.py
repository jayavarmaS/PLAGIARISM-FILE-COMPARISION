import streamlit as st
import pandas as pd
import nltk
nltk.download('punkt')
from nltk import tokenize
import io
import docx2txt
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px

# Function to extract sentences from text
def get_sentences(text):
    return tokenize.sent_tokenize(text)

# Function to generate multiple Google Search URLs for plagiarism check
def get_search_urls(sentence):
    base_google_url = "https://www.google.com/search?q="
    base_youtube_url = "https://www.youtube.com/results?search_query="
    
    query = sentence.replace(" ", "+")
    
    return {
        "Google General Search": base_google_url + query,
        "Google Scholar Search": base_google_url + query + "+site:scholar.google.com",
        "Google Books Search": base_google_url + query + "+site:books.google.com",
        "Google News Search": base_google_url + query + "+site:news.google.com",
        "YouTube Related Videos": base_youtube_url + query
    }

# File reading functions
def read_text_file(file):
    content = ""
    with io.open(file.name, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def read_docx_file(file):
    text = docx2txt.process(file)
    return text

def read_pdf_file(file):
    text = ""
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to get text from an uploaded file
def get_text_from_file(uploaded_file):
    content = ""
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            content = read_text_file(uploaded_file)
        elif uploaded_file.type == "application/pdf":
            content = read_pdf_file(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            content = read_docx_file(uploaded_file)
    return content

# Function to clean and prepare text (remove unnecessary spaces, newlines)
def clean_text(text):
    return " ".join(text.split())

# Cosine Similarity calculation
def get_similarity(text1, text2):
    text1_clean = clean_text(text1)
    text2_clean = clean_text(text2)
    text_list = [text1_clean, text2_clean]
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(text_list)
    return cosine_similarity(count_matrix)[0][1]

# Function to compare two files and display graph
def compare_two_files(file1, file2):
    text1 = get_text_from_file(file1)
    text2 = get_text_from_file(file2)
    
    if not text1 or not text2:
        st.write("### One or both files have no content to compare.")
        return None
    
    similarity_score = get_similarity(text1, text2)
    
    # Display similarity graph
    data = pd.DataFrame({
        'File 1': [file1.name],
        'File 2': [file2.name],
        'Similarity': [similarity_score]
    })
    
    fig = px.bar(data, x='File 1', y='Similarity', color='File 2', title=f'Similarity Score: {similarity_score*100:.2f}%')
    st.plotly_chart(fig)
    
    st.write(f"### Similarity Score between the two files: {similarity_score * 100:.2f}%")
    return similarity_score

# Streamlit UI for plagiarism check and file comparison
st.set_page_config(page_title="Plagiarism Detection & File Comparison")
st.title('Plagiarism Detector and File Comparison')

# Option selection
option = st.radio(
    "Select input option:",
    ("Online Search", "Manual File Input", "Compare Two Files")
)

# Handling user input and file uploads
if option == "Online Search":
    text = st.text_area("Enter text here", height=200)

elif option == "Manual File Input":
    uploaded_file = st.file_uploader("Upload a file (.docx, .pdf, .txt)", type=["docx", "pdf", "txt"])
    text = get_text_from_file(uploaded_file) if uploaded_file else ""

elif option == "Compare Two Files":
    uploaded_files = st.file_uploader("Upload two files (.docx, .pdf, .txt)", type=["docx", "pdf", "txt"], accept_multiple_files=True)
    if len(uploaded_files) == 2:
        file1 = uploaded_files[0]
        file2 = uploaded_files[1]
    else:
        st.write("Please upload exactly two files to compare.")
        st.stop()

# Button to check plagiarism or similarity
if st.button("Check for plagiarism or find similarities"):
    st.write("### Checking for plagiarism or finding similarities...")

    if option == "Online Search" and not text:
        st.write("### No text found for plagiarism check.")
        st.stop()

    if option == "Manual File Input" and not text:
        st.write("### No content found in the uploaded file.")
        st.stop()

    if option == "Online Search":
        sentences = get_sentences(text)
        st.write("### Click the links below to manually check for plagiarism and related resources:")
        for sentence in sentences:
            st.write(f"🔹 **Sentence:** {sentence}")
            search_urls = get_search_urls(sentence)
            for name, url in search_urls.items():
                st.markdown(f"- **[{name}]({url})**")
            st.write("---")  # Add a divider between results

    elif option == "Manual File Input":
        if text:
            sentences = get_sentences(text)
            st.write("### Click the links below to manually check for plagiarism and related resources:")
            for sentence in sentences:
                st.write(f"🔹 **Sentence:** {sentence}")
                search_urls = get_search_urls(sentence)
                for name, url in search_urls.items():
                    st.markdown(f"- **[{name}]({url})**")
                st.write("---")  # Add a divider between results

    elif option == "Compare Two Files":
        similarity_score = compare_two_files(file1, file2)
        if similarity_score is not None:
            st.write(f"### Similarity Score: {similarity_score * 100:.2f}%")
