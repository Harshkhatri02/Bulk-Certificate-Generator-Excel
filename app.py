from flask import Flask, render_template, request, redirect, session, send_file, jsonify, flash,url_for
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import shutil
import json
import mysql.connector
from datetime import datetime
import qrcode
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import Error
from dotenv import load_dotenv
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Ensure upload directories exist
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('certificates', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

def create_connection():
    try:
        # Get the database URL from environment variable
        db_url = os.getenv('DB_HOST')
        
        if db_url and ('mysql://' in db_url or '@' in db_url):
            # Parse the URL if it's in the format mysql://user:pass@host:port/db
            parsed = urlparse(db_url)
            user = parsed.username or os.getenv('DB_USER')
            password = parsed.password or os.getenv('DB_PASSWORD')
            host = parsed.hostname
            port = parsed.port or 3306
            # Use DB_NAME from environment with certificate-gen as fallback
            database = os.getenv('DB_NAME', 'certificate-gen')
            
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
        else:
            # Fallback to individual environment variables
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME', 'certificate-gen')  # Use environment variable with fallback
            )
        
        logger.info("Database connection successful")
        return connection
    except Error as e:
        logger.error(f"Database connection failed: {e}")
        return None

def insert_update(connection, email):
    try:
        cursor = connection.cursor()  # Create a cursor from the connection
        # Prepare the SQL insert statement
        sql_insert_query = """INSERT INTO get_updates (email) VALUES (%s)"""
        
        # Data to be inserted
        record = (email,)  # Correctly formatted tuple

        # Execute the insert statement
        cursor.execute(sql_insert_query, record)

        # Commit the transaction
        connection.commit()  # Commit using the connection
        print(f"Record inserted successfully: {record}")

    except Error as e:
        print(f"Error occurred: {e}")

    finally:
        cursor.close()  # Ensure the cursor is closed after operation

@app.route('/submit_update', methods=['POST'])
def submit_update():
    # Retrieve the email from the form data
    email = request.form['email']

    # Establish a connection and insert the email
    connection = create_connection()  # Create a new database connection
    try:
        if connection.is_connected():
            insert_update(connection, email)  # Call the function to insert the email
    except Error as e:
        print(f"Connection error: {e}")
    finally:
        if connection.is_connected():
            connection.close()  # Ensure the connection is closed

    # Redirect to a success page after processing
    return redirect(url_for('success'))

@app.route('/success')
def success():
    return "Thank you for subscribing! You'll receive updates soon."


def insert_subscription(samt, s_time, s_type, oid):
    conn = create_connection()
    cursor = conn.cursor()
    
    query = "INSERT INTO subscription (samt, s_time, s_type, oid) VALUES (%s, %s, %s, %s)"
    # Data Stored in Buffer
    cursor.execute(query, (samt, s_time, s_type, oid))
    # Storing in Database
    conn.commit()
    cursor.close()
    conn.close()
    print("Inserted into subscription")


# Insert a record into 'payment' table
def insert_payment(pamt, date, time, modeOfPayment, sid):
    conn = create_connection()
    cursor = conn.cursor()
    
    query = "INSERT INTO payment (pamt, date, time, modeOfPayment, sid) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (pamt, date, time, modeOfPayment, sid))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Inserted into payment")


# Insert a record into 'reviews' table
def insert_review(description, oid):
    conn = create_connection()
    cursor = conn.cursor()
    
    query = "INSERT INTO reviews (description, oid) VALUES (%s, %s)"
    cursor.execute(query, (description, oid))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Inserted into reviews")


def insert_organisation(email, institution, password, iagree):
    try:
        conn = create_connection()
        if conn is None:
            flash("Unable to connect to database. Please try again later.")
            return False
            
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        query = "INSERT INTO organisation (email, institution, password, Iagree) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (email, institution, hashed_password, iagree))
        conn.commit()
        logger.info(f"Successfully registered user: {email}")
        return True
    except mysql.connector.Error as err:
        logger.error(f"Database error during registration: {err}")
        flash("Database error occurred. Please try again.")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def validate_login(email, password):
    try:
        conn = create_connection()
        if conn is None:
            flash("Unable to connect to database. Please try again later.")
            return False
            
        cursor = conn.cursor()
        query = "SELECT password FROM organisation WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        
        if result and check_password_hash(result[0], password):
            logger.info(f"Successful login for user: {email}")
            return True
        logger.warning(f"Failed login attempt for user: {email}")
        return False
    except mysql.connector.Error as err:
        logger.error(f"Database error during login: {err}")
        flash("Database error occurred. Please try again.")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# Base SignUP and Login Route
@app.route("/signupAndLogin", methods=["GET", "POST"])
def signup_and_login():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "Sign up":
            email = request.form.get("uname")
            institution = request.form.get("institution")
            password = request.form.get("password")
            iagree = request.form.get("iagree") == 'on'

            # Check if email already exists
            try:
                conn = create_connection()
                if conn is None:
                    flash("Unable to connect to database. Please try again later.")
                    return redirect("/signupAndLogin")
                    
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM organisation WHERE email = %s", (email,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    flash("Email already exists. You can SignIn!")
                    return redirect("/signupAndLogin")

                if insert_organisation(email, institution, password, iagree):
                    flash("Sign up successful! You can now log in.")
                return redirect("/signupAndLogin")
            except mysql.connector.Error as err:
                logger.error(f"Database error checking existing user: {err}")
                flash("An error occurred. Please try again.")
                return redirect("/signupAndLogin")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals() and conn.is_connected():
                    conn.close()

        elif action == "Login":
            email = request.form.get("luname")
            password = request.form.get("lpass")
            if validate_login(email, password):
                session['user_email'] = email
                flash("Login successful!")
                return redirect("/home")
            else:
                flash("Invalid email or password. Please try again.")
                return redirect("/signupAndLogin")

    return render_template('loginpage.html')

@app.route("/logout")
def logout():
    session.pop('user_email', None)  # Remove user email from session
    flash("You have been logged out.")
    return redirect("/home")

# Insert a record into 'subscription' table

@app.route('/tools', methods=["GET", "POST"])
def tools():
    if 'user_email' not in session:
        flash("Please log in to access the tools.")
        return redirect(url_for('signup_and_login'))
    if request.method == "POST":
        template_file = request.files['template']
        download_option = request.form.get('download_option')
        qr_code_url = request.form.get('qr_code_url')  # Get the QR code URL

        template_path = os.path.join("static/uploads", template_file.filename)
        template_file.save(template_path)

        session['template_path'] = template_path
        session['download_option'] = download_option
        session['qr_code_url'] = qr_code_url  # Save QR code URL in the session

        if download_option == 'zip':
            excel_file = request.files['excel_file']
            excel_path = os.path.join("static/uploads", excel_file.filename)
            excel_file.save(excel_path)
            session['excel_path'] = excel_path
        else:
            field_names = {key.replace('field_name_', ''): request.form[key] 
                           for key in request.form 
                           if key.startswith('field_name_')}
            session['data'] = field_names
        #POST for both
        return redirect(f'/setup?template={template_file.filename}')
    # GET
    return render_template("tools.html",user=session.get('user_email'))




# Write into the JSON file in /setup route as per requested postions from Frontend
@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        positions = request.json
        with open('positions.json', 'w') as f:
            json.dump(positions, f)
        
        if session.get('download_option') == 'zip':
            return jsonify({'status': 'download'})
        else:
            return jsonify({'status': 'success'})
    else:
        template = request.args.get('template')
        qr_code_url = session.get('qr_code_url')  # Get the QR code URL from session

        if session.get('download_option') == 'single':
            fields = list(session['data'].keys())
        else:
            df = pd.read_excel(session['excel_path'])
            fields = df.columns.str.strip().str.lower().tolist()

        return render_template('setup.html', template=template, fields=fields, qr_code_url=qr_code_url)



def create_certificate(template_path, data, output_path):
    template = Image.open(template_path)
    draw = ImageDraw.Draw(template)
    try:
        with open('positions.json') as f:
            positions = json.load(f)
            print("Loaded positions:", positions)
    except FileNotFoundError:
        print("positions.json not found.")
        positions = {}
    def parse_position(pos):
        try:
            return round(float(pos.replace('px', '').strip()))
        except ValueError:
            return 0
    # Debugging: Print the data received for the certificate
    print("Generating certificate with data:", data)
    # Define a dictionary to map font names to their corresponding .ttf files
    font_files = {
        "Arial": "Arial.ttf",
        "Times New Roman": "times.ttf",
        "Courier New": "cour.ttf",
        "Verdana": "verdana.ttf",
        "Georgia": "georgia.ttf",
        "Comic Sans MS": "comic.ttf"
    }
    for field, value in data.items():
        field_lower = field.strip().lower()  # Normalize to lowercase
        if field_lower in (k.lower() for k in positions.keys()):  # Check in lowercase
            position_data = positions[next(k for k in positions if k.lower() == field_lower)]
            position = (parse_position(position_data['left']), parse_position(position_data['top']))
            # Handle date formatting
            if isinstance(value, datetime):
                value = value.strftime('%d/%m/%Y')  # Format the date as DD/MM/YYYY
            
            font_name = position_data.get('font', 'Arial')  # Default to Arial if not set
            font_size = int(position_data.get('fontSize', 24))  # Default to size 24 if not set
            # Get the .ttf file for the selected font
            font_path = font_files.get(font_name, "Arial.ttf")  # Default to Arial if not found
            # Try to load the selected font
            try:
                font = ImageFont.truetype(font_path, font_size)
                print(f"Using font: {font_name} from file {font_path}")
            except IOError:
                print(f"Font {font_name} not found at {font_path}. Falling back to Vera.ttf.")
                font = ImageFont.truetype("./Vera.ttf", font_size)
            # Debugging: Print what will be drawn on the certificate
            print(f"Drawing field '{field}' with value '{value}' at {position} with font '{font_name}' and size {font_size}")
            draw.text(position, str(value).strip(), fill="black", font=font)
        else:
            print(f"Field '{field}' not found in positions.json. Skipping this field.")
    # Generate QR code if URL is provided
    qr_code_url = session.get('qr_code_url')
    if qr_code_url:
        qr_size = int(positions['qr_code'].get('qrSize', 100))  # Get the QR code size from positions.json
        qr_code_img = qrcode.make(qr_code_url)
        qr_code_img = qr_code_img.resize((qr_size, qr_size), Image.LANCZOS)  # Resize QR code to selected size
        qr_code_img_path = "static/uploads/qr_code.png"
        qr_code_img.save(qr_code_img_path)
        qr_position = (parse_position(positions['qr_code']['left']), parse_position(positions['qr_code']['top']))
        template.paste(qr_code_img, qr_position)
        # Save the final certificate as a PDF
    template.save(output_path, "PDF")
    print(f"Certificate saved to {output_path}")



@app.route("/", methods=["GET"])
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', user=session.get('user_email'))


@app.route('/about_us')
def about_us():
    return render_template('about_us.html', user=session.get('user_email'))


@app.route('/our_services')
def our_services():
    return render_template('our_services.html', user=session.get('user_email'))


@app.route('/generate-certificates')
def generate_certificates():
    try:
        output_dir = r"certificates"

        os.makedirs(output_dir, exist_ok=True)

        # Removed the premature file check. Removed file existence check here.
        for file in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, file))  # Only cleanup files


        template_path = session.get('template_path')
        download_option = session.get('download_option')
        print(f"Download option: {download_option} and {template_path}")
        if download_option == 'zip':
            excel_path = session.get('excel_path')
            df = pd.read_excel(excel_path)

            for _, row in df.iterrows():
                data = {col.strip().lower(): row[col] for col in df.columns}
                output_path = os.path.join(output_dir, f"{data.get('name', 'certificate')}.pdf")
                create_certificate(template_path, data, output_path)

            zip_file_path = shutil.make_archive("certificates", 'zip', output_dir)
            return send_file(zip_file_path, as_attachment=True)
        else:
            data = session.get('data')
            output_path = os.path.join(output_dir, "certificate.pdf")
            create_certificate(template_path, data, output_path)
            return send_file(output_path, as_attachment=True)
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
