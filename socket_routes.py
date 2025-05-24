from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import json
import jwt
import datetime
from utils.logger import log_action

# 연결된 클라이언트들 관리
connected_drivers = {}  # {cid: socket_id}
connected_admins = {}  # {session_id: socket_id}

SECRET_KEY = "quickbot-secret-key-2025"


def init_socketio(app):
    """SocketIO 초기화"""
    socketio = SocketIO(app, cors_allowed_origins="*")

    @socketio.on('connect')
    def on_connect():
        print(f"클라이언트 연결됨: {request.sid}")
        log_action("WebSocket", f"클라이언트 연결: {request.sid}")

    @socketio.on('disconnect')
    def on_disconnect():
        print(f"클라이언트 연결 해제: {request.sid}")

        # 연결된 기사 목록에서 제거
        for cid, sid in list(connected_drivers.items()):
            if sid == request.sid:
                del connected_drivers[cid]
                print(f"기사 연결 해제: {cid}")
                break

        # 연결된 관리자 목록에서 제거
        for session_id, sid in list(connected_admins.items()):
            if sid == request.sid:
                del connected_admins[session_id]
                print(f"관리자 연결 해제: {session_id}")
                break

        log_action("WebSocket", f"클라이언트 연결 해제: {request.sid}")

    @socketio.on('driver_login')
    def on_driver_login(data):
        """기사 로그인 처리"""
        try:
            token = data.get('token')
            if not token:
                emit('error', {'message': '토큰이 필요합니다'})
                return

            # JWT 토큰 검증
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            cid = decoded.get('cid')
            phone = decoded.get('phone')

            if cid:
                # 기존 연결이 있다면 해제
                if cid in connected_drivers:
                    old_sid = connected_drivers[cid]
                    socketio.emit('force_logout', {'message': '다른 기기에서 로그인됨'}, room=old_sid)

                # 새 연결 등록
                connected_drivers[cid] = request.sid
                join_room(f"driver_{cid}")

                emit('login_success', {
                    'message': '로그인 성공',
                    'cid': cid,
                    'phone': phone
                })

                # 관리자들에게 기사 접속 알림
                socketio.emit('driver_connected', {
                    'cid': cid,
                    'phone': phone,
                    'timestamp': datetime.datetime.now().isoformat()
                }, room='admins')

                log_action("기사 접속", f"CID: {cid}, Phone: {phone}")
                print(f"기사 로그인: {cid} ({phone})")

        except jwt.ExpiredSignatureError:
            emit('error', {'message': '토큰이 만료되었습니다'})
        except jwt.InvalidTokenError:
            emit('error', {'message': '유효하지 않은 토큰입니다'})
        except Exception as e:
            emit('error', {'message': f'로그인 처리 오류: {str(e)}'})

    @socketio.on('admin_login')
    def on_admin_login(data):
        """관리자 로그인 처리"""
        try:
            # 간단한 관리자 인증 (실제로는 더 강화된 인증 필요)
            session_id = data.get('session_id', request.sid)

            connected_admins[session_id] = request.sid
            join_room('admins')

            emit('admin_login_success', {
                'message': '관리자 로그인 성공',
                'connected_drivers': len(connected_drivers)
            })

            # 현재 접속한 기사 목록 전송
            driver_list = []
            for cid, sid in connected_drivers.items():
                driver_list.append({
                    'cid': cid,
                    'status': 'online'
                })

            emit('driver_list_update', {'drivers': driver_list})

            log_action("관리자 접속", f"Session: {session_id}")
            print(f"관리자 로그인: {session_id}")

        except Exception as e:
            emit('error', {'message': f'관리자 로그인 오류: {str(e)}'})

    @socketio.on('send_order')
    def on_send_order(data):
        """오더 전송 (관리자 → 기사)"""
        try:
            target_cid = data.get('target_cid')
            order_data = data.get('order_data')

            if not target_cid or not order_data:
                emit('error', {'message': '필수 데이터가 누락되었습니다'})
                return

            # 해당 기사가 접속 중인지 확인
            if target_cid not in connected_drivers:
                emit('order_send_failed', {
                    'message': f'기사 {target_cid}가 접속 중이 아닙니다',
                    'target_cid': target_cid
                })
                return

            # 기사에게 오더 전송
            target_sid = connected_drivers[target_cid]
            socketio.emit('new_order', {
                'order_id': order_data.get('order_id'),
                'pickup_address': order_data.get('pickup_address'),
                'delivery_address': order_data.get('delivery_address'),
                'customer_phone': order_data.get('customer_phone'),
                'fee': order_data.get('fee'),
                'memo': order_data.get('memo', ''),
                'timestamp': datetime.datetime.now().isoformat()
            }, room=target_sid)

            # 관리자에게 전송 성공 알림
            emit('order_send_success', {
                'message': f'기사 {target_cid}에게 오더를 전송했습니다',
                'target_cid': target_cid,
                'order_id': order_data.get('order_id')
            })

            log_action("오더 전송", f"CID: {target_cid}, Order: {order_data.get('order_id')}")

        except Exception as e:
            emit('error', {'message': f'오더 전송 오류: {str(e)}'})

    @socketio.on('order_response')
    def on_order_response(data):
        """오더 응답 (기사 → 관리자)"""
        try:
            order_id = data.get('order_id')
            response = data.get('response')  # 'accept' 또는 'reject'
            cid = data.get('cid')
            reason = data.get('reason', '')

            # 관리자들에게 응답 전송
            socketio.emit('order_response_received', {
                'order_id': order_id,
                'cid': cid,
                'response': response,
                'reason': reason,
                'timestamp': datetime.datetime.now().isoformat()
            }, room='admins')

            # 기사에게 응답 접수 확인
            emit('response_confirmed', {
                'message': '응답이 전송되었습니다',
                'order_id': order_id,
                'response': response
            })

            log_action("오더 응답", f"CID: {cid}, Order: {order_id}, Response: {response}")

        except Exception as e:
            emit('error', {'message': f'응답 처리 오류: {str(e)}'})

    @socketio.on('driver_status_update')
    def on_driver_status_update(data):
        """기사 상태 업데이트"""
        try:
            cid = data.get('cid')
            status = data.get('status')  # 'available', 'busy', 'offline'
            location = data.get('location', {})

            # 관리자들에게 상태 업데이트 전송
            socketio.emit('driver_status_changed', {
                'cid': cid,
                'status': status,
                'location': location,
                'timestamp': datetime.datetime.now().isoformat()
            }, room='admins')

            emit('status_update_confirmed', {
                'message': '상태가 업데이트되었습니다',
                'status': status
            })

        except Exception as e:
            emit('error', {'message': f'상태 업데이트 오류: {str(e)}'})

    @socketio.on('get_connected_drivers')
    def on_get_connected_drivers():
        """현재 접속한 기사 목록 요청"""
        try:
            driver_list = []
            for cid, sid in connected_drivers.items():
                driver_list.append({
                    'cid': cid,
                    'status': 'online',
                    'connected_at': datetime.datetime.now().isoformat()
                })

            emit('connected_drivers_list', {
                'drivers': driver_list,
                'total_count': len(driver_list)
            })

        except Exception as e:
            emit('error', {'message': f'기사 목록 조회 오류: {str(e)}'})

    return socketio