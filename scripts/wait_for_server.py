import time
from urllib.request import urlopen
from urllib.error import URLError

for attempt in range(40):
    try:
        with urlopen("http://127.0.0.1:8000/api/health", timeout=2) as response:
            if response.status == 200:
                break
    except (URLError, OSError):
        time.sleep(.5)
else:
    raise SystemExit("CrowdForge did not become healthy within 20 seconds.")
