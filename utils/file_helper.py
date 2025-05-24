import json
import os
import pandas as pd

USER_FILE = "data/users.json"

# JSON
def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

# Excel -> JSON
def import_users_from_excel(filepath):
    df = pd.read_excel(filepath)
    if 'phone' not in df.columns or 'cid' not in df.columns:
        raise ValueError("Excel must contain 'phone' and 'cid' columns")
    return df.to_dict(orient="records")

# JSON -> Excel
def export_users_to_excel(filepath, users):
    df = pd.DataFrame(users)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_excel(filepath, index=False)

    # 자동 열 너비 조정 방지 (엑셀에서 #### 깨짐 방지)
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.book.active
        for col in worksheet.columns:
            max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in col)
            worksheet.column_dimensions[col[0].column_letter].width = max_length + 2
