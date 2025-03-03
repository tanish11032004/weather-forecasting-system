from django.shortcuts import render
import requests
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta
import pytz
import os
import logging
from django.contrib import messages

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_KEY = '9f39358739a87c32ca64c4a33f26f292'
BASE_URL = 'https://api.openweathermap.org/data/2.5/'

# 1) Fetch current data from the API with error handling
def get_current_weather(city):
    try:
        url = f'{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric'
        response = requests.get(url, timeout=10)  # Add timeout for API requests
        
        if response.status_code != 200:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return None
            
        data = response.json()
        
        # Check if the response has all required fields
        required_fields = ['name', 'main', 'weather', 'sys', 'wind', 'clouds', 'visibility']
        if not all(field in data for field in required_fields):
            logger.error(f"Missing fields in API response: {data}")
            return None
        
        # Get current temperature
        current_temp = round(data['main']['temp'])
        
        # Calculate realistic min and max temperatures
        temp_variation = 5  # Temperature variation of ±5°C
        temp_min = round(min(data['main']['temp_min'], current_temp - temp_variation), 1)
        temp_max = round(max(data['main']['temp_max'], current_temp + temp_variation), 1)
        
        # Ensure min and max temperatures are different
        if temp_min == temp_max:
            temp_min = current_temp - 2
            temp_max = current_temp + 2
            
        return {
            'city': data['name'],
            'current_temp': current_temp,
            'feels_like': round(data['main']['feels_like']),
            'temp_min': temp_min,
            'temp_max': temp_max,
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'country': data['sys']['country'],
            'wind_gust_dir': data['wind'].get('deg', 0),  # Use get with default value
            'pressure': data['main']['pressure'],
            'wind_Gust_Speed': data['wind'].get('speed', 0),  # Use get with default value
            'clouds': data['clouds']['all'],
            'visibility': data.get('visibility', 0),  # Use get with default value
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None
    except KeyError as e:
        logger.error(f"KeyError in API response: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

# 2) Read Historical data from the CSV file with error handling
def read_historical_data(filename):
    try:
        if not os.path.exists(filename):
            logger.error(f"File not found: {filename}")
            return None
            
        df = pd.read_csv(filename)
        df = df.dropna()
        df = df.drop_duplicates()
        
        # Validate that required columns exist
        required_columns = ['MinTemp', 'MaxTemp', 'WindGustDir', 'WindGustSpeed', 
                           'Humidity', 'Pressure', 'Temp', 'RainTomorrow']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns in {filename}")
            return None
            
        return df
    except pd.errors.EmptyDataError:
        logger.error(f"Empty CSV file: {filename}")
        return None
    except pd.errors.ParserError:
        logger.error(f"CSV parsing error: {filename}")
        return None
    except Exception as e:
        logger.error(f"Error reading historical data: {e}")
        return None

# 3) Prepare the data for training
def prepare_data(data):
    try:
        le = LabelEncoder()
        data['WindGustDir'] = le.fit_transform(data['WindGustDir'])
        data['RainTomorrow'] = le.fit_transform(data['RainTomorrow'])
        
        X = data[['MinTemp', 'MaxTemp', 'WindGustDir', 'WindGustSpeed', 'Humidity', 'Pressure', 'Temp']]
        y = data['RainTomorrow']
        
        return X, y, le
    except Exception as e:
        logger.error(f"Error preparing data: {e}")
        return None, None, None

# 4) Train the rain prediction model
def train_rain_model(X, y):
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        logger.info(f"Mean Squared Error for Rain Model: {mse}")
        
        return model
    except Exception as e:
        logger.error(f"Error training rain model: {e}")
        return None

# 5) Prepare regression data
def prepare_regression_data(data, feature):
    try:
        X, y = [], []
        
        for i in range(len(data)-1):
            X.append(data[feature].iloc[i])
            y.append(data[feature].iloc[i+1])
            
        X = np.array(X).reshape(-1, 1)
        y = np.array(y)
        return X, y
    except Exception as e:
        logger.error(f"Error preparing regression data for {feature}: {e}")
        return None, None

# 6) Train the regression model
def train_regression_model(X, y):
    try:
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        return model
    except Exception as e:
        logger.error(f"Error training regression model: {e}")
        return None

# 7) Predict the future weather
def predict_future_weather(model, current_value):
    try:
        predictions = [current_value]
        
        for i in range(5):
            next_value = model.predict(np.array([[predictions[-1]]]))
            predictions.append(next_value[0])
            
        return predictions[1:]
    except Exception as e:
        logger.error(f"Error predicting future weather: {e}")
        return [current_value] * 5  # Return current value repeated as fallback

# 8) Weather analysis function
def weather_view(request):
    context = {}
    
    try:
        if request.method == 'POST':
            city = request.POST.get('city', '')
            if not city:
                messages.error(request, "Please enter a city name")
                return render(request, 'weather.html', context)
                
            # Fetch current weather
            current_weather = get_current_weather(city)
            if not current_weather:
                messages.error(request, f"Unable to get weather data for {city}. Please check the city name and try again.")
                return render(request, 'weather.html', context)
            
            # Load historical data
            csv_path = os.path.join('D:\\machine learning project\\weather.csv')
            historical_data = read_historical_data(csv_path)
            
            if historical_data is None:
                messages.error(request, "Error loading historical weather data. Using current data only.")
                # Set up fallback forecasting using just the current data
                timezone = pytz.timezone('Asia/karachi')
                now = datetime.now(timezone)
                next_hour = now + timedelta(hours=1)
                next_hour = next_hour.replace(minute=0, second=0, microsecond=0)
                
                future_times = [(next_hour + timedelta(hours=i)).strftime("%H:00") for i in range(1, 6)]
                time1, time2, time3, time4, time5 = future_times
                
                # Simple fallback forecast - just use current values
                temp1 = temp2 = temp3 = temp4 = temp5 = current_weather['current_temp']
                hum1 = hum2 = hum3 = hum4 = hum5 = current_weather['humidity']
            else:
                # Prepare and train models
                X, y, le = prepare_data(historical_data)
                if X is None or y is None:
                    messages.warning(request, "Error preparing data for prediction models. Using simplified forecast.")
                    rain_model = None
                else:
                    rain_model = train_rain_model(X, y)
                
                # Map wind direction to compass points
                wind_deg = current_weather['wind_gust_dir'] % 360
                compass_points = [
                    ("N", 0, 11.25), ("NNE", 11.25, 33.75), ("NE", 33.75, 56.25), ("ENE", 56.25, 78.75),
                    ("E", 78.75, 101.25), ("ESE", 101.25, 123.75), ("SE", 123.75, 146.25), ("SSE", 146.25, 168.75),
                    ("S", 168.75, 191.25), ("SSW", 191.25, 213.75), ("SW", 213.75, 236.25), ("WSW", 236.25, 258.75),
                    ("W", 258.75, 281.25), ("WNW", 281.25, 303.75), ("NW", 303.75, 326.25), ("NNW", 326.25, 348.75),
                ]
                
                compass_direction = "N"  # Default value
                for point, start, end in compass_points:
                    if start <= wind_deg < end:
                        compass_direction = point
                        break
                
                compass_direction_encoded = -1
                if le is not None and hasattr(le, 'classes_'):
                    compass_direction_encoded = le.transform([compass_direction])[0] if compass_direction in le.classes_ else -1
                
                current_data = {
                    'MinTemp': current_weather['temp_min'],
                    'MaxTemp': current_weather['temp_max'],
                    'WindGustDir': compass_direction_encoded,
                    'WindGustSpeed': current_weather['wind_Gust_Speed'],
                    'Humidity': current_weather['humidity'],
                    'Pressure': current_weather['pressure'],
                    'Temp': current_weather['current_temp']
                }
                
                current_df = pd.DataFrame([current_data])
                
                # Prepare regression models with error handling
                X_temp, y_temp = prepare_regression_data(historical_data, 'Temp')
                X_hum, y_hum = prepare_regression_data(historical_data, 'Humidity')
                
                if X_temp is None or y_temp is None or X_hum is None or y_hum is None:
                    messages.warning(request, "Error in preparing regression data. Using simplified forecast.")
                    temp_model = hum_model = None
                else:
                    temp_model = train_regression_model(X_temp, y_temp)
                    hum_model = train_regression_model(X_hum, y_hum)
                
                # Predict future values with fallbacks
                if temp_model is None:
                    future_temp = [current_weather['current_temp']] * 5
                else:
                    future_temp = predict_future_weather(temp_model, current_weather['current_temp'])
                
                if hum_model is None:
                    future_humidity = [current_weather['humidity']] * 5
                else:
                    future_humidity = predict_future_weather(hum_model, current_weather['humidity'])
                
                # Prepare time data
                timezone = pytz.timezone('Asia/karachi')
                now = datetime.now(timezone)
                next_hour = now + timedelta(hours=1)
                next_hour = next_hour.replace(minute=0, second=0, microsecond=0)
                
                future_times = [(next_hour + timedelta(hours=i)).strftime("%H:00") for i in range(1, 6)]
                time1, time2, time3, time4, time5 = future_times
                temp1, temp2, temp3, temp4, temp5 = [round(t, 1) for t in future_temp]
                hum1, hum2, hum3, hum4, hum5 = [round(h, 1) for h in future_humidity]
            
            # Pass data to template
            context = {
                'location': city,
                'current_temp': current_weather['current_temp'],
                'MinTemp': current_weather['temp_min'],
                'MaxTemp': current_weather['temp_max'],
                'feels_like': current_weather['feels_like'],
                'humidity': current_weather['humidity'],
                'clouds': current_weather['clouds'],
                'description': current_weather['description'],
                'city': current_weather['city'],
                'country': current_weather['country'],
                
                'time': datetime.now(),
                'date': datetime.now().strftime("%B %d, %Y"),
                
                'wind': current_weather['wind_Gust_Speed'],
                'pressure': current_weather['pressure'],
                'visibility': current_weather['visibility'],
                
                'time1': time1,
                'time2': time2,
                'time3': time3,
                'time4': time4,
                'time5': time5,
                
                'temp1': f"{temp1}",
                'temp2': f"{temp2}",
                'temp3': f"{temp3}",
                'temp4': f"{temp4}",
                'temp5': f"{temp5}",
                
                'hum1': f"{hum1}",
                'hum2': f"{hum2}", 
                'hum3': f"{hum3}",
                'hum4': f"{hum4}", 
                'hum5': f"{hum5}",
            }
    
    except Exception as e:
        logger.error(f"Unexpected error in weather_view: {e}")
        messages.error(request, "An unexpected error occurred. Please try again later.")
    return render(request, 'weather.html', context)
