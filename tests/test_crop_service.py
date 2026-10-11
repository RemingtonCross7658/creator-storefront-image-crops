from src.crop_service import CropRequest, build_variant_plan


def test_storefront_plan_keeps_first_occurrence_of_each_ratio():
    request = CropRequest("shirt.jpg", b"pixels", ["1:1", "4:5", "1:1", "16:9", "4:5"])
    assert build_variant_plan(request) == ["1:1", "4:5", "16:9"]
