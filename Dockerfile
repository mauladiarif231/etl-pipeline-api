FROM apache/airflow:2.9.1-python3.10

USER airflow

COPY --chown=airflow:airflow requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

# Create necessary directories that are not mounted by volumes
# Airflow's user (airflow) needs write permissions to these
RUN mkdir -p /opt/airflow/data/int_test_input \
           /opt/airflow/data/int_test_output \
           /opt/airflow/src/integrations \
           /opt/airflow/src/transformers \
           /opt/airflow/src/utils \
           /opt/airflow/tests && \
    chown -R airflow:airflow /opt/airflow/data /opt/airflow/src /opt/airflow/tests
