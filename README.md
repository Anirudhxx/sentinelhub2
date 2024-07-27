# Sentinel-2 NDVI Data Fetcher

This project provides an API to fetch NDVI (Normalized Difference Vegetation Index) statistics using Sentinel-2 L2A data from the Planetary Computer STAC API.

## Features

- Query NDVI statistics for a given date and geographic area.
- Uses Sentinel-2 L2A data.
- Filters data based on cloud cover.

## Requirements

- Python 3.8+
- Docker (for containerized deployment)

## Setup

### Local Development

1. **Clone the repository**

    ```sh
    git clone https://github.com/Anirudhxx/sentinelhub2.git
    cd sentinelhub2
    ```

2. **Create and activate a virtual environment**

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**

    ```sh
    pip3 install -r requirements.txt
    ```

4. **Run the application**

    ```sh
    uvicorn main:app --reload
    ```
### Docker Hub

1. **Pull the Docker Image**
    ```sh
    docker pull anirudhchauhan10/fastapi-sentinel2:latest
    ```

2. **Run the Docker container**

    ```sh
    docker run -p 8000:8000  anirudhchauhan10/fastapi-sentinel2
    ```
## Usage

### API Endpoint

**POST /query**

Fetch NDVI statistics for a given date and geographic area.

#### Request Body

```json
{
  "timestamp": "2022-07-01",
  "geojson": {
    "type": "Polygon",
    "coordinates": [
      [
        [-149.56536865234375, 60.80072385643073],
        [-148.44338989257812, 60.80072385643073],
        [-148.44338989257812, 61.18363894915102],
        [-149.56536865234375, 61.18363894915102],
        [-149.56536865234375, 60.80072385643073]
      ]
    ]
  }
}
```
#### Response

```json
{
  "mean": 0.42,
  "std": 0.1,
  "min": 0.0,
  "max": 1.0
}
```
## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.
