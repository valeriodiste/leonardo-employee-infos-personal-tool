# Simple flask app that uses the get_infos function from get_hrnext_data.py
from flask import Flask, request, jsonify
import get_hrnext_data
import requests
import os

app = Flask(__name__)

# Allow the requiest to be made with mode 'no-cors' (CORS policy)
@app.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
	return response

# Route to get HR NEXT data
@app.route('/get_job_infos', methods=['GET'])
def get_hrnext_hours_data():
	"""Get HR NEXT data using username and password from URL parameters."""

	username = request.args.get('username')
	password = request.args.get('password')

	if not username or not password:
		return jsonify({"error": "Username and password are required as URL parameters (username, password)"}), 400
	
	#Function to recover missing data (using another web app deployed at render.com)
	def recover_missing_data(username, password):
		"""Recover missing data from another web app."""
		# URL of the web app to recover data from
		url = f"https://get-leonardo-hrnext-infos.onrender.com/get_job_infos?username={username}&password={password}"
		try:
			response = requests.get(url)
			if response.status_code == 200:
				return response.json()
			else:
				return {"error": "Failed to get and then recover data..."}
		except Exception as e:
			return {"error": "While recovering from a previous error, the following error occured: " + str(e)}

	# Whether to recover data in case of an error via a call to a deployed web app on render.com or not
	# NOTE: Should not try to recover data if already running on render.com...
	recover_data = False

	# Call the function to get HR NEXT data
	try:
		data = get_hrnext_data.get_infos(username, password)
	except Exception as e:
		print(f"Error retrieving data: {e}")
		# Check if we should recover data
		# NOTE: Should not try to recover data if already running on render.com...
		if recover_data:
			print("> Trying to recover missing data...")
			data = recover_missing_data(username, password)
		else:
			return jsonify({"error": "Failed to retrieve data"}), 500

	return jsonify(data)
	
if __name__ == '__main__':
	port = 5000  # Default port
	if 'PORT' in os.environ:
		port = int(os.environ['PORT'])
	app.run(host='0.0.0.0', port=port)  # Ensure the app is accessible to external traffic