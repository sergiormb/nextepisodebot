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
        "host": url.hostname,
        "port": url.port,
        "user": url.username,
        "password": url.password,
        "database": url.path[1:],
    }

else:
    PORT = None
    params = {
        "host": "localhost",
        "user": "admin",
        "password": "admin",
        "database": "nextepisodebot",
    }
