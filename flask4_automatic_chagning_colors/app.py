from flask import Flask, render_template, jsonify
import threading
import time

app = Flask(__name__)

lights = {
    "color1": "#ff0000",
    "color2": "#00ff00",
    "color3": "#0000ff",
}
send_data = {"color": None}

def func1():
    global send_data
    while True:
        for color_name, color_value in lights.items():
            send_data["color"] = color_value
            time.sleep(5)

# Start the function in a background thread
threading.Thread(target=func1, daemon=True).start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/light-status")
def light_status():
    return jsonify(send_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
