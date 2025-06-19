#!/bin/bash

# ETL Assignment Test Runner
# This script runs all unit tests for the ETL pipeline components

echo "🧪 Running ETL Pipeline Unit Tests"
echo "=================================="

# Set PYTHONPATH to include src directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Load environment variables
source .env

# Create test output directory if it doesn't exist
mkdir -p data/int_test_output

echo ""
echo "📋 Test Configuration:"
echo "PYTHONPATH: $PYTHONPATH"
echo "API Key configured: $([ -n "$LOCATIONIQ_API_KEY" ] && echo "✅ Yes" || echo "❌ No")"
echo ""

# Run individual test files with verbose output
echo "🔍 Testing Geocoding Utility..."
python -m pytest tests/test_geocode_util.py -v

echo ""
echo "📖 Testing Reader Utility..."
python -m pytest tests/test_reader.py -v

echo ""
echo "✏️  Testing Writer Utility..."
python -m pytest tests/test_writer.py -v

echo ""
echo "🔄 Testing Address Transformer..."
python -m pytest tests/test_address_transformer.py -v

echo ""
echo "🎯 Running All Tests with Coverage..."
python -m pytest tests/ -v --tb=short

echo ""
echo "✅ All tests completed!"
echo ""
echo "🚀 To run the Airflow ETL pipeline:"
echo "   1. Start the services: docker-compose up -d"
echo "   2. Access Airflow UI: http://localhost:8080"
echo "   3. Login with admin/admin"
echo "   4. Enable and trigger the 'address_enrichment_etl' DAG"