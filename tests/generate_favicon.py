"""
Generate favicon files using PIL

This script creates favicon.ico and PNG files directly using PIL.
Requires: pip install pillow
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Paths
STATIC_DIR = Path("app/static")

print("Generating favicon files...")

def create_laser_icon(size):
    """Create a laser-themed icon at the specified size"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale factors
    s = size / 100

    # Background circle - blue
    draw.ellipse([2*s, 2*s, (size-2)*s, (size-2)*s], fill='#1e40af', outline='#3b82f6', width=max(1, int(2*s)))

    # Laser source (top rectangle)
    draw.rectangle([42*s, 20*s, 58*s, 28*s], fill='#fbbf24', outline='#f59e0b', width=max(1, int(s)))

    # Laser beam (red line)
    draw.line([50*s, 28*s, 50*s, 45*s], fill='#ef4444', width=max(2, int(3*s)))

    # Impact point (red circle)
    draw.ellipse([46*s, 41*s, 54*s, 49*s], fill='#ef4444')
    draw.ellipse([48*s, 43*s, 52*s, 47*s], fill='#fbbf24')

    # Material being cut (gray rectangle)
    draw.rectangle([30*s, 45*s, 70*s, 70*s], fill='#64748b', outline='#475569', width=max(1, int(2*s)))

    # Cut line (dashed) - only for larger icons
    if size >= 32:
        step = max(1, int(4*s))
        for y in range(int(45*s), int(70*s), step):
            draw.line([50*s, y, 50*s, y+int(2*s)], fill='#1e293b', width=max(1, int(2*s)))

    # Letter "L" at bottom
    try:
        # Try to use a font, fall back to default if not available
        font_size = max(12, int(24*s))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Draw text
        text = "L"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size - text_width) / 2
        text_y = 88*s - text_height

        draw.text((text_x, text_y), text, fill='#ffffff', font=font)
    except:
        # If font fails, just skip the text for small icons
        pass

    return img

# Generate PNG files at different sizes
sizes = {
    16: "favicon-16x16.png",
    32: "favicon-32x32.png",
    180: "apple-touch-icon.png"
}

images = {}
for size, filename in sizes.items():
    print(f"  Creating {size}x{size} PNG...")
    img = create_laser_icon(size)
    output_path = STATIC_DIR / filename
    img.save(output_path, 'PNG')
    images[size] = img
    print(f"    ✓ Saved: {output_path}")

# Generate favicon.ico (multi-size ICO file)
print("  Creating favicon.ico...")
ico_path = STATIC_DIR / "favicon.ico"
images[32].save(
    ico_path,
    format='ICO',
    sizes=[(16, 16), (32, 32)]
)
print(f"    ✓ Saved: {ico_path}")

print("\n✅ Favicon generation complete!")
print("\nGenerated files:")
print(f"  • {STATIC_DIR / 'favicon.ico'}")
print(f"  • {STATIC_DIR / 'favicon-16x16.png'}")
print(f"  • {STATIC_DIR / 'favicon-32x32.png'}")
print(f"  • {STATIC_DIR / 'apple-touch-icon.png'}")
print("\nThe favicon should now appear in your browser tab!")
print("You may need to hard refresh (Ctrl+Shift+R) to see the change.")

