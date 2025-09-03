# WASDE PDF Summarizer

A FastAPI-based application for extracting, processing, and summarizing commodity information from USDA WASDE (World Agricultural Supply and Demand Estimates) PDF reports using AI-powered analysis.

## Overview

This application provides an intelligent PDF processing system that can extract text from WASDE reports, vectorize the content for semantic search, and generate summaries or answer questions about agricultural commodity data using Large Language Models (LLMs).

## Features

- **PDF Processing**: Extract and parse WASDE PDF reports into structured text chunks
- **Vector Search**: Store and retrieve document content using ChromaDB for semantic similarity search
- **AI-Powered Analysis**: Leverage OpenAI's GPT models for intelligent summarization and Q&A
- **RESTful API**: Clean FastAPI interface for all operations
- **Chat Interface**: Interactive chat functionality for querying processed documents
- **Modular Architecture**: Well-organized service-based structure for maintainability

## Project Structure

```
summarizer/
├── app/
│   ├── pydantics/          # Pydantic models for data validation
│   │   └── models.py       # Request/response models
│   ├── routers/            # API route handlers
│   │   ├── chat_router.py  # Chat endpoints
│   │   ├── health_router.py # Health check endpoints
│   │   └── pdf_router.py   # PDF processing endpoints
│   ├── services/           # Business logic layer
│   │   ├── chat_service.py # Chat functionality
│   │   ├── llm_service.py  # LLM integration
│   │   ├── pdf_service.py  # PDF extraction
│   │   ├── streamlit_service.py # Streamlit utilities
│   │   └── vector_service.py # Vector database operations
│   └── templates/          # Prompt templates
│       └── prompt_template.py
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── .env                   # Environment variables (not tracked)
```

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd summarizer
```

2. Create a virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix/MacOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the project root with the following variables:
```env
OPENAI_API_KEY=your_openai_api_key
VECTOR_PERSIST=false
EMBEDDING_MODEL=all-MiniLM-L6-v2
API_BASE_URL=http://127.0.0.1:8000
```

## Usage

### Starting the Server

Run the application:
```bash
python main.py
```

The server will start at `http://127.0.0.1:8000`

### API Documentation

Once running, access the interactive API documentation:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### API Endpoints

#### Health Check
- `GET /` - Root endpoint with API information
- Health router endpoints for server status monitoring

#### PDF Processing
- `POST /upload-pdf` - Upload and process a WASDE PDF
  - Parameters:
    - `file`: PDF file to upload
    - `operation`: "summarize" or "chat" mode
  - Returns: Processing result with extracted content or summary

#### Chat Interface
- Chat endpoints for interactive Q&A with processed documents

## Key Components

### PDF Service
Extracts text from PDF files and splits them into manageable chunks (10 pages per part) for processing. Extracted text is stored in the `app/utils/` directory organized by document name.

### Vector Service
Manages document embeddings using ChromaDB and Sentence Transformers for semantic search capabilities. This enables context-aware retrieval for chat and summarization.

### LLM Service
Integrates with OpenAI's GPT models to provide intelligent summarization and question-answering capabilities based on the processed PDF content.

### Chat Service
Handles interactive chat sessions, maintaining context and providing relevant responses based on the vectorized document content.

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **PyMuPDF (fitz)**: PDF text extraction
- **OpenAI API**: Large Language Model integration
- **ChromaDB**: Vector database for semantic search
- **Sentence Transformers**: Document embedding generation
- **NLTK**: Natural language processing utilities
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for FastAPI
- **Streamlit**: Web app framework (for potential UI extensions)

## Configuration

The application uses environment variables for configuration. Key settings include:

- `OPENAI_API_KEY`: Required for LLM functionality (must be provided by user)
- `VECTOR_PERSIST`: Set to `false` for non-persistent vector storage
- `EMBEDDING_MODEL`: Uses `all-MiniLM-L6-v2` for document embeddings
- `API_BASE_URL`: Default is `http://127.0.0.1:8000`
- API host and port can be configured in `main.py`
- CORS settings are configured to allow all origins (modify for production)

## Development

### Running in Development Mode

The application runs with auto-reload enabled by default when started with:
```bash
python main.py
```

### Adding New Features

1. Create new service classes in `app/services/`
2. Add corresponding routers in `app/routers/`
3. Define data models in `app/pydantics/`
4. Include new routers in `main.py`

## Error Handling

The application includes comprehensive error handling for:
- Invalid PDF files
- API failures
- Missing environment variables
- Processing errors

Errors are returned with appropriate HTTP status codes and descriptive messages.

## Security Considerations

- Store sensitive configuration in environment variables
- The current CORS configuration allows all origins - restrict this in production
- Validate and sanitize all user inputs
- Implement rate limiting for production deployments
- Add authentication/authorization as needed

## License

[Specify your license here]

## Support

For issues, questions, or contributions, please [specify contact information or contribution guidelines].