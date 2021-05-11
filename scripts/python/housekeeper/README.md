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
   - `FIELDS`    Files used for the query.
   - `T_LIMIT`   Number of days till when you want to keep the data.
   - `TRIES`     The maximum number of attempts.
   - `DELAY`     Initial delay between attempts.
   - `BACKOFF`   Multiplier applied to delay between attempts.
   - `MAX_DELAY` The maximum value of delay.
   - `TZ`        The Timezone of the server.
   - `BATCH`     Amount of data take it in one time.
   - `GLOBAL_RETENTION` Global Retention time for all the layers.
   - `LAYERS`    List of layers to use.
   - `COLUMN_TIME_NAME` Name of the column where the time is.

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

### Deployment of the script to kubernetes.

1. Go to the directory where the files for deploy to kubernetes are:
    ```shell
    cd k8s/
    ```
2. Create the configmap for the Script.
  ```shell
  kubectl create configmap cleaner-config --from-env-file=.env -n chosen-namespace
  ```
3. Create the CronJob to run the Script.
  ```shell
  kubectl create -f cleaner-cronJob.yaml
  ```
