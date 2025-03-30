# Appraisal AI Agent

An AI-powered agent application for appraisal companies, built using the Llama Stack Apps framework and Nebius inference API for meta-llama/Meta-Llama-3.1-70B-Instruct.

## Features

### 1. Project Management and Integrated CRM
- Task assignment with deadlines, priorities, and automatic allocation
- Client tracking with history, reminders, and regulatory alerts
- Automated distribution of appraisal cases based on team workload

### 2. Integration with External Databases
- Digital cadastres for property verification
- Financial market APIs for interest rates and market data
- Automatic retrieval of comparable properties

### 3. Analysis and Valuation Tools
- Automated valuation methods (sales comparison, cost, income approaches)
- Advanced financial modeling with scenario simulations
- GIS integration with property value heatmaps

### 4. Report Generation and Regulatory Compliance
- Customizable report templates for different clients
- Multi-platform export options
- Automated compliance checking for various standards (USPAP, IVSC)

### 5. Quality Control
- Role-based access for team collaboration
- Version control and real-time comments
- Inconsistency alerts and plagiarism checks

### 6. Mobile-Friendly Interface
- On-site data capture with geotagged photos
- Property measurement tools

### 7. Security and Scalability
- End-to-end encryption for sensitive data
- Automatic backups
- Modular architecture for extensibility

## Installation

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

4. Set up environment variables:
- Copy `.env.example` to `.env`
- Add your Nebius API key and other configuration

## Usage

### Running the Application

Run both the API server and UI:
```bash
python run.py
```

Run only the API server:
```bash
python run.py --api-only
```

Run only the UI:
```bash
python run.py --ui-only
```

### Accessing the Application

- **Web UI**: http://localhost:7860
- **API Documentation**: http://localhost:8000/api/v1/docs
- **API Redoc**: http://localhost:8000/api/v1/redoc

## Deployment

### Deploying to Render

The AppraisalAI application can be easily deployed to Render using the provided configuration files:

1. Create a Render account at [render.com](https://render.com) if you don't have one already.

2. Connect your GitHub repository to Render:
   - Go to the Render Dashboard
   - Click "New" and select "Blueprint"
   - Connect your GitHub account and select the AppraisalAI repository

3. Configure environment variables:
   - In the Render dashboard, navigate to your service
   - Go to the "Environment" tab
   - Add the following environment variables:
     - `NEBIUS_API_KEY`: Your Nebius API key
     - `SECRET_KEY`: A secure random string for encryption
     - `ENVIRONMENT`: Set to "production"
     - `DEBUG`: Set to "false"

4. Deploy the application:
   - Render will automatically detect the `render.yaml` file and deploy the application
   - The deployment process will take a few minutes
   - Once complete, you can access your application at the provided URL

5. Database setup:
   - The application will use SQLite by default
   - For production, consider using PostgreSQL by updating the `DATABASE_URL` environment variable

### Manual Deployment

You can also deploy the application manually using Docker:

```bash
# Build the Docker image
docker build -t appraisalai .

# Run the container
docker run -p 8002:8002 -e NEBIUS_API_KEY=your_api_key appraisalai
```

## API Endpoints

### Agent
- `POST /api/v1/agent`: Query the AI agent
- `POST /api/v1/agent/execute-tool`: Execute a tool call

### Projects
- `GET /api/v1/projects`: List all projects
- `POST /api/v1/projects`: Create a new project
- `GET /api/v1/projects/{project_id}`: Get project details
- `PUT /api/v1/projects/{project_id}`: Update a project
- `DELETE /api/v1/projects/{project_id}`: Delete a project

### Properties
- `GET /api/v1/properties`: List all properties
- `POST /api/v1/properties`: Create a new property
- `GET /api/v1/properties/{property_id}`: Get property details
- `PUT /api/v1/properties/{property_id}`: Update a property
- `DELETE /api/v1/properties/{property_id}`: Delete a property

### Reports
- `GET /api/v1/reports`: List all reports
- `POST /api/v1/reports`: Create a new report
- `GET /api/v1/reports/{report_id}`: Get report details
- `PUT /api/v1/reports/{report_id}`: Update a report
- `DELETE /api/v1/reports/{report_id}`: Delete a report

### Clients
- `GET /api/v1/clients`: List all clients
- `POST /api/v1/clients`: Create a new client
- `GET /api/v1/clients/{client_id}`: Get client details
- `PUT /api/v1/clients/{client_id}`: Update a client
- `DELETE /api/v1/clients/{client_id}`: Delete a client

## Nebius Integration
To use the Nebius inference API:

1. Create an account on [Nebius](https://studio.nebius.com/)
2. Generate an API key
3. Add the API key to your `.env` file:
```
NEBIUS_API_KEY=your_nebius_api_key_here
NEBIUS_ENDPOINT=https://api.studio.nebius.com/v1/chat/completions
MODEL_NAME=meta-llama/Meta-Llama-3.1-70B-Instruct
```

#### Troubleshooting Nebius API Connection
If you encounter issues connecting to the Nebius API:

1. Verify your API key is valid and has not expired
2. Ensure you're using the correct endpoint format:
   - The base URL should be `https://api.studio.nebius.com/v1/`
   - For chat completions: `https://api.studio.nebius.com/v1/chat/completions`
3. Use the correct model name format: `meta-llama/Meta-Llama-3.1-70B-Instruct`
4. Check that your authentication header uses the Bearer token format:
   ```
   Authorization: Bearer your_api_key_here
   ```
5. Run the test scripts to diagnose connection issues:
   ```bash
   python test_nebius_api.py
   python test_llm_connection.py
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Llama Stack Apps](https://github.com/meta-llama/llama-stack-apps) for the framework
- [Nebius](https://studio.nebius.com/) for the inference API
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Gradio](https://gradio.app/) for the UI components
