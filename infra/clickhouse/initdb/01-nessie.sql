CREATE DATABASE lakehouse
ENGINE = DataLakeCatalog('http://nessie:19120/iceberg')
SETTINGS
    catalog_type = 'rest',
    storage_endpoint = 'http://rustfs:9000/iceberg',
    warehouse = 'warehouse';
