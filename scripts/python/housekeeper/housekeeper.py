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

# Initializing the environment variables from dotenv file.
env = Env()
env.read_env()
tries = env.int("TRIES")
delay = env.int("DELAY")
backoff = env.int("BACKOFF")
max_delay = env.int("MAX_DELAY")
global_retention = env.list("GLOBAL_RETENTION")
layers_list = env.list("LAYERS")
time_limit = ""
fields = env("FIELDS")
fields_list = env("FIELDS").split(",")
tz = pytz.timezone(env("TZ"))  # set timezone
t_now = datetime.now(tz=tz)
batch = env.int("BATCH")

# configuring the logs format.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(app_name)s %(levelname)s:%(message)s')
layer_name = ""

# Creating classes to manipulate the logs.
class AppFilter(logging.Filter):
    filter_name = ""
    def filter(self, record):
        record.app_name = self.filter_name
        return True

class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)

    def format(self, record):
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result
# Setting the logger to the systemd.
handler = logging.StreamHandler()
formatter = OneLineExceptionFormatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
cleaner = logging.getLogger(layer_name)
cleaner.setLevel(os.environ.get("LOGLEVEL", "INFO"))
filter = AppFilter()
cleaner.addFilter(filter)
cleaner.addHandler(handler)


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

        cleaner.info("connected to database")
        return connection

    except (Exception, Error) as error:
        cleaner.exception("Error while connecting to PostgreSQL", error)
        raise


@retry((ValueError, TypeError), tries=tries, delay=delay, backoff=backoff, max_delay=max_delay)
def getdata(conn, time_limit, schema, table, col_time_name):
    """
    :param conn: connection parameter returned from connect function.
    :param time_limit: retention time of the records.
    :param schema: Name of schema of the database where the tables reside.
    :param table: Name of table where the records reside.
    :param col_time_name: Name of column where the time records reside.
    :return:
    """
    date_t = (t_now - timedelta(hours=time_limit)).strftime('%Y-%m-%d %H:%M:%S.%f')
    sql_query = f'SELECT {fields} FROM {schema}."{table}" WHERE \'{date_t}\' > "{table}".{col_time_name};'
    conn.autocommit = True

    try:
        # Opening a cursor to query the database.
        with conn.cursor() as curs:
            cleaner.info("Quering the database")
            curs.execute(sql_query)
            cleaner.info(curs.statusmessage)
            statusmessage = curs.statusmessage
            results = "SELECT 0"
            if statusmessage != results:
                batch = env.int("BATCH")
                # setting the number of rows to be fetched at the time.
                curs.arraysize = batch
                for x in curs.fetchmany():
                    filename = str(x[0])
                    mod_date = str(x[1])
                    sql_drop = f'DELETE FROM {schema}."{table}" WHERE \'{date_t}\' > "{table}".{col_time_name};'
                    # writing the the records in a file to delete after.
                    with open('files.txt', 'w') as a_writer:
                        a_writer.write(f'{filename}\n')
                        cleaner.info(f"writing the {filename} record to delete later")
                        a_writer.close()
                    # Comparing the date of the db records to delete the olders than date_t
                    cleaner.info("deleting the entries in the database")
                    cleaner.info(curs.execute(sql_drop))
                    cleaner.info(curs.statusmessage)
                    with open('files.txt', 'r') as a_reader:
                        for line in a_reader:
                            try:
                                if os.path.exists(filename):
                                    os.remove(filename)
                                    cleaner.info(f'This file have been deleted: {filename}')
                            except (Exception, Error) as er:
                                cleaner.error(er)
                        a_reader.close()
                    if os.path.exists("files.txt"):
                        cleaner.info("deleting the path container file")
                        os.remove("files.txt")
            else:
                cleaner.info("Nothing to clean. See you on the next Cleaning")
        conn.close()
    except (Exception, Error) as e:
        print(e)
        cleaner.error(e)
        with open('errors.txt', 'w') as a_writer:
            a_writer.write(f'Filename Path: \t\t\t timestamp:\n{filename} \t\t\t {mod_date}\n')
            a_writer.close()
        conn.rollback()
        raise e

def notification():
    cleaner.info("creating the email to send")
    subject = "Cleaning Task is finished"
    body = "This is the file that contains the records that could not be deleted"
    body2 = "The Clean process finished without any problems."

    sender_email = env("SENDER")
    receiver_email = env("RECEIVER")
    password = env("PASS")
    filename = "errors.txt"

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    try:
        if os.path.exists(filename):
            cleaner.info("attaching the list of file with errors to send")
            # Add body to email
            message.attach(MIMEText(body, "plain"))

            with open(filename, 'rb') as attachment:
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
        else:
            message.attach(MIMEText(body2, "plain"))
    except:
        cleaner.exception('No file to send')

    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    cleaner.info("Sending the email")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

def housekeeper():
    # Setting up the function to start the process.
    cleaner.info("Starting the Cleaning Process.")
    column_time = env("COLUMN_TIME")
    global_retention_time = int(global_retention[1])
    # getting data from the layer list.
    for layers in layers_list:
        layer = layers.split(";")
        layer_name = layer[0]
        layer_time = layer[-1]
        layer_parameters = layer[1].split(".")
        filter.filter_name = layer_name
        schema = layer_parameters[0]
        table = layer_parameters[1]
        # Implementing the granule housekeeping process configuration.
        if global_retention_time > 0:
            cleaner.info(f"Running the Housekeeper script with the Global Retention Time: {global_retention_time}")
            getdata(conn=connect(), time_limit=global_retention_time, schema=schema, table=table, col_time_name=column_time)
        else:
            cleaner.info(f"Running the Housekeeper script with the Layer Retention Time: {layer_time}")
            getdata(conn=connect(), time_limit=layer_time, schema=schema, table=table, col_time_name=column_time)

    # Sending a email when the job is done.
    notification()
    cleaner.info("DONE")

if __name__ == '__main__':
    housekeeper()
