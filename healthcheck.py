import os
import sys

import requests


def main():
    port = os.getenv('PORT', 8000)
    res = requests.get(f'http://localhost:{port}/')
    if res.status_code >= 400:
        sys.exit(1)


if __name__ == '__main__':
    main()
