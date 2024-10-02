# Project Management

## Getting Started

### Step 1: Clone the Repository

`git clone https://github.com/shawn-carter/ProjectManagemen`

### Step 2: Navigate into the Project Folder

`cd ProjectManagement`

### Step 3: Create a Virtual Environment
Create a new virtual environment to keep dependencies isolated:

`python -m venv venv`

### Step 4: Activate the Virtual Environment

Windows:

`venv\Scripts\activate`

Linux:

`source venv/bin/activate`

### Step 5: Install Requirements
Install all dependencies from the requirements.txt file:

`pip install -r requirements.txt`

### Step 6: Create new SQLite3 DB and import the DBUser model

`python manage.py migrate`

### Step 7: Create a Superuser
Create a superuser to access the admin panel:

`python manage.py createsuperuser`

### Step 8: Collect Static File
If necessary:

`python manage.py collectstatic`

### Step 10: Run the Development Server
Start the development server to ensure everything is working:

`python manage.py runserver`
