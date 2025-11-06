# Dialpad Framework Automation

## Overview
This is an automated framework for Dialpad application development and testing.

## Project Structure

- **client/** - Frontend Vue.js application
- **server/** - Backend Python (Sanic) server
- **devops/** - Docker, Terraform, and deployment configurations
- **data/** - Endpoint definitions and configuration data
- **.github/workflows/** - CI/CD automation workflows

## Prerequisites

- Python 3.8+
- Node.js 20+
- Docker (for containerized deployment)

## Setup Instructions

### Server Setup
```bash
cd server
pip install -r requirements/dev.txt
python server.py
```

### Client Setup
```bash
cd client
npm install
npm run dev
```

## Development

### Running Tests
```bash
# Server tests
cd server
pytest tests/

# Client tests
cd client
npm test
```

### Docker Deployment
```bash
cd devops/docker/compose
docker-compose up -d
```

## Configuration

- Endpoints are defined in `data/endpoints.json`
- Environment variables can be managed through `devops/` scripts
- Client configuration is in `client/src/config.js`
- Server configuration is in `server/core/config.py`

## Contributing

1. Create a feature branch (`DI-XXX`)
2. Make your changes
3. Submit a pull request to `main`

## Automated Workflows

- **Auto Generate Code**: Automatically generates code when `data/endpoints.json` changes
- **Auto Generate README**: Updates this README on main branch pushes

## License

Copyright © 2025 Dialpad. All rights reserved.

---
*Last updated: 2025-11-06*
