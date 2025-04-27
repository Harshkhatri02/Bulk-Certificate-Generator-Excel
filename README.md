# Certificate Generator

A web application for generating customized certificates with dynamic fields and QR code support.

## Features

- Custom certificate template upload
- Dynamic field positioning
- QR code integration
- Bulk certificate generation from Excel
- User authentication and organization management
- Multiple font support
- PDF output format

## Tech Stack

- Python Flask
- MySQL Database
- PIL (Python Imaging Library)
- pandas for Excel processing
- QR Code generation

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your configuration
4. Initialize the MySQL database:
   ```bash
   # Log into MySQL
   mysql -u your_db_user -p
   
   # Create the database
   CREATE DATABASE your_db_name;
   
   # Exit MySQL
   exit;
   
   # Import the database schema
   mysql -u your_db_user -p your_db_name < database_setup.sql
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Environment Variables

Create a `.env` file with the following variables:
```
SECRET_KEY=your_secret_key
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
``` 