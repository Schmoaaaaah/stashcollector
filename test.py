import json

import requests


def call(url, method, args):
  data = {
    'method': method,
    'params': [args]
  }
  res = requests.post(url=url, json=data, headers={'Content-Type': 'application/json'})
  response = json.loads(res.text)
  return response


def test():
    url = "http://localhost:4444/rpc"
    args = {'URL': "https://de.pornhub.com/view_video.php?viewkey=ph5cd9f72a0dffc",
            'Params': ["--write-info-json", "--add-metadata", "-o", "/%(webpage_url_domain)s/%(uploader)s/%(title)s.%(ext)s"]
            }
    call(url, 'Service.Exec', args)

test()