# Apeko Website and Admin Dashboard Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [User Interface](#user-interface)
5. [Admin Dashboard](#admin-dashboard)
6. [Customizing the Website](#customizing-the-website)
7. [AI Agent](#ai-agent)
8. [RAG Database](#rag-database)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

## Introduction

Apeko is a comprehensive property appraisal platform that combines traditional appraisal methodologies with cutting-edge AI technology. The platform consists of a customer-facing website and an admin dashboard for managing appraisals, clients, and the AI agent.

### Key Features

- **AI-Powered Appraisals**: Leverage artificial intelligence to assist in property valuations
- **Client Management**: Track and manage client information and interactions
- **Document Management**: Store and organize appraisal documents and related files
- **RAG Database**: Retrieval-Augmented Generation system for providing context-aware responses
- **Analytics Dashboard**: Visualize key metrics and performance indicators

## Installation

### System Requirements

- Python 3.9 or higher
- SQLite (default) or PostgreSQL database
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AppraisalAI.git
   cd AppraisalAI
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python -m app.database.init_db
   ```

5. Start the application:
   ```bash
   python -m app.main
   ```

6. Access the application at http://localhost:8001

## Getting Started

After installation, you'll need to set up your initial admin account:

1. Navigate to http://localhost:8001/admin/login
2. Use the default credentials:
   - Username: admin
   - Password: apeko2025
3. You will be prompted to change your password on first login

## User Interface

The Apeko website consists of several key sections:

### Home Page

The home page showcases the main services offered by Apeko, including:
- Residential Appraisals
- Commercial Appraisals
- Market Analysis
- AI-Assisted Valuations

### Services

Detailed information about each service offered, including:
- Process descriptions
- Pricing information
- Turnaround times
- Sample reports

### About Us

Information about the company, team members, qualifications, and certifications.

### Contact

A contact form and company information for clients to reach out.

## Admin Dashboard

The admin dashboard is the control center for managing all aspects of the Apeko platform.

### Dashboard Overview

The main dashboard displays key metrics:
- Total clients
- Active projects
- Pending requests
- Recent activities

### Clients Management

The clients section allows you to:
- View all clients
- Add new clients
- Edit client information
- Archive inactive clients

### Appraisals Management

The appraisals section allows you to:
- Create new appraisal reports
- Track appraisal status
- Assign appraisers
- Generate final reports

### File Explorer

The file explorer provides:
- Document organization by client and project
- Upload functionality
- Version control
- Search capabilities

### AI Agent

The AI agent section allows you to:
- Interact with the AI assistant
- View chat history
- Configure AI settings
- Train the AI with new data

### RAG Database

The RAG (Retrieval-Augmented Generation) database section allows you to:
- Upload documents to the knowledge base
- Manage document categories
- View query history
- Monitor system performance

### Analytics

The analytics section provides:
- Appraisal volume trends
- Client acquisition metrics
- Revenue analysis
- AI usage statistics

### Settings

The settings section allows you to:
- Manage user accounts
- Configure system settings
- Customize email templates
- Set up integrations

## Customizing the Website

### Modifying Website Content

The website content can be modified by editing the template files located in:
```
app/templates/
```

Key template files include:
- `index.html`: Home page
- `services.html`: Services page
- `about.html`: About page
- `contact.html`: Contact page

### Changing Images

To change images on the website:

1. Prepare your new images with the appropriate dimensions:
   - Hero banner: 1920x1080px
   - Service icons: 512x512px
   - Team photos: 800x800px

2. Place your images in the static directory:
   ```
   app/static/images/
   ```

3. Update the image references in the template files:
   ```html
   <img src="{{ url_for('static', path='/images/your-new-image.jpg') }}" alt="Description">
   ```

### Modifying CSS Styles

To change the website's appearance:

1. Edit the main CSS file:
   ```
   app/static/css/apeko.css
   ```

2. Key style sections:
   - Color scheme variables at the top of the file
   - Typography styles
   - Component-specific styles
   - Responsive design breakpoints

3. Example of changing the primary color:
   ```css
   :root {
     --apeko-primary: #9d0208;  /* Change this to your desired color */
     --apeko-secondary: #dc2f02;
     --apeko-accent: #f48c06;
   }
   ```

### Adding New Pages

To add a new page to the website:

1. Create a new template file in `app/templates/`

2. Add a new route in `app/web/controllers.py`:
   ```python
   @router.get("/your-new-page", response_class=HTMLResponse)
   async def your_new_page(request: Request, db: Session = Depends(get_db)):
       return templates.TemplateResponse(
           "your-new-page.html",
           {"request": request}
       )
   ```

3. Add a link to the new page in the navigation menu in `app/templates/base.html`

## AI Agent

### Configuring the AI Agent

The AI agent is powered by the Nebius API and can be configured in:
```
app/core/config.py
```

Key configuration options:
- `NEBIUS_API_KEY`: Your Nebius API key
- `NEBIUS_API_ENDPOINT`: API endpoint URL
- `NEBIUS_MODEL_NAME`: Model name to use (default: meta-llama/Meta-Llama-3.1-70B-Instruct)

### Training the AI Agent

The AI agent uses a RAG (Retrieval-Augmented Generation) system to provide context-aware responses:

1. Upload relevant documents to the RAG database through the admin dashboard
2. Categorize documents appropriately
3. The AI will automatically use these documents to provide more accurate responses

### Using the AI Agent

To use the AI agent:

1. Navigate to the AI Agent section in the admin dashboard
2. Type your query in the chat interface
3. The AI will respond with information based on its training and the documents in the RAG database
4. You can view the sources used by the AI by clicking "View Sources" below each response

## RAG Database

### Adding Documents

To add documents to the RAG database:

1. Navigate to the RAG Database section in the admin dashboard
2. Click "Add Document"
3. Fill in the document details:
   - Title
   - Document type
   - Upload the document file
   - Add optional description
4. Click "Add Document" to process and index the document

### Document Types

The system supports various document types:
- Appraisal Reports
- Market Analysis
- Regulations
- Property Data
- Other

### Monitoring Performance

The RAG Database dashboard provides metrics on:
- Total documents
- Total chunks
- Query volume
- Relevance scores

## Troubleshooting

### Common Issues

#### Application Won't Start

**Problem**: The application fails to start with an error message.

**Solution**:
1. Check if the correct Python version is installed
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Ensure the database is properly initialized: `python -m app.database.init_db`
4. Check for port conflicts and change the port if needed in `app/core/config.py`

#### Database Errors

**Problem**: Database-related error messages appear.

**Solution**:
1. Verify database connection settings in `app/core/config.py`
2. Ensure the database server is running (if using PostgreSQL)
3. Check database permissions
4. Try reinitializing the database: `python -m app.database.init_db`

#### AI Agent Not Responding

**Problem**: The AI agent doesn't respond to queries.

**Solution**:
1. Verify your Nebius API key in `app/core/config.py`
2. Check internet connectivity
3. Ensure the model name is correct
4. Check the API logs for error messages

## FAQ

### General Questions

**Q: Can I use a different database system?**

A: Yes, the application supports SQLite (default) and PostgreSQL. To switch to PostgreSQL, update the `DATABASE_URL` in `app/core/config.py`.

**Q: How do I backup my data?**

A: For SQLite, copy the `app.db` file. For PostgreSQL, use standard PostgreSQL backup procedures.

**Q: How do I add a new admin user?**

A: Navigate to Settings > User Management in the admin dashboard and click "Add User."

### Customization Questions

**Q: Can I change the logo?**

A: Yes, replace the logo file at `app/static/images/APEKOLOGO.png` with your own logo (maintain the same filename or update references in templates).

**Q: How do I change the color scheme?**

A: Edit the CSS variables in `app/static/css/apeko.css` to change the color scheme throughout the site.

**Q: Can I add custom JavaScript?**

A: Yes, add your custom JavaScript to `app/static/js/` and include it in the templates using:
```html
<script src="{{ url_for('static', path='/js/your-script.js') }}"></script>
```

### Technical Questions

**Q: What AI model is used?**

A: The application uses the Meta-Llama-3.1-70B-Instruct model via the Nebius API.

**Q: How are document embeddings generated?**

A: Document embeddings are generated using the same model as the AI agent, with a dimension of 1536.

**Q: Can I deploy this to a production server?**

A: Yes, for production deployment, we recommend:
1. Using a production ASGI server like Uvicorn or Hypercorn
2. Setting up proper authentication
3. Using PostgreSQL instead of SQLite
4. Configuring HTTPS
5. Setting appropriate environment variables
