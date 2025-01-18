
---

# **Basic CI/CD Pipeline with GitHub Actions**

This project demonstrates setting up a **Basic Flask Application** with a **CI/CD Pipeline** using **GitHub Actions**. It automates the testing and deployment of the application to an **AWS EC2 instance** upon successful code changes.

---

## **Table of Contents**
- [**Basic CI/CD Pipeline with GitHub Actions**](#basic-cicd-pipeline-with-github-actions)
  - [**Table of Contents**](#table-of-contents)
  - [**1. Prerequisites**](#1-prerequisites)
  - [**2. Directory Structure**](#2-directory-structure)
  - [**3. Setup Instructions**](#3-setup-instructions)
    - [**A. Setting Up the Flask Application**](#a-setting-up-the-flask-application)
    - [**B. Setting Up the Test Suite**](#b-setting-up-the-test-suite)
    - [**C. Generating and Using an SSH Key**](#c-generating-and-using-an-ssh-key)
      - [**Step 1: Generate an SSH Key on the EC2 Instance**](#step-1-generate-an-ssh-key-on-the-ec2-instance)
      - [**Step 2: Configure the Public Key on the EC2 Instance**](#step-2-configure-the-public-key-on-the-ec2-instance)
      - [**Step 3: Add the Private Key to GitHub Secrets**](#step-3-add-the-private-key-to-github-secrets)
      - [**Step 4: Add EC2 Details to GitHub Secrets**](#step-4-add-ec2-details-to-github-secrets)
    - [**D. Creating the GitHub Actions Workflow**](#d-creating-the-github-actions-workflow)
    - [**E. Deploying to AWS EC2**](#e-deploying-to-aws-ec2)
  - [**4. Verification**](#4-verification)
  - [**5. Screenshots**](#5-screenshots)
    - [**Deployed Webpage**](#deployed-webpage)
    - [**Successful Deployment**](#successful-deployment)
  - [**6. Final Notes**](#6-final-notes)

---

## **1. Prerequisites**

To follow this guide, you need:
- **AWS EC2 Instance** (Ubuntu 22.04 or higher recommended).
- **Python 3.10+** installed on the EC2 instance.
- **GitHub Repository** for your Flask app.
- Basic knowledge of SSH and Git.

---

## **2. Directory Structure**

```plaintext
project2/
├── app/
│   ├── __init__.py         # Initializes the Flask app
│   ├── main.py             # Entry point for the Flask app
│   ├── routes.py           # Defines application routes
│   └── templates/
│       └── index.html      # HTML template for the homepage
├── requirements.txt        # Python dependencies
├── tests/
│   └── test_app.py         # Test file for the application
├── conftest.py             # Pytest configuration file
├── pytest.ini              # Pytest settings file
└── .github/
    └── workflows/
        └── ci-cd.yml       # GitHub Actions workflow file
```

---

## **3. Setup Instructions**


### **A. Setting Up the Flask Application**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/<repository-name>.git
   cd <repository-name>
   ```

2. **Install Dependencies**:
   - Create a virtual environment:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Install required packages:
   - ```bash
     pip install --upgrade pip
     ```
     ```bash
     pip install -r requirements.txt
     ```

3. **Application Files**:
   - **`app/__init__.py`**:
     ```python
     from flask import Flask

     app = Flask(__name__)

     from app import routes
     ```
   - **`app/main.py`**:
     ```python
     import sys
     import os
     import logging
     sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

     from app import app

     if __name__ == "__main__":
     logging.basicConfig(
        filename="flask.log",
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
     )
     app.run(host="0.0.0.0", port=5000, debug=True)

     ```
   - **`app/routes.py`**:
     ```python
     from app import app
     from flask import render_template

     @app.route("/")
     def home():
         return render_template("index.html")
     ```
   - **`app/templates/index.html`**:
     ```html
     <!DOCTYPE html>
     <html lang="en">
     <head>
         <meta charset="UTF-8">
         <meta name="viewport" content="width=device-width, initial-scale=1.0">
         <title>Basic Flask App</title>
     </head>
     <body>
         <h1>Welcome to the Basic Flask App!</h1>
     </body>
     </html>
     ```
   - **`requirements.txt`**:
     ```python
     flask
     pytest
     ```
   - **`conftest.py`**:
     ```python
     import os
     import sys

     def pytest_configure(config):
     # Add the current directory to the Python path
     sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
     ```
   - **`pytest.ini`**:
     ```python
     [pytest]
     ```

4. **Run the Flask App**:
   ```bash
   python app/main.py
   ```
   Access the app at: `http://127.0.0.1:5000`.

---

### **B. Setting Up the Test Suite**

1. **Create the Test File**:
   - **`tests/test_app.py`**:
     ```python
     import pytest
     from app import app

     @pytest.fixture
     def client():
         app.config['TESTING'] = True
         with app.test_client() as client:
             yield client

     def test_home(client):
         response = client.get("/")
         assert response.status_code == 200
         assert b"Welcome to the Basic Flask App!" in response.data
     ```

2. **Run Tests**:
   ```bash
   pytest
   ```

---

### **C. Generating and Using an SSH Key**

GitHub Actions needs secure access to the EC2 instance to deploy the Flask app. This is achieved by generating and using an SSH key pair **on the EC2 instance**.

#### **Step 1: Generate an SSH Key on the EC2 Instance**
1. SSH into your EC2 instance:
   ```bash
   ssh -i /path/to/your-ec2-key.pem ubuntu@<EC2-Public-IP>
   ```

2. Generate the SSH key pair:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github_deploy_key" -f ~/.ssh/github_deploy_key
   ```
   - This creates two files:
     - Private key: `/home/ubuntu/.ssh/github_deploy_key`
     - Public key: `/home/ubuntu/.ssh/github_deploy_key.pub`

---

#### **Step 2: Configure the Public Key on the EC2 Instance**
1. Add the public key to `~/.ssh/authorized_keys`:
   ```bash
   cat ~/.ssh/github_deploy_key.pub >> ~/.ssh/authorized_keys
   ```
2. Set appropriate permissions:
   ```bash
   chmod 600 ~/.ssh/authorized_keys
   ```

---

#### **Step 3: Add the Private Key to GitHub Secrets**
1. Copy the private key:
   ```bash
   cat ~/.ssh/github_deploy_key
   ```
2. Add it to your GitHub repository:
   - Navigate to **Settings > Secrets and variables > Actions > New repository secret**.
   - Add a secret with:
     - **Name:** `EC2_SSH_KEY`
     - **Value:** Paste the private key.

---

#### **Step 4: Add EC2 Details to GitHub Secrets**
- **`EC2_HOST`**: Add the public IP of the EC2 instance.
- **`EC2_USER`**: Add the username (`ubuntu`).

---

### **D. Creating the GitHub Actions Workflow**

1. **Create Workflow File**:
   - **`ci-cd.yml`**:
     ```yaml
     name: Deploy to AWS EC2

     on:
       push:
         branches:
           - main

     jobs:
       deploy:
         name: Deploy to AWS EC2
         runs-on: ubuntu-latest

         steps:
           - name: Checkout code
             uses: actions/checkout@v3

           - name: Set up SSH
             run: |
               mkdir -p ~/.ssh
               echo "${{ secrets.EC2_SSH_KEY }}" > ~/.ssh/id_rsa
               chmod 600 ~/.ssh/id_rsa
               ssh-keyscan -H ${{ secrets.EC2_HOST }} >> ~/.ssh/known_hosts

           - name: Deploy to EC2
             run: |
               ssh ${{ secrets.EC2_USER }}@${{ secrets.EC2_HOST }} << 'EOF'
               cd ~/project2-test
               git pull origin main
               source venv/bin/activate
               pip install --upgrade pip
               pip install -r requirements.txt
               nohup /home/ubuntu/project2-test/venv/bin/python app/main.py > flask.log 2>&1 &
               EOF

           - name: Verify Flask log
             run: |
               ssh ${{ secrets.EC2_USER }}@${{ secrets.EC2_HOST }} << 'EOF'
               cd ~/project2-test
               tail -n 10 flask.log || echo "Unable to read flask.log"
               EOF
     ```

2. **Set Up GitHub Secrets**:
   - **`EC2_SSH_KEY`**: Private SSH key for EC2 instance.
   - **`EC2_HOST`**: EC2 instance public IP.
   - **`EC2_USER`**: Default EC2 username (e.g., `ubuntu`).

3. **Push Changes**:
   ```bash
   git add .
   git commit -m "Add CI/CD workflow"
   git push origin main
   ```

---

### **E. Deploying to AWS EC2**

1. **Set Up AWS EC2**:
   - Launch an Ubuntu instance.
   - Configure security groups to allow SSH (port 22) and HTTP (port 5000).

2. **Deploy Using GitHub Actions**:
   - Monitor the **Actions** tab in your GitHub repository.
   - Verify successful deployment.

---

## **4. Verification**

- **Access the Application**:
  Visit `http://<EC2-Public-IP>:5000` in your browser to confirm the app is running.

- **Check Logs**:
   SSH into the instance and verify the logs:
   ```bash
   tail -f ~/project2-test/flask.log
   ```

---

## **5. Screenshots**

### **Deployed Webpage**
![Webpage Screenshot](Screenshot%20from%202025-01-18%2016-20-51.png)

### **Successful Deployment**
![GitHub Actions Workflow](Screenshot%20from%202025-01-18%2016-21-54.png)

---

## **6. Final Notes**

This guide provides step-by-step instructions to set up a basic CI/CD pipeline for a Flask app with GitHub Actions. It includes:
- Application setup.
- Automated testing.
- Secure deployment using SSH to an AWS EC2 instance.

--- 
