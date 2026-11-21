
import os
import re
import csv
import io
import time
import random
import string
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

API_KEY = os.environ.get("DASHBOARD_API_KEY", "")

def authenticate():
    if not API_KEY:
        return False
    return request.headers.get("X-API-Key") == API_KEY

def generate_code():
    chars = string.ascii_uppercase + string.digits
    return random.choice("78") + "".join(
        random.choices(chars, k=11)
    )

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "online"})

@app.route("/api/generate", methods=["POST"])
def generate():
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}

    try:
        count = int(data.get("count", 1))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid count"}), 400

    if not 1 <= count <= 1000:
        return jsonify({"error": "Count must be 1–1000"}), 400

    results = []
    for i in range(count):
        results.append({
            "number": i + 1,
            "code": generate_code(),
            "status": "SIMULATED",
            "created": int(time.time())
        })

    return jsonify({
        "success": True,
        "total": count,
        "results": results
    })

@app.route("/api/export", methods=["POST"])
def export():
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    results = data.get("results", [])

    if not isinstance(results, list) or len(results) > 1000:
        return jsonify({"error": "Invalid results"}), 400

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Number", "Code", "Status", "Created"])

    for item in results:
        if not isinstance(item, dict):
            continue

        writer.writerow([
            item.get("number", ""),
            item.get("code", ""),
            item.get("status", ""),
            item.get("created", "")
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=test_codes.csv"
        }
    )

# Vercel entry point
