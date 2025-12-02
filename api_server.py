from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import re

app = FastAPI(title="VulnFix-AI API", version="1.0")

# Add CORS middleware to handle browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

class CodeRequest(BaseModel):
    code: str
    language: str = "python"

class VulnFixAI:
    def __init__(self, model_path="./vulnfix-ai-model"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
    
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
        
        if "Explanation:" in response:
            exp_start = response.find("Explanation:") + len("Explanation:")
            exp_end = response.find("Fixed Code:")
            if exp_end == -1:
                exp_end = len(response)
            result["explanation"] = response[exp_start:exp_end].strip()
        
        if "Fixed Code:" in response:
            code_start = response.find("Fixed Code:") + len("Fixed Code:")
            result["fixed_code"] = response[code_start:].strip()
        
        return result

# Initialize the model
print("Loading VulnFix-AI model...")
analyzer = VulnFixAI()
print("Model loaded successfully!")
print("CORS enabled - Web interface should work now!")

@app.get("/")
async def root():
    return {"message": "VulnFix-AI API", "status": "running", "cors": "enabled"}

@app.post("/analyze")
async def analyze_code(request: CodeRequest):
    try:
        print(f"Analyzing code: {request.code[:100]}...")
        result = analyzer.analyze_code(request.code)
        return {
            "status": "success",
            "analysis": result
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": True}

# Handle OPTIONS requests for CORS preflight
@app.options("/analyze")
async def analyze_options():
    return {"message": "CORS preflight"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
