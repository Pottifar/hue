import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from phue import Bridge
from color_convert import convert_color

app = Flask(__name__)

# Philips Hue Bridge IP
BRIDGE_IP = "10.0.0.1"
b = Bridge(BRIDGE_IP)
b.connect()

@app.route("/")
def index():
    room_lights = {}
    groups = b.get_group()
    for group in groups.values():
        room_name = group['name']
        room_lights[room_name] = {}
        for light_id in group['lights']:
            light = b.get_light(int(light_id))
            name = light['name']
            state = light['state']
            if state['on']:
                brightness = state.get('bri', 0)
                colortemp = state.get('ct', 153)
                rgb = convert_color(colortemp, brightness)
                room_lights[room_name][name] = {"on": True, "rgb": rgb}
            else:
                room_lights[room_name][name] = {"on": False, "rgb": (0, 0, 0)}  # Light is off
    return render_template("index.html", room_lights=room_lights)

@app.route("/toggle-light", methods=["POST"])
def toggle_light_ajax():
    data = request.get_json()
    room_name = data.get("room_name")
    light_name = data.get("light_name")

    groups = b.get_group()
    for group in groups.values():
        if group["name"] == room_name:
            for light_id in group["lights"]:
                light = b.get_light(int(light_id))
                if light["name"] == light_name:
                    # Toggle the light state
                    new_state = not light["state"]["on"]
                    b.set_light(int(light_id), "on", new_state)

                    # Get updated state and RGB
                    updated_light = b.get_light(int(light_id))
                    brightness = updated_light["state"].get("bri", 0)
                    colortemp = updated_light["state"].get("ct", 153)
                    rgb = convert_color(colortemp, brightness) if new_state else (0, 0, 0)

                    return jsonify({"new_state": new_state, "new_rgb": rgb})
    return jsonify({"error": "Light not found"}), 404

@app.route("/toggle-room-lights", methods=["POST"])
def toggle_room_lights():
    data = request.get_json()
    room_name = data.get("room_name")

    groups = b.get_group()
    for group in groups.values():
        if group["name"] == room_name:
            lights_updated = []
            # Check if any lights are currently on
            any_on = any(b.get_light(int(light_id))["state"]["on"] for light_id in group["lights"])
            new_state = not any_on  # Toggle logic: turn all on or off

            for light_id in group["lights"]:
                b.set_light(int(light_id), "on", new_state)

                # Get updated state and RGB
                updated_light = b.get_light(int(light_id))
                brightness = updated_light["state"].get("bri", 0)
                colortemp = updated_light["state"].get("ct", 153)
                rgb = convert_color(colortemp, brightness) if new_state else (0, 0, 0)

                lights_updated.append({
                    "name": updated_light["name"],
                    "state": updated_light["state"],
                    "rgb": rgb,
                })

            return jsonify({"success": True, "lights_updated": lights_updated})
    return jsonify({"error": "Room not found"}), 404

@app.route("/room-status/<room_name>")
def room_status(room_name):
    groups = b.get_group()
    group = next((g for g in groups.values() if g["name"] == room_name), None)
    if not group:
        return jsonify({"error": "Room not found"}), 404

    all_on = all(b.get_light(int(light_id))["state"]["on"] for light_id in group["lights"])
    return jsonify({"all_on": all_on})

@app.route("/get-lights", methods=["GET"])
def get_lights():
    lights_data = []
    groups = b.get_group()
    for group in groups.values():
        for light_id in group["lights"]:
            light = b.get_light(int(light_id))
            name = light["name"]
            state = light["state"]
            rgb = convert_color(state.get("ct", 153), state.get("bri", 0)) if state["on"] else (0, 0, 0)
            lights_data.append({"name": name, "state": state, "rgb": rgb})
    return jsonify({"lights": lights_data})

@app.route("/set-room-brightness", methods=["POST"])
def set_room_brightness():
    data = request.get_json()
    room_name = data.get("room_name")
    brightness = data.get("brightness")

    if brightness is None or not (1 <= brightness <= 254):
        return jsonify({"error": "Invalid brightness value"}), 400

    groups = b.get_group()
    for group in groups.values():
        if group["name"] == room_name:
            for light_id in group["lights"]:
                b.set_light(int(light_id), "bri", brightness)

            return jsonify({"success": True, "brightness": brightness})

    return jsonify({"error": "Room not found"}), 404

@app.route("/set-room-temp", methods=["POST"])
def set_room_temp():
    data = request.get_json()
    room_name = data.get("room_name")
    temperature = data.get("temperature")

    if temperature is None or not (153 <= temperature <= 500):
        return jsonify({"error": "Invalid temperature value"}), 400

    groups = b.get_group()
    for group in groups.values():
        if group["name"] == room_name:
            for light_id in group["lights"]:
                b.set_light(int(light_id), "ct", temperature)

            return jsonify({"success": True, "temperature": temperature})

    return jsonify({"error": "Room not found"}), 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
