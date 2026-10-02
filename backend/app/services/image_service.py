from io import BytesIO
from PIL import Image

def inspect_image(data: bytes):
    result = {"width":0,"height":0,"format":None,"ocr_text":""}
    try:
        image = Image.open(BytesIO(data))
        result.update({"width":image.width,"height":image.height,"format":image.format})
    except Exception:
        return result
    try:
        import pytesseract
        result["ocr_text"] = pytesseract.image_to_string(image)[:12000]
    except Exception:
        pass
    return result
