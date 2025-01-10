$(document).ready(function() {
    console.log("DOM fully loaded. Starting script.");

    // Toggle Light
    $(".toggle-light").click(function() {
        const button = $(this);
        const roomName = button.data("room");
        const lightName = button.data("light");
        const sanitizedLightName = lightName.replace(/ /g, '_');

        console.log(`Toggling light: ${lightName} in room: ${roomName}`);

        // Send AJAX request to toggle the light
        $.ajax({
            url: "/toggle-light",
            type: "POST",
            data: JSON.stringify({ room_name: roomName, light_name: lightName }),
            contentType: "application/json",
            success: function(response) {
                console.log(`Light toggled successfully: ${lightName}`, response);

                const newState = response.new_state;
                const newRGB = response.new_rgb;

                // Update DOM elements
                $(`#${sanitizedLightName}-status`).text(`Status: ${newState ? 'On' : 'Off'}`);
                $(`#${sanitizedLightName}-rgb`).text(`RGB: (${newRGB[0]}, ${newRGB[1]}, ${newRGB[2]})`);
                button.text(newState ? 'Turn Off' : 'Turn On');
                $(`#${sanitizedLightName}-card`).css('background-color', `rgb(${newRGB[0]}, ${newRGB[1]}, ${newRGB[2]})`);
            },
            error: function(error) {
                console.error(`Failed to toggle light: ${lightName}`, error);
                alert("Failed to toggle the light. Please try again.");
            }
        });
    });

    // Toggle All Lights in a Room
    $(".toggle-room-lights").click(function() {
        const button = $(this);
        const roomName = button.data("room");
        console.log(`Toggling all lights in room: ${roomName}`);

        // Send AJAX request to toggle all lights
        $.ajax({
            url: "/toggle-room-lights",
            type: "POST",
            data: JSON.stringify({ room_name: roomName }),
            contentType: "application/json",
            success: function(response) {
                console.log(`All lights toggled in room: ${roomName}`, response);

                // Update DOM for each light in the room
                response.lights_updated.forEach(light => {
                    const sanitizedLightName = light.name.replace(/ /g, '_');
                    const newState = light.state.on;
                    const newRGB = light.rgb;

                    $(`#${sanitizedLightName}-status`).text(`Status: ${newState ? 'On' : 'Off'}`);
                    $(`#${sanitizedLightName}-rgb`).text(`RGB: (${newRGB[0]}, ${newRGB[1]}, ${newRGB[2]})`);
                    $(`#${sanitizedLightName}-button`).text(newState ? 'Turn Off' : 'Turn On');
                    $(`#${sanitizedLightName}-card`).css("background-color", `rgb(${newRGB[0]}, ${newRGB[1]}, ${newRGB[2]})`);
                });
            },
            error: function(error) {
                console.error(`Failed to toggle all lights in room: ${roomName}`, error);
                alert("Failed to toggle all lights. Please try again.");
            }
        });
    });
});