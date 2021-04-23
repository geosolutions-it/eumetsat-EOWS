import psycopg2
from psycopg2 import Error
import os
from datetime import datetime, timedelta
import sys
from io import StringIO
import smtplib, ssl, email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from retry import retry
import pytz

tries = int(os.getenv("TRIES"))
delay = int(os.getenv("DELAY"))
backoff = int(os.getenv("BACKOFF"))
max_delay = int(os.getenv("MAX_DELAY"))


def connect():
    """
    This a function to create a connection to the postgresql.
    :param user: user used to connect to database.
    :param password: user used to connect to database.
    :param host: user used to connect to database.
    :param port: user used to connect to database.
    :param database: user used to connect to database.
    :return:
    """
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user=os.getenv("DB_USER"),
                                      password=os.getenv("DB_PASS"),
                                      host=os.getenv("DB_HOST"),
                                      port=os.getenv("DB_PORT"),
                                      database=os.getenv("DB_NAME")
                                      )

        # Create a cursor to perform database operations
        # cursor = connection.cursor()
        return connection

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        raise



# use retry decorator to retry the make many attempts as need it if the delete failed.
@retry((ValueError, TypeError), tries=tries, delay=delay, backoff=backoff, max_delay=max_delay)
def getdata(conn, env="TABLE", tlimit="T_LIMIT"):
    """
    :param conn: connection parameter returned from connect function.
    :param env: Name of the table where the query will be.
    :param tlimit: date used as reference.
    :return:
    """
    table = os.getenv(env)
    sql_query = f'SELECT "location", ingestion FROM {table};'
    # sql_drop = f'DELETE FROM {table} WHERE ingestion < {datetime.fromtimestamp(mod_date)};'
    tz = pytz.timezone(os.getenv("TZ"))  # set timezone
    time_limit = int(os.getenv(tlimit))
    t_now = datetime.now(tz=tz)
    date_t = (t_now - timedelta(days = time_limit)).strftime('%Y-%m-%d %H:%M:%S')
    datetime_object = datetime.strptime(date_t, '%Y-%m-%d %H:%M:%S')

    try:
        with conn.cursor() as curs:
            curs.execute(sql_query)
            # Looping the data to get the time and the path of the files.
            for x in curs.fetchall():
                filename = str(x[0])
                mod_date = datetime.timestamp(x[1])
                sql_drop = f"DELETE FROM {table} WHERE location = '{filename}';"
                # Comparing the date of the db records to delete the olders than T_LIMIT
                if mod_date < datetime.timestamp(datetime_object):
                    curs.execute(sql_drop)
                    conn.commit()  # commiting the operation.
                    # Printing the records that were deleted.
                    print(f'this entry has been deleted: {filename}, {mod_date}')
                    # Deleting the files in the filesystem and printing the result.
                    os.remove(filename)
                    print(f'This file have been deleted: {filename}')
                # curs.close()
    except (Exception, Error) as e:
        print(e)
        with open('errors.txt', 'w') as a_writer:
            a_writer.write(f'Filename Path: \t\t\t timestamp:\n{filename} \t\t\t {mod_date}\n')
            a_writer.close()
        conn.rollback()
        raise e


def notification():
    subject = "Cleaning Task is finished"
    body = "This is the file that contains the records that cuold not be deleted"
    sender_email = os.getenv("SENDER")
    receiver_email = os.getenv("RECEIVER")
    password = os.getenv("PASS")

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "files.txt"  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


if __name__ == '__main__':
    getdata(conn=connect(), env="TABLE", tlimit="T_LIMIT")
    notification()
