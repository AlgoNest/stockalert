from flask import Flask, render_template, request, jsonify
import os

from github_service import GitHubService

app = Flask(__name__)

def get_github_service():
    token = os.environ.get("GITHUB_TOKEN")
    repo_owner = os.environ.get("GITHUB_REPO_OWNER")
    repo_name = os.environ.get("GITHUB_REPO_NAME")
    if not token or not repo_owner or not repo_name:
        return None
    return GitHubService(token, repo_owner, repo_name)

@app.route("/")
def index():
    return render_template("final-landing-page.html")

@app.route("/mockup/<path:filename>")
def mockup(filename):
    return render_template(filename)

@app.route("/waitlist", methods=["GET"])
def waitlist():
    return render_template("waitlist.html")

@app.route("/waitlist", methods=["POST"])
def waitlist_submit():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        email = data.get("email")
        if not email:
            return jsonify({"error": "Email is required"}), 400

        entry = {
            "name": data.get("name", ""),
            "email": email,
            "plan": data.get("plan", ""),
            "problem": data.get("problem", ""),
            "urgency": data.get("urgency", ""),
            "current_tool": data.get("current_tool", ""),
            "willing_to_pay": data.get("willing_to_pay", ""),
            "commitments": data.get("commitments", []),
            "note": data.get("note", ""),
        }

        gh = get_github_service()
        if gh is None:
            return jsonify({"error": "GitHub service not configured"}), 500

        gh.add_waitlist_entry(entry)

        return jsonify({"message": "Success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
