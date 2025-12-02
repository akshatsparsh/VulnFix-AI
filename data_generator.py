import json
import random

def generate_sql_injection_dataset(num_samples=200):
    """Generate synthetic SQL injection vulnerable/fixed pairs"""
    dataset = []
    
    templates = [
        {
            "vulnerable": "cursor.execute(\"SELECT * FROM users WHERE username = '\" + username + \"'\")\n",
            "fixed": "cursor.execute(\"SELECT * FROM users WHERE username = %s\", (username,))\n",
            "vuln_type": "SQL Injection",
            "explanation": "Direct string concatenation allows SQL injection attacks"
        },
        {
            "vulnerable": "query = f\"DELETE FROM products WHERE id = {user_input}\"\ncursor.execute(query)\n",
            "fixed": "cursor.execute(\"DELETE FROM products WHERE id = %s\", (user_input,))\n",
            "vuln_type": "SQL Injection", 
            "explanation": "f-string interpolation still vulnerable to SQL injection"
        },
        {
            "vulnerable": "cursor.execute(\"UPDATE accounts SET balance = \" + amount + \" WHERE user_id = \" + user_id)\n",
            "fixed": "cursor.execute(\"UPDATE accounts SET balance = %s WHERE user_id = %s\", (amount, user_id))\n",
            "vuln_type": "SQL Injection",
            "explanation": "Numerical SQL injection vulnerability"
        }
    ]
    
    for i in range(num_samples):
        template = random.choice(templates)
        
        prompt = f"""Analyze this Python code for security vulnerabilities and provide a secure fix:

Code:
{template['vulnerable']}

Explain the vulnerability and provide the patched code."""
        
        completion = f"""Vulnerability: {template['vuln_type']}
Explanation: {template['explanation']}
Fixed Code:
{template['fixed']}"""
        
        dataset.append({
            "prompt": prompt,
            "completion": completion
        })
    
    return dataset

if __name__ == "__main__":
    dataset = generate_sql_injection_dataset()
    with open('training_data.jsonl', 'w') as f:
        for item in dataset:
            f.write(json.dumps(item) + '\n')
    print(f"Generated {len(dataset)} training samples")
