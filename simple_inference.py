import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import re

class SimpleVulnFixAI:
    def __init__(self, model_path="./vulnfix-ai-model"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        print("Loading tokenizer and model...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        print("Model loaded successfully!")
    
    def analyze_code(self, code_snippet):
        prompt = f"""Analyze this Python code for security vulnerabilities and provide a secure fix:

Code:
{code_snippet}

Explain the vulnerability and provide the patched code."""
        
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=400,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                num_return_sequences=1
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response[len(prompt):].strip()
        
        return self.parse_response(response)
    
    def parse_response(self, response):
        result = {
            "vulnerability": "Unknown",
            "explanation": "",
            "risk_level": "Medium",
            "fixed_code": "",
            "recommendation": ""
        }
        
        if "SQL Injection" in response:
            result["vulnerability"] = "SQL Injection"
            result["risk_level"] = "High"
        
        # Extract explanation
        if "Explanation:" in response:
            exp_start = response.find("Explanation:") + len("Explanation:")
            exp_end = response.find("Fixed Code:")
            if exp_end == -1:
                exp_end = len(response)
            result["explanation"] = response[exp_start:exp_end].strip()
        
        # Extract fixed code
        if "Fixed Code:" in response:
            code_start = response.find("Fixed Code:") + len("Fixed Code:")
            result["fixed_code"] = response[code_start:].strip()
        else:
            # Fallback: look for code blocks
            lines = response.split('\n')
            code_lines = []
            in_code = False
            for line in lines:
                if 'def ' in line or 'cursor.' in line or 'execute' in line:
                    code_lines.append(line)
                    in_code = True
                elif in_code and line.strip() and not line.startswith(' '):
                    break
            if code_lines:
                result["fixed_code"] = '\n'.join(code_lines)
        
        return result

if __name__ == "__main__":
    print("🚀 Testing VulnFix-AI with trained model...")
    print("=" * 60)
    
    # Initialize the analyzer with our trained model
    analyzer = SimpleVulnFixAI("./vulnfix-ai-model")
    
    test_cases = [
        {
            "name": "Basic SQL Injection",
            "code": """def get_user(username):
    cursor.execute("SELECT * FROM users WHERE username = '" + username + "'")
    return cursor.fetchone()"""
        },
        {
            "name": "F-string SQL Injection", 
            "code": """def delete_product(product_id):
    query = f"DELETE FROM products WHERE id = {product_id}"
    cursor.execute(query)"""
        },
        {
            "name": "Multiple Concatenation",
            "code": """def update_user(user_id, new_email):
    cursor.execute("UPDATE users SET email = '" + new_email + "' WHERE id = " + user_id)"""
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST CASE {i}: {test_case['name']}")
        print("=" * 50)
        print("📝 Input Code:")
        print(test_case['code'])
        print("\n🔍 Analysis Result:")
        
        try:
            result = analyzer.analyze_code(test_case['code'])
            for key, value in result.items():
                print(f"   {key}: {value}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ VulnFix-AI Testing Completed!")
