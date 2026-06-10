import random
import time

from bs4 import BeautifulSoup
import requests


def fetch_html(
    session: requests.Session,
    url: str,
    delay_min: float = 1.0,
    delay_max: float = 3.0,
    verify: bool = False
):

    try:

      time.sleep(random.uniform(delay_min, delay_max))

      response = session.get(
          url,
          timeout=(10, 30),
          verify=verify,
          allow_redirects=True
      )

      response.raise_for_status()

      response.encoding = response.apparent_encoding

      text = response.text.lower()

      if (
          "cf-browser-verification" in text
          or "attention required" in text
          or "cloudflare" in text and "ray id" in text
      ):
          print(f"Cloudflare detectado: {url}")
          return None

      return BeautifulSoup(
          response.text,
          "html.parser"
      )

    except requests.exceptions.SSLError as e:
        print(f"SSL Error {url}: {e}")

    except requests.exceptions.Timeout:
        print(f"Timeout: {url}")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error {url}: {e}")

    except Exception as e:
        print(f"Error {url}: {e}")

    return None
