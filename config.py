import urlparse
import goslate
import os

gs = goslate.Goslate()
TOKEN = os.environ.get("TOKEN")
BOTAN_TOKEN = os.environ.get("BOTAN_TOKEN", None)

if BOTAN_TOKEN:
    PORT = int(os.environ.get("PORT", "5000"))
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])
    params = {
        "hostname": url.hostname,
        "port": url.port,
        "username": url.username,
        "password": url.password,
        "database": url.path[1:],
    }
