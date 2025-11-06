# Dify Project Overview

This document provides a comprehensive overview of the Dify project, its architecture, and instructions for building, running, and contributing to the project.

## Project Overview

Dify is an open-source LLM application development platform. It provides a user-friendly interface for creating and managing AI applications, including features like agentic AI workflows, RAG pipelines, and model management.

The project is composed of two main components:

*   **Backend API:** A Python-based backend built with Flask, responsible for handling business logic, data processing, and communication with the database and other services.
*   **Frontend Web Application:** A Next.js-based frontend that provides the user interface for interacting with the Dify platform.

The project uses Docker Compose for orchestration, making it easy to set up and run all the necessary services in a development environment.

## Building and Running

The recommended way to run Dify is by using Docker Compose.

**Prerequisites:**

*   Docker
*   Docker Compose

**Steps:**

1.  Navigate to the `docker` directory:
    ```bash
    cd docker
    ```
2.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
3.  Start the application using Docker Compose:
    ```bash
    docker-compose up -d
    ```

After the services are up and running, you can access the Dify dashboard at `http://localhost/install` to begin the setup process.

## Development Conventions

### Backend

The backend is a Python project using Flask. Key directories include:

*   `api/controllers`: Contains the API endpoints.
*   `api/services`: Contains the business logic.
*   `api/models`: Contains the database models.
*   `api/tests`: Contains the tests for the backend.

The project uses `pyproject.toml` for dependency management.

### Frontend

The frontend is a Next.js project. Key directories include:

*   `web/app`: Contains the pages and components of the web application.
*   `web/hooks`: Contains custom React hooks.
*   `web/service`: Contains the frontend service layer for making API calls.

The project uses `pnpm` for package management.

### Contributing

Contributions are welcome! Please refer to the `CONTRIBUTING.md` file for guidelines on how to contribute to the project.
