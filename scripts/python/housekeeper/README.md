# Script to clean the ImageMosaic records from the Database and the filesystem.

### Requirements:
- Python 3.x.
- `.env`

### Components:
- Function to check and create the connection to the PostgreSQL.
- Function to query and delete the entries in the database and the files in the filesystem.
- Function to send an email after the process finished.

### Utilization:
- Variables to fill to run the script:
   - `DB_HOST`   Ip or name of the server where PostgreSQL is running. 
   - `DB_NAME`   name of the database, where the query will be.
   - `DB_PASS`   password the user used to authenticate to the postgreSQL. 
   - `DB_PORT`   port served by the PostgreSQL.
   - `DB_USER`   Username user to authenticated in the postgreSQL.
   - `PASS`      Password of the email account used to send the notifications.
   - `RECEIVER`  Email address to where you will send the notifications.  
   - `SENDER`    Email account used to send the notifications.
   - `TABLE`     Table used for the query.
   - `T_LIMIT`   Number of days till when you want to keep the data. 
   - `TRIES`     The maximum number of attempts.
   - `DELAY`     Initial delay between attempts.
   - `BACKOFF`   Multiplier applied to delay between attempts.
   - `MAX_DELAY` The maximum value of delay.
   - `TZ`        The Timezone of the server.

1. to run the script:
    - ```shell
        python3 housekeeper.py
      ```
2. You can build a Docker image, running:
    ```shell
    docker build -t <registry/tag> .
    ```
    - to run the docker image you should have a .env file with all the env variables declare there.
      ```shell
        docker run --env-file .env -d <registry/tag>
      ```