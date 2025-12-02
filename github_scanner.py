import requests
import os
import base64
from github import Github

def scan_github_repo(repo_url, api_key):
    """Scan a GitHub repository for security vulnerabilities"""
    
    # Extract owner and repo name from URL
    parts = repo_url.rstrip('/').split('/')
    owner, repo = parts[-2], parts[-1]
    
    g = Github(api_key)
    repo = g.get_repo(f"{owner}/{repo}")
    
    print(f"Scanning repository: {repo.full_name}")
    
    vulnerabilities_found = []
    
    # Get all Python files
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        elif file_content.name.endswith('.py'):
            print(f"Analyzing: {file_content.path}")
            
            # Get file content
            content = base64.b64decode(file_content.content).decode('utf-8')
            
            # Send to VulnFix AI
            response = requests.post('http://localhost:8002/analyze', json={
                'code': content,
                'language': 'python'
            })
            
            if response.status_code == 200:
                result = response.json()
                if result['analysis']['vulnerability'] != 'Unknown':
                    vulnerabilities_found.append({
                        'file': file_content.path,
                        'analysis': result['analysis']
                    })
    
    return vulnerabilities_found

def generate_report(vulnerabilities, output_file='security_report.md'):
    """Generate a security report"""
    
    with open(output_file, 'w') as f:
        f.write("# Security Vulnerability Report\n\n")
        f.write(f"Found {len(vulnerabilities)} potential vulnerabilities\n\n")
        
        for vuln in vulnerabilities:
            f.write(f"## File: {vuln['file']}\n")
            f.write(f"**Vulnerability**: {vuln['analysis']['vulnerability']}\n")
            f.write(f"**Risk Level**: {vuln['analysis']['risk_level']}\n")
            f.write(f"**Explanation**: {vuln['analysis']['explanation']}\n")
            f.write("**Fixed Code**:\n```python\n")
            f.write(vuln['analysis']['fixed_code'])
            f.write("\n```\n\n")
    
    print(f"Report generated: {output_file}")

if __name__ == "__main__":
    # Example usage
    repo_url = "https://github.com/example/repo"  # Replace with actual repo
    api_key = "your_github_token"  # Replace with your token
    
    vulnerabilities = scan_github_repo(repo_url, api_key)
    generate_report(vulnerabilities)
