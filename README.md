# RealtimeCollab Backend

This is the backend for the RealtimeCollab application. It is built with Django and Django Channels to support real-time collaboration features. The backend uses PostgreSQL as the database and Redis for channel layers.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Setup Instructions

Follow the steps below to set up and run the backend using Docker.

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/VishnuJampalaUB/realtimecollab-backend.git
cd realtimecollab-backend
```

### 2. Build and Run Docker Containers

```bash
docker-compose up --build
```

### 3. Apply Migrations

```bash
docker-compose exec backend python manage.py migrate
```

### 4. Create a Superuser

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 5. Access the Application

The backend server will be running on http://localhost:8000.

### 6. Configuration

The environment variables for this project are specified in the `docker-compose.yml` file. These settings are crucial for connecting to the database and securing the Django application.

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgres://vishnu:vishnu123@db:5432/collabdb
      - SECRET_KEY=your_secret_key_here

  db:
    environment:
      - POSTGRES_DB=collabdb
      - POSTGRES_USER=vishnu
      - POSTGRES_PASSWORD=vishnu123

