import os
import base64


def encode_image_base64(image_path: str) -> str:
    if not os.path.exists(image_path):
        return ""

    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
