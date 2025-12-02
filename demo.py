import requests
import json

def demo():
    print("🚀 VULNFIX-AI FINAL DEMO")
    print("=" * 60)
    print("A working AI-powered security vulnerability detection system!")
    print("=" * 60)
    
    base_url = "http://localhost:8002"  # CHANGED TO 8002
    
    # Test cases
    test_cases = [
        {
            "name": "User Login - SQL Injection",
            "code": """def user_login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    return cursor.fetchone()"""
        },
        {
            "name": "Product Search - F-string Injection", 
            "code": """def search_products(keyword):
    cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{keyword}%'")
    return cursor.fetchall()"""
        },
        {
            "name": "Account Update - Multiple Vulnerabilities",
            "code": """def update_account(user_id, balance):
    cursor.execute("UPDATE accounts SET balance = " + balance + " WHERE user_id = " + user_id)
    cursor.execute("INSERT INTO audit_log VALUES ('" + user_id + "', 'balance_updated')")"""
        }
    ]
    
    print("\n📊 Testing AI Model on Real-World Scenarios...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"SCENARIO {i}: {test_case['name']}")
        print(f"{'='*50}")
        print("💻 VULNERABLE CODE:")
        print(test_case['code'])
        
        try:
            response = requests.post(f"{base_url}/analyze", json={"code": test_case['code']})
            
            if response.status_code == 200:
                result = response.json()
                analysis = result["analysis"]
                
                print("\n🔍 AI ANALYSIS:")
                print(f"   🚨 Vulnerability: {analysis['vulnerability']}")
                print(f"   📝 Explanation: {analysis['explanation']}")
                print(f"   ⚠️  Risk Level: {analysis['risk_level']}")
                print(f"   ✅ Fixed Code:\n{analysis['fixed_code']}")
            else:
                print(f"\n❌ API Error: {response.text}")
                
        except Exception as e:
            print(f"\n❌ Connection Error: {e}")
            print("   Make sure the API server is running: python api_server.py")
    
    print(f"\n{'='*60}")
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("📁 Your trained model: ./vulnfix-ai-model/")
    print("🌐 Your API server: http://localhost:8002")  # CHANGED TO 8002
    print("🔧 Next steps: Expand training data, add more vulnerability types!")
    print("=" * 60)

if __name__ == "__main__":
    demo()
