// On document ready
$(document).ready(function () {

	// On page load, send an immediate request to the server to wake it up (with no-cors)
	console.log("Waking up server...");
	let server_test_url = `https://get-leonardo-hrnext-infos.onrender.com/get_job_infos`;
	$.ajax({
		url: server_test_url,
		type: "GET",
		dataType: "json",
		// Set the timeout to 5 seconds
		success: function () {
			console.log("> Server is awake!");
		},
		error: function (xhr, status, error) {
			console.log("> Error waking up server (but server should be awake)...");
		}
	});

	// Check if the page has, in its url parameters, the "username" and/or "password" parameters
	if (window.location.search.includes("username")) {
		// Fill out the input with the username parameter value
		const username = new URLSearchParams(window.location.search).get("username");
		$("#username").val(username);
	}
	if (window.location.search.includes("password")) {
		// Fill out the input with the password parameter value
		const password = new URLSearchParams(window.location.search).get("password");
		$("#password").val(password);
	}

	// Function to set the infos loading state
	function setInfosLoadingState(isLoading) {
		if (isLoading) {
			$("#infos-loading").css("display", "block");
		} else {
			$("#infos-loading").css("display", "none");
		}
	}
	// On click on the "GET INFOS" button, send a request to the server to get the infos based on the username and password
	$("#get-infos").click(function () {
		const username = $("#username").val();
		const password = $("#password").val();
		if (username && password) {
			// Send a request to the server to get the infos JSON based on the username and password
			let infos_url = `https://get-leonardo-hrnext-infos.onrender.com/get_job_infos?username=${username}&password=${password}`;
			console.log(`Getting infos from ${infos_url}`);
			// Show the loading state
			setInfosLoadingState(true);
			// Make the AJAX request to get the infos JSON
			let timeout_minutes = 15;
			$.ajax({
				url: infos_url,
				type: "GET",
				dataType: "json",
				// Set the timeout to 10 minutes (300000 milliseconds)
				timeout: timeout_minutes * 60 * 1000,
				success: function (data) {
					console.log("Data received:", data);
					// If the request is successful, redirect to the "infos.html" page with the JSON data in the URL parameters
					if (data) {
						setInfosLoadingState(false);
						/*
						The retrieved data has the form:
						{
							"days_ago": 0,
							"entrata": "08:32",
							"saldo_ore": "-00:46",
							"user": "NOME COGNOME",
							"opzioni_uscita": {
								"6_hours": "15:18",
								"8_hours": "17:18",
								"azzera_saldo_ore": "18:04",
							},
						}
						*/
						let jsonResponse = data;
						// For debug, edit the jsonResponse to actually have other values
						// jsonResponse = {
						// 	"days_ago": 0,
						// 	"entrata": "08:32",
						// 	"saldo_ore": "-00:46",
						// 	"user": "NOME COGNOME",
						// 	"opzioni_uscita": {
						// 		"6_hours": "15:18",
						// 		"8_hours": "17:18",
						// 		"azzera_saldo_ore": "18:04",
						// 	},
						// }
						// Get the needed data from the JSON response
						let user = jsonResponse.user;
						let entranceTime = jsonResponse.entrata;
						let daysAgo = jsonResponse.days_ago;
						let hoursBalance = jsonResponse.saldo_ore;
						if (daysAgo == 0) {
							// Calculat the actual entrance time
							let actualEntranceTime = new Date();
							actualEntranceTime.setHours(entranceTime.split(":")[0], entranceTime.split(":")[1], 0, 0);
							// Set the entrance time to the input field
							$("#entrance-hours").val(new Date(actualEntranceTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }));
							// Set the flexibility hours to the input field
							$("#flexibility-hours").val(hoursBalance);
							// Show a log with the real user name
							console.log(`Retrieved infos for ${user}`);
						} else {
							// If the days ago is greater than 0, dont calculate the exit times
							$("#entrance-hours").val(null);
							$("#flexibility-hours").val(null);
							alert(`Retrieved infos for ${user} but the data is from ${daysAgo} days ago, not calculating the exit times...`);
						}
						// Update the results section with the entrance time and flexibility hours
						refreshResultsSection();
					} else {
						setInfosLoadingState(false);
						// If the data is empty, show an alert
						alert("No data found for the provided username and password.");
					}
				},
				error: function (xhr, status, error) {
					setInfosLoadingState(false);
					// If the request fails, show an alert with the error message
					alert("Error: " + xhr.status + "\n" + xhr.statusText);
				}
			});
		} else {
			alert("Please fill out both fields.");
		}
	});

	// Function to update the results section
	function refreshResultsSection() {
		// Get the values from the inputs
		let enterHours = $("#entrance-hours").val(); // string of the form "HH:mm"
		let flexibilityHours = $("#flexibility-hours").val(); // string of the form "HH:mm", "+HH:mm" or "-HH:mm"
		console.log(`Enter hours: ${enterHours}, Flexibility hours: ${flexibilityHours}`);
		// Check if the enter hours and flexibility hours are in the correct format (HH:mm)
		let formatIsValid = true;
		if (enterHours && !enterHours.match(/^\d{2}:\d{2}$/)) {
			// Try to recover the enter hours from the input type="time"
			let newValue = undefined;
			let enterHoursArray = enterHours.split(":");
			if (enterHoursArray.length == 2) {
				if ((enterHoursArray[0].length == 1 || enterHoursArray[0].length == 2) && enterHoursArray[1].length == 2) {
					newValue = (enterHoursArray[0].length == 1 ? "0" + enterHoursArray[0] : enterHoursArray[0]) + ":" + enterHoursArray[1];
				}
			}
			if (newValue) {
				enterHours = newValue;
			} else {
				// alert(`Invalid enter hours format: ${enterHours}`);
				formatIsValid = false;
			}
		}
		if (flexibilityHours && !flexibilityHours.match(/^\+?\d{2}:\d{2}$/) && !flexibilityHours.match(/^\-\d{2}:\d{2}$/)) {
			// Try to recover the flexibility hours from the input type="time"
			let newValue = undefined;
			let flexibilityHoursArray = flexibilityHours.split(":");
			let sign = flexibilityHoursArray[0].includes("-") ? "-" : "+";
			if (sign == "-") {
				flexibilityHoursArray[0] = flexibilityHoursArray[0].replace("-", "");
			}
			if (flexibilityHoursArray.length == 2) {
				if ((flexibilityHoursArray[0].length == 1 || flexibilityHoursArray[0].length == 2) && flexibilityHoursArray[1].length == 2) {
					newValue = (flexibilityHoursArray[0].length == 1 ? "0" + flexibilityHoursArray[0] : flexibilityHoursArray[0]) + ":" + flexibilityHoursArray[1];
				}
			}
			if (newValue) {
				flexibilityHours = sign + newValue;
			} else {
				// alert(`Invalid flexibility hours format: ${flexibilityHours}`);
				formatIsValid = false;
			}
		}
		if (formatIsValid) {
			// try {
			// update the sections below
			let launchBreakDurationMinutes = 45;
			// Calculate the exit times as the enter hours plus launchBreakDurationMinutes minutes and 8 hours or 6 hours
			// NOTE: time should use the 24 hours format
			let exit_8_hours = new Date();
			exit_8_hours.setHours(enterHours.split(":")[0], enterHours.split(":")[1], 0, 0);
			exit_8_hours.setMinutes(exit_8_hours.getMinutes() + launchBreakDurationMinutes + 480); // 8 hours = 480 minutes
			$("#exit-hours-8").text(new Date(exit_8_hours).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }));
			let exit_6_hours = new Date();
			exit_6_hours.setHours(enterHours.split(":")[0], enterHours.split(":")[1], 0, 0);
			exit_6_hours.setMinutes(exit_6_hours.getMinutes() + launchBreakDurationMinutes + 360); // 6 hours = 360 minutes
			$("#exit-hours-6").text(new Date(exit_6_hours).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }));
			// Calculate the exit that brings the flexibility hours to 0
			let exit_0_hours = new Date();
			exit_0_hours.setHours(enterHours.split(":")[0], enterHours.split(":")[1], 0, 0);
			exit_0_hours.setMinutes(exit_0_hours.getMinutes() + launchBreakDurationMinutes + 480); // 8 hours = 480 minutes
			let flexibilityHoursInt = 0;
			let flexibilityMinutesInt = 0;
			if (flexibilityHours.includes("-")) {
				// If the flexibility hours are negative, subtract them from the exit time (subtract hours and minutes)
				let flexibilityHoursArray = flexibilityHours.split(":");
				flexibilityHoursInt = parseInt(flexibilityHoursArray[0].replace("-", ""));
				flexibilityMinutesInt = parseInt(flexibilityHoursArray[1]);

			} else {
				// If the flexibility hours are positive, add them to the exit time (add hours and minutes)
				let flexibilityHoursArray = flexibilityHours.split(":");
				flexibilityHoursInt = -1 * parseInt(flexibilityHoursArray[0]);
				flexibilityMinutesInt = -1 * parseInt(flexibilityHoursArray[1]);
			}
			exit_0_hours.setHours(exit_0_hours.getHours() + flexibilityHoursInt);
			exit_0_hours.setMinutes(exit_0_hours.getMinutes() + flexibilityMinutesInt);
			// Format the exit time to HH:mm
			$("#exit-hours-0").text(new Date(exit_0_hours).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }));
			// } catch (error) {
			// 	// alert("Error calculating the exit times:\n" + error.message);
			// }
		} else {
			// If the format is not valid, show all hours as "??:??"
			$("#exit-hours-8").text("??:??");
			$("#exit-hours-6").text("??:??");
			$("#exit-hours-0").text("??:??");
		}
	}

	// On change onto either #entrance-hours or #flexibility-hours, update the results section
	$("#entrance-hours").change(refreshResultsSection);
	$("#flexibility-hours").change(refreshResultsSection);

});