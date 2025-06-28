// On document ready
$(document).ready(function () {

	// Check if we should use the login server features (to get the user hours infos from the website)
	let useLoginServerFeatures = false;
	if (useLoginServerFeatures) {

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
				let append_parameters_in_url = false;
				let infos_url = `https://get-leonardo-hrnext-infos.onrender.com/get_job_infos`;
				let requestData = null;
				if (append_parameters_in_url) {
					// Append the username and password to the URL as parameters
					infos_url += `?username=${username}&password=${password}`;
				} else {
					requestData = {
						username: username,
						password: password
					};
				}
				// Show the loading state
				console.log(`Getting infos from ${infos_url}`);
				// Show the loading state
				setInfosLoadingState(true);
				// Make the AJAX request to get the infos JSON
				let timeout_minutes = 15;
				$.ajax({
					url: infos_url,
					type: "GET",
					data: requestData,
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
								$("#flexibility-hours").val(hoursBalance);
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

	} else {
		// If we are not using the login server features, hide the login inputs (if any)
		$(".credentials-section").css("display", "none");
	}

	// Function to update the results section
	function refreshResultsSection() {
		// Get the values from the inputs
		let enterHours = $("#entrance-hours").val(); // string of the form "HH:mm"
		let flexibilityHours = $("#flexibility-hours").val(); // string of the form "HH:mm", "+HH:mm" or "-HH:mm"
		let extraWorkHours = $("#extra-work-hours").val(); // string of the form "HH:mm", "+HH:mm" or "-HH:mm"
		let otherHours = $("#other-hours").val(); // string of the form "HH:mm", "+HH:mm" or "-HH:mm"
		// console.log(`Enter hours: ${enterHours}, Flexibility hours: ${flexibilityHours}, Extra work hours: ${extraWorkHours}, Other hours: ${otherHours}`);
		// Function to check if the given hours (either signed or not) are in the correct format (HH:mm or +HH:mm or -HH:mm), and return true or false, while also trying to recover the value from the input type="time"
		function checkHoursFormat(hours, isSigned) {
			let formatIsValid = true;
			if (hours && !hours.match(/^\d{2}:\d{2}$/) && !hours.match(/^\+?\d{2}:\d{2}$/) && !hours.match(/^\-\d{2}:\d{2}$/)) {
				// Try to recover the hours from the input type="time"
				let newValue = undefined;
				let hoursArray = hours.split(":");
				let sign = isSigned ? (hoursArray[0].includes("-") ? "-" : "+") : "";
				hoursArray[0] = hoursArray[0].replace("-", "").replace("+", "");
				if (hoursArray.length == 2) {
					if ((hoursArray[0].length == 1 || hoursArray[0].length == 2) && hoursArray[1].length == 2) {
						newValue = (hoursArray[0].length == 1 ? "0" + hoursArray[0] : hoursArray[0]) + ":" + hoursArray[1];
					}
				}
				if (newValue) {
					hours = sign + newValue;
				} else {
					// alert(`Invalid ${isSigned ? "signed" : "unsigned"} hours format: ${hours}`);
					formatIsValid = false;
				}
			}
			return {
				formatIsValid: formatIsValid,
				fixedHours: hours
			}
		}
		// Check if the enter hours, flexibility hours, extra work hours and other hours are in the correct format (HH:mm)
		let formatIsValid = true;
		// Check if the enter hours and flexibility hours are in the correct format (HH:mm)
		let enterHoursCheck = checkHoursFormat(enterHours, false);
		enterHours = enterHoursCheck.fixedHours;
		formatIsValid = formatIsValid && enterHoursCheck.formatIsValid;
		let flexibilityHoursCheck = checkHoursFormat(flexibilityHours, true);
		flexibilityHours = flexibilityHoursCheck.fixedHours;
		formatIsValid = formatIsValid && flexibilityHoursCheck.formatIsValid;
		// Check if the extra work hours and other hours are in the correct format (HH:mm)
		let extraWorkHoursCheck = checkHoursFormat(extraWorkHours, true);
		extraWorkHours = extraWorkHoursCheck.fixedHours;
		formatIsValid = formatIsValid && extraWorkHoursCheck.formatIsValid;
		let otherHoursCheck = checkHoursFormat(otherHours, true);
		otherHours = otherHoursCheck.fixedHours;
		formatIsValid = formatIsValid && otherHoursCheck.formatIsValid;
		// Function to get the total flexibility hours and minutes from the flexibility hours string, subtracting the extra work hours string and also adding or subtracting the other hours balance string (HH:mm, +HH:mm or -HH:mm)
		function getTotalFlexibilityHours(flexibilityHours, extraWorkHours, otherHours) {
			// Function to calculate the total hours, minutes and sign of the varoius hours
			function calculateTotalHours(timeString) {
				let sign = 1;
				if (timeString.includes("-")) sign = -1;
				let timeArray = timeString.split(":");
				if (timeArray.length == 2) {
					let hours = parseInt(timeArray[0].replace("-", "").replace("+", ""));
					let minutes = parseInt(timeArray[1]);
					return {
						sign: sign,
						hours: hours,
						minutes: minutes
					}
				}
				return {
					sign: 1,
					hours: 0,
					minutes: 0
				}
			}
			// Calculate the total hours and minutes of the flexibility hours, extra work hours and other hours
			let flexibility = calculateTotalHours(flexibilityHours);
			let extraWork = calculateTotalHours(extraWorkHours);
			let other = calculateTotalHours(otherHours);
			// Calculate the total flexibility in minutes
			let totalFlexibility = (flexibility.sign * (flexibility.hours * 60 + flexibility.minutes)) - (extraWork.sign * (extraWork.hours * 60 + extraWork.minutes)) + (other.sign * (other.hours * 60 + other.minutes));
			// Calculate the total flexibility hours and minutes
			let totalFlexibilityHours = totalFlexibility > 0 ? Math.floor(totalFlexibility / 60) : Math.ceil(totalFlexibility / 60);
			let totalFlexibilityMinutes = totalFlexibility > 0 ? totalFlexibility % 60 : -1 * (Math.abs(totalFlexibility) % 60);
			// Format the total flexibility hours and minutes to HH:mm
			let totalFlexibilityString = (totalFlexibilityHours < 0 ? "-" : "+") + Math.abs(totalFlexibilityHours).toString().padStart(2, "0") + ":" + Math.abs(totalFlexibilityMinutes).toString().padStart(2, "0");
			return totalFlexibilityString;
		}
		// If the format is valid, calculate the exit times
		if (formatIsValid) {
			// update the sections below
			let launchBreakDurationMinutes = 45;
			// Calculate the exit times as the enter hours plus launchBreakDurationMinutes minutes and 8 hours or 6 hours
			// NOTE: time should use the 24 hours format
			let exit_8_hours = new Date(Date.now());
			exit_8_hours.setHours(enterHours.split(":")[0], enterHours.split(":")[1], 0, 0);
			exit_8_hours.setMinutes(exit_8_hours.getMinutes() + launchBreakDurationMinutes + (8 * 60));
			$("#exit-hours-8").text(new Date(exit_8_hours).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }));
			let exit_6_hours = new Date(Date.now());
			exit_6_hours.setHours(enterHours.split(":")[0], enterHours.split(":")[1], 0, 0);
			exit_6_hours.setMinutes(exit_6_hours.getMinutes() + launchBreakDurationMinutes + (6 * 60)); // 6 hours = 360 minutes
			$("#exit-hours-6").text(new Date(exit_6_hours).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }));
			// Calculate the exit that brings the flexibility hours to 0
			let exit_0_hours = new Date(Date.now());
			exit_0_hours.setHours(enterHours.split(":")[0], enterHours.split(":")[1], 0, 0);
			exit_0_hours.setMinutes(exit_0_hours.getMinutes() + launchBreakDurationMinutes + (8 * 60)); // 8 hours = 480 minutes
			let realFlexibilityHoursString = getTotalFlexibilityHours(flexibilityHours, extraWorkHours, otherHours);
			let flexibilityHoursInt = 0;
			let flexibilityMinutesInt = 0;
			if (realFlexibilityHoursString.includes("-")) {
				// If the flexibility hours are negative, subtract them from the exit time (subtract hours and minutes)
				let flexibilityHoursArray = realFlexibilityHoursString.split(":");
				flexibilityHoursInt = parseInt(flexibilityHoursArray[0].replace("-", ""));
				flexibilityMinutesInt = parseInt(flexibilityHoursArray[1]);
			} else {
				// If the flexibility hours are positive, add them to the exit time (add hours and minutes)
				let flexibilityHoursArray = realFlexibilityHoursString.split(":");
				flexibilityHoursInt = -1 * parseInt(flexibilityHoursArray[0]);
				flexibilityMinutesInt = -1 * parseInt(flexibilityHoursArray[1]);
			}
			// exit_0_hours.setHours(exit_0_hours.getHours() + flexibilityHoursInt);
			// exit_0_hours.setMinutes(exit_0_hours.getMinutes() + flexibilityMinutesInt);
			exit_0_hours.setTime(exit_0_hours.getTime() + (flexibilityHoursInt * 60 * 60 * 1000) + (flexibilityMinutesInt * 60 * 1000)); // add the flexibility hours and minutes to the exit time
			// Calculate the days offset (in case flex hours are too much or too many to bring the final exit hours to the prevoius or next day)
			let daysOffset = -1 * (exit_8_hours.getDate() - exit_0_hours.getDate());
			daysOffset = Math.floor(daysOffset);
			// Format the exit time to HH:mm
			let exitHours0_text =
				new Date(exit_0_hours).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
				+ (daysOffset > 0 ? ` (+${daysOffset} days)` : (daysOffset < 0 ? ` (-${-1 * daysOffset} days)` : ""));
			$("#exit-hours-0").text(exitHours0_text);
			// Set the exit "warning" class to exit-hours-0 if the exit time is less than the 6 hours time
			let exitHours0 = $("#exit-hours-0").text();
			let exitHours6 = $("#exit-hours-6").text();
			if (exitHours0 < exitHours6) {
				$("#exit-hours-0").parent().addClass("warning");
			} else if (daysOffset > 0) {
				$("#exit-hours-0").parent().addClass("warning");
			} else {
				$("#exit-hours-0").parent().removeClass("warning");
			}
			// Set the text of the #flexibility-hours-real to the total flexibility hours
			if (flexibilityHours == "") $("#flexibility-hours-real").text("+??:??");
			else $("#flexibility-hours-real").text(realFlexibilityHoursString);
		} else {
			// If the format is not valid, show all hours as "??:??"
			$("#exit-hours-8").text("??:??");
			$("#exit-hours-6").text("??:??");
			$("#exit-hours-0").text("??:??");
		}
	}

	// On change onto either #entrance-hours or #flexibility-hours, update the results section
	$("#entrance-hours").on("input", refreshResultsSection);
	$("#flexibility-hours").on("input", refreshResultsSection);
	$("#extra-work-hours").on("input", refreshResultsSection);
	$("#other-hours").on("input", refreshResultsSection);

});