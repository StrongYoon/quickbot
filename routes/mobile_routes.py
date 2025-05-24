from flask import Blueprint, request, jsonify
import jwt
import datetime
import json
import os

mobile_bp = Blueprint("mobile", __name__)
SECRET_KEY = "quickbot-secret-key-2025"  # 나중에 환경변수로 변경
USER_FILE = "data/users.json"


def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return json.load(f)


# 모바일 로그인
@mobile_bp.route("/mobile/login", methods=["POST"])
def mobile_login():
    data = request.get_json()
    phone = data.get("phone")
    cid = data.get("cid")

    # 기존 회원 확인
    users = load_users()
    user_exists = any(u["phone"] == phone and u["cid"] == cid for u in users)

    if user_exists:
        # JWT 토큰 생성
        token = jwt.encode({
            'phone': phone,
            'cid': cid,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({
            "status": "success",
            "token": token,
            "message": "로그인 성공"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "등록되지 않은 사용자입니다"
        }), 401


# 토큰 검증
@mobile_bp.route("/mobile/verify", methods=["POST"])
def verify_token():
    token = request.headers.get("Authorization")

    try:
        if token and token.startswith("Bearer "):
            token = token[7:]  # "Bearer " 제거

        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return jsonify({"status": "valid", "user": decoded})
    except:
        return jsonify({"status": "invalid"}), 401


mobile_routes = mobile_bp