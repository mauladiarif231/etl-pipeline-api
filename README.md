# ETL Pipeline Project

A simplified ETL (Extract, Transform, Load) pipeline using Python and Apache Airflow that processes and enriches JSON data with geocoding information.

## Project Overview

This project simulates an ETL process that:
- Extracts JSON data from local files
- Transforms the data by enriching addresses with geocoding information (latitude, longitude, full address)
- Loads the enriched data into output JSON files

## Project Structure

```
.
├── dags/
│   ├── __init__.py
│   └── etl_dag.py                    
├── data/
│   ├── int_test_input/               
│   └── int_test_output/             
├── src/
│   ├── integrations/
│   │   ├── __init__.py
│   │   └── geocode_util.py           
│   ├── transformers/
│   │   ├── __init__.py
│   │   └── address_transformer.py    
│   └── utils/
│       ├── __init__.py
│       ├── reader.py                 
│       └── writer.py                 
├── tests/
│   ├── __init__.py
│   ├── test_address_transformer.py   
│   ├── test_geocode_util.py         
│   ├── test_reader.py               
│   └── test_writer.py               
├── .env                             
├── docker-compose.yml               
├── Dockerfile                       
├── requirements.txt                 
└── run_tests.sh                     
```

## Features

### Core Components

1. **Geocoding Integration** (`src/integrations/geocode_util.py`)
   - Integrates with LocationIQ API for address geocoding
   - Handles API rate limiting and error responses
   - Returns full address, latitude, and longitude

2. **Data Reader** (`src/utils/reader.py`)
   - Reads JSON files from specified directories
   - Returns an iterator over records for memory efficiency
   - Handles file reading errors gracefully

3. **Data Writer** (`src/utils/writer.py`)
   - Writes enriched data to JSON files
   - Supports both single records and iterators
   - Handles file writing errors and directory creation

4. **Address Transformer** (`src/transformers/address_transformer.py`)
   - Orchestrates the address enrichment process
   - Handles missing or invalid address data
   - Integrates geocoding results into original records

### Airflow DAG

The ETL pipeline is orchestrated using Apache Airflow with the following tasks:
- **extract_data**: Reads input JSON files
- **transform_data**: Enriches addresses with geocoding information
- **load_data**: Writes enriched data to output files

## Setup and Installation

### Prerequisites

- Docker v28+
- Docker Compose v2.25+
- Bash shell
- Ubuntu or Mac-based system

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/mauladiarif231/etl-pipeline-api.git
cd etl-pipeline-api
```

2. Create a `.env` file with your LocationIQ API key:
```bash
LOCATIONIQ_API_KEY=pk.2293b5f90b2057ebe343c0e11f2f222b
```

3. Build and start the Docker containers:
```bash
docker-compose up -d
```

4. Access Airflow web interface at `http://localhost:8080`
   - Username: `airflow`
   - Password: `airflow`

## Usage

### Running the ETL Pipeline

1. **Via Airflow UI**:
   - Navigate to `http://localhost:8080`
   - Find the `etl_dag` in the DAGs list
   - Toggle the DAG to "On" and trigger a run

2. **Via Command Line**:
```bash
docker-compose exec airflow-webserver airflow dags trigger etl_dag
```

### Running Tests

Run the comprehensive test suite:
```bash
chmod +x run_tests.sh && ./run_tests.sh
```

Or run individual test files:
```bash
python -m pytest tests/test_geocode_util.py -v
python -m pytest tests/test_reader.py -v
python -m pytest tests/test_writer.py -v
python -m pytest tests/test_address_transformer.py -v
```

## API Integration

### LocationIQ Geocoding API

The project uses LocationIQ's free tier for geocoding services:
- **Endpoint**: `https://us1.locationiq.com/v1/search.php`
- **Rate Limit**: Handles API rate limiting gracefully
- **Error Handling**: Comprehensive error handling for API failures

### Configuration

Set your LocationIQ API key in the `.env` file:
```
LOCATIONIQ_API_KEY=pk.2293b5f90b2057ebe343c0e11f2f222b
```

## Input/Output Format

### Input Format
```json
{
  "id": "1",
  "name": "John Doe",
  "address": "123 Main St, New York"
}
```

### Output Format
```json
{
  "id": "1",
  "name": "John Doe",
  "address": "123 Main St, New York",
  "enriched_address": {
    "full_address": "123 Main Street, New York, NY 10001, USA",
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

## Error Handling

The pipeline includes comprehensive error handling for:
- **API Failures**: Graceful handling of geocoding API errors
- **File Operations**: Proper error handling for file read/write operations
- **Data Validation**: Validation of input data and API responses
- **Rate Limiting**: Automatic retry logic for API rate limits

## Testing

The project includes comprehensive unit tests covering:
- Geocoding utility functionality
- File reader and writer operations
- Address transformation logic
- Error handling scenarios
- Mock API responses

### Test Coverage

- **Geocoding Tests**: API integration, error handling, response parsing
- **Reader Tests**: File reading, iterator functionality, error cases
- **Writer Tests**: File writing, directory creation, data serialization
- **Transformer Tests**: End-to-end transformation logic

## Development

### Adding New Features

1. **New Transformers**: Add transformation logic in `src/transformers/`
2. **New Integrations**: Add API integrations in `src/integrations/`
3. **New Utilities**: Add utility functions in `src/utils/`

### Code Quality

- Follow PEP 8 style guidelines
- Add comprehensive unit tests for new functionality
- Include proper error handling and logging
- Document new functions and classes

## Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Ensure your LocationIQ API key is valid and added to `.env`
   - Check API rate limits and quotas

2. **Docker Issues**:
   - Ensure Docker and Docker Compose are running
   - Check container logs: `docker-compose logs`

3. **File Permissions**:
   - Ensure proper read/write permissions for data directories

### Logs

Check Airflow logs for detailed error information:
```bash
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request