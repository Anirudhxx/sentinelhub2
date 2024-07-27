from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict
import datetime
import numpy as np
import rasterio
from rasterio import windows, features, warp
from pystac_client import Client
import planetary_computer
from shapely.geometry import shape
from pystac.extensions.eo import EOExtension

app = FastAPI()

class QueryRequest(BaseModel):
    timestamp: datetime.date
    geojson: Dict[str, Any] = Field(..., example={
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
    })

def fetch_ndvi_stats(timestamp: datetime.date, geometry: Dict[str, Any]) -> Dict[str, float]:
    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    area_of_interest = geometry
    time_of_interest = f"{timestamp.strftime('%Y-%m-%d')}/{(timestamp + datetime.timedelta(days=1)).strftime('%Y-%m-%d')}"

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        intersects=area_of_interest,
        datetime=time_of_interest,
        query={"eo:cloud_cover": {"lt": 10}},
    )

    items = search.item_collection()
    if not items:
        raise HTTPException(status_code=404, detail="No Sentinel-2 data found for the specified date and region.")

    least_cloudy_item = min(items, key=lambda item: EOExtension.ext(item).cloud_cover)

    asset_href_red = least_cloudy_item.assets["B04"].href  # B04 is typically the Red band
    asset_href_nir = least_cloudy_item.assets["B08"].href  # B08 is typically the NIR band

    polygon = shape(geometry)
    aoi_bounds = features.bounds(polygon)

    with rasterio.open(asset_href_red) as ds_red, rasterio.open(asset_href_nir) as ds_nir:
        warped_aoi_bounds = warp.transform_bounds("epsg:4326", ds_red.crs, *aoi_bounds)
        aoi_window = windows.from_bounds(transform=ds_red.transform, *warped_aoi_bounds)

        red_band = ds_red.read(1, window=aoi_window)
        nir_band = ds_nir.read(1, window=aoi_window)

    with np.errstate(divide='ignore', invalid='ignore'):
        ndvi = (nir_band - red_band) / (nir_band + red_band)
        ndvi = np.where(np.isfinite(ndvi), ndvi, np.nan)

    valid_ndvi = ndvi[~np.isnan(ndvi)]
    if valid_ndvi.size == 0:
        raise HTTPException(status_code=500, detail="No valid NDVI values found.")

    return {
        "mean": float(np.nanmean(valid_ndvi)),
        "std": float(np.nanstd(valid_ndvi)),
        "min": float(np.nanmin(valid_ndvi)),
        "max": float(np.nanmax(valid_ndvi))
    }

@app.post("/query")
def query_sentinel2_data(request: QueryRequest):
    try:
        stats = fetch_ndvi_stats(request.timestamp, request.geojson)
        return stats
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
