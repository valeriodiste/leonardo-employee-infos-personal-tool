'''
Script to get the HR NEXT data from the Leonardo S.p.A. portal using the provided username and password.
NOTE: Can be paired with a Flask app to create a web service providing username and password as URL parameters.
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time
import json
import os
import sys

# Function to get the HR NEXT data from the Leonardo S.p.A. portal
def get_infos(username, password):
	"""
	Get the HR NEXT data from the Leonardo S.p.A. portal using the provided username and password.
	
	Args:
		username (str): The username for the HR NEXT portal.
		password (str): The password for the HR NEXT portal.

	Returns:
		dict: A dictionary containing the user's information of the form:
			{
				"user": str,
				"saldo_ore": str,
				"entrata": str,
				"days_ago": int,
				
			}
	"""

	#Get the start time
	start_time = time.time()

	# Print the username and password (for debugging purposes)
	print(f"\nGetting infos for user: {username} (password: {password})")

	# Default wait time
	default_wait_time = 0.1
	long_wait_time = 0.1

	# Returned infos
	infos = {
		"user": username,
		"saldo_ore": None,
		"entrata": None,
		"days_ago": None,
		"opzioni_uscita": {
			"8_hours": None,
			"6_hours": None,
			"azzera_saldo_ore": None
		}
	}

	# Website URL
	login_page_url = "https://gpnx-leonardo.datamanagement.it/gepe-gerip-online-war/next/app/#/dipe"

	# Create a new Chrome session
	options = Options()
	options.add_argument("--no-sandbox")
	options.add_argument("--headless")  # Run in headless mode (no GUI)
	options.add_argument("--disable-gpu")
	options.add_argument("--window-size=1920x1080")  # Set the window size to avoid issues with elements not being found
	options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
	
	# Set up ChromeDriver with WebDriver Manager
	print("Setting up ChromeDriver...")
	driver = None
	# Check if running on a Linux server (e.g., Google Colab, Render.com, local yaml-compatible server, etc.)
	try:
		is_windows = sys.platform.startswith("win")
		is_colab = "google.colab" in sys.modules
		if not is_windows and not is_colab:
			print("> Not running on Windows or Google Colab...")
			chrome_driver_path = "/usr/bin/chromedriver"
			if os.path.exists("/usr/bin/chromedriver"):
				# Use the system-installed ChromeDriver
				print("> Using system-installed ChromeDriver...")
				from selenium.webdriver.chrome.service import Service
				service = Service(executable_path=chrome_driver_path)
				driver = webdriver.Chrome(service=service, options=options)
			else:
				# Try to recover errors by installing the needed packages
				print("> Installing ChromeDriver using WebDriver Manager...")
				from selenium.webdriver.chrome.service import Service
				from webdriver_manager.chrome import ChromeDriverManager
				service = Service(ChromeDriverManager(
					driver_version="135.0.7049.42"
				).install())
				driver = webdriver.Chrome(service=service, options=options)
				print("> ChromeDriver setup complete....")
		else:
			# Use the default ChromeDriver for Windows or Google Colab
			print("> Running on Windows or Google Colab...")
			driver = webdriver.Chrome(options=options)
	except Exception as e:
		print(f"> Error setting up ChromeDriver: {e}")
		print("> Trying to use the default ChromeDriver...")
		driver = webdriver.Chrome(options=options)

	# Function to wait until an element is present in the DOM
	def wait_till_element_comes_up(css_selector, inner_text=None, max_attempts=50):
		"""Wait until the specified element is present in the DOM."""
		check_frequency = 0.25  # seconds
		while max_attempts > 0:
			try:
				if inner_text is not None:
					element = None
					elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
					if len(elements) > 0:
						for e in elements:
							if e.text.strip() == inner_text.strip():
								element = e
								break
					if element is None:
						# print(f"Element with text '{inner_text}' not found.")
						pass
				else:
					element = driver.find_element(By.CSS_SELECTOR, css_selector)
				if element is not None and element.is_displayed():
					return element
			except Exception as e:
				pass
			max_attempts -= 1
			time.sleep(check_frequency)
		return None
	
	# Open the website
	print("\nOpening website...")
	driver.get(login_page_url)
	time.sleep(default_wait_time)
	username_input = wait_till_element_comes_up("input#username")
	time.sleep(default_wait_time)
	username_input.send_keys(username)
	password_input = wait_till_element_comes_up("input#password")
	password_input.send_keys(password)
	time.sleep(default_wait_time)  # Wait for a second before clicking the login button
	submit_button = wait_till_element_comes_up("input[name='submit'][type='submit']")
	submit_button.click()
	time.sleep(long_wait_time)
	time_next_section_button_div = wait_till_element_comes_up("div.widget-main.hidden-background-image > div.row > div:nth-child(2) > div > div > div")
	time.sleep(long_wait_time)  # Wait for a second before clicking the next button
	time_next_section_button_div.click()
	time.sleep(long_wait_time)

	# We are now on the maini "Time Next" page
	hours_counter_select_field = wait_till_element_comes_up("div[ng-if='mostraContatorVsTimbrature'] select#form-field-select-1")
	time.sleep(long_wait_time)  # Wait for a second before executing the next command
	oggi_button = wait_till_element_comes_up("div[aria-label='Calendario eventi'] button[type='button']", "Oggi")
	previous_day_button = wait_till_element_comes_up("div[aria-label='Calendario eventi'] button[type='button']", "<")
	next_day_button = wait_till_element_comes_up("div[aria-label='Calendario eventi'] button[type='button']", ">")
	oggi_button.click()
	time.sleep(long_wait_time)  # Wait for a second before executing the next command

	# Get "entrata"
	print("Getting 'entrata'...")
	giorno_switch_button = wait_till_element_comes_up("div[aria-label='Calendario eventi'] button[type='button']", "Giorno")
	mese_switch_button = wait_till_element_comes_up("div[aria-label='Calendario eventi'] button[type='button']", "Mese")
	giorno_switch_button.click()
	time.sleep(long_wait_time)  # Wait for a second before executing the next command
	print("> Switching to 'Giorno' view...")
	# Search for the "entrata" element hour
	# NOTE: if not found, we may be looking at a day in the weekend, or a day when we didn't enter the office, hence we should check the previous day...
	days_offset = 0
	ora_entrata = None
	while True:
		if days_offset > 6:
			print("No 'entrata' found in the last 7 days.")
			break
		timbrature_entrata_element = wait_till_element_comes_up("#timbratureList > li > div.ng-binding", max_attempts=5)
		if timbrature_entrata_element is not None:
			ora_entrata = timbrature_entrata_element.text
			break
		else:
			# Try again for the previous day
			previous_day_button.click()
			time.sleep(long_wait_time)  # Wait for a second before executing the next command
			days_offset += 1
			print(f"> Trying again for the previous day ({days_offset} days ago)...")
	infos["entrata"] = ora_entrata
	infos["days_ago"] = days_offset

	# Get "saldo ore"
	print("Getting 'saldo ore'...")
	mese_switch_button.click()
	time.sleep(long_wait_time)  # Wait for a second before executing the next command
	hours_counter_select_field = wait_till_element_comes_up("div[ng-if='mostraContatorVsTimbrature'] select#form-field-select-1")
	hours_counter_select = Select(hours_counter_select_field)
	last_option = hours_counter_select.options[-1]  # Get the last option element
	hours_counter_select.select_by_value(last_option.get_attribute("value"))  # Select the last option by value
	time.sleep(long_wait_time)  # Wait for a second before clicking the next button
	saldo_ore_element = wait_till_element_comes_up("table#contatoriTable tr > td", "Saldo compensazione giornaliero")
	saldo_ore = saldo_ore_element.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "td")[-2].text
	infos["saldo_ore"] = saldo_ore

	# Get the final user name and surname
	user_name_element = wait_till_element_comes_up("div.user-info")
	user_name = user_name_element.get_attribute("title").strip()
	infos["user"] = user_name

	# Calculate the "uscita" options
	print("Calculating 'uscita' options...")
	launch_break_duration = 0.75  # 45 minutes
	uscita_options = {
		"8_hours": None,
		"6_hours": None,
		"azzera_saldo_ore": None
	}
	if ora_entrata is not None and days_offset == 0:
		# Get the "uscita" options based on the "entrata" time
		time_zero = time.mktime(time.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"))  # Reference time (epoch)
		hour, minute = map(int, ora_entrata.split(":"))
		uscita_options["8_hours"] = time.strftime("%H:%M", time.localtime(time_zero + (hour + 8 + launch_break_duration) * 3600 + minute * 60))
		uscita_options["6_hours"] = time.strftime("%H:%M", time.localtime(time_zero + (hour + 6 + launch_break_duration) * 3600 + minute * 60))
		if saldo_ore is not None:
			saldo_ore_hours, saldo_ore_minutes = map(int, saldo_ore[1:].split(":"))
			if saldo_ore[0] == "-":
				# If the "saldo ore" is negative, we need to do 8 hours plus the "saldo ore" hours/minutes
				uscita_options["azzera_saldo_ore"] = time.strftime("%H:%M", time.localtime(time_zero + (hour + 8 + launch_break_duration - saldo_ore_hours) * 3600 + (minute - saldo_ore_minutes) * 60))
			else:
				# If the "saldo ore" is positive, we need to do 8 hours minus the "saldo ore" hours/minutes
				uscita_options["azzera_saldo_ore"] = time.strftime("%H:%M", time.localtime(time_zero + (hour + 8 + launch_break_duration - saldo_ore_hours) * 3600 + (minute - saldo_ore_minutes) * 60))
	infos["opzioni_uscita"] = uscita_options
	
	# Print the results
	print("\nResults:")
	print(json.dumps(infos, indent=4))
	
	# input("Press Enter to continue...")

	driver.quit()

	print(f"\nExecution time: {time.time() - start_time:.2f} seconds")

	return infos

# Example usage
if __name__ == "__main__":
	# Get the credentials from the "credentials.json" file
	username = None
	password = None
	try:
		credentials_file = "credentials.json"
		with open(credentials_file, "r") as file:
			credentials = json.load(file)
			username = credentials["username"]
			password = credentials["password"]
	except FileNotFoundError:
		print(f"Credentials file '{credentials_file}' not found, using default credentials.")
		try:
			if credentials is None:
				# Default credentials if the file is not found
				credentials = {
					"username": "null",
					"password": "null"
				}
			username = credentials["username"]
			password = credentials["password"]
		except Exception as e:
			print(f"Error reading credentials: {e}")
			username = input("Enter username: ")
			password = input("Enter password: ")
	# Get the information
	get_infos(username, password)