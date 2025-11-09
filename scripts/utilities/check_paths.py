from app import create_app, db
from app.models import DesignFile
import os

app = create_app()
app.app_context().push()

files = DesignFile.query.all()
base = app.config['UPLOAD_FOLDER']

print("Current file paths in DB:")
for f in files:
    print(f'  ID {f.id}: "{f.file_path}"')

print('\nFull path construction:')
for f in files:
    full = os.path.join(base, f.file_path)
    exists = os.path.exists(full)
    print(f'  ID {f.id}: {full}')
    print(f'    Exists: {exists}')

