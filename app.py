import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import base64
from textwrap import dedent
from googletrans import Translator  # Example for translation, install googletrans library

# Function to generate transcript in English
def generate_transcript(video_id, language='en'):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        script = ""
        for text in transcript:
            t = text["text"]
            if t != '[Music]':
                script += t + " "
        return script, len(script.split())
    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
        return None, 0
    except NoTranscriptFound:
        st.error("No transcript found for this video.")
        return None, 0
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None, 0

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="YouTube Summarizer",
    page_icon='favicon.ico',
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide Streamlit Footer and buttons
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.css-1l02zno {padding: 0 !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Adding logo for the App
file_ = open("app_logo.gif", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()

st.sidebar.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="" style="height:300px; width:400px;">',
    unsafe_allow_html=True,
)

# Set background color
st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6;
    }
    .summary-container {
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 20px;
        background-color: #ADD8E6;
        margin-bottom: 20px;
    }
    .summary-container h3 {
        color: #333;
    }
    .summary-container p {
        color: #555;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Input Video Link
url = st.sidebar.text_input('Video URL', 'https://www.youtube.com/watch?v=TOosNVLqXZ8')

# Extract video ID from URL
parsed_url = urlparse(url)
if parsed_url.hostname == 'youtu.be':
    video_id = parsed_url.path[1:]
else:
    video_id = parse_qs(parsed_url.query)['v'][0]

if video_id:
    try:
        # Display Video and Title
        r = requests.get(url)
        soup = BeautifulSoup(r.text, features="html.parser")
        link = soup.find_all(name="title")[0]
        title = str(link).replace("<title>","").replace("</title>","").replace("&amp;","&")
        st.info("### " + title)

        # Display Video
        st.video(url)

        # Specify Summarization type
        sumtype = st.sidebar.selectbox(
            'Specify Summarization Type',
            options=['Extractive', 'Abstractive (Subtitles)'],
            index=0,
            format_func=lambda x: 'Select an option' if x == '' else x,
            disabled=False
        )

        if sumtype == 'Extractive':
            # Specify the summary length
            length = st.sidebar.select_slider(
                'Specify length of Summary',
                options=['10%', '20%', '30%', '40%', '50%']
            )

            if st.sidebar.button('Summarize'):
                st.success("### Success! Extractive summary generated.")

                # Generate Transcript
                transcript, no_of_words = generate_transcript(video_id, language='hi')

                if transcript:
                    # Example translation to English using googletrans (replace with your actual translation method)
                    translator = Translator()
                    translated_text = translator.translate(transcript, src='hi', dest='en').text

                    # Generate summary using Spacy or BART (not shown here for brevity)
                    # Replace with your summarization function call

                    # Display Transcript
                    st.markdown(dedent(f"""
                    <div class="summary-container">
                        <h3>\U0001F4D6 Summary</h3>
                        <p>{translated_text}</p>
                    </div>
                    """), unsafe_allow_html=True)

        elif sumtype == 'Abstractive (Subtitles)':
            if st.sidebar.button('Summarize'):
                st.success("### Success! Subtitles generated.")

                # Generate Transcript
                transcript, no_of_words = generate_transcript(video_id, language='hi')

                if transcript:
                    # Example translation to English using googletrans (replace with your actual translation method)
                    translator = Translator()
                    translated_text = translator.translate(transcript, src='hi', dest='en').text

                    # Display subtitles inside a bordered container
                    st.markdown(dedent(f"""
                    <div class="summary-container">
                        <h3>\U0001F3A5 Subtitles</h3>
                        <p>{translated_text}</p>
                    </div>
                    """), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    st.error("Invalid YouTube URL. Please provide a valid URL.")

# Add Sidebar Info
st.sidebar.info(
    dedent(
        """
        This web app is made by\n
        TEAM - 4
        """
    )
)
