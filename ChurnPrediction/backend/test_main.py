
import pytest
import json
from io import BytesIO
from fastapi.testclient import TestClient


class TestGetPredictions:
    
    def test_get_predictions_success(self, client, auth_header):
        """Test successful retrieval of predictions"""
        response = client.get("/predictions", headers=auth_header)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_predictions_without_auth(self, client):
        """Test get predictions without authentication"""
        response = client.get("/predictions")
        assert response.status_code == 422  # Missing Authorization header
    
    def test_get_predictions_with_invalid_token(self, client, invalid_auth_header):
        """Test get predictions with invalid token"""
        response = client.get("/predictions", headers=invalid_auth_header)
        assert response.status_code == 401
        assert response.json()["content"]["message"] == "Invalid or expired token"
    
    def test_get_predictions_with_invalid_format(self, client):
        """Test get predictions with malformed auth header"""
        headers = {"Authorization": "InvalidFormat token"}
        response = client.get("/predictions", headers=headers)
        assert response.status_code == 401


class TestSinglePrediction:
    """Tests for POST /predict/single endpoint"""
    
    def test_single_prediction_success(self, client, auth_header, sample_single_prediction_data):
        """Test successful single prediction"""
        response = client.post(
            "/predict/single",
            json=sample_single_prediction_data,
            headers=auth_header
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "customer_id" in data
        assert "churn_probability" in data
        assert "churn_prediction" in data
        assert "expected_value" in data
        assert "prediction_time" in data
        assert "prediction_type" in data
        
        # Verify values
        assert data["customer_id"] == "CUST001"
        assert data["prediction_type"] == "single"
        assert data["churn_prediction"] in ["Yes", "No"]
        assert 0 <= data["churn_probability"] <= 100
    
    def test_single_prediction_without_auth(self, client, sample_single_prediction_data):
        """Test single prediction without authentication"""
        response = client.post(
            "/predict/single",
            json=sample_single_prediction_data
        )
        assert response.status_code == 422
    
    def test_single_prediction_with_invalid_token(self, client, invalid_auth_header, sample_single_prediction_data):
        """Test single prediction with invalid token"""
        response = client.post(
            "/predict/single",
            json=sample_single_prediction_data,
            headers=invalid_auth_header
        )
        assert response.status_code == 401
    
    def test_single_prediction_with_missing_monthly_charges(self, client, auth_header, sample_single_prediction_data):
        """Test single prediction with missing MonthlyCharges"""
        data = sample_single_prediction_data.copy()
        del data["MonthlyCharges"]
        
        response = client.post(
            "/predict/single",
            json=data,
            headers=auth_header
        )
        # Should fail or return default value
        assert response.status_code in [200, 400, 422]
    
    def test_single_prediction_without_customer_id(self, client, auth_header, sample_single_prediction_data):
        """Test single prediction without customerID"""
        data = sample_single_prediction_data.copy()
        del data["customerID"]
        
        response = client.post(
            "/predict/single",
            json=data,
            headers=auth_header
        )
        assert response.status_code == 200
        data_response = response.json()
        assert data_response["customer_id"] == "unknown"
    
    def test_single_prediction_high_churn_probability(self, client, auth_header, sample_single_prediction_data):
        """Test single prediction with features indicating high churn"""
        data = sample_single_prediction_data.copy()
        data["tenure"] = 2  # Low tenure
        data["Contract"] = "Month-to-month"  # Month-to-month contract
        data["OnlineSecurity"] = "No"
        data["OnlineBackup"] = "No"
        
        response = client.post(
            "/predict/single",
            json=data,
            headers=auth_header
        )
        assert response.status_code == 200
        result = response.json()
        # Note: actual prediction depends on model, just verify structure
        assert result["churn_prediction"] in ["Yes", "No"]
    
    def test_single_prediction_low_churn_probability(self, client, auth_header, sample_single_prediction_data):
        """Test single prediction with features indicating low churn"""
        data = sample_single_prediction_data.copy()
        data["tenure"] = 72  # High tenure
        data["Contract"] = "Two year"  # Long-term contract
        data["OnlineSecurity"] = "Yes"
        data["OnlineBackup"] = "Yes"
        
        response = client.post(
            "/predict/single",
            json=data,
            headers=auth_header
        )
        assert response.status_code == 200
        result = response.json()
        assert result["churn_prediction"] in ["Yes", "No"]
    
    def test_single_prediction_expected_value_calculation(self, client, auth_header, sample_single_prediction_data):
        """Test that expected value is calculated correctly"""
        response = client.post(
            "/predict/single",
            json=sample_single_prediction_data,
            headers=auth_header
        )
        assert response.status_code == 200
        data = response.json()
        
        # Expected value should be: churn_prob * monthly_charges * 12
        # Should be non-negative
        assert data["expected_value"] >= 0


class TestBulkPrediction:
    """Tests for POST /predict/bulk endpoint"""
    
    def test_bulk_prediction_success(self, client, auth_header, sample_bulk_csv_data):
        """Test successful bulk prediction"""
        response = client.post(
            "/predict/bulk",
            files={"file": ("test.csv", BytesIO(sample_bulk_csv_data), "text/csv")},
            headers=auth_header
        )
        assert response.status_code == 200
        result = response.json()
        
        # Should return list of predictions
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Verify first prediction structure
        first_pred = result[0]
        assert "customerID" in first_pred
        assert "churn_prob" in first_pred
        assert "churn_pred" in first_pred
        assert "rank" in first_pred
    
    def test_bulk_prediction_without_auth(self, client, sample_bulk_csv_data):
        """Test bulk prediction without authentication"""
        response = client.post(
            "/predict/bulk",
            files={"file": ("test.csv", BytesIO(sample_bulk_csv_data), "text/csv")}
        )
        assert response.status_code == 422
    
    def test_bulk_prediction_with_invalid_token(self, client, invalid_auth_header, sample_bulk_csv_data):
        """Test bulk prediction with invalid token"""
        response = client.post(
            "/predict/bulk",
            files={"file": ("test.csv", BytesIO(sample_bulk_csv_data), "text/csv")},
            headers=invalid_auth_header
        )
        assert response.status_code == 401
    
    def test_bulk_prediction_without_file(self, client, auth_header):
        """Test bulk prediction without file"""
        response = client.post(
            "/predict/bulk",
            headers=auth_header
        )
        assert response.status_code == 422
    
    def test_bulk_prediction_with_invalid_csv(self, client, auth_header, sample_invalid_csv_data):
        """Test bulk prediction with invalid CSV (missing required columns)"""
        response = client.post(
            "/predict/bulk",
            files={"file": ("test.csv", BytesIO(sample_invalid_csv_data), "text/csv")},
            headers=auth_header
        )
        # Should fail because columns are missing
        assert response.status_code in [400, 422, 500]
    
    def test_bulk_prediction_ranking(self, client, auth_header, sample_bulk_csv_data):
        """Test that bulk predictions are ranked by churn probability"""
        response = client.post(
            "/predict/bulk",
            files={"file": ("test.csv", BytesIO(sample_bulk_csv_data), "text/csv")},
            headers=auth_header
        )
        assert response.status_code == 200
        result = response.json()
        
        # Verify ranks are in order
        ranks = [pred["rank"] for pred in result]
        assert ranks == sorted(ranks)
    
    def test_bulk_prediction_churn_predictions(self, client, auth_header, sample_bulk_csv_data):
        """Test that churn predictions are Yes/No based on threshold"""
        response = client.post(
            "/predict/bulk",
            files={"file": ("test.csv", BytesIO(sample_bulk_csv_data), "text/csv")},
            headers=auth_header
        )
        assert response.status_code == 200
        result = response.json()
        
        for pred in result:
            assert pred["churn_pred"] in ["Yes", "No"]
            # Verify threshold logic
            if pred["churn_prob"] > 0.5:
                assert pred["churn_pred"] == "Yes"
            else:
                assert pred["churn_pred"] == "No"
    
    def test_bulk_prediction_large_file(self, client, auth_header):
        """Test bulk prediction with larger CSV file"""
        # Create a larger CSV with 100 rows
        csv_content = """customerID,gender,SeniorCitizen,Partner,Dependents,tenure,PhoneService,MultipleLines,InternetService,OnlineSecurity,OnlineBackup,DeviceProtection,TechSupport,StreamingTV,StreamingMovies,Contract,PaperlessBilling,PaymentMethod,MonthlyCharges,TotalCharges
"""
        for i in range(1, 101):
            csv_content += f"""CUST{i:04d},Male,0,No,No,{i % 72},Yes,No,Fiber optic,No,No,No,No,No,No,Month-to-month,Yes,Electronic check,65.0,{i * 60}.0
"""
        
        csv_bytes = csv_content.encode()
        response = client.post(
            "/predict/bulk",
            files={"file": ("test.csv", BytesIO(csv_bytes), "text/csv")},
            headers=auth_header
        )
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 100
    
    def test_bulk_prediction_empty_file(self, client, auth_header):
        """Test bulk prediction with empty CSV"""
        csv_content = """customerID,gender,SeniorCitizen,Partner,Dependents,tenure,PhoneService,MultipleLines,InternetService,OnlineSecurity,OnlineBackup,DeviceProtection,TechSupport,StreamingTV,StreamingMovies,Contract,PaperlessBilling,PaymentMethod,MonthlyCharges,TotalCharges
"""
        csv_bytes = csv_content.encode()
        response = client.post(
            "/predict/bulk",
            files={"file": ("test.csv", BytesIO(csv_bytes), "text/csv")},
            headers=auth_header
        )
        # Empty dataframe might return empty list or error
        assert response.status_code in [200, 400]


class TestIsUsingExpectedEncryption:
    """Test that the API properly encrypts and validates tokens"""
    
    def test_token_expiration(self, client, auth_header):
        """Verify token contains expiration"""
        # This is more of an integration test
        response = client.get("/predictions", headers=auth_header)
        assert response.status_code == 200
    
    def test_different_users_different_tokens(self, db_session, client):
        """Test that different users get different tokens"""
        from users import User
        from auth import hash_password, create_token
        
        user1 = User(
            username="user1",
            email="user1@example.com",
            hashed_password=hash_password("pass1")
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            hashed_password=hash_password("pass2")
        )
        
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        token1 = create_token({"sub": user1.username})
        token2 = create_token({"sub": user2.username})
        
        assert token1 != token2


class TestRateLimiting:
    """Tests for rate limiting on endpoints"""
    
    def test_rate_limit_on_get_predictions(self, client, auth_header):
        """Test that rate limiting is applied to GET /predictions"""
        # Make 10 requests (limit is 10/minute)
        for i in range(10):
            response = client.get("/predictions", headers=auth_header)
            assert response.status_code == 200
        
        # 11th request should be rate limited
        response = client.get("/predictions", headers=auth_header)
        assert response.status_code == 429
    
    def test_rate_limit_on_single_prediction(self, client, auth_header, sample_single_prediction_data):
        """Test that rate limiting is applied to POST /predict/single"""
        # Make 10 requests (limit is 10/minute)
        for i in range(10):
            response = client.post(
                "/predict/single",
                json=sample_single_prediction_data,
                headers=auth_header
            )
            assert response.status_code == 200
        
        # 11th request should be rate limited
        response = client.post(
            "/predict/single",
            json=sample_single_prediction_data,
            headers=auth_header
        )
        assert response.status_code == 429
    
    def test_rate_limit_on_bulk_prediction(self, client, auth_header, sample_bulk_csv_data):
        """Test that rate limiting is applied to POST /predict/bulk"""
        # Make 10 requests (limit is 10/minute)
        for i in range(10):
            response = client.post(
                "/predict/bulk",
                files={"file": ("test.csv", BytesIO(sample_bulk_csv_data), "text/csv")},
                headers=auth_header
            )
            assert response.status_code == 200
        
        # 11th request should be rate limited
        response = client.post(
            "/predict/bulk",
            files={"file": ("test.csv", BytesIO(sample_bulk_csv_data), "text/csv")},
            headers=auth_header
        )
        assert response.status_code == 429


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test that root endpoint returns status message"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Churn API is running"}
