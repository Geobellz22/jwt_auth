# jwt_auth
this is a django backend project
gunicorn has been installed
update settings

## **Installation**

Follow these steps to set up the project locally:

### **Prerequisites**
- Python 3.x
- Pip
- Django (>= 4.x)
- Django REST Framework (>= 3.x)

### **Setup Instructions**
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   ```
2. Create and activate a virtual environment:
    ```bash
    python3 -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
    ```
3. Install dependencies:
    ```bash
    pip install -r jwt_auth/requirements.txt
    ```

4. Run migrations:
    ```bash
    python manage.py migrate
    ```

5. Start the development server:
    ```bash
    python manage.py runserver
    ```

6. Managing Dependencies
    The project uses a requirements.txt file to manage Python dependencies.

    Adding New Dependencies
    Install the library using pip:
    ```bash
    pip install library-name
    ```
    Add the dependency to requirements.txt:

    ```bash
    pip freeze > jwt_auth/requirements.txt
    ```
    Alternatively, append the new library directly:

    ```bash
    echo "library-name==version" >> requirements.txt
    ```
    Commit the updated requirements.txt:

    ```bash
    git add requirements.txt
    git commit -m "Added library-name to requirements"
    ```
    Installing Dependencies
    To install all dependencies listed in requirements.txt, run:

    ```bash
    pip install -r jwt_auth/requirements.txt
    ```

    Upgrading Dependencies
    Upgrade a specific library:

    ```bash
    pip install --upgrade library-name
    ```
    Update the requirements.txt file:

    ```bash
    pip freeze > jwt_auth/requirements.txt
    ```