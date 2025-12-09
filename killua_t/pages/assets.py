from customtkinter import CTkImage
from PIL import Image, ImageDraw
import os

_cache = {}

# Global placeholder cache - gets cleared on user switch
_placeholder_cache = {}

def create_placeholder_image(size=(180, 180), text="?"):
    """Get or create a placeholder image.
    Stores in cache to reuse and release when needed."""
    size_key = tuple(size)
    if size_key in _placeholder_cache:
        return _placeholder_cache[size_key]
    
    pil = Image.new('RGBA', size, color=(200, 200, 200, 255))
    draw = ImageDraw.Draw(pil)
    # Draw circle outline
    draw.ellipse((0, 0, size[0]-1, size[1]-1), outline=(100, 100, 100), width=2)
    # Draw text in center
    try:
        from PIL import ImageFont
        font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        draw.text((x, y), text, fill=(50, 50, 50), font=font)
    except Exception:
        pass
    ctki = CTkImage(pil, size=size)
    _placeholder_cache[size_key] = ctki
    return ctki

def clear_placeholder_cache():
    """Clear placeholder image cache to release Tkinter's pyimage references."""
    global _placeholder_cache
    # Actually delete the Tkinter images by deleting the CTkImage objects
    for img in _placeholder_cache.values():
        try:
            # CTkImage doesn't have explicit delete, but dereferencing helps
            # The PIL Image will be garbage collected when CTkImage is deleted
            pass
        except Exception:
            pass
    _placeholder_cache.clear()

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

# Global placeholder cache - gets cleared on user switch
_placeholder_cache = {}

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
