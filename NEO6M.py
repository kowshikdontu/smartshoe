from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE

def get_gps_coordinates():
    # Create a GPS object
    session = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE, device='/dev/ttyS0')

    try:
        # Stream GPS data
        session.stream(WATCH_ENABLE | WATCH_NEWSTYLE)

        while True:
            # Get data from the GPS
            report = session.next()

            # Check if GPS fix is valid
            if report['class'] == 'TPV' and hasattr(report, 'lat') and hasattr(report, 'lon'):
                latitude = report.lat
                longitude = report.lon
                print(f"Latitude: {latitude}, Longitude: {longitude}")
                return latitude, longitude

    except KeyboardInterrupt:
        print("Exiting GPS data fetching.")

if __name__ == "__main__":
    get_gps_coordinates()
