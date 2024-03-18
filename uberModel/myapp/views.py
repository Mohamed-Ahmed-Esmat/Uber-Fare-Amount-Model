import json
import logging
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from joblib import load
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
import numpy as np
import pandas as pd

model = load('./savedModels/model.job')

logger = logging.getLogger(__name__)


kenedy_lat = 40.641766
kenedy_lng = -73.780968

ny_intern_lat = 40.689491
ny_intern_lng = -74.174538

nyc_lat = 40.7128
nyc_lng = -74.0060

liberty_lat = 40.689247
liberty_lng = -74.044502

ny_guird_lat = 40.7747
ny_guird_lng = -73.8720


def encode_year(year):
        return year - 2009

def reverse_min_max_scaling(scaled_value, min_value, max_value):
    return (scaled_value * (max_value - min_value)) + min_value


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r
def min_max_scaling(value, min_value, max_value):
    """
    Apply Min-Max scaling to a value.

    Parameters:
    value (float): The value to scale.
    min_value (float): The minimum value in the dataset.
    max_value (float): The maximum value in the dataset.

    Returns:
    float: The scaled value.
    """
    return (value - min_value) / (max_value - min_value)

def scale_time_with_sin_cos(value, max_value):
        """
        Scale time data using sine and cosine for cyclical nature.

        Parameters:
        value (int): The time value to scale.
        max_value (int): The maximum value in the time cycle.

        Returns:
        tuple: The scaled sine and cosine values.
        """
        value_scaled = (value % max_value) / float(max_value)
        value_sin = sin(value_scaled * 2 * np.pi)
        value_cos = cos(value_scaled * 2 * np.pi)
        return value_sin, value_cos

  
# Create your views here.
def index(request):
    print("Here I am")
    return render(request, 'index.html')

@csrf_exempt
def predict(request):
    original_fare_amount = None
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            print("Request Body:", request.body.decode('utf-8'))
            data2 = json.loads(request.body.decode('utf-8'))
            #data = request.POST
            
            # Handle the request data
            pick_lat = float(data2.get('pick_lat'))
            pick_long = float(data2.get('pick_long'))
            drop_lat = float(data2.get('drop_lat'))
            drop_long = float(data2.get('drop_long'))
            distance = haversine(pick_long, pick_lat, drop_long, drop_lat)
            kenedy = haversine(pick_long, pick_lat, kenedy_lng, kenedy_lat)
            ny_intern = haversine(pick_long, pick_lat, ny_intern_lng, ny_intern_lat)
            nyc = haversine(pick_long, pick_lat, nyc_lng, nyc_lat)
            liberty = haversine(pick_long, pick_lat, liberty_lng, liberty_lat)
            ny_guird = haversine(pick_long, pick_lat, ny_guird_lng, ny_guird_lat)
            date = data2.get('trip-date')
            time = data2.get('trip-time')
            pass_count = data2.get('passenger-count')
            pass_count = int(pass_count)
            
            # Combine the date and time into a single string
            datetime_str = f'{date} {time}'

            # Convert the string to a datetime object
            datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

            # Extract the year, month, day, and hour
            year = datetime_obj.year
            month = datetime_obj.month
            day = datetime_obj.day
            hour = datetime_obj.hour

              # Scale the time data
            scaled_month_sin, scaled_month_cos = scale_time_with_sin_cos(month, 12)
            scaled_hour_sin, scaled_hour_cos = scale_time_with_sin_cos(hour, 24)
            # Encode the year
            encoded_year = encode_year(year)
            # Scale the data
            min_distance, max_distance = 0.0000, 22.547218
            min_kenedy, max_kenedy = 20.031786, 47.201416
            min_ny_intern, max_ny_intern = 24.123381, 46.879962
            min_nyc, max_nyc = 0.080500, 24.633961
            min_liberty, max_liberty = 5.654745, 32.381789
            min_ny_guird, max_ny_guird = 6.590799, 29.415188
            min_pass_count, max_pass_count = 1, 6
            min_pick_lat, max_pick_lat = 40.614025, 40.865630
            min_pick_long, max_pick_long = -74.046275, -73.783575
            min_drop_lat, max_drop_lat = 40.600642, 40.870930
            min_drop_long, max_drop_long = -74.049725, -73.779822

            scaled_distance = min_max_scaling(distance, min_distance, max_distance)
            scaled_kenedy = min_max_scaling(kenedy, min_kenedy, max_kenedy)
            scaled_ny_intern = min_max_scaling(ny_intern, min_ny_intern, max_ny_intern)
            scaled_nyc = min_max_scaling(nyc, min_nyc, max_nyc)
            scaled_liberty = min_max_scaling(liberty, min_liberty, max_liberty)
            scaled_ny_guird = min_max_scaling(ny_guird, min_ny_guird, max_ny_guird)
            scaled_pass_count = min_max_scaling(pass_count, min_pass_count, max_pass_count)
            scaled_pick_lat = min_max_scaling(pick_lat, min_pick_lat, max_pick_lat)
            scaled_pick_long = min_max_scaling(pick_long, min_pick_long, max_pick_long)
            scaled_drop_lat = min_max_scaling(drop_lat, min_drop_lat, max_drop_lat)
            scaled_drop_long = min_max_scaling(drop_long, min_drop_long, max_drop_long)

            scaled_vars = [
                scaled_distance, 
                scaled_kenedy, 
                scaled_drop_long, 
                scaled_pick_long, 
                scaled_ny_intern, 
                scaled_nyc, 
                scaled_liberty, 
                scaled_ny_guird, 
                year, 
                scaled_drop_lat, 
                scaled_pick_lat, 
                scaled_month_sin, 
                scaled_pass_count, 
                scaled_hour_sin
            ]

  

            # Create a DataFrame from scaled_vars
            scaled_vars_df = pd.DataFrame([scaled_vars], columns=[
                'distance', 
                'distance_from_john_Kennedy_airport', 
                'dropoff_longitude',
                'pickup_longitude',
                'distance_from Neywork_Liberty_International_Airport', 
                'nyc_dist',
                'distance_from_status_of_liberity',
                'New_York_Municipal_Airport_LaGuardia_Field', 
                'year',
                'dropoff_latitude', 
                'pickup_latitude', 
                'month_sin', 
                'passenger_count',
                'hour_sin'
            ])

            # Predict the fare_amount using the model
            fare_amount_predicted = model.predict(scaled_vars_df)

            # Assume min_fare and max_fare are the minimum and maximum fare amounts used for scaling
            min_fare = -18.100000
            max_fare = 450.000000

            # Reverse the scaling of the predicted fare amount
            original_fare_amount = reverse_min_max_scaling(fare_amount_predicted, min_fare, max_fare)

            # Print the predicted fare_amount
            print("Predicted Fare Amount:", fare_amount_predicted)

            # Print the original fare amount
            print("Original Fare Amount:", original_fare_amount)

            

            # Print statements for testing
            print("Scaled Distance:", scaled_distance)
            print("Scaled Kenedy:", scaled_kenedy)
            print("Scaled NY Intern:", scaled_ny_intern)
            print("Scaled NYC:", scaled_nyc)
            print("Scaled Liberty:", scaled_liberty)
            print("Scaled NY Guird:", scaled_ny_guird)
            print("Scaled Passenger Count:", scaled_pass_count)
            print("Scaled Pick Latitude:", scaled_pick_lat)
            print("Scaled Pick Longitude:", scaled_pick_long)
            print("Scaled Drop Latitude:", scaled_drop_lat)
            print("Scaled Drop Longitude:", scaled_drop_long)
            print("Scaled Hour Sine:", scaled_hour_sin)
            print("Scaled Month Sine:", scaled_month_sin)
            print("Encoded Year: ", encoded_year)

            # Print statements for testing
            print("pick_lat:", pick_lat)
            print("pick_long:", pick_long)
            print("drop_lat:", drop_lat)
            print("drop_long:", drop_long)
            print("distance:", distance)
            print("kenedy:", kenedy)
            print("ny_intern:", ny_intern)
            print("nyc:", nyc)
            print("liberty:", liberty)
            print("ny_guird:", ny_guird)
            print("Date: ", date)
            print("Time: ", time)
            print("Passenger Count: ", pass_count)
            print("Year: ", year)
            print("Month: ", month)
            print("Day: ", day)
            print("Hour: ", hour)

            # Render the template with the result
            return JsonResponse({'result': original_fare_amount.item()})
        except json.JSONDecodeError as e:
            return JsonResponse({'message': 'Error decoding JSON data'}, status=400)
        except Exception as e:
            logger.exception("An error occurred during prediction")
            return JsonResponse({'message': 'An error occurred during prediction', 'error': str(e)}, status=500)
    else:
        # Render the template without the result
        return render(request, 'index.html')
