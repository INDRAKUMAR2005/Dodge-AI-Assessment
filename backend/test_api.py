from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_graph_endpoint():
    response = client.get("/api/graph")
    if response.status_code == 200:
        data = response.json()
        print(f"Nodes: {len(data['nodes'])}")
        print(f"Links: {len(data['links'])}")
        print("Sample Node:", data['nodes'][0] if data['nodes'] else "None")
        print("Sample Link:", data['links'][0] if data['links'] else "None")
    else:
        print(f"Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_graph_endpoint()
