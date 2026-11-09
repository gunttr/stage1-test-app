import pytest
from fastapi.testclient import TestClient
from app import app, orders

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_orders():
    """Очищает заказы перед каждым тестом"""
    orders.clear()
    yield


class TestRootEndpoint:
    def test_root_returns_hello_message(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello this is test app!"}


class TestHealthEndpoint:
    def test_health_returns_healthy_status(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestPostOrder:
    def test_create_order_successfully(self):
        order_data = {
            "username": "test_user",
            "product_name": "Test Product",
            "quantity": 5
        }
        
        response = client.post("/orders", json=order_data)
        
        assert response.status_code == 200
        assert "order_id" in response.json()
        assert isinstance(response.json()["order_id"], int)
    
    def test_create_order_with_invalid_data(self):
        invalid_order = {
            "username": "",
            "product_name": "Product",
            "quantity": -1
        }
        
        response = client.post("/orders", json=invalid_order)
        assert response.status_code == 422
    
    def test_create_order_missing_fields(self):
        incomplete_order = {
            "username": "test_user"
        }
        
        response = client.post("/orders", json=incomplete_order)
        assert response.status_code == 422


class TestGetOrder:
    def test_get_existing_order(self):
        # Сначала создаем заказ
        order_data = {
            "username": "test_user",
            "product_name": "Test Product",
            "quantity": 3
        }
        create_response = client.post("/orders", json=order_data)
        order_id = create_response.json()["order_id"]
        
        # Получаем заказ
        response = client.get(f"/order/{order_id}")
        
        assert response.status_code == 200
        assert response.json()["id"] == order_id
        assert "created_at" in response.json()
    
    def test_get_nonexistent_order(self):
        response = client.get("/order/9999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Not found"
    
    def test_get_order_with_zero_id(self):
        response = client.get("/order/0")
        assert response.status_code == 404
    
    def test_get_order_with_negative_id(self):
        response = client.get("/order/-1")
        assert response.status_code == 404


class TestOrderFlow:
    def test_create_and_retrieve_order(self):
        order_data = {
            "username": "john_doe",
            "product_name": "Laptop",
            "quantity": 2
        }
        
        create_response = client.post("/orders", json=order_data)
        assert create_response.status_code == 200
        order_id = create_response.json()["order_id"]
        
        get_response = client.get(f"/order/{order_id}")
        assert get_response.status_code == 200
        
        order = get_response.json()
        assert order["id"] == order_id
        assert "created_at" in order