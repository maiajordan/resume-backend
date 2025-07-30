import logging
import azure.functions as func
import os
from azure.data.tables import TableServiceClient, UpdateMode

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing visitor count request.')

    try:
        connection_string = os.getenv("AzureWebJobsStorage")
        table_name = "VisitorCount"

        # Connect to Azure Table Storage
        service = TableServiceClient.from_connection_string(conn_str=connection_string)
        table_client = service.get_table_client(table_name=table_name)

        partition_key = "counter"
        row_key = "visits"

        # Try to retrieve the counter
        try:
            entity = table_client.get_entity(partition_key=partition_key, row_key=row_key)
            count = entity.get("Count", 0)
        except:
            # If not found, start from 0
            count = 0
            table_client.create_entity({
                "PartitionKey": partition_key,
                "RowKey": row_key,
                "Count": count
            })

        # Increment the counter
        count += 1
        table_client.update_entity({
            "PartitionKey": partition_key,
            "RowKey": row_key,
            "Count": count
        }, mode=UpdateMode.REPLACE)

        return func.HttpResponse(str(count), status_code=200)

    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse("Internal server error", status_code=500)
