# File Analyzer

An AI-powered file analysis tool that converts various document formats into clear, concise summaries using OpenAI.

## Features

- 📄 Supports multiple file formats (PDF, DOCX, PPTX, Images, etc.)
- 🤖 AI-powered document summarization
- 🖼️ Intelligent image analysis and text extraction
- 📊 Text extraction from various formats
- 📱 Mobile-friendly interface
- 🔄 Conversion history tracking
- 🔒 Secure file handling
- ⚡ Fast processing

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/timtech4u/ai-file-analyzer.git
cd file-analyzer
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
DEBUG=False
MAX_FILE_SIZE=10  # in MB
```

## Usage

### Running Locally

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Visit `http://localhost:8501` in your web browser.

### Docker Deployment

#### Using Pre-built Image (Recommended)

The easiest way to run File Analyzer is using our pre-built Docker image:

```bash
docker pull ghcr.io/timtech4u/ai-file-analyzer:latest
docker run -p 8501:8501 -e OPENAI_API_KEY=your-api-key ghcr.io/timtech4u/ai-file-analyzer:latest
```

Available tags:
- `latest`: Latest stable release
- `vX.Y.Z`: Specific version releases
- `main`: Latest development build

#### Building Locally

If you prefer to build the image yourself:

1. Build the Docker image:
```bash
docker build -t file-analyzer .
```

2. Run the container:
```bash
docker run -p 8501:8501 -e OPENAI_API_KEY=your-api-key file-analyzer
```

## API Documentation

### File Processing

The application processes files through several stages:

1. **Upload**: Files are temporarily stored and validated
2. **Processing**: Content is extracted based on file type
3. **Analysis**: AI generates summaries and extracts key information
4. **Response**: Results are displayed and stored in history

### Supported File Types

| Type | Extensions | Features |
|------|------------|----------|
| Documents | PDF, DOCX, PPTX, XLSX | Full text extraction, summarization |
| Images | JPG, PNG | OCR, content description |
| Audio | MP3, WAV | Transcription (coming soon) |
| Web/Data | HTML, CSV, JSON, XML | Structure preservation |
| Archives | ZIP | Content listing |

## Development

### Project Structure

```
file-analyzer/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── Dockerfile         # Container configuration
├── .env              # Environment variables
└── tests/            # Test suite
```

### Running Tests

```bash
pytest tests/
```

### Code Style

This project follows PEP 8 guidelines. Run linting with:
```bash
flake8 .
```

## Error Handling

The application implements comprehensive error handling:

- File validation errors
- API connection issues
- Processing timeouts
- Size limit exceeded
- Unsupported file types

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Add tests for new features
- Update documentation
- Follow the existing code style
- Add type hints to new functions
- Include error handling

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI](https://openai.com/)
- Uses [MarkItDown](https://github.com/markitdown/markitdown) for file conversion

## Support

For support, please open an issue in the GitHub repository.