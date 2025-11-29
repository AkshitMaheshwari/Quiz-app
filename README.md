# Quiz Master Application

This is a full-fledged Quiz Master website built with Python and Flask.

## Features

- User Authentication (Login/Register)
- Admin Dashboard
- Quiz Management (Create, Edit, Delete Quizzes)
- Subject and Chapter Management
- User Score Tracking
- Search Functionality

## Prerequisites

- Python 3.x installed on your system.

## Installation

1.  Clone the repository (if you haven't already):
    ```bash
    git clone <your-repo-url>
    cd <your-repo-folder>
    ```

2.  Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    ```

3.  Activate the virtual environment:
    -   **Windows:**
        ```bash
        venv\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  Initialize the database (if needed):
    The application is set up to create the database tables automatically on the first run.

2.  Run the application:
    ```bash
    python app.py
    ```

3.  Open your web browser and go to `http://127.0.0.1:5000`.

## Default Admin Credentials

-   **Username:** admin@example.com
-   **Password:** admin123

## Project Structure

-   `app.py`: Main application entry point.
-   `controllers/`: Contains the route handlers (admin, auth, main).
-   `models/`: Database models.
-   `templates/`: HTML templates.
-   `static/`: Static files (CSS, JS, images).
-   `instance/`: Instance-specific files (database, etc.).

## Deployment

To deploy this application, ensure you set the `SECRET_KEY` environment variable in your production environment and use a production-ready WSGI server like Gunicorn.
