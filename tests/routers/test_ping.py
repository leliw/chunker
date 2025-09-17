def test_ping(client):
    # When: A GET request is made to /api/ping
    response = client.get("/api/ping")
    # Then: The response status code is 200
    assert 200 == response.status_code
