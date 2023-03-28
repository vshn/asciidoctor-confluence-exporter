#!/usr/bin/env python3

# This script uses the Confluence API to convert pages in a Confluence wiki into
# files in the AsciiDoc format. The username and password required to connect to
# the API must be passed as environment variables: `CONFLUENCE_USERNAME` and
# `CONFLUENCE_PASSWORD`.

import requests
import argparse
import subprocess
import os
import logging
import sys

# Used to build the URL to connect to, stripping extra slashes if needed
def slash_join(*args):
    return "/".join(arg.strip("/") for arg in args)

# Parsing command arguments
parser = argparse.ArgumentParser(description="Reads a series of pages from a Confluence `--wiki` server as numeric IDs, and writes each one to stdout.")
parser.add_argument("-w", "--wiki", help="base URL of the Confluence wiki", required=True)
parser.add_argument("-v", "--verbose", help="show all logging messages during execution", action="store_true")
parser.add_argument("--version", action="version", version="%(prog)s 1.0")
parser.add_argument("pages", help="Confluence page IDs to export", metavar="N", nargs="+", type=int)
args = parser.parse_args()

# Setting logger parameters
level = logging.WARNING
if args.verbose:
    level = logging.INFO
logging.basicConfig(format='%(levelname)s: %(message)s', level=level)

logging.info("Starting program with parameters:")
logging.info("Wiki: '{}'".format(args.wiki))
logging.info("Page IDs: '{}'".format(args.pages))

# Read username and password from the environment
CONFLUENCE_USERNAME = os.environ.get("CONFLUENCE_USERNAME")
CONFLUENCE_PASSWORD = os.environ.get("CONFLUENCE_PASSWORD")

if not CONFLUENCE_USERNAME or not CONFLUENCE_PASSWORD:
    logging.error("Environment variables CONFLUENCE_USERNAME and/or CONFLUENCE_PASSWORD are unset. Exiting.")
    exit(1)

logging.info("Environment variables set.")

# Pandoc command to transform HTML into AsciiDoc.
cmd = ["/usr/local/bin/pandoc", "--from=html", "--to=asciidoctor", "--wrap=none"]
base_url = slash_join(args.wiki, "rest", "api", "content")
logging.info("Base URL is '{}'.".format(base_url))

# Fetch each page and save as AsciiDoc
try:
    for page in args.pages:
        url = "{}/{}?expand=body.storage".format(base_url, page)
        resp = requests.get(url=url, auth=(CONFLUENCE_USERNAME, CONFLUENCE_PASSWORD))
        if resp.status_code != 200:
            logging.error("Status code {} for '{}'. Continuing.".format(resp.status_code, url))
            continue
        logging.info("Status code {} for '{}'.".format(resp.status_code, url))
        data = resp.json()
        title = data["title"]
        html = data["body"]["storage"]["value"]

        # Transform to AsciiDoc using Pandoc
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        comm = proc.communicate(input=html.encode())[0]
        adoc = comm.decode().strip()

        # Output to stdout
        logging.info("Printing page '{}'".format(page))
        print(adoc)
except:
    e = sys.exc_info()[0]
    logging.error("Error: '{}'. Exiting.".format(e))
    exit(1)
