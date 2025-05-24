from flask import Flask
from routes.user_routes import user_routes
from routes.excel_routes import excel_routes
import os

app = Flask(__name__)

# 라우터 등록
app.register_blueprint(user_routes)
app.register_blueprint(excel_routes)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    app.run(host="0.0.0.0", port=8080)
