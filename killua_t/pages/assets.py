from customtkinter import CTkImage
from PIL import Image
import os

_cache = {}

def clear_image_cache(path=None):
    """Clear cached images for a specific path, or clear entire cache if path is None."""
    global _cache
    if path is None:
        _cache.clear()
    else:
        # Remove all cache entries that reference this path (with any size or circle setting)
        keys_to_remove = [k for k in _cache.keys() if k[0] == path]
        for k in keys_to_remove:
            del _cache[k]

def get_logo(size=(28, 28)):
    """Return a CTkImage for the project's logo (PNG or JPG), cached by size."""
    key = tuple(size)
    if key in _cache:
        return _cache[key]

    assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))
    img_path = os.path.join(assets_dir, "killua.png")
    if not os.path.exists(img_path):
        img_path = os.path.join(assets_dir, "killua.jpg")

    if os.path.exists(img_path):
        try:
            pil = Image.open(img_path).convert("RGBA").resize(size)
            ctki = CTkImage(pil, size=size)
            _cache[key] = ctki
            return ctki
        except Exception:
            pass

    # Fallback: return None if image not available
    return None


def load_image(path, size=(28, 28), circle=False):
    """Load an image from a path and return a CTkImage (cached by path+size+circle).

    If `circle=True`, the image will be masked to a circle (RGBA) which looks
    like a circular profile picture in the UI.
    """
    if not path:
        return None
    key = (path, tuple(size), bool(circle))
    if key in _cache:
        return _cache[key]
    full = os.path.normpath(path)
    if not os.path.isabs(full):
        # allow relative to assets folder
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        full = os.path.join(assets_dir, full)
    if os.path.exists(full):
        try:
            pil = Image.open(full).convert("RGBA").resize(size, Image.LANCZOS)
            if circle:
                # create circular mask
                mask = Image.new('L', pil.size, 0)
                from PIL import ImageDraw
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, pil.size[0], pil.size[1]), fill=255)
                # apply mask to alpha channel
                pil.putalpha(mask)
            ctki = CTkImage(pil, size=size)
            _cache[key] = ctki
            return ctki
        except Exception:
            return None
    return None
