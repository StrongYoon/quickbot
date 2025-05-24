import datetime
import os
import json


def log_action(action_type, details):
    """
    시스템 액션을 로그에 기록합니다.

    Args:
        action_type (str): 액션 타입 (예: "등록", "삭제", "오더 전송")
        details (str): 상세 내용
    """
    try:
        # 로그 디렉토리 생성
        os.makedirs("logs", exist_ok=True)

        # 오늘 날짜로 로그 파일명 생성
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = f"logs/quickbot_{today}.log"

        # 로그 엔트리 생성
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "action_type": action_type,
            "details": details
        }

        # 로그 파일에 추가
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        # 콘솔에도 출력
        print(f"[{timestamp}] {action_type}: {details}")

    except Exception as e:
        print(f"로그 기록 오류: {e}")


def get_today_logs():
    """
    오늘의 로그를 조회합니다.

    Returns:
        list: 오늘의 로그 엔트리 목록
    """
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = f"logs/quickbot_{today}.log"

        if not os.path.exists(log_file):
            return []

        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    continue

        return logs

    except Exception as e:
        print(f"로그 조회 오류: {e}")
        return []


def get_logs_by_date(date_str):
    """
    특정 날짜의 로그를 조회합니다.

    Args:
        date_str (str): 날짜 문자열 (YYYY-MM-DD 형식)

    Returns:
        list: 해당 날짜의 로그 엔트리 목록
    """
    try:
        log_file = f"logs/quickbot_{date_str}.log"

        if not os.path.exists(log_file):
            return []

        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    continue

        return logs

    except Exception as e:
        print(f"로그 조회 오류: {e}")
        return []