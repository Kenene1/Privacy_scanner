import requests
import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime

def check_https(url):
    """
    This function checks if a website uses HTTPS, validates its SSL/TLS certificate,
    and returns detailed information about the website's security status.
    """
    try:
        # Ensure the URL starts with "https://"
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = "https://" + url  # Prepend "https://" if not present

        # Check if the URL uses HTTPS
        if not url.startswith("https://"):
            return f"❌ The website {url} does not use HTTPS."

        # Check the SSL/TLS certificate validity
        ssl_certificate_info = check_ssl_certificate(url)
        if ssl_certificate_info['valid']:
            return f"✔ The website {url} is using HTTPS and has a valid SSL/TLS certificate.\n" + \
                   f"Certificate details:\n" + \
                   f"Issuer: {ssl_certificate_info['issuer']}\n" + \
                   f"Expiration Date: {ssl_certificate_info['expiration_date']}"
        else:
            return f"❌ The website {url} has an SSL/TLS certificate issue:\n" + \
                   f"Issuer: {ssl_certificate_info['issuer']}\n" + \
                   f"Expiration Date: {ssl_certificate_info['expiration_date']}"

    except requests.exceptions.RequestException as e:
        # Handle connection errors, invalid URL, or timeouts
        return f"❌ There was an error checking {url}: {e}"

def check_ssl_certificate(url):
    """
    This function checks the SSL/TLS certificate of the given URL.
    It retrieves details like issuer, expiration date, and validity.
    """
    # Parsing the URL to get the domain
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path.split('/')[0]

    # Establish a secure SSL connection to the website
    try:
        # Using SSLContext to create a secure connection
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                ssl_info = ssock.getpeercert()
                issuer = ssl_info.get('issuer', 'Unknown Issuer')
                expiration_date = ssl_info.get('notAfter', 'Unknown Expiration Date')
                expiration_date = format_certificate_date(expiration_date)
                is_valid = check_certificate_expiry(expiration_date)

                return {
                    'valid': is_valid,
                    'issuer': issuer,
                    'expiration_date': expiration_date
                }

    except Exception as e:
        return {'valid': False, 'issuer': 'Unknown', 'expiration_date': 'Unknown'}

def format_certificate_date(expiration_date_str):
    """
    Format the SSL certificate expiration date from its raw format.
    """
    try:
        # SSL cert expiration date is in the format "MMM DD HH:MM:SS YYYY GMT"
        expiration_date = datetime.strptime(expiration_date_str, "%b %d %H:%M:%S %Y GMT")
        return expiration_date.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return expiration_date_str  # If the format doesn't match, return as is.

def check_certificate_expiry(expiration_date_str):
    """
    Check whether the certificate is expired or valid.
    """
    try:
        expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now()
        return expiration_date > current_date  # Return True if the certificate is still valid
    except ValueError:
        return False
