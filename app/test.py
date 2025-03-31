import requests

def get_historical_job_data():
    url = "https://data.usajobs.gov/api/HistoricJoa"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.RequestException as e:
        print(f"Error making request: {e}")
        return None

if __name__ == "__main__":
    data = get_historical_job_data()
    if data:
        print(data)


