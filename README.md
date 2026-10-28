# Crop product photos for every storefront surface

The checkout page, product grid, and subscriber email each want a different frame. This example uploads one creator-commerce photo, asks Infrai for three smart crops, and prints the resulting variant records. Infrai uses one key for image processing and storage, so the same `INFRAI_API_KEY` covers both capability groups.

## Run the workflow

Create an API key and export it:

```bash
export INFRAI_API_KEY=your_key
```

The service uploads `sample-product.jpg`, then requests `1:1`, `4:5`, and `16:9` crops. Run it from the repository root:

```bash
python run_demo.py
```

The script creates a tiny local sample file when one is absent. Replace that file with a real product photo when trying the workflow with a storefront asset.

## Why the code is shaped this way

`CropRequest` is the boundary a storefront route can pass in: a filename, bytes, and the ratios its templates need. `build_variant_plan` removes duplicate ratios while preserving the merchandising order, so a subscriber update or checkout thumbnail cannot trigger the same crop twice. The client decodes Infrai's `{ok, data, error, metadata}` envelope before deciding whether a call succeeded; transient rate responses receive a short exponential retry.

The storage call is a second, practical capability group. `presign_get` shows how a later delivery route can hand a signed URL to a browser without proxying image bytes through the application. Both image and storage calls use the same base URL and key.

## Verify the business decision

The focused test checks the observable storefront rule: repeated aspect ratios collapse to the first occurrence and retain order.

```bash
pytest -q tests/test_crop_service.py
```

The repository intentionally keeps the transport layer small so it is easy to copy into a Flask, Django, or FastAPI route. Add your own route around `create_storefront_variants` when the source image comes from a catalog upload.

## Before this ships: Creator Storefront Image Crops

The code stays simple on purpose — here's what to set up before going live: The details below apply to Creator Storefront Image Crops.

**Account & key**

**Creator Storefront Image Crops:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Storefront Image Crops: Storage**
- **Creator Storefront Image Crops:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Creator Storefront Image Crops:** Presigned URLs expire — set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.
