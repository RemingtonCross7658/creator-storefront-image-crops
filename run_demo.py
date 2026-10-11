from pathlib import Path

from src.crop_service import CropRequest, client_from_environment, create_storefront_variants


def main() -> None:
    source = Path("sample-product.jpg")
    if not source.exists():
        source.write_bytes(b"demo image bytes")
    request = CropRequest(source.name, source.read_bytes(), ["1:1", "4:5", "16:9"])
    variants = create_storefront_variants(client_from_environment(), request)
    for aspect, result in variants.items():
        print(f"{aspect}: {result}")


if __name__ == "__main__":
    main()
