import psycopg2
from psycopg2 import Error
import os
from datetime import datetime, timedelta
import smtplib, ssl, email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from retry import retry
import pytz
from environs import Env
import logging

env = Env()
env.read_env()
print(env)
tries = env.int("TRIES")
delay = env.int("DELAY")
backoff = env.int("BACKOFF")
max_delay = env.int("MAX_DELAY")
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)


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
        connection = psycopg2.connect(user=env("DB_USER"),
                                      password=env("DB_PASS"),
                                      host=env("DB_HOST"),
                                      port=env("DB_PORT"),
                                      database=env("DB_NAME")
                                      )

        logging.info("connected to database")
        return connection

    except (Exception, Error) as error:
        logging.critical("Error while connecting to PostgreSQL", error)
        raise


# use retry decorator to retry the make many attempts as need it if the delete failed.
@retry((ValueError, TypeError), tries=tries, delay=delay, backoff=backoff, max_delay=max_delay)
def getdata(conn):
    """
    :param conn: connection parameter returned from connect function.
    :return:
    """
    # table = env(o_table)
    table = env.str("TABLE")
    time_limit = env.int("T_LIMIT")
    schema = env.str("SCHEMA")
    fields = env("FIELDS")
    tz = pytz.timezone(env("TZ"))  # set timezone
    t_now = datetime.now(tz=tz)
    date_t = (t_now - timedelta(days=time_limit)).strftime('%Y-%m-%d %H:%M:%S.%f')
    sql_query = f'SELECT {fields} FROM {schema}."{table}" WHERE \'{date_t}\' > "{table}".ingestion;'

    try:
        with conn.cursor() as curs:
            logging.info("Quering the database")
            curs.execute(sql_query)
            # Looping the data to get the time and the path of the files.
            batch = env.int("BATCH")
            for x in curs.fetchall():
                curs.itersize = batch
                filename = str(x[0])
                mod_date = str(x[1])
                sql_drop = f'DELETE FROM {schema}."{table}" WHERE \'{date_t}\' < "{table}".ingestion;'
                # sql_show = f'SELECT * FROM {schema}."{table}" WHERE \'{date_t}\' > "{table}".ingestion;'

                with open('files.txt', 'w') as a_writer:
                    a_writer.write(f'{filename}\n')
                    a_writer.close()
                # Comparing the date of the db records to delete the olders than T_LIMIT
                curs.execute(sql_drop)
                conn.commit()  # commiting the operation.
                with open('files.txt', 'r') as a_reader:
                    for line in a_reader:
                        os.remove(filename)
                        logging.info(f'This file have been deleted: {filename}')
                    a_reader.close()
                if os.path.exists("files.txt"):
                    os.remove("files.txt")
        conn.close()
    except (Exception, Error) as e:
        print(e)
        logging.error(e)
        with open('errors.txt', 'w') as a_writer:
            a_writer.write(f'Filename Path: \t\t\t timestamp:\n{filename} \t\t\t {mod_date}\n')
            a_writer.close()
        conn.rollback()
        raise e


def notification():
    subject = "Cleaning Task is finished"
    body = "This is the file that contains the records that cuold not be deleted"
    sender_email = env("SENDER")
    receiver_email = env("RECEIVER")
    password = env("PASS")

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
    getdata(conn=connect())
    notification()
