from waitress import serve #type: ignore
from run import app

if __name__ == "__main__":
    # Configure production server
    serve(
        app,
        host="0.0.0.0",  # Listen on all available network interfaces
        port=8080,       # You can change this port as needed
        threads=4        # Adjust based on server capacity
    )