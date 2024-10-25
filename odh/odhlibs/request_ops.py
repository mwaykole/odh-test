import warnings
import requests
import json

# Suppress InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)

import requests
import time


def infer_model(input_data, endpoint="", url=None, token=None, retries=3, retry_timeout=5):
    if url is None or endpoint == "":
        raise ValueError("Both url and endpoint must be provided.")

    full_url = f"{url}/{endpoint}"

    headers = {
        'Content-Type': 'application/json'
    }

    if token is not None:
        headers['Authorization'] = f'Bearer {token}'

    for attempt in range(retries):
        try:
            # Disable SSL verification (for testing only)
            response = requests.post(full_url, headers=headers, json=input_data, verify=False)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
            return response.json()

        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_timeout} seconds...")
                time.sleep(retry_timeout)
            else:
                print(f"Attempt {attempt + 1} failed. No more retries left.")
                return None  # Re-raise the exception if all attempts fail

inp={ "model_name": "example-onnx-mnist", "inputs": [{ "name": "Input3", "shape": [1, 1, 28, 28], "datatype": "FP32", "data": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01176471, 0.07058824, 0.07058824, 0.07058824, 0.49411765, 0.53333336, 0.6862745, 0.10196079, 0.6509804, 1.0, 0.96862745, 0.49803922, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.11764706, 0.14117648, 0.36862746, 0.6039216, 0.6666667, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.88235295, 0.6745098, 0.99215686, 0.9490196, 0.7647059, 0.2509804, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.19215687, 0.93333334, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.9843137, 0.3647059, 0.32156864, 0.32156864, 0.21960784, 0.15294118, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.07058824, 0.85882354, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.7764706, 0.7137255, 0.96862745, 0.94509804, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3137255, 0.6117647, 0.41960785, 0.99215686, 0.99215686, 0.8039216, 0.04313726, 0.0, 0.16862746, 0.6039216, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05490196, 0.00392157, 0.6039216, 0.99215686, 0.3529412, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.54509807, 0.99215686, 0.74509805, 0.00784314, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.04313726, 0.74509805, 0.99215686, 0.27450982, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.13725491, 0.94509804, 0.88235295, 0.627451, 0.42352942, 0.00392157, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.31764707, 0.9411765, 0.99215686, 0.99215686, 0.46666667, 0.09803922, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1764706, 0.7294118, 0.99215686, 0.99215686, 0.5882353, 0.10588235, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0627451, 0.3647059, 0.9882353, 0.99215686, 0.73333335, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9764706, 0.99215686, 0.9764706, 0.2509804, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.18039216, 0.50980395, 0.7176471, 0.99215686, 0.99215686, 0.8117647, 0.00784314, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.15294118, 0.5803922, 0.8980392, 0.99215686, 0.99215686, 0.99215686, 0.98039216, 0.7137255, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.09411765, 0.44705883, 0.8666667, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.7882353, 0.30588236, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.09019608, 0.25882354, 0.8352941, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.7764706, 0.31764707, 0.00784314, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.07058824, 0.67058825, 0.85882354, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.7647059, 0.3137255, 0.03529412, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.21568628, 0.6745098, 0.8862745, 0.99215686, 0.99215686, 0.99215686, 0.99215686, 0.95686275, 0.52156866, 0.04313726, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.53333336, 0.99215686, 0.99215686, 0.99215686, 0.83137256, 0.5294118, 0.5176471, 0.0627451, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] }]}

# infer_model(input_data= inp,
#             url="https://test-mnist-serverless-1-test.apps-crc.testing",
#             endpoint="v2/models/test-mnist-serverless-1/infer",
#             token="eyJhbGciOiJSUzI1NiIsImtpZCI6InlEQWdDV0h2aWc0b2t0cGZjcnB0OGFwNV9hNWluYnVhbUZvamVGbV9XaUkifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjIl0sImV4cCI6MTcyOTc5ODYwMiwiaWF0IjoxNzI5Nzk1MDAyLCJpc3MiOiJodHRwczovL2t1YmVybmV0ZXMuZGVmYXVsdC5zdmMiLCJqdGkiOiI5ZWQ4Y2IwMi00NTIwLTQ1YTAtYjczZS03MDljOWM5YjA5OWYiLCJrdWJlcm5ldGVzLmlvIjp7Im5hbWVzcGFjZSI6InRlc3QiLCJzZXJ2aWNlYWNjb3VudCI6eyJuYW1lIjoibW9kZWxzLWJ1Y2tldC1zYSIsInVpZCI6ImNiMWRiZGFmLTY3MDctNDUwZi1iODRkLTQ5ZTQyMTE4ZGVmMCJ9fSwibmJmIjoxNzI5Nzk1MDAyLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6dGVzdDptb2RlbHMtYnVja2V0LXNhIn0.WKnMITVQyAu5DEJ-6tNLJn9-RuSGAhbXWnclFrkd0PjrWeJFURGPNNlfas4F4Yj7P5pnxYkDDSlj2upk0K_vdQIzBnl8K5qbnxaPAIaZDIqP8LFR35Ll5PwRPI14OGCebNN3k_3l1Csx2mCwfrYooJp2oiH0WaprInx5f7k7tlTeH7XW1ITRTLg21hfBR51k2QguD0sX9F4wCVFgEOZf2I7p4Nd3jTKzhfzX6HtVAOmfjCW-dWP527b66b14zBYIo3orh8piKceS4jddBDNWQUtnqvNop4Sa6ftm0TF40m3NImnWuaXCI4_UyN4RFvimST-laSW0tWBRSiZj4IEjIr4_FrLsest0SlbPwXnMrVq5wDNPszGCtjurR2eCdgWFA-J7nDnjA37IwbkKACJ46hZ2RjM_96zjJ1_0syCDsRP8hXb09cIV_58d4783VZnrOYWSGHK-dKuH8V6mGdiWzgqosZlIxpLmOc7AtQKb0yjeejyBqH2Y4niDmg_VDSsD4xyOgmrUzoaGRJ3oLfKjDDevwUF9DrLu_oNQipy7MjgMiX7KTm-kS5Qo4NUfz6v4IEHZGDZk8opmFnjvt0hVi6EiQeG0OJ8f0U8-W_RQwKjNQ9kIcZJRUkAJjamwSteuE57G7-yct9mhCnouplJlpkufpHlIGqozrS65hQNPths"
#             )