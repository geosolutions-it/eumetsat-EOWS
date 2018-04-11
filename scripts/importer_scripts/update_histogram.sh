### NOTE: this script will need a postgresql client to be already installed
###
### For example : postgresql-client-9.6

##################################
# Set PSQL variables with defaults
##################################

export PGHOST=${PGHOST-localhost}
export PGPORT=${PGPORT-5432}
export PGDATABASE=${PGDATABASE-database}
export PGUSER=${PGUSER-username}
export PGPASSWORD=${PGPASSWORD-password}

##################################
# Actual query
##################################

psql -c "Insert into metopa_histogram  select time, st_setsrid(st_extent(the_geom)::geometry, 4326) as the_geom from metopa where time = '$1' group by time ON CONFLICT (time) DO UPDATE SET the_geom = EXCLUDED.the_geom"
