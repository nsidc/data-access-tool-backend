from app import app

def test_app():
    with app.test_client() as client:
        result = client.get("/")
        assert result.status_code == 200
