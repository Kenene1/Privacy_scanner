import ssl
import socket
import dns.resolver
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Check for SSL Certificate
def check_ssl_cert(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
        return {"status": "Valid", "details": cert}
    except Exception as e:
        return {"status": "Invalid or Absent", "details": str(e)}

# Check DNS Records
def check_dns(domain):
    results = {}
    try:
        a_records = dns.resolver.resolve(domain, "A")
        results["A"] = [str(record) for record in a_records]
    except Exception as e:
        results["A"] = f"Error: {e}"

    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        results["MX"] = [str(record) for record in mx_records]
    except Exception as e:
        results["MX"] = f"Error: {e}"

    return results

# Analyze HTTP Headers for Privacy and Security
def analyze_headers(domain):
    try:
        response = requests.get(f"https://{domain}", timeout=5)
        headers = response.headers

        required_headers = {
            "Strict-Transport-Security": "HSTS ensures secure HTTPS connections.",
            "Content-Security-Policy": "CSP mitigates cross-site scripting (XSS) attacks.",
            "X-Content-Type-Options": "Prevents MIME type confusion.",
            "Referrer-Policy": "Controls referrer information sharing.",
        }

        strengths = []
        weaknesses = []

        for header, description in required_headers.items():
            if header in headers:
                strengths.append(f"{header}: {description}")
            else:
                weaknesses.append(f"{header}: Missing - {description}")

        return strengths, weaknesses
    except Exception as e:
        return [], [f"Error analyzing headers: {str(e)}"]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        domain = request.form.get("domain")
        ssl_result = check_ssl_cert(domain)
        dns_result = check_dns(domain)
        strengths, weaknesses = analyze_headers(domain)

        return render_template(
            "result.html",
            domain=domain,
            ssl_result=ssl_result,
            dns_result=dns_result,
            strengths=strengths,
            weaknesses=weaknesses,
        )
    return render_template("index.html")

@app.route("/health")
def health():
    return "App is running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True, ssl_context=("certs/cert.pem", "certs/key.pem"))
