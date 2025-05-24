from flask import Blueprint, request, jsonify
import os, json
import pandas as pd
from utils.logger import log_action

excel_bp = Blueprint("excel", __name__)
USER_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

@excel_bp.route("/upload_excel", methods=["POST"])
def upload_excel():
    file = request.files.get("file")
    if not file:
        return jsonify({"status": "fail", "reason": "No file uploaded"}), 400

    df = pd.read_excel(file)
    users = load_users()
    count = 0

    for _, row in df.iterrows():
        phone = str(row.get("phone"))
        cid = str(row.get("cid"))
        if not phone or not cid:
            continue
        if not any(u["cid"] == cid for u in users):
            users.append({"phone": phone, "cid": cid})
            count += 1

    save_users(users)
    log_action("엑셀 업로드", f"{count}명 등록")
    return jsonify({"status": "ok", "count": count})

@excel_bp.route("/download_excel", methods=["GET"])
def download_excel():
    users = load_users()
    df = pd.DataFrame(users)
    output_path = "downloads/member_list.xlsx"
    os.makedirs("downloads", exist_ok=True)
    df.to_excel(output_path, index=False)
    return open(output_path, "rb").read()

excel_routes = excel_bp