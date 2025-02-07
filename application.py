import sys
import streamlit as st
import pdfplumber
from Resume_scanner import compare
from gensim.summarization import keywords

def extract_pdf_data(file_path):
    data = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                data += text
    return data


def extract_text_data(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data

def extract_keywords(resume_text, job_description):
    jd_keywords = keywords(job_description, ratio=0.7).split('\n')
    resume_keywords = keywords(resume_text, ratio=0.7).split('\n')
    
    # Find missing keywords
    missing_keywords = [kw for kw in jd_keywords if kw not in resume_keywords]
    return missing_keywords


# Command-line argument processing
if len(sys.argv) > 1:

    if len(sys.argv) == 3:
        resume_path = sys.argv[1]
        jd_path = sys.argv[2]

        resume_data = extract_pdf_data(resume_path)
        jd_data = extract_text_data(jd_path)

        result = compare([resume_data], jd_data, flag='HuggingFace-BERT')

    sys.exit()

# Sidebar
flag_1 = 'For You'
with st.sidebar:
    st.markdown('**For whom you\'re using the ATS**')
    options_1 = st.selectbox('For what you\'re using the ATS',
                           ['For You', 'For Work'],
                           label_visibility="collapsed")
    flag_1 = options_1

flag = 'HuggingFace-BERT'
# with st.sidebar:
#     st.markdown('**Which embedding do you want to use**')
#     options = st.selectbox('Which embedding do you want to use',
#                            ['HuggingFace-BERT', 'Doc2Vec'],
#                            label_visibility="collapsed")
#     flag = options
    
if(flag_1 == 'For You'):

    # Main content
    tab1, tab2 = st.tabs(["**Home**", "**Results**"])

    # Tab Home
    with tab1:
        st.title("Applicant Tracking System")
        uploaded_files = st.file_uploader(
            '**Choose your resume.pdf file:** ', type="pdf", accept_multiple_files=True)
        JD = st.text_area("**Enter the job description:**")
        comp_pressed = st.button("Compare")

        if comp_pressed and uploaded_files:
            # Streamlit file_uploader gives file-like objects, not paths
            uploaded_file_paths = [extract_pdf_data(
                file) for file in uploaded_files]
            score = compare(uploaded_file_paths, JD, flag)
            # missing_keywords = [extract_keywords(resume_data, JD) for resume_data in uploaded_file_paths]
            missing_keywords = [extract_keywords(resume_data, JD) for resume_data in uploaded_file_paths]
        if comp_pressed and uploaded_files is not None and not all(uploaded_files):
                st.alert("Please upload at least one resume file.")

    # Tab Results
    with tab2:
        st.header("Results")
        my_dict = {}
        if comp_pressed and uploaded_files:
            for i in range(len(score)):
                my_dict[uploaded_files[i].name] = score[i]
            sorted_dict = dict(sorted(my_dict.items()))
            for idx, (file_name, score_val) in enumerate(sorted_dict.items()):
                with st.expander(str(file_name)):
                    st.write("Score is: ", score_val)
                    st.write("Missing Keywords:")
                    for keyword in missing_keywords[idx]:
                        st.write(f"- {keyword}")

else:
    # Main content
    tab1, tab2 = st.tabs(["**Home**", "**Results**"])

    # Tab Home
    with tab1:
        st.title("Applicant Tracking System")
        uploaded_files = st.file_uploader(
            '**Choose the resume.pdf file:** ', type="pdf", accept_multiple_files=True)
        JD = st.text_area("**Enter the job description:**")
        with st.expander("Customization Option"):
            threshold = st.slider("Similarity Threshold", min_value=0, max_value=100, value=50)
        comp_pressed = st.button("Compare")
        if comp_pressed and uploaded_files:
            # Streamlit file_uploader gives file-like objects, not paths
            uploaded_file_paths = [extract_pdf_data(
                file) for file in uploaded_files]
            score = compare(uploaded_file_paths, JD, flag)
            # missing_keywords = [extract_keywords(resume_data, JD) for resume_data in uploaded_file_paths]
        if comp_pressed and uploaded_files is not None and not all(uploaded_files):
                st.alert("Please upload at least one resume file.")

    # Tab Results
    with tab2:
        st.header("Results")
        comp_ressed_1 = st.button("Filter")
        my_dict = {}
        if comp_pressed and uploaded_files:
            for i in range(len(score)):
                my_dict[uploaded_files[i].name] = score[i]
            sorted_dict = dict(sorted(my_dict.items()))
            for i in sorted_dict.items():
                with st.expander(str(i[0])):
                    st.write("Score is: ", i[1])
                    if(float(i[1])<threshold):
                        st.write("Not a suitable match")
                    else:
                        st.write("Candidate is eligible for selection")
            
        if comp_ressed_1 and uploaded_files:
            uploaded_file_paths = [extract_pdf_data(
                file) for file in uploaded_files]
            score = compare(uploaded_file_paths, JD, flag)
            
            for i in range(len(score)):
                my_dict[uploaded_files[i].name] = score[i]
            sorted_dict = dict(sorted(my_dict.items()))
            for i in sorted_dict.items():
                with st.expander(str(i[0])):
                    if(float(i[1])>=threshold):
                        st.write("Score is: ", i[1])