#!/bin/bash

# Exit on error
set -e

# Function to display help message
show_help() {
    echo "Usage: ./docker.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  up           Start all services without rebuilding"
    echo "  build        Build or rebuild services"
    echo "  down         Stop and remove containers, networks"
    echo "  restart      Restart services"
    echo "  logs         View output from containers"
    echo "  shell        Open a shell in the web container"
    echo "  manage       Run Django management commands"
    echo "  test         Run Django tests"
    echo "  help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./docker.sh up              # Start services"
    echo "  ./docker.sh build           # Build services"
    echo "  ./docker.sh down            # Stop services"
    echo "  ./docker.sh restart         # Restart services"
    echo "  ./docker.sh logs            # View logs"
    echo "  ./docker.sh shell           # Open shell"
    echo "  ./docker.sh manage migrate  # Run migrations"
    echo "  ./docker.sh test            # Run all tests"
    echo "  ./docker.sh test apps.user  # Run specific tests"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running or not installed"
    exit 1
fi

# Process commands
case "$1" in
    up)
        echo "Starting services..."
        docker compose up --build
        ;;
    build)
        echo "Building services..."
        docker compose build
        ;;
    down)
        echo "Stopping services..."
        docker compose down
        ;;
    restart)
        echo "Restarting services..."
        docker compose restart
        ;;
    logs)
        echo "Showing logs..."
        docker compose logs -f
        ;;
    shell)
        echo "Opening shell in web container..."
        docker compose exec web bash
        ;;
    manage)
        shift
        echo "Running Django management command: $@"
        docker compose exec web python manage.py "$@"
        ;;
    test)
        shift
        if [ -z "$1" ]; then
            echo "Running all tests..."
            docker compose exec web python manage.py test
        else
            echo "Running tests for $@..."
            docker compose exec web python manage.py test "$@"
        fi
        ;;
    help|*)
        show_help
        ;;
esac
