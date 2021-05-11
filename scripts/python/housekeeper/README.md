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
   - `TRIES`     The maximum number of attempts.
   - `DELAY`     Initial delay between attempts.
   - `BACKOFF`   Multiplier applied to delay between attempts.
   - `MAX_DELAY` The maximum value of delay.
   - `TZ`        The Timezone of the server.
   - `BATCH`     Amount of data take it in one time.
   - `GLOBAL_RETENTION` Global Retention time for all the layers.
   - `LAYERS`    List of layers to use.
   - `COLUMN_TIME` Name of the column where the time is.

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

1. Go to the directory where the files for deploy to Kubernetes are:
    ```shell
    cd k8s/
    ```
2. The content of the directory should look like follow:
```shell
.
├── .env.example
├── cleaner-cronjob.yaml
└── kustomization.yaml
```
  - `.env.example` where the environment variables are. 
  *NOTE* this file need to be modified with the values that you need for your cluster.
  - `cleaner-cronjob.yaml` the deployment of the cronjob.
  - `kustomization.yaml` the kustomize file where the whole deployment occurred.

2. Create the full deployment for the Script with the kustomization.yaml file.
  ```shell
  kubectl create -k .
  ```
  - the output of that command:
    ```shell
    configmap/cleaner-config-855569dg4b created
    secret/cleaner-db-pass-9dg7b6859m created
    secret/cleaner-email-pass-bf4gmmd755 created
    cronjob.batch/imagemosaiccleaner created
    ```
