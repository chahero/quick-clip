#!/bin/bash

# quick-clip Management Script
# Usage: ./manage.sh [start|stop|restart|status|logs|install|setup|help]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="quick-clip"
PID_FILE="app.pid"
LOG_FILE="app.log"
VENV_DIR=".venv"
PYTHON_CMD="python3"
MAIN_SCRIPT="main.py"
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Print colored messages
print_info() {
    echo -e "${BLUE}ℹ  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✔ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠  $1${NC}"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found"
        print_info "Run './manage.sh install' to create it"
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        # shellcheck disable=SC1091
        source "$VENV_DIR/bin/activate"
    fi
}

detect_python() {
    if command -v "$PYTHON_CMD" >/dev/null 2>&1; then
        return
    fi

    if command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
        return
    fi

    print_error "python3 (or python) not found"
    exit 1
}

# Install dependencies
install() {
    detect_python

    print_info "Creating virtual environment..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"

    print_info "Activating virtual environment..."
    activate_venv

    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel

    print_info "Installing dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup environment
setup() {
    print_info "Setting up application..."

    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            print_info "Creating .env from .env.example..."
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            print_warning "Please edit .env with your configuration"
        else
            print_error ".env file not found"
            exit 1
        fi
    else
        print_success ".env file already exists"
    fi
}

# Start application
start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            print_warning "Application is already running (PID: $PID)"
            return
        else
            print_info "Removing stale PID file..."
            rm "$PID_FILE"
        fi
    fi

    check_venv
    detect_python
    activate_venv

    print_info "Starting $APP_NAME..."

    # Start the application in background
    nohup "$PYTHON_CMD" "$MAIN_SCRIPT" > "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"

    # Wait a moment to check if process started successfully
    sleep 2
    if kill -0 "$NEW_PID" 2>/dev/null; then
        print_success "$APP_NAME started successfully (PID: $NEW_PID)"
        print_info "Log file: $LOG_FILE"
    else
        print_error "Failed to start $APP_NAME"
        print_info "Check log file: $LOG_FILE"
        rm "$PID_FILE"
        exit 1
    fi
}

# Stop application
stop() {
    if [ ! -f "$PID_FILE" ]; then
        print_warning "Application is not running"
        return
    fi

    PID=$(cat "$PID_FILE")

    if ! kill -0 "$PID" 2>/dev/null; then
        print_warning "Process with PID $PID not found"
        rm "$PID_FILE"
        return
    fi

    print_info "Stopping $APP_NAME (PID: $PID)..."

    # Try graceful shutdown first
    kill "$PID"

    # Wait for process to terminate
    for i in {1..10}; do
        if ! kill -0 "$PID" 2>/dev/null; then
            print_success "$APP_NAME stopped successfully"
            rm "$PID_FILE"
            return
        fi
        sleep 1
    done

    # Force kill if necessary
    print_warning "Forcing shutdown..."
    kill -9 "$PID"
    sleep 1
    rm "$PID_FILE"
    print_success "$APP_NAME stopped"
}

# Restart application
restart() {
    print_info "Restarting $APP_NAME..."
    stop
    sleep 1
    start
}

# Check status
status() {
    if [ ! -f "$PID_FILE" ]; then
        print_warning "$APP_NAME is not running"
        return 1
    fi

    PID=$(cat "$PID_FILE")

    if kill -0 "$PID" 2>/dev/null; then
        print_success "$APP_NAME is running (PID: $PID)"
        return 0
    else
        print_error "$APP_NAME is not running"
        rm "$PID_FILE"
        return 1
    fi
}

# Show logs
logs() {
    if [ ! -f "$LOG_FILE" ]; then
        print_warning "Log file not found: $LOG_FILE"
        return
    fi

    print_info "Showing logs (press Ctrl+C to exit)..."
    tail -f "$LOG_FILE"
}

# Display help
help() {
    cat << EOF
${BLUE}quick-clip Management Script${NC}

${YELLOW}Usage:${NC}
    ./manage.sh [command]

${YELLOW}Commands:${NC}
    install       Install dependencies and create virtual environment
    setup         Setup .env configuration file
    start         Start the application
    stop          Stop the application
    restart       Restart the application
    status        Show application status
    logs          Show application logs (tail -f)
    help          Show this help message

${YELLOW}Examples:${NC}
    ./manage.sh install       # First time setup
    ./manage.sh setup         # Create .env from .env.example
    ./manage.sh start         # Start the application
    ./manage.sh status        # Check if running
    ./manage.sh logs          # View logs
    ./manage.sh restart       # Restart the application

${YELLOW}Quick Start:${NC}
    1. ./manage.sh install
    2. ./manage.sh setup
    3. ./manage.sh start
    4. Check http://localhost:8000

EOF
}

# Main script logic
case "${1:-help}" in
    install)
        install
        ;;
    setup)
        setup
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    help)
        help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        help
        exit 1
        ;;
esac
