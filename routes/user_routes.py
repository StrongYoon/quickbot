from flask import Blueprint, request, jsonify
import json, os
from utils.logger import log_action

user_bp = Blueprint("user", __name__)
USER_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

@user_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    phone = data.get("phone")
    cid = data.get("cid")
    if not phone or not cid:
        return jsonify({"status": "fail", "reason": "Missing phone or cid"}), 400

    users = load_users()
    if any(user["cid"] == cid for user in users):
        return jsonify({"status": "exists"})

    users.append({"phone": phone, "cid": cid})
    save_users(users)
    log_action("등록", f"{phone} / {cid}")
    return jsonify({"status": "ok"})

@user_bp.route("/unregister", methods=["POST"])
def unregister_user():
    data = request.get_json()
    cid = data.get("cid")

    users = load_users()
    users = [user for user in users if user["cid"] != cid]
    save_users(users)
    log_action("삭제", f"CID: {cid}")
    return jsonify({"status": "deleted"})

@user_bp.route("/users", methods=["GET"])
def list_users():
    return jsonify(load_users())


@user_bp.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "서버가 정상 작동 중입니다!"})

user_routes = user_bp