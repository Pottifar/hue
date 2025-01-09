from flask import Flask, render_template, request, redirect, url_for
from phue import Bridge
from color_convert import convert_color

app = Flask(__name__)

# Replace with your Philips Hue Bridge IP
BRIDGE_IP = "10.0.0.1"
b = Bridge(BRIDGE_IP)
b.connect()

# Get lights on the bridge
lights = b.get_light_objects('name')

@app.route('/')
def index():
    # Pass light status and RGB values to the template
    light_status = {}
    for name, light in lights.items():
        if light.on:
            brightness = light.brightness
            colortemp = light.colortemp
            rgb = convert_color(colortemp, brightness)
            light_status[name] = {'on': True, 'rgb': rgb}
        else:
            light_status[name] = {'on': False, 'rgb': (0, 0, 0)}  # Light is off, RGB is black
    return render_template('index.html', light_status=light_status)

@app.route('/toggle/<light_name>', methods=['POST'])
def toggle_light(light_name):
    if light_name in lights:
        light = lights[light_name]
        light.on = not light.on  # Toggle the light
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
