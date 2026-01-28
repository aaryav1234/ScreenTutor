from PIL import ImageGrab


def capture_screen(bbox=None):
    """
    Captures the screen. If bbox is provided, captures only that region.
    bbox: (x1, y1, x2, y2)
    """
    return ImageGrab.grab(bbox=bbox)
