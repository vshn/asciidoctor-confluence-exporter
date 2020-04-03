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

# Used to build the URL to connect to, stripping extra slashes if needed
def slash_join(*args):
    return "/".join(arg.strip("/") for arg in args)

# Parsing command arguments
parser = argparse.ArgumentParser(description="Reads a series of pages from a Confluence `--wiki` server as numeric IDs, and writes each one to an AsciiDoc file into the specified `--output` folder.")
parser.add_argument("-o", "--output", help="folder where to export files", required=True)
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
logging.info("Output: '{}'".format(args.output))
logging.info("Page IDs: '{}'".format(args.pages))

# Verify that the specified output argument is a folder
if os.path.exists(args.output) and not os.path.isdir(args.output):
    logging.error("Invalid output folder name '{}'. Exiting.".format(args.output))
    exit(1)

# If the folder does not exist, create it
if not os.path.exists(args.output):
    logging.info("Creating output folder '{}'".format(args.output))
    os.makedirs(args.output)

# Read username and password from the environment
CONFLUENCE_USERNAME = os.environ.get("CONFLUENCE_USERNAME")
CONFLUENCE_PASSWORD = os.environ.get("CONFLUENCE_PASSWORD")

if not CONFLUENCE_USERNAME or not CONFLUENCE_PASSWORD:
    logging.error("Environment variables CONFLUENCE_USERNAME and/or CONFLUENCE_PASSWORD are unset. Exiting.")
    exit(1)

logging.info("Environment variables set.")

# Pandoc command to transform HTML into AsciiDoc.
cmd = ["/usr/bin/pandoc", "--from=html", "--to=asciidoctor", "--wrap=none"]
base_url = slash_join(args.wiki, "rest", "api", "content")
logging.info("Base URL is '{}'.".format(base_url))

# Fetch each page and save as AsciiDoc
for page in args.pages:
    url = "{}/{}?expand=body.storage".format(base_url, page)
    resp = requests.get(url=url, auth=(CONFLUENCE_USERNAME, CONFLUENCE_PASSWORD))
    if resp.status_code != 200:
        logging.error("Status code {} for '{}'. Continuing.".format(resp.status_code, url))
        continue
    logging.info("Status code {} for '{}'.".format(resp.status_code, url))
    data = resp.json()
    html = data["body"]["storage"]["value"]

    # Transform to AsciiDoc using Pandoc
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    comm = proc.communicate(input=html.encode())[0]
    adoc = comm.decode().strip()

    # Save to file
    filename = "{}/{}.adoc".format(args.output, page)
    file = open(filename, "w")
    file.write(adoc)
    file.close()
    logging.info("Saved AsciiDoc file '{}'".format(filename))
