import streamlit as st
import google.generativeai as genai
from PIL import Image
from typing import Tuple
import logging

# --- Logger Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Gemini Vision Analyzer ---
class GeminiVisionAnalyzer:
    def __init__(self, api_key: str):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini model initialized.")
        except Exception as e:
            logger.error(f"Gemini init failed: {str(e)}")
            raise

    def analyze_image(self, image: Image.Image, question: str) -> Tuple[bool, str]:
        try:
            prompt = f"Please analyze the picture and answer the question: {question}"
            response = self.model.generate_content([prompt, image])
            if response.text:
                return True, response.text
            else:
                return False, "No response from model."
        except Exception as e:
            return False, f"Error: {str(e)}"

# --- Image Validator ---
def validate_image(uploaded_file):
    if uploaded_file is None:
        return False, None, "No file uploaded."
    try:
        if uploaded_file.size > 10 * 1024 * 1024:
            return False, None, "File size exceeds 10MB."
        image = Image.open(uploaded_file)
        if image.mode in ["RGBA", "LA", "P"]:
            image = image.convert("RGB")
        return True, image, "Image validated successfully."
    except Exception as e:
        return False, None, f"Invalid image file: {str(e)}"

# --- Streamlit App ---
def main():
    st.set_page_config(
        page_title="👑 Gemini Vision Analyzer",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- Royal CSS Styling ---
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        color: transparent;
        background-image: linear-gradient(to right, #4b0082, #6a0dad);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.75rem;
        font-weight: bold;
        color: #006400;
        border-bottom: 2px solid #32CD32;
        padding-bottom: 5px;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #eef6ff;
        border-left: 6px solid #1e90ff;
        border-radius: 0.75rem;
        padding: 1rem;
        font-weight: 500;
        color: #003366;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #ffe6e6;
        border-left: 6px solid #b22222;
        border-radius: 0.75rem;
        padding: 1rem;
        font-weight: 500;
        color: #8b0000;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e6fff2;
        border-left: 6px solid #228b22;
        border-radius: 0.75rem;
        padding: 1rem;
        font-weight: 500;
        color: #006400;
        margin: 1rem 0;
    }
    .stButton > button {
        background-color: #6a0dad;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        transition: 0.3s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #8a2be2;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-header'>Gemini Vision Analyzer</div>", unsafe_allow_html=True)

    # --- Sidebar Configuration ---
    with st.sidebar:
        st.markdown("<div class='section-header'>🔐 API Configuration</div>", unsafe_allow_html=True)
        api_key = st.text_input("Enter your Google API Key", type="password")

        if api_key:
            st.markdown('<div class="success-box">✅ API key configured</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
            <strong>Setup Instructions:</strong><br>
            1. Visit <a href="https://makersuite.google.com/" target="_blank">Google AI Studio</a><br>
            2. Enable Gemini API in a new project<br>
            3. Generate your API key<br>
            4. Paste it above to begin
            </div>
            """, unsafe_allow_html=True)

    # --- Layout Columns ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>📤 Upload Image</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload JPG, PNG, or WebP", type=["jpg", "jpeg", "png", "webp"])

        if uploaded_file:
            is_valid, image, msg = validate_image(uploaded_file)
            if is_valid:
                st.image(image, caption="Uploaded Image", use_column_width=True)
                st.markdown(f"<div class='success-box'>{msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='error-box'>{msg}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-header'>❓ Ask About the Image</div>", unsafe_allow_html=True)
        question = st.text_area(
            "Enter your question below",
            placeholder="E.g., Describe the scene. What objects do you see?",
            height=120
        )

        analyze = st.button("🔍 Analyze Image")

        if analyze:
            if not api_key:
                st.markdown("<div class='error-box'>❗ Please provide your API key.</div>", unsafe_allow_html=True)
            elif not uploaded_file:
                st.markdown("<div class='error-box'>❗ Please upload an image.</div>", unsafe_allow_html=True)
            elif not question.strip():
                st.markdown("<div class='error-box'>❗ Please enter a question.</div>", unsafe_allow_html=True)
            else:
                is_valid, image, msg = validate_image(uploaded_file)
                if not is_valid:
                    st.markdown(f"<div class='error-box'>{msg}</div>", unsafe_allow_html=True)
                else:
                    try:
                        with st.spinner("Initializing Gemini..."):
                            analyzer = GeminiVisionAnalyzer(api_key)

                        with st.spinner("Analyzing image..."):
                            success, result = analyzer.analyze_image(image, question)

                        if success:
                            st.markdown("<div class='section-header'>📋 Result</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='success-box'>{result}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='error-box'>{result}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f"<div class='error-box'>🚫 Error: {str(e)}</div>", unsafe_allow_html=True)

    # --- Footer Info ---
    st.markdown("---")
    with st.expander("📘 About This App"):
        st.markdown("""
        **Gemini Vision Analyzer 👑**

        This app uses **Google Gemini 1.5 Flash** model to interpret images and answer user-defined questions.

        **Features**:
        - Royal-themed UI 🌈
        - Image upload & validation 🖼️
        - Live image-based Q&A using Gemini 🤖
        - Secure API usage 🔐

        **Supported Formats:** JPG, JPEG, PNG, WebP  
        **Max Size:** 10MB  
        **Powered by:** Google Generative AI

        ---
        Made with ❤️ using Streamlit and Gemini API  
        👨‍💻 **Created by:** Rohit Sharma  
        📧 **Email:** rohittnps@gmail.com
        """)

if __name__ == "__main__":
    main()
