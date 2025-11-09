from app import create_app, db
from app.models import DesignFile
import os
from pathlib import Path

app = create_app()
app.app_context().push()

f = DesignFile.query.first()
base = app.config['UPLOAD_FOLDER']

print(f"File path in DB: {f.file_path}")
print(f"Base folder: {base}")
print(f"Type of base: {type(base)}")

# Method 1: os.path.join
path1 = os.path.join(base, f.file_path)
print(f"\nMethod 1 (os.path.join):")
print(f"  Result: {path1}")
print(f"  Is absolute: {os.path.isabs(path1)}")
print(f"  Exists: {os.path.exists(path1)}")

# Method 2: Path
path2 = str(Path(base) / f.file_path)
print(f"\nMethod 2 (Path):")
print(f"  Result: {path2}")
print(f"  Is absolute: {os.path.isabs(path2)}")
print(f"  Exists: {os.path.exists(path2)}")

# Method 3: os.path.abspath
path3 = os.path.abspath(os.path.join(base, f.file_path))
print(f"\nMethod 3 (abspath):")
print(f"  Result: {path3}")
print(f"  Is absolute: {os.path.isabs(path3)}")
print(f"  Exists: {os.path.exists(path3)}")

