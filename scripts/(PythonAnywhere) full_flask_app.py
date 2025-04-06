# This Flask web app simply acts as a server for restless API requests I may need to make.

# Main imports
from flask import Flask, request, jsonify
import requests
import json
from spire.pdf import PdfDocument, FileFormat, Stream
import PyPDF2
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_text_to_fp
from io import BytesIO
from urllib.parse import quote_plus
import os

# My modules (python scripts)
import get_hrnext_data

# Flask app
app = Flask(__name__)

# Allow the requiest to be made with mode 'no-cors' (CORS policy)
@app.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
	return response

@app.route('/', methods=['GET', 'POST'])
def root():
	instructions = '''
		This is a Flask web app that acts as a server for restless API requests I may need to make.
		
		To use it, simply add the desired API request as a route to this server.

		Currently available routes:
		- /api/buythisgame/count: Returns the number of purchases of my game "Buy This Game To See How Many People Bought This Game" on itch.io.
		- /pdf2html: Converts PDF files to HTML files. Use the 'simple' parameter to choose between simple and advanced conversion.
		- /save: Saves a file locally on the server. Use the 'content' and 'extension' parameters to specify the content and file extension.
		- /steam_reviews: Retrieves all steam reviews for the given game's appid using the Steam API. Use the 'appid' and 'english_only' parameters to specify the appid and language.
		- /get_job_infos: Get HR NEXT data using username and password from URL parameters. Use the 'username' and 'password' parameters to specify the username and password.
		- ...

	'''
	# Format the instructions as HTML
	webpage = """
		<!DOCTYPE html>
		<html lang="en">
		<head>
			<meta charset="UTF-8">
			<meta name="viewport" content="width=device-width, initial-scale=1.0">
			<title>API Instructions</title>
			<style>
				body {{ font-family: Arial, sans-serif; padding: 20px; }}
				pre {{ background-color: #f4f4f4; padding: 20px;}}
			</style>
		</head>
		<body>
			<div>
			""" + \
			instructions.replace('\n', '<br>') + \
			"""
			</div>
		</body>
		</html>
		"""
	# Return the instructions as HTML
	return webpage

# Retrieves the number of purchases of my game "Buy This Game To See How Many People Bought This Game" on itch.io (probably published under the "aldopanecaldo" itch.io account)
@app.route('/api/buythisgame/count', methods=['GET', 'POST'])
def count():
	def get_purchases_count():
		# API infos
		apiKey = "ukvu7zyn0yfmXlqxaQOoORuoT7q6Ji0Moute2dOz"
		itchAPI_myGames = "https://itch.io/api/1/key/my-games"
		# Request
		response = requests.get(itchAPI_myGames, headers={"Authorization": f"Bearer {apiKey}"})
		'''
		Responses from the itch.io API are in JSON format.
		{
			"games":[
				{
					"cover_url":"http:\/\/img.itch.io\/aW1hZ2UvMy8xODM3LnBuZw==\/315x250%23\/y2uYQI.png",
					"created_at":"2013-03-03 23:02:14",
					"downloads_count":109,
					"id":3,
					"min_price":0,
					"p_android":false,
					"p_linux":true,
					"p_osx":true,
					"p_windows":true,
					"published":true,
					"published_at":"2013-03-03 23:02:14",
					"purchases_count":4,
					"short_text":"Humans have been colonizing planets. It's time to stop them!",
					"title":"X-Moon",
					"type":"default",
					"url":"http:\/\/leafo.itch.io\/x-moon",
					"views_count":2682,
					"earnings":[
						{
						"currency":"USD",
						"amount_formatted":"$50.47",
						"amount":5047
						}
					]
				}
			]
		}
		'''
		# Check response status
		if response.status_code != 200:
			return "Error: " + str(response.status_code)
		# Response
		games = response.json()["games"]
		purchasesCount = -1
		game = next((game for game in games if game["title"].lower().find("buy this game to see") != -1), None)
		if game:
			purchasesCount = game["purchases_count"]
			return purchasesCount
	# Get the purchases count
	purchasesCount = get_purchases_count()
	# Define a default starting purchases count to always add to the actual purchases count
	fakePurchasesCountToAdd = 7
	# Return a JSON response
	finanlPurchaseCount = purchasesCount + fakePurchasesCountToAdd
	response = {
		"count": finanlPurchaseCount
	}
	return json.dumps(response)

# Define a route to transform PDF files into HTML files
@app.route('/pdf2html', methods=['POST'])
def pdf2html():
	try:
		# Get the URL parameter 'simple' from the request
		simple_convertion = request.args.get('simple') == 'true'
		# Get the PDF file from the request
		pdf_file = request.files.get('pdf')		# FileStorage object
		# Read the PDF file as a byte array
		pdf_bytes_data = pdf_file.read()	# bytes object
		# Convert the PDF file to an HTML file (using either simple or advanced conversion)
		response = convertPDF(pdf_bytes_data, simple_convertion)
		# Return the response as a JSON object
		return response
	except Exception as e:
		# Return an error message if an exception occurs
		return {
			'error': str(e)	# Error message
		}
def convertPDF(pdf_bytes_data, simple_conversion):
	if simple_conversion:
		# Use the pdfminer library to convert the received PDF file into an HTML file
		# Create an in-memory buffer to store the HTML output
		output_buffer = BytesIO()
		# Convert the PDF to HTML and write the HTML to the buffer
		# laParams = LAParams(
		# 	line_overlap=0.5,
		# 	char_margin=0.2,
		# 	line_margin=0.5,
		# 	word_margin=0.175,
		# 	boxes_flow=0.5,
		# 	detect_vertical=True,
		# 	all_texts=False
		# )
		laParams = LAParams()
		method = 'html'
		# method = 'text'
		# layout_mode = 'exact'
		layout_mode = 'normal'
		extract_text_to_fp(BytesIO(pdf_bytes_data), output_buffer, output_type=method, codec='utf-8', laparams=laParams, layoutmode=layout_mode)
		# Retrieve the HTML content from the buffer
		html_bytes_obj = output_buffer.getvalue()
		# Return the HTML content as a string
		html_str = html_bytes_obj.decode('utf-8')
		html_documents = [html_str]
		return {
			'html_documents': html_documents	# List of HTML document strings
		}
	else:
		# Use the spire.pdf library to convert PDF files to 1:1 replicas as HTML files
		# Auxiliary function to convert the PDF file (as a bytes stream) to an HTML file (max 10 pages per conversion)
		def convertPDFPages(pdf_bytes_data):
			#Convert the pdf data to a stream
			pdf_stream = Stream(pdf_bytes_data)
			# Create a PDF document from the stream
			pdf = PdfDocument(pdf_stream)
			# Set the conversion options
			pdf.ConvertOptions.SetPdfToHtmlOptions(True,True)
			# Convert the PDF document to an HTML document
			html_stream = Stream()
			pdf.SaveToStream(html_stream, FileFormat.HTML)
			# Convert the HTML stream to a byte array
			html_bytes_data = html_stream.ToArray()
			bytes_object = bytes(html_bytes_data)
			# Return the HTML document as a string
			return bytes_object.decode('utf-8')
		# Auxiliary function to split the PDF file into chunks of 10 pages using the library PyPDF2, returning a list of byte arrays
		def splitPDFPages(pdf_bytes_data):
			# Create a PdfFileReader object from the PDF file
			pdf_reader = PyPDF2.PdfFileReader(BytesIO(pdf_bytes_data))
			# Get the number of pages in the PDF file
			num_pages = pdf_reader.getNumPages()
			# Initialize the list of byte arrays
			pdf_chunks = []
			# Split the PDF file into chunks of 10 pages
			for i in range(0, num_pages, 10):
				# Create a PdfFileWriter object
				pdf_writer = PyPDF2.PdfFileWriter()
				# Add 10 pages to the PdfFileWriter object
				for j in range(i, min(i+10, num_pages)):
					pdf_writer.addPage(pdf_reader.getPage(j))
				# Create a byte array from the PdfFileWriter object
				pdf_chunk = BytesIO()
				pdf_writer.write(pdf_chunk)
				# Add the byte array to the list
				pdf_chunks.append(pdf_chunk.getvalue())
			# Return the list of byte arrays
			return pdf_chunks
		# Split the PDF file into chunks of 10 pages
		pdf_chunks = splitPDFPages(pdf_bytes_data)
		# Initialize the list of HTML documents
		html_documents = []
		# Convert each chunk of 10 pages into an HTML document
		for pdf_chunk in pdf_chunks:
			html_document = convertPDFPages(pdf_chunk)
			html_documents.append(html_document)
		# Return the list of HTML documents
		return {
			'html_documents': html_documents	# List of HTML document strings
		}

# Route to save a file locally on the server
@app.route('/save', methods=['POST'])
def save_file():
	try:
		# Get the request's parameters from the body
		content = request.json.get('content')
		fileExtension = request.json.get('extension')
		allowedExtensions = ['html', 'txt', 'json', 'js']
		if not content:
			return {
				"status": "error",
				"message": "Content not provided"
			}
		if not fileExtension or fileExtension not in allowedExtensions:
			return {
				"status": "error",
				"message": f"Invalid file extension. Allowed extensions: {', '.join(allowedExtensions)}"
			}
		# Define the filename so that the file can be found in the given path
		filename = "./mysite/static/saved." + fileExtension
		fileURLResource = "/static/saved." + fileExtension
		# Save the file to a local server file (create the file if it doesn't exist)
		with open(filename, 'w') as file:
			file.write(content)
		return {
			"status": "success",
			"filename": fileURLResource
		}
	except Exception as e:
		return {
			"status": "error",
			"message": str(e)
	}

# Get all steam reviews for the given game's appid using the Steam API
@app.route('/steam_reviews', methods=['GET','POST'])
def get_reviews_api():
	# Get the request's parameters
	appid = request.args.get('appid')
	english_only = request.args.get('english_only')
	# Get the reviews
	reviews = get_reviews(appid, english_only)
	return json.dumps(reviews)
def get_reviews(appid, english_only=True):
	# API infos
	steamAPI = f"http://store.steampowered.com/appreviews/{appid}"
	parameters = {
		"json": 1,
		"filter": "recent",	# [recent, updated, all]
		"language": "english" if english_only else "all",
		# "day_range": "365",
		"review_type": "all",	# [all, positive, negative]
		"purchase_type": "all",		# [all, non_steam_purchase, steam_purchase]
		"num_per_page": 100,
		"filter_offtopic_activity": 1,	# Don't include review bombs (if detected)
		"cursor": "*"
	}
	steamAPI += "?" + "&".join([f"{key}={value}" for key, value in parameters.items()])
	steamAPI = quote_plus(steamAPI, safe=':/?&=,')
	# Request
	response = requests.get(steamAPI)
	# print(json.dumps(response.json(), indent=4))
	# Get the "cursor" from the response and use it to get all reviews
	cursor = response.json()['cursor']
	reviews = response.json()['reviews']
	total_review_count = response.json()['query_summary']['total_reviews']
	print("Getting ", total_review_count, " reviews for appid ", appid, "...",sep="")
	while cursor:
		# Update the cursor
		parameters['cursor'] = cursor
		steamAPI = f"http://store.steampowered.com/appreviews/{appid}"
		steamAPI += "?" + "&".join([f"{key}={value}" for key, value in parameters.items()])
		steamAPI = quote_plus(steamAPI, safe=':/?&=,')
		# Request
		response = requests.get(steamAPI)
		response = response.json()
		if 'reviews' not in response:
			print("Error: ", response)
			break
		# Check if the response is empty (we reached the end of the reviews)
		if not response['reviews'] or not response['cursor']:
			break
		reviews.extend(response['reviews'])
		cursor = response['cursor']
		# Print the completion percentage
		completion_percentage = len(reviews) / total_review_count * 100
		print(f"\r{len(reviews)} / {total_review_count} ({completion_percentage:.2f}%)", end="")
	return reviews

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

	# Call the function to get HR NEXT data
	try:
		data = get_hrnext_data.get_infos(username, password)
	except Exception as e:
		print(f"Error retrieving data: {e}")
		# Check if running on render.com (onrender.com) and if NOT so, call the recovery function
		if 'onrender.com' not in os.environ.get('HOSTNAME', ''):
			print("> Trying to recover missing data...")
			data = recover_missing_data(username, password)
		else:
			return jsonify({"error": "Failed to retrieve data"}), 500

	return jsonify(data)
	