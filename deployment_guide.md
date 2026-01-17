# Deploying HOURX to PythonAnywhere (Free Tier)

Since everything is set up in your code, follow these steps on the [PythonAnywhere website](https://www.pythonanywhere.com/).

## Step 1: Update Your Code
1.  **Log in** to your PythonAnywhere Dashboard.
2.  Click on **"Consoles"** -> **"Bash"**.
3.  Navigate to your project folder:
    ```bash
    cd hourx
    ```
4.  Pull the latest "Professional UI" changes:
    ```bash
    git pull
    ```

## Step 2: Install Dependencies (If not done)
```bash
pip install -r requirements.txt
```

## Step 3: IMPORTANT - Update Static Files
This is the step that fixes the "broken layout" issue. Run this command:

```bash
python manage.py collectstatic
```
> **Type `yes` and hit Enter** when asked if you want to overwrite existing files.

## Step 4: Configure the Web App (If not done)
1.  Go to the **"Web"** tab (top right).
2.  **Static Files Section**:
    *   **URL**: `/static/`
    *   **Directory**: `/home/yourusername/hourx/staticfiles`
    *(Important: It must end in `staticfiles`, not just `static`)*

## Step 5: Reload
1.  Go to the **Web** tab.
2.  Click the big green **"Reload"** button.
3.  Click the link at the top (e.g., `yourusername.pythonanywhere.com`) to see your **Premium, Styled Site**!
