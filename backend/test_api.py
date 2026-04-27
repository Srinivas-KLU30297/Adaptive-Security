import requests

# 1. Login
login_data = {
    "email": "admin@cybershield.ai",
    "password": "Admin@123"
}
response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
print("Login status:", response.status_code)
if response.status_code != 200:
    print(response.text)
    exit()

token = response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# 2. Analyze Email
email_data = {"text": "URGENT! Click here"}
response = requests.post("http://localhost:8000/api/v1/analyze/email", json=email_data, headers=headers)
print("Analyze status:", response.status_code)
if response.status_code != 200:
    print(response.text)
    exit()

case_id = response.json().get("case_id")
print("Case ID:", case_id)

# 3. Download Report
response = requests.get(f"http://localhost:8000/api/v1/cases/{case_id}/report", headers=headers)
print("Report status:", response.status_code)
if response.status_code != 200:
    print(response.text)
