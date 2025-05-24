from flask import Flask, jsonify, request, make_response
from routes.user_routes import user_routes
from routes.excel_routes import excel_routes
from routes.mobile_routes import mobile_routes
from socket_routes import init_socketio
import os

app = Flask(__name__)


# 수동 CORS 설정만 사용
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Allow-Methods'] = '*'
        return response


# 라우터 등록
app.register_blueprint(user_routes)
app.register_blueprint(excel_routes)
app.register_blueprint(mobile_routes)

# SocketIO 초기화
socketio = init_socketio(app)


# 관리자 전용 - 실시간 모니터링 API
@app.route("/admin/realtime-status", methods=["GET"])
def realtime_status():
    """실시간 시스템 상태 조회"""
    from socket_routes import connected_drivers, connected_admins

    return jsonify({
        "status": "ok",
        "connected_drivers": len(connected_drivers),
        "connected_admins": len(connected_admins),
        "driver_list": list(connected_drivers.keys()),
        "timestamp": "2025-05-25T12:00:00"
    })


# 관리자 전용 - 오더 전송 API
@app.route("/admin/send-order", methods=["POST"])
def send_order_api():
    """REST API를 통한 오더 전송"""
    data = request.get_json()
    target_cid = data.get("target_cid")
    order_data = data.get("order_data")

    if not target_cid or not order_data:
        return jsonify({"status": "fail", "reason": "필수 데이터 누락"}), 400

    from socket_routes import connected_drivers

    # 기사 접속 상태 확인
    if target_cid not in connected_drivers:
        return jsonify({
            "status": "fail",
            "reason": f"기사 {target_cid}가 접속 중이 아닙니다"
        }), 404

    # SocketIO를 통해 실시간 오더 전송
    socketio.emit('new_order', {
        'order_id': order_data.get('order_id'),
        'pickup_address': order_data.get('pickup_address'),
        'delivery_address': order_data.get('delivery_address'),
        'customer_phone': order_data.get('customer_phone'),
        'fee': order_data.get('fee'),
        'memo': order_data.get('memo', ''),
        'timestamp': "2025-05-25T12:00:00"
    }, room=connected_drivers[target_cid])

    return jsonify({
        "status": "ok",
        "message": f"기사 {target_cid}에게 오더를 전송했습니다"
    })


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)

    # SocketIO 서버 실행
    print("🚀 QuickBot WebSocket 서버 시작!")
    print("📡 실시간 통신 시스템 준비 완료!")
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)