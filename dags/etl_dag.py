from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Add src directory to path
sys.path.append('/opt/airflow/src')
from utils.reader import read_json
from transformers.address_transformer import AddressTransformer
from utils.writer import write_json

# Default arguments for the DAG
default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'etl_json_pipeline',  # Changed from address_enrichment_etl
    default_args=default_args,
    description='ETL pipeline for address enrichment using geocoding',
    schedule_interval=None,  # Manual trigger
    catchup=False,
    tags=['etl', 'geocoding', 'address'],
)

def extract_data(**context):
    """Extract data from input JSON file"""
    input_path = '/opt/airflow/data/int_test_input/input_sample.json'  # Changed to input.json
    records = list(read_json(input_path))
    print(f"Extracted {len(records)} records from {input_path}")
    return records

def transform_data(**context):
    """Transform data by enriching addresses with geocoding"""
    records = context['task_instance'].xcom_pull(task_ids='extract_task')
    transformer = AddressTransformer()  # Instantiate the class
    enriched_records = list(transformer.transform(iter(records)))  # Call method
    print(f"Transformed {len(enriched_records)} records")
    return enriched_records

def load_data(**context):
    """Load enriched data to output file"""
    enriched_records = context['task_instance'].xcom_pull(task_ids='transform_task')
    output_path = '/opt/airflow/data/int_test_output/enriched_data.json'
    write_json(iter(enriched_records), output_path)
    print(f"Loaded {len(enriched_records)} records to {output_path}")

# Define tasks
extract_task = PythonOperator(
    task_id='extract_task',
    python_callable=extract_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_task',
    python_callable=transform_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_task',
    python_callable=load_data,
    dag=dag,
)

# Set task dependencies
extract_task >> transform_task >> load_task