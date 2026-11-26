"""Sale (y despierta al chat) cuando la ventana visible (9333) ya entró a Bizurai, o a los 25 min."""
import time
from cdp9333 import Pestana
fin = time.time() + 25 * 60
while time.time() < fin:
    try:
        u = Pestana().js("location.href") or ""
        if "/v2/location/" in u or "/location/" in u:
            print("LOGIN OK", u[:90]); break
    except Exception as e:
        pass
    time.sleep(10)
else:
    print("SIN LOGIN en 25 min")
