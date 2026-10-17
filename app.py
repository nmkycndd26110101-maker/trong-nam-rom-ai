from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Server AI Trong Nam Rom Dang Hoat Dong!", 200

@app.route('/api/telemetry', methods=['POST'])
def receive_telemetry():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data"}), 400

    # Lấy dữ liệu cảm biến gửi từ ESP32
    temp_in = float(data.get("tempIn", 0.0))
    hum_in = float(data.get("humIn", 0.0))
    soil = float(data.get("soil", 0.0))
    set_temp = float(data.get("setTemp", 32.0))
    set_hum = float(data.get("setHum", 85.0))
    is_fruiting = bool(data.get("stage", False))

    # THUẬT TOÁN AI QUYẾT ĐỊNH ĐÓNG/NGẮT THIẾT BỊ
    pump, fan1, fan2, light, heat = False, False, False, False, False

    if not is_fruiting:
        # Giai đoạn Ủ Tơ
        if temp_in < (set_temp - 1.0): heat = True
        if hum_in < set_hum or soil < 65: pump = True
    else:
        # Giai đoạn Ra Thể Quả
        if temp_in < (set_temp - 1.5): heat = True
        if hum_in < set_hum: pump = True
        if temp_in > (set_temp + 1.5) or hum_in > 95.0:
            fan1, fan2 = True, True
        light = True

    # Trả về kết quả điều khiển Relay dạng JSON
    return jsonify({
        "pump": pump,
        "fan1": fan1,
        "fan2": fan2,
        "light": light,
        "heat": heat
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
