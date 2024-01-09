#!/bin/bash

here="$(pwd)"
config_path="${here}/lute/config/config.yml"
db_name="khmer_db.db"
app_data_path="${here}/app_data"

echo "Current directory: ${here}"
echo "Creating a configuration file at: ${config_path}"
printf "ENV: dev\nDBNAME: khmer_db.db\nDATAPATH: /home/justin/Documents/Projects/lute/lute-v3-khmer/app_data\n" > "${config_path}"
