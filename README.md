# AI-Powered Appraisal System

An advanced AI-powered appraisal system for real estate valuation and property assessment.

## Features

- Project Management & CRM Integration
- Automated Valuation Methods
- Advanced Financial Modeling
- Image Recognition & AI Analysis
- Report Generation & Compliance
- Mobile Fieldwork Tools
- Security & Scalability

## Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
app/
├── api/              # API endpoints
├── core/             # Core application logic
├── models/           # Database models
├── services/         # Business services
├── tools/            # AI tools and integrations
└── utils/           # Utility functions
```

## Environment Variables

Create a `.env` file with the following variables:

```
# Database
DATABASE_URL=sqlite:///./appraisal.db

# Llama Stack
LLAMA_API_KEY=your_api_key
LLAMA_API_URL=http://localhost:8321

# External Services
MLS_API_KEY=your_mls_key
COSTAR_API_KEY=your_costar_key
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
