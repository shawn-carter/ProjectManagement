# DjangoTemplate

This template serves as a starting point for Django projects. It includes the necessary configurations and folder structure to quickly get up and running.

## Getting Started

### Step 1: Clone the Repository

`git clone https://github.com/shawn-carter/DjangoTemplate`

### Step 2: Rename the Folder
You can rename the cloned folder to whatever you like at this point. Use the following commands based on your operating system:

Windows PowerShell:

`move DjangoTemplate NewProject`

Linux:

`mv DjangoTemplate NewProject`

### Step 3: Navigate into the Project Folder

`cd NewProject`

### Step 4: Create a Virtual Environment
Create a new virtual environment to keep dependencies isolated:

`python -m venv venv`

### Step 5: Activate the Virtual Environment

Windows:

`venv\Scripts\activate`

Linux:

`source venv/bin/activate`

### Step 6: Install Requirements
Install all dependencies from the requirements.txt file:

`pip install -r requirements.txt`

### Step 7: Create new SQLite3 DB and import the DBUser model

`python manage.py migrate`

### Step 8: Create a Superuser
Create a superuser to access the admin panel:

`python manage.py createsuperuser`

### Step 9: Collect Static File
If necessary:

`python manage.py collectstatic`

### Step 10: Run the Development Server
Start the development server to ensure everything is working:

`python manage.py runserver`

### Optional: Setting Up Your Own Repository
If you want to create your own repository based on this template, follow these additional steps:

Delete the Existing .git Folder:

Windows:

`rmdir /s /q .git`

Linux/Mac:

`rm -rf .git`

Initialise a New Git Repository:

`git init`

Create a New Repository on GitHub:

Go to GitHub and create a new repository (e.g., NewProject). Copy the repository URL.

Add the New GitHub Remote:

`git remote add origin https://github.com/your-username/NewProject.git`

Stage, Commit, and Push the Template:

`git add .`

`git commit -m "Initial commit based on DjangoTemplate"`

`git push -u origin main`

Additional Notes
Static Files: If you need to run collectstatic, ensure that STATIC_ROOT is set in settings.py.

jQuery: jQuery 3.7.1 is already included in this template for any JavaScript-related functionality.

Modifying the NavBar: The default template includes a navbar with login/logout functionality. Modify it as needed based on your project requirements.

This template is designed to make it easy to start new Django projects with a consistent setup. Enjoy building your applications!
