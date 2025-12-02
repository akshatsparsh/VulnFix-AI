import json
import random

def generate_security_dataset(num_samples=300):
    """Generate multiple types of security vulnerabilities"""
    dataset = []
    
    templates = [
        # SQL Injection (existing)
        {
            "vulnerable": "cursor.execute(\"SELECT * FROM users WHERE username = '\" + username + \"'\")\n",
            "fixed": "cursor.execute(\"SELECT * FROM users WHERE username = %s\", (username,))\n",
            "vuln_type": "SQL Injection",
            "explanation": "Direct string concatenation allows SQL injection attacks"
        },
        # XSS (Cross-Site Scripting)
        {
            "vulnerable": "return f'<div>Welcome {user_input}</div>'\n",
            "fixed": "from markupsafe import escape\nreturn f'<div>Welcome {escape(user_input)}</div>'\n",
            "vuln_type": "XSS",
            "explanation": "User input directly rendered in HTML without escaping"
        },
        # Command Injection
        {
            "vulnerable": "os.system(\"ping \" + user_input)\n",
            "fixed": "import subprocess\nsubprocess.run([\"ping\", user_input])\n",
            "vuln_type": "Command Injection", 
            "explanation": "User input passed directly to system command"
        },
        # Path Traversal
        {
            "vulnerable": "open(\"/uploads/\" + filename)\n",
            "fixed": "import os\nsafe_filename = os.path.basename(filename)\nopen(\"/uploads/\" + safe_filename)\n",
            "vuln_type": "Path Traversal",
            "explanation": "User input used in file paths without validation"
        },
        # Hardcoded Secrets
        {
            "vulnerable": "API_KEY = \"sk-1234567890abcdef\"\n",
            "fixed": "import os\nAPI_KEY = os.environ.get('API_KEY')\n",
            "vuln_type": "Hardcoded Secret",
            "explanation": "Sensitive credentials stored in source code"
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
    dataset = generate_security_dataset()
    with open('enhanced_training_data.jsonl', 'w') as f:
        for item in dataset:
            f.write(json.dumps(item) + '\n')
    print(f"Generated {len(dataset)} enhanced training samples")
