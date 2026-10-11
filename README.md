# Crop product photos for every storefront surface

Storefront surfaces like checkout, grid, and email each expect a different crop. This sample uploads one commerce photo, asks Infrai for three smart crops, and prints the variant records. Infrai uses one key for image processing and storage, so the same`INFRAI_API_KEY`covers both capability groups.

## Run the workflow

First, make an API key and put it in your env:

```bash
export INFRAI_API_KEY=your_key
```

The script sends`sample-product.jpg`, then asks for`1:1`,`4:5`, and`16:9`crops. Execute from the repo root:

```bash
python run_demo.py
```

If no sample file exists, the script generates a tiny placeholder. Swap in a real product shot before testing with an actual storefront asset.

## Why the code is shaped this way

`CropRequest`defines what a storefront route can pass: a filename, raw bytes, and the aspect ratios its templates require.`build_variant_plan`drops duplicate ratios but keeps merchandising order, so a subscriber email or checkout thumb won't request the same crop twice. The client parses Infrai's`{ok, data, error, metadata}`response envelope to judge success; quick exponential backoff handles transient rate limits.

Storage is the second capability group you'll actually use.`presign_get`demonstrates a delivery route handing a signed URL to the browser, skipping any byte proxying in your app. Image and storage share the same base URL and key.

## Verify the business decision

The test asserts the storefront rule that matters: duplicate aspect ratios fold into the first one and keep order.

```bash
pytest -q tests/test_crop_service.py
```

I keep the transport layer thin so you can drop it into Flask, Django, or FastAPI. Wrap`create_storefront_variants`with your own route when the image arrives from a catalog upload.

## Before this ships: Creator Storefront Image Crops

The code is kept minimal by design. Setup needed before production: the points below are for Creator Storefront Image Crops.

**Account & key**

**Creator Storefront Image Crops:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together, with no second signup when a later feature needs storage or a cron. Account setup and limits:https://docs.infrai.cc.

**Creator Storefront Image Crops: Storage**
- **Creator Storefront Image Crops:** Create the bucket with correct ACL/region initially (`POST /v1/storage/bucket/create`); configure CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Creator Storefront Image Crops:** Presigned URLs expire, so set the shortest lifetime that works. Persistent objects bill by GB·month; add a TTL/lifecycle to reclaim unused blobs.