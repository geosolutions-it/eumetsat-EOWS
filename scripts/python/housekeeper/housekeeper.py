import psycopg2
from psycopg2 import Error
import os
from datetime import datetime
import sys
from io import StringIO
import smtplib, ssl, email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from retry import retry


def connect():
    """
    This a function to create a connection to the postgresql.
    :param env:
    :return:
    """
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user = os.getenv("DB_USER"),
                                      password = os.getenv("DB_PASS"),
                                      host = os.getenv("DB_HOST"),
                                      port = os.getenv("DB_PORT"),
                                      database = os.getenv("DB_NAME")
                                      )

        # Create a cursor to perform database operations
        # connection.autocommit()
        cursor = connection.cursor()
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)

    return connection


@retry((ValueError, TypeError), delay=1, backoff=2, max_delay=10)
def getdata(conn, env="TABLE", tlimit="T_LIMIT"):
    table = os.getenv(env)
    sql_query = f'SELECT "location", ingestion FROM {table};'
    # sql_drop = f'DELETE FROM {table} WHERE ingestion < {datetime.fromtimestamp(mod_date)};'
    time_limit = os.getenv(tlimit)
    datetime_object = datetime.strptime(time_limit, '%Y-%m-%d %H:%M:%S')

    try:
        with conn.cursor() as curs:
            curs.execute(sql_query)
            for x in curs.fetchall():
                filename = str(x[0])
                mod_date = datetime.timestamp(x[1])
                sql_drop = f"DELETE FROM {table} WHERE location = '{filename}';"
                # print(filename, mod_date)
                if mod_date < datetime.timestamp(datetime_object):
                    curs.execute(sql_drop)
                    conn.commit()
                    print(f'this entry has been deleted: {filename}, {mod_date}')
                    # print(f'this entry has been deleted: {sql_drop}')
                    # os.remove(filename)
                    # print(f'This file have been deleted: {filename}')
            curs.close()
    except (Exception, Error) as e:
        with open('errors.txt', 'w') as a_writer:
            a_writer.write(f'{filename}\n')
            a_writer.close()
        conn.rollback()
        raise e

def notification():
    subject = "Cleaning Task is finished"
    body = "This is the file that contains the records that cuold not be deleted"
    sender_email = os.getenv("SENDER")
    receiver_email = os.getenv("RECEIVER")
    # password = input("Type your password and press enter:")
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
    # notification()
