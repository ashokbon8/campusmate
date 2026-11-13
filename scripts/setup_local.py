"""Create a private local configuration once; retain existing configuration."""
from pathlib import Path
import secrets
import shutil

root = Path(__file__).resolve().parents[1]
target = root / 'backend/.env'
if not target.exists():
    if (root / '.env').exists():
        shutil.copyfile(root / '.env', target)
    else:
        target.write_text('SECRET_KEY=' + secrets.token_urlsafe(48) + '\n'
            'CAMPUSMATE_DATASET=jscoe\nCAMPUSMATE_SEED=1\n', encoding='utf-8')
print('Local configuration ready. Existing settings were retained.')
