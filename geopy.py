from geopy.geocoders import Nominatim

def get_address(latitude, longitude):
    # Create a geolocator object using Nominatim
    geolocator = Nominatim(user_agent="geo_locator")

    # Combine latitude and longitude into a tuple
    location = (latitude, longitude)

    try:
        # Use reverse geocoding to get the address
        address = geolocator.reverse(location, language='en')
        return address.address if address else "Address not found"
    except Exception as e:
        print(f"Error: {e}")
        return "Error fetching address"

# Example coordinates (replace with your actual GPS coordinates)
latitude = 37.7749
longitude = -122.4194

# Get the human-readable address
address = get_address(latitude, longitude)

# Print the result
print(f"Coordinates: {latitude}, {longitude}")
print(f"Address: {address}")
