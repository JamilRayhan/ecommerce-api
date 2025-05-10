# Docker Setup for E-commerce API

This document provides instructions for running the E-commerce API using Docker and Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Services

The Docker setup includes the following services:

1. **web**: The Django application
2. **db**: PostgreSQL database
3. **valkey**: Redis alternative for caching
4. **mailpit**: Email testing service
5. **pgadmin**: PostgreSQL admin interface (development only)

## Configuration Files

- `docker-compose.yml`: Base configuration for all environments
- `docker-compose.override.yml`: Development-specific overrides (used by default)
- `docker-compose.prod.yml`: Production-specific configuration
- `.env.docker`: Environment variables for Docker development
- `Dockerfile`: Instructions for building the application container
- `docker-entrypoint.sh`: Startup script for the application container
- `docker.sh`: Helper script for common Docker operations

## Development Setup

1. **Build and start the services**:

   ```bash
   # First time setup (builds the image)
   ./docker.sh build
   ./docker.sh up

   # Subsequent runs (no rebuild needed)
   ./docker.sh up
   ```

2. **Access the services**:

   - Django application: http://localhost:8000
   - Mailpit web interface: http://localhost:8025
   - PgAdmin: http://localhost:5050 (login with admin@example.com / admin)

3. **Run management commands**:

   ```bash
   ./docker.sh manage <command>

   # Examples:
   ./docker.sh manage migrate
   ./docker.sh manage createsuperuser
   ```

4. **Run tests**:

   ```bash
   ./docker.sh test

   # Run specific tests:
   ./docker.sh test apps.user
   ```

5. **Open a shell in the container**:

   ```bash
   ./docker.sh shell
   ```

## Production Setup

1. **Create a production environment file**:

   ```bash
   cp .env.docker .env.prod
   ```

   Edit `.env.prod` to set secure values for production.

2. **Build and start the production services**:

   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
   ```

3. **Access the application**:

   - Production application: http://localhost (port 80)

## Email Testing with Mailpit

Mailpit provides a simple SMTP server for testing email functionality without sending real emails. All emails sent by the application in development will be captured by Mailpit and can be viewed in its web interface.

- SMTP server: mailpit:1025
- Web interface: http://localhost:8025

## Caching with Valkey

Valkey is a Redis-compatible in-memory data store used for caching. The application is configured to use Valkey for caching when running in Docker.

## Database Management with PgAdmin

PgAdmin provides a web interface for managing PostgreSQL databases. To connect to the database:

1. Access PgAdmin at http://localhost:5050
2. Login with admin@example.com / admin
3. Add a new server with the following details:
   - Name: ecommerce_db
   - Host: db
   - Port: 5432
   - Username: postgres
   - Password: postgres

## Troubleshooting

- **Database connection issues**: Ensure the database container is running and healthy.
- **Permission issues**: Check that the application has the necessary permissions to write to mounted volumes.
- **Container startup failures**: Check the logs with `docker-compose logs <service>`.

## Cleanup

- **Stop all services**:

  ```bash
  docker-compose down
  ```

- **Remove volumes** (will delete all data):

  ```bash
  docker-compose down -v
  ```
