import pandas as pd
import re
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the CSV file
df = pd.read_csv("D:/django/edit 2/vaultspace/users/tests/99acres.csv")

# Function to convert "Lac" values to numbers
def convert_rent(rent):
    rent = str(rent).replace("₹", "").strip()  # Remove currency symbol

    # Convert "Lac" to numerical lakh format
    if "Lac" in rent:
        number = re.findall(r"[\d.]+", rent)  # Extract numeric value
        if number:
            return float(number[0]) * 100000  # Convert Lac to Lakh numbering
    else:
        number = re.findall(r"[\d,]+", rent)  # Extract normal numbers
        if number:
            return int(number[0].replace(",", ""))  # Remove commas

# Function to get coordinates for a location
def get_coordinates(location):
    try:
        # Add "Kerala, India" to improve geocoding accuracy
        location_with_state = f"{location}, Kerala, India"
        geolocator = Nominatim(user_agent="my_agent")
        location = geolocator.geocode(location_with_state)
        if location:
            return pd.Series([location.latitude, location.longitude])
        return pd.Series([None, None])
    except GeocoderTimedOut:
        return pd.Series([None, None])
    except Exception as e:
        print(f"Error geocoding {location}: {str(e)}")
        return pd.Series([None, None])

# Apply conversion to the rent column


# Add coordinates columns
print("Converting locations to coordinates...")
df[["latitude", "longitude"]] = df["Location"].apply(get_coordinates)

# Add delay between requests to avoid rate limiting
time.sleep(1)

# Save the modified data back to CSV in current directory
output_csv = os.path.join(current_dir, "99acres_warehouse_rentals_updated.csv")
df.to_csv(output_csv, index=False)

print(f"Updated CSV saved in: {output_csv}")
