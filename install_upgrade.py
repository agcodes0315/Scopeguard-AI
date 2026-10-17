"""Install the additive ScopeGuard Atlas decision explanation without backend edits."""
from pathlib import Path
import shutil
import sys

root = Path.cwd()
html = root / 'frontend' / 'atlas.html'
source = Path(__file__).resolve().parent / 'frontend' / 'decision-replay.js'
target = root / 'frontend' / 'decision-replay.js'
if not (root / 'backend' / 'atlas.py').is_file() or not html.is_file():
    sys.exit('ERROR: Run this installer from the root of the scopeguard-ai repository.')
body = html.read_text(encoding='utf-8')
anchor = '<script src="/atlas.js"></script>'
addon = '<script src="/decision-replay.js"></script>'
if body.count(anchor) != 1:
    sys.exit('ERROR: Unexpected atlas.html script layout; nothing modified.')
if target.exists() and target.read_bytes() != source.read_bytes():
    sys.exit('ERROR: Existing decision-replay.js differs; refusing to overwrite.')
if body.count(addon) > 1:
    sys.exit('ERROR: Duplicate add-on tags detected; nothing modified.')
if target.exists() and addon in body:
    print('Already installed. No modifications needed.')
    sys.exit(0)
# Make source available before changing the HTML.
shutil.copyfile(source,target)
if addon not in body:
    html.write_text(body.replace(anchor,anchor+'\n'+addon),encoding='utf-8')
print('Installed frontend/decision-replay.js and registered script in frontend/atlas.html')
print('No backend, classification, proposal or pricing files changed.')
