# Windows Local Execution Guide

## Supported Windows Version
* Windows 10 / 11

## Required Runtime and Versions
* Python 3.10+
* Git for Windows

## Installation Steps
1. Clone the repository: `git clone https://github.com/javierb507/darmasala-community.git`
2. Create virtual environment: `python -m venv venv`
3. Activate environment: `.\venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`

## Environment Variable Configuration
Create a `.env` file from the example:
```powershell
copy .env.example .env
```

## Application Start Instructions
```powershell
python app.py
```
Default port: 5001

## Troubleshooting Section
* **Database Errors**: Ensure `sqlite` is available (default with Python).
* **Missing Icons**: Check internet connection for FontAwesome CDN.

## Logs Location
* Console output (stdout)
