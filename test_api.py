import requests
import json

def test_api():
    base_url = "http://localhost:8002"
    
    test_codes = [
        {
            "name": "SQL Injection Test",
            "code": """def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'")
    return cursor.fetchone()"""
        }
    ]
    
    print("Testing VulnFix-AI API...")
    print("=" * 60)
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{base_url}/health")
        print("Health Check:", health_response.json())
    except:
        print("❌ API server is not running. Please start it with: python api_server.py")
        return
    
    for test_case in test_codes:
        print(f"\n🔍 Testing: {test_case['name']}")
        print("Input Code:")
        print(test_case['code'])
        
        response = requests.post(f"{base_url}/analyze", json={"code": test_case['code']})
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Analysis Results:")
            analysis = result["analysis"]
            for key, value in analysis.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_api()
