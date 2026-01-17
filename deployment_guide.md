# Deploying HOURX to PythonAnywhere (Free Tier)

Since everything is set up in your code, follow these steps on the [PythonAnywhere website](https://www.pythonanywhere.com/).

## Step 1: Get the Code
1.  **Log in** to your PythonAnywhere Dashboard.
2.  Click on **"Consoles"** -> **"Bash"**.
3.  Type this command to download your code:
    ```bash
    git clone https://github.com/Tusarkanta-07/hourx.git
    ```
    *(If it says directory exists, run `cd hourx && git pull` instead)*

## Step 2: Install Dependencies (Django, etc.)
In the same Bash console, run:
```bash
cd hourx
pip install -r requirements.txt
```

## Step 3: Set up Database & Static Files
Still in the console, run these three commands one by one:
```bash
# 1. Prepare the database
python manage.py migrate

# 2. Create the folder for CSS/Images
python manage.py collectstatic
# (Type 'yes' if asked)

# 3. Create your admin account (so you can log in)
python manage.py createsuperuser
```

## Step 4: Configure the Web App
1.  Go to the **"Web"** tab (top right).
2.  Click **"Add a new web app"** -> **"Next"** -> **"Manual Configuration"** (NOT Django) -> **"Python 3.10"** (or whatever version you see).
3.  **Source Code Section**:
    *   Enter path: `/home/yourusername/hourx` (Replace `yourusername` with your actual account name).
4.  **Virtualenv Section**:
    *   Leave empty (since we installed packages globally for free tier).
5.  **Static Files Section**:
    *   **URL**: `/static/`
    *   **Directory**: `/home/yourusername/hourx/staticfiles`
    *(Important: It must end in `staticfiles`, not just `static`)*

## Step 5: Configure the WSGI File
1.  In the **Web** tab, find the "WSGI configuration file" link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`) and click it.
2.  Delete EVERYTHING in that file and paste this:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/hourx'  # <--- CHANGE 'yourusername'
if path not in sys.path:
    sys.path.append(path)

# Set environment variable for settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'hourx.settings'

# Import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
3.  **Save** the file.

## Step 6: Finalize
1.  Go back to the **Web** tab.
2.  Set your Gmail Environment Variables (Optional but recommended):
    *   You can set these in the WSGI file or just rely on the placeholders for now.
3.  Click the big green **"Reload"** button.
4.  Click the link at the top (e.g., `yourusername.pythonanywhere.com`) to see your site!
