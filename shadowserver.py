#!/usr/bin/env python3
import requests
import re
import argparse
import pickle
import logging
from logging.handlers import RotatingFileHandler
import sys
import os

match_downloads = b'(https:\/\/dl.shadowserver.org\/[^"]+)'
state_file = "./state_file"
script_name = "shadowserver-to-splunk"
default_download_folder = "./shadowserver-reports"

parser = argparse.ArgumentParser(description='Download all reports from shadowserver')
parser.add_argument('-u', '--user', help='Username', required=True)
parser.add_argument('-p', '--password', help='Password', required=True)
parser.add_argument('-s', '--server', help='Full URL for the reports page', required=False, default="https://dl.shadowserver.org/reports/index.php")
parser.add_argument('-k', '--keep_state', help='Keep state (in "' + state_file + '")', required=False, action="store_true", default=False)
parser.add_argument('-r', '--read_file', help='Read this file instead of making a web request (for DEBUG)', required=False)
parser.add_argument('-l', '--log_file', help='Log to file instead of STDERR', required=False)
parser.add_argument('-D', '--debug', help='Debug', action="store_true", required=False)
parser.add_argument('-d', '--download_folder', help='Destination folder for CSVs - default to "' + default_download_folder + '"', required=False, default=default_download_folder)
args = parser.parse_args()

# Logging
if args.debug:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

logger = logging.getLogger()
logger.level = log_level

if args.log_file:
    rotationHandler = RotatingFileHandler(args.log_file, mode='a', maxBytes=5 * 1024 * 1024, backupCount=1)
    rotationHandler.setLevel(log_level)
    rotationHandler.setFormatter(logging.Formatter('%(asctime)s - ' + script_name + ' - %(levelname)s - %(message)s'))
    logger.addHandler(rotationHandler)
else:
    logger.addHandler(logging.StreamHandler())

# Log the command line options
logger.debug(args)


def read_state(state_file):
    try:
        logger.debug("Reading State")
        with open(state_file, 'r') as state:
            return pickle.load(state)

    except Exception:
        e = sys.exc_info()
        logger.warn("Cannot read state moving on anyway with an empty state: " + str(e))
        return []


def store_state(state_file, already_processed):
    try:
        logger.debug("Storing State")
        with open(state_file, 'w') as state:
            pickle.dump(already_processed, state)

    except Exception:
        e = sys.exc_info()
        logger.error("Cannot save state: " + str(e))


def download_element(session, url, download_folder):
    logging.debug("[Downloading] '" + url + "' to '" + download_folder + "'")

    try:
        response = session.get(url)
        if response.status_code == 200:
            content_disposition = response.headers['content-disposition']
            filename = re.findall("filename=(.+)", content_disposition)[0]

            dest_file = download_folder + "/" + filename
            with open(dest_file, 'wb') as outputfile:
                outputfile.write(response.content)
                logging.debug(url + " saved to " + dest_file)

            return True

        else:
            raise ValueError('Response status is not 200')

    except Exception:
        e = sys.exc_info()
        logger.warn("Cannot download '" + url +  "': " + str(e))
        return False


if args.keep_state:
    already_processed = read_state(state_file)
    # logging.debug("Already processed according to state:")
    # for element in already_processed:
    #    logging.debug(element)
else:
    already_processed = []
    logger.debug("I will not keep state for this run")

auth_details = {'user': args.user, 'password': args.password, 'login': 'Login'}

# Init a requests session that is used either here or later
session = requests.Session()
if args.read_file:
    logger.info("Will read file '" + args.read_file + "' instead of issuing a web request")
    page = open(args.read_file, "r")
    html_content = page.read()
else:
    response = session.post(args.server, data=auth_details)
    html_content = response.content

if not os.path.exists(args.download_folder):
    os.mkdir(args.download_folder)

# Extract all the URLs for reports and proceed to download all the ones we don't have already
for download_me in re.finditer(match_downloads, html_content, re.MULTILINE):
    url = download_me.group(1).decode()
    if url not in already_processed:
        succeeded = download_element(session, url, args.download_folder)
        if succeeded:
            already_processed.append(url)
        else:
            logger.debug("Not going to add '" + url + "' in the list of correctly processed files")
    else:
        logger.debug("[Already downloaded] " + url)

if args.keep_state:
    store_state(state_file, already_processed)
