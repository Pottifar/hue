from flask import Flask, render_template, request, redirect, url_for, jsonify
from phue import Bridge
from color_convert import convert_color

app = Flask(__name__)

# Replace with your Philips Hue Bridge IP
BRIDGE_IP = "10.0.0.1"
b = Bridge(BRIDGE_IP)
b.connect()

@app.route('/')
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
                brightness = state['bri']
                colortemp = state.get('ct', 153)
                rgb = convert_color(colortemp, brightness)
                room_lights[room_name][name] = {'on': True, 'rgb': rgb}
            else:
                room_lights[room_name][name] = {'on': False, 'rgb': (0, 0, 0)}  # Light is off
    return render_template('index.html', room_lights=room_lights)


@app.route('/room/<room_name>')
def room(room_name):
    # Retrieve all lights in the specified room
    group = next((group for group in b.get_group().values() if group['name'] == room_name), None)
    if not group:
        return f"Room '{room_name}' not found.", 404

    light_ids = group['lights']
    light_status = {}

    for light_id in light_ids:
        light = b.get_light(int(light_id))
        name = light['name']
        state = light['state']
        if state['on']:
            brightness = state['bri']
            colortemp = state.get('ct', 153)  # Default to a valid color temp
            rgb = convert_color(colortemp, brightness)
            light_status[name] = {'on': True, 'rgb': rgb}
        else:
            light_status[name] = {'on': False, 'rgb': (0, 0, 0)}  # Light is off, RGB is black

    return render_template('room.html', room_name=room_name, light_status=light_status)

# Your existing imports and setup code...

@app.route('/toggle-light', methods=['POST'])
def toggle_light_ajax():
    data = request.get_json()
    room_name = data['room_name']
    light_name = data['light_name']

    # Find the light in the specified room
    groups = b.get_group()
    for group in groups.values():
        if group['name'] == room_name:
            for light_id in group['lights']:
                light = b.get_light(int(light_id))
                if light['name'] == light_name:
                    # Toggle the light
                    new_state = not light['state']['on']
                    b.set_light(int(light_id), 'on', new_state)

                    # Get updated state and RGB
                    updated_light = b.get_light(int(light_id))
                    brightness = updated_light['state'].get('bri', 0)
                    colortemp = updated_light['state'].get('ct', 153)
                    rgb = convert_color(colortemp, brightness) if new_state else (0, 0, 0)

                    return jsonify({'new_state': new_state, 'new_rgb': rgb})
    return jsonify({'error': 'Light not found'}), 404

@app.route('/get-lights', methods=['GET'])
def get_lights():
    lights_data = []
    groups = b.get_group()
    for group in groups.values():
        for light_id in group['lights']:
            light = b.get_light(int(light_id))
            name = light['name']
            state = light['state']
            rgb = (0, 0, 0) if not state['on'] else convert_color(state.get('ct', 153), state.get('bri', 0))
            lights_data.append({'name': name, 'state': state, 'rgb': rgb})
    return jsonify({'lights': lights_data})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
