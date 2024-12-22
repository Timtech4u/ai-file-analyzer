import streamlit as st
from markitdown import MarkItDown 
from openai import OpenAI
import mimetypes
import os
import tempfile
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
class Config:
    """Application configuration."""
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    MAX_FILE_SIZE: int = int(os.getenv('MAX_FILE_SIZE', '10')) * 1024 * 1024  # MB to bytes
    MODEL_NAME: str = "gpt-4"

# Validate configuration
if not Config.OPENAI_API_KEY:
    st.error("⚠️ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

# Initialize OpenAI client
try:
    client = OpenAI()
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    st.error("Failed to initialize AI services. Please check your configuration.")
    st.stop()

# Type definitions
FileInfo = Dict[str, Dict[str, str]]
HistoryItem = Dict[str, Any]

# Initialize session state for history
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history: List[HistoryItem] = []

# File type definitions with type hints
FILE_TYPES: FileInfo = {
    "pdf": {"icon": "📄", "name": "PDF Document", "mime": "application/pdf"},
    "docx": {"icon": "📝", "name": "Word Document", "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    "pptx": {"icon": "📊", "name": "PowerPoint", "mime": "application/vnd.openxmlformats-officedocument.presentationml.presentation"},
    "xlsx": {"icon": "📈", "name": "Excel Spreadsheet", "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    "jpg": {"icon": "🖼️", "name": "JPEG Image", "mime": "image/jpeg"},
    "jpeg": {"icon": "🖼️", "name": "JPEG Image", "mime": "image/jpeg"},
    "png": {"icon": "🖼️", "name": "PNG Image", "mime": "image/png"},
    "mp3": {"icon": "🎵", "name": "Audio File", "mime": "audio/mpeg"},
    "wav": {"icon": "🎵", "name": "Audio File", "mime": "audio/wav"},
    "html": {"icon": "🌐", "name": "HTML Document", "mime": "text/html"},
    "csv": {"icon": "📊", "name": "CSV File", "mime": "text/csv"},
    "json": {"icon": "📋", "name": "JSON File", "mime": "application/json"},
    "xml": {"icon": "📋", "name": "XML File", "mime": "application/xml"},
    "zip": {"icon": "📦", "name": "ZIP Archive", "mime": "application/zip"},
}

def validate_file(file: Any) -> Tuple[bool, str]:
    """
    Validate the uploaded file.
    
    Args:
        file: The uploaded file object
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if file.size > Config.MAX_FILE_SIZE:
        return False, f"File size exceeds {Config.MAX_FILE_SIZE // (1024*1024)}MB limit"
    
    file_ext = Path(file.name).suffix[1:].lower()
    if file_ext not in FILE_TYPES:
        return False, f"Unsupported file type: {file_ext}"
    
    return True, ""

def generate_smart_summary(text: str, client: OpenAI) -> str:
    """
    Generate an AI-powered summary of the text content.
    
    Args:
        text: The text to summarize
        client: OpenAI client instance
        
    Returns:
        str: Generated summary
        
    Raises:
        Exception: If summary generation fails
    """
    try:
        response = client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=[
                {"role": "system", "content": "Create a concise but informative summary of the following content. Use bullet points if the content is structured."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise Exception(f"Failed to generate summary: {str(e)}")

def save_to_history(filename: str, summary: str, content: str) -> None:
    """
    Save conversion result to history.
    
    Args:
        filename: Name of the processed file
        summary: Generated summary
        content: Full content
    """
    history_item = {
        'timestamp': datetime.now().isoformat(),
        'filename': filename,
        'summary': summary,
        'content': content
    }
    st.session_state.conversion_history.insert(0, history_item)
    # Keep only last 10 items
    st.session_state.conversion_history = st.session_state.conversion_history[:10]

def process_image(image_path: str, client: OpenAI) -> Tuple[str, bytes]:
    """
    Process image and return description and image data.
    
    Args:
        image_path: Path to the image file
        client: OpenAI client instance
        
    Returns:
        Tuple[str, bytes]: (description, image_data)
        
    Raises:
        Exception: If image processing fails
    """
    try:
        # Read image for display
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            
        # Create markdown instance with OpenAI
        markitdown = MarkItDown(mlm_client=client, mlm_model=Config.MODEL_NAME)
        result = markitdown.convert(image_path)
        
        return result.text_content or "No description available.", image_data
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise Exception(f"Image processing failed: {str(e)}")

st.set_page_config(
    page_title="LernUp File Analyzer",
    page_icon="📄",
    layout="centered"  # Changed to centered for better mobile view
)

# Simplified CSS - remove file-type styling
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #1E90FF;
    }
    .upload-message {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
    }
    .main-content {
        max-width: 100%;
        padding: 10px;
    }
    .history-item {
        background-color: #f0f2f6;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        cursor: pointer;
    }
    .history-item:hover {
        background-color: #e0e2e6;
    }
</style>
""", unsafe_allow_html=True)

# Updated title section with enhanced description
st.title("📄 File Analyzer")
st.markdown("""
Transform any document into clear, concise summaries using AI. 
Features intelligent image analysis - our AI can describe images and extract text from them. 
Perfect for quick document analysis and image understanding.

🤖 **AI-Powered Features:**
- Smart document summarization
- Image content description
- Text extraction from images
- Multi-format support
""")

# Updated file types display - simpler version
st.caption("Supported file types:")
cols = st.columns([1] * 4)  # Reduced to 4 columns for mobile
for idx, (ext, info) in enumerate(FILE_TYPES.items()):
    with cols[idx % 4]:
        st.markdown(f"{info['icon']} {ext}")

# Main upload section
uploaded_file = st.file_uploader("Choose a file", 
                                type=list(FILE_TYPES.keys()),
                                help="Select a file to convert to Markdown")

if uploaded_file is not None:
    file_ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
    
    st.info(f"📁 {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

    with st.spinner("Converting and analyzing..."):
        progress_bar = st.progress(0)
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            progress_bar.progress(30)
            
            # Handle images directly
            if file_ext.lower() in ['jpg', 'jpeg', 'png']:
                st.info("🖼️ Analyzing image...")
                try:
                    description, image_data = process_image(tmp_path, client)
                    os.unlink(tmp_path)
                    
                    progress_bar.progress(100)
                    st.success("✨ Analysis complete!")
                    
                    # Create two columns with AI Analysis first
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        st.markdown("### 🤖 AI Image Analysis")
                        st.markdown(description)
                    
                    with col2:
                        with st.expander("📸 View Original Image", expanded=True):
                            if image_data:
                                st.image(image_data, caption="Uploaded Image")
                    
                    save_to_history(uploaded_file.name, "Image Analysis", description)
                except Exception as e:
                    st.error(f"Image analysis error: {str(e)}")
                    if "mlm_client" in str(e):
                        st.info("Please check OpenAI configuration.")
            else:
                # Use MarkItDown for all other file types
                markitdown = MarkItDown(mlm_client=client, mlm_model="gpt-4o")  # Fixed parameter name
                result = markitdown.convert(tmp_path)

                os.unlink(tmp_path)

                text_content = (result.text_content or "").strip()
                if text_content:
                    progress_bar.progress(60)
                    st.info("🤖 Generating AI-powered summary...")
                    
                    summary = generate_smart_summary(text_content, client)
                    
                    # Save to history
                    save_to_history(uploaded_file.name, summary, text_content)
                    
                    progress_bar.progress(100)
                    st.success("✨ Analysis complete!")
                    
                    # Show summary first, then full content (removed download buttons)
                    tab1, tab2 = st.tabs(["📑 Smart Summary", "📝 Full Content"])
                    with tab1:
                        st.markdown("### AI-Generated Summary")
                        st.markdown(summary)
                    with tab2:
                        st.markdown("### Full Converted Content")
                        st.markdown(text_content)
                else:
                    st.warning("⚠️ No text content could be extracted from this file.")
                
        except Exception as e:
            st.error(f"🚨 Error processing file: {str(e)}")
        finally:
            progress_bar.empty()
else:
    st.markdown("""
    <div class="upload-message">
        <p>Upload a file to begin</p>
    </div>
    """, unsafe_allow_html=True)

