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

### Deployment of the script to kubernetes.

1. Go to the directory where the files for deploy to Kubernetes are:
    ```shell
    cd helm/
    ```
2. The content of the directory should look like follow:
```shell
.
└── imagemosaic-cleaner
    ├── Chart.yaml
    ├── templates
    │         ├── NOTES.txt
    │         ├── _helpers.tpl
    │         ├── configmap.yaml
    │         ├── cronjob.yaml
    │         └── secrets.yaml
    └── values.yaml
```

2. Create the full deployment for the Script with helm.
  ```shell
  helm install -n <namespace> <name-of-the-app> imagemosaic-cleaner/
  ```
  - ex:
    ```shell
    helm install -n geosolutions housekeeper imagemosaic-cleaner/
    ```
  - the output of that command:
    ```shell
    NAME: housekeeper
    LAST DEPLOYED: Wed May 12 10:25:28 2021
    NAMESPACE: geosolutions
    STATUS: deployed
    REVISION: 1
    TEST SUITE: None
    NOTES:
    1. Check if cronjob was installed:
       kubectl --namespace geosolutions get cronjob
    
    2. Run it once as a job:
       kubectl --namespace geosolutions create job 0-test --from=cronjob/housekeeper-imagemosaic-cleaner-0
        ```
