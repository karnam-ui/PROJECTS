# Churn Prediction API - Test Suite

This document explains how to run the test suite for the Churn Prediction API.

## Setup

### 1. Install Dependencies
First, ensure pytest is installed along with other test dependencies:

```bash
pip install -r requirements.txt
```

The requirements now include:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `httpx` - HTTP client for testing FastAPI apps

### 2. Environment Setup
Make sure your `.env` file is configured in the backend directory. The tests use an in-memory SQLite database, so they don't require a MySQL connection.

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest test_main.py
```

### Run Specific Test Class
```bash
pytest test_main.py::TestSinglePrediction
```

### Run Specific Test
```bash
pytest test_main.py::TestSinglePrediction::test_single_prediction_success
```

### Run Tests with Coverage
```bash
# First install pytest-cov
pip install pytest-cov

# Run tests with coverage report
pytest --cov=. --cov-report=html
```

### Run Only Fast Tests (skip rate limiting tests)
```bash
pytest -m "not rate_limit"
```

### Run Tests with Custom Markers
```bash
# Run only prediction tests
pytest -m "predictions"

# Run only auth-related tests
pytest -m "auth"
```

## Test Structure

The test suite is organized into several test classes:

### 1. **TestGetPredictions**
Tests for the `GET /predictions` endpoint
- Success case with valid authentication
- Missing authentication
- Invalid token handling
- Malformed headers

### 2. **TestSinglePrediction**
Tests for the `POST /predict/single` endpoint
- Successful prediction
- Authentication enforcement
- Missing fields handling
- Edge cases (high/low churn probability)
- Expected value calculation

### 3. **TestBulkPrediction**
Tests for the `POST /predict/bulk` endpoint
- Successful bulk predictions
- Authentication enforcement
- Invalid CSV handling
- Ranking verification
- Large file handling
- Empty file handling

### 4. **TestIsUsingExpectedEncryption**
Tests for token and authentication
- Token expiration verification
- Different tokens for different users

### 5. **TestRateLimiting**
Tests for rate limiting (10 requests per minute per endpoint)
- GET /predictions rate limiting
- POST /predict/single rate limiting
- POST /predict/bulk rate limiting

### 6. **TestRootEndpoint**
Basic health check endpoint test

## Fixtures

The `conftest.py` file provides several reusable fixtures:

- **engine**: Test database engine
- **db_session**: Fresh database session for each test
- **client**: FastAPI TestClient with overridden dependencies
- **test_user**: Pre-created test user
- **auth_token**: Valid JWT token
- **auth_header**: Authorization header with valid token
- **invalid_auth_header**: Authorization header with invalid token
- **sample_single_prediction_data**: Sample data for single prediction
- **sample_bulk_csv_data**: Sample CSV data for bulk prediction
- **sample_invalid_csv_data**: Invalid CSV data for error testing

## Key Testing Features

1. **Isolated Database**: Each test runs with a fresh in-memory SQLite database
2. **Authentication Testing**: Proper JWT token generation and validation
3. **Error Handling**: Tests for various error scenarios
4. **Edge Cases**: Tests for boundary conditions and special scenarios
5. **Rate Limiting**: Verification of rate limit enforcement
6. **Data Validation**: Ensures predictions and responses are properly formatted

## Continuous Integration

To integrate these tests into CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Troubleshooting

### Tests fail with "ModuleNotFoundError"
Make sure you're running pytest from the backend directory:
```bash
cd ChurnPrediction/backend
pytest
```

### Tests hang or timeout
- Check that the model file `churn_model.pkl` exists
- Ensure no external services are blocking

### Rate limiting tests fail intermittently
Rate limiting is based on request timestamps. Tests might fail if run across minute boundaries. Consider adding a delay or adjusting the test logic.

## Performance Notes

- Full test suite typically runs in 5-10 seconds
- Each test is isolated with its own database
- Tests use in-memory SQLite for speed

## Future Enhancements

- Add performance benchmarking tests
- Add more edge case scenarios
- Add load testing for bulk predictions
- Add database transaction tests
- Add concurrent request testing
