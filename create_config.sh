#!/bin/bash

here="$(pwd)"
config_path="${here}/lute/config/config.yml"
db_name="khmer_db.db"
app_data_path="${here}/app_data"

echo "Current directory: ${here}"
echo "Creating a configuration file at: ${config_path}"
printf "ENV: dev\nDBNAME: ${db_name}\nDATAPATH: ${app_data_path}\n" > "${config_path}"
