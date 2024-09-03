from flask import Flask, render_template, request  # Import necessary modules from Flask
import requests  # Import the requests library to make HTTP requests
from dotenv import load_dotenv  # Import load_dotenv to load environment variables from a .env file
import os  # Import os to interact with the operating system

# Load environment variables from a .env file into the application
load_dotenv()

# Retrieve API Key and Base URLs from the environment variables for secure access
API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')
BASE_URL_FORECAST = os.getenv('BASE_URL_FORECAST')

# Initialize the Flask application
app = Flask(__name__)

def convert_to_fahrenheit(celsius):
    """
    Convert temperature from Celsius to Fahrenheit.
    :param celsius: Temperature in Celsius.
    :return: Temperature in Fahrenheit.
    """
    return celsius * 9/5 + 32

def get_weather_by_city_and_state(city_name, state_code):
    """
    Fetch current weather data for a specific city and state.
    :param city_name: Name of the city.
    :param state_code: Two-letter state code.
    :return: A dictionary containing weather data or None if the data is not found.
    """
    # Format the query string with the city, state, and country code
    query = f"{city_name},{state_code},US"  
    # Construct the full API request URL for current weather
    url = f"{BASE_URL}q={query}&appid={API_KEY}&units=metric"
    
    # Send a GET request to the weather API and get the response
    response = requests.get(url)
    data = response.json()
    
    # Check if the API response indicates a successful data retrieval
    if data["cod"] == 200:
        main = data['main']  # Main weather data (temperature, humidity, etc.)
        weather = data['weather'][0]  # Weather description
        wind = data['wind']  # Wind data
        
        temp_celsius = main['temp']  # Current temperature in Celsius
        temp_fahrenheit = convert_to_fahrenheit(temp_celsius)  # Convert temperature to Fahrenheit
        
        # Organize the relevant weather data into a dictionary
        weather_data = {
            "city": city_name,
            "state": state_code,
            "temperature_celsius": f"{temp_celsius:.2f}",
            "temperature_fahrenheit": f"{temp_fahrenheit:.2f}",
            "humidity": main['humidity'],
            "description": weather['description'].title(),
            "wind_speed": wind['speed']
        }
        return weather_data  # Return the dictionary containing weather data
    else:
        return None  # Return None if the data was not successfully retrieved

def get_5_day_forecast_by_city_and_state(city_name, state_code):
    """
    Fetch a 5-day weather forecast for a specific city and state.
    :param city_name: Name of the city.
    :param state_code: Two-letter state code.
    :return: A list of dictionaries containing forecast data or None if the data is not found.
    """
    # Format the query string with the city, state, and country code
    query = f"{city_name},{state_code},US"  
    # Construct the full API request URL for the 5-day forecast
    url = f"{BASE_URL_FORECAST}q={query}&appid={API_KEY}&units=metric"
    
    # Send a GET request to the weather API and get the response
    response = requests.get(url)
    data = response.json()

    forecast_data = []  # Initialize an empty list to store the forecast data

    # Check if the API response indicates a successful data retrieval
    if data["cod"] == "200":
        previous_date = ""  # Variable to track the date of the last forecast entry
        for forecast in data['list']:
            dt_txt = forecast['dt_txt']  # Date and time of the forecast
            temp_celsius = forecast['main']['temp']  # Forecast temperature in Celsius
            temp_fahrenheit = convert_to_fahrenheit(temp_celsius)  # Convert temperature to Fahrenheit
            description = forecast['weather'][0]['description']  # Weather description
            current_date = dt_txt.split()[0]  # Extract the date (without time)

            # Check if the forecast is for a new day
            if current_date != previous_date:
                forecast_data.append({"date": current_date, "entries": []})
                previous_date = current_date
            
            # Append the forecast data to the most recent date entry
            forecast_data[-1]["entries"].append({
                "datetime": dt_txt,
                "temp_celsius": f"{temp_celsius:.2f}",
                "temp_fahrenheit": f"{temp_fahrenheit:.2f}",
                "description": description.title()
            })
        
        return forecast_data  # Return the list of forecast data
    else:
        return None  # Return None if the data was not successfully retrieved

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handle requests to the root URL ('/').
    :return: Render the appropriate template based on user input.
    """
    if request.method == 'POST':  # Check if the form has been submitted
        city = request.form.get('city')  # Get the city name from the form
        state = request.form.get('state')  # Get the state code from the form
        choice = request.form.get('choice')  # Get the user's choice (current weather or forecast)

        if choice == 'current':
            weather_data = get_weather_by_city_and_state(city, state)  # Fetch current weather data
            if weather_data:
                return render_template('index.html', weather=weather_data)
            else:
                return render_template('index.html', error="Could not find weather data. Please check your input.")
        elif choice == 'forecast':
            forecast_data = get_5_day_forecast_by_city_and_state(city, state)  # Fetch 5-day forecast data
            if forecast_data:
                return render_template('forecast.html', forecast=forecast_data)
            else:
                return render_template('index.html', error="Could not find forecast data. Please check your input.")
    return render_template('index.html')  # Render the index page for GET requests

if __name__ == "__main__":
    app.run(debug=True)  # Run the Flask application in debug mode