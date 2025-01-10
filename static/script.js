$(document).ready(function () {
    console.log("DOM fully loaded. Starting script.");

    // Initialize Room Buttons
    $(".toggle-room-lights").each(function () {
        const button = $(this);
        const roomName = button.data("room");

        // Get the initial status of the room (all lights on or off)
        $.ajax({
            url: `/room-status/${roomName}`,
            type: "GET",
            success: function (response) {
                const allOn = response.all_on; // true if all lights are on
                button.find(".toggle-room-text").text(allOn ? "Skru av alle" : "Skru på alle");
                button.data("status", allOn ? "on" : "off");
            },
            error: function (error) {
                console.error(`Failed to get room status for ${roomName}:`, error);
            }
        });
    });

    // Toggle Individual Light
    $(".light").click(function (event) {
        event.preventDefault(); // Prevent default anchor behavior

        const card = $(this);
        const roomName = card.data("room");
        const lightName = card.data("light");
        const sanitizedLightName = lightName.replace(/ /g, '_');
        const currentStatus = card.data("status"); // 'on' or 'off'

        console.log(`Toggling light: ${lightName} in room: ${roomName}`);

        // Send AJAX request to toggle the light
        $.ajax({
            url: "/toggle-light",
            type: "POST",
            data: JSON.stringify({ room_name: roomName, light_name: lightName }),
            contentType: "application/json",
            success: function (response) {
                const newState = response.new_state;
                const newRGB = response.new_rgb;

                // Update the light card
                card.css("background-color", `rgb(${newRGB[0]}, ${newRGB[1]}, ${newRGB[2]})`);
                card.data("status", newState ? "on" : "off");
                card.find(`#${sanitizedLightName}-status-text`).text(newState ? "Skru Av" : "Skru På");
            },
            error: function (error) {
                console.error(`Failed to toggle light: ${lightName}`, error);
                alert("Failed to toggle the light. Please try again.");
            }
        });
    });

    // Toggle All Lights in a Room
    $(".toggle-room-lights").click(function () {
        const button = $(this);
        const roomName = button.data("room");
        const currentStatus = button.data("status"); // 'on' or 'off'

        console.log(`Toggling all lights in room: ${roomName}, current status: ${currentStatus}`);

        // Send AJAX request to toggle all lights
        $.ajax({
            url: "/toggle-room-lights",
            type: "POST",
            data: JSON.stringify({ room_name: roomName }),
            contentType: "application/json",
            success: function (response) {
                const lightsUpdated = response.lights_updated;
                const allOn = lightsUpdated.every((light) => light.state.on);

                // Update each light in the room
                lightsUpdated.forEach((light) => {
                    const sanitizedLightName = light.name.replace(/ /g, '_');
                    const card = $(`#${sanitizedLightName}-card`);
                    const newRGB = light.rgb;

                    // Update light card
                    card.css("background-color", `rgb(${newRGB[0]}, ${newRGB[1]}, ${newRGB[2]})`);
                    card.data("status", light.state.on ? "on" : "off");
                    card.find(`#${sanitizedLightName}-status-text`).text(light.state.on ? "Skru Av" : "Skru På");
                });

                // Update room button
                button.data("status", allOn ? "on" : "off");
                button.find(".toggle-room-text").text(allOn ? "Skru av alle" : "Skru på alle");
            },
            error: function (error) {
                console.error(`Failed to toggle all lights in room: ${roomName}`, error);
                alert("Failed to toggle all lights. Please try again.");
            }
        });
    });

    // Function to update light statuses dynamically
    function updateLightStatuses() {
        console.log("Updating light statuses...");
        $.ajax({
            url: "/get-lights", // Endpoint to get the latest light statuses
            type: "GET",
            success: function (response) {
                response.lights.forEach(light => {
                    const sanitizedLightName = light.name.replace(/ /g, '_');
                    const isOn = light.state.on;
                    const rgb = light.rgb;

                    // Update DOM elements for each light
                    $(`#${sanitizedLightName}-status`).text(`Status: ${isOn ? 'On' : 'Off'}`);
                    $(`#${sanitizedLightName}-rgb`).text(`RGB: (${rgb[0]}, ${rgb[1]}, ${rgb[2]})`);
                    $(`#${sanitizedLightName}-button`).text(isOn ? 'Turn Off' : 'Turn On');
                    $(`#${sanitizedLightName}-card`).css("background-color", `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`);
                });
            },
            error: function (error) {
                console.error("Failed to fetch light statuses:", error);
            }
        });
    }

    setInterval(updateLightStatuses, 2000);
});
