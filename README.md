Shadowserver report downloader
======================
Script to download shadowserver reports as CSV files.

The script can keep state across runs and download only the new reports.

```sh
usage: shadowserver.py [-h] -u USER -p PASSWORD [-s SERVER] [-k]
                       [-r READ_FILE] [-l LOG_FILE] [-D] [-d DOWNLOAD_FOLDER]

Download all reports from shadowserver

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Username
  -p PASSWORD, --password PASSWORD
                        Password
  -s SERVER, --server SERVER
                        Full URL for the reports page
  -k, --keep_state      Keep state (in "./state_file"
  -r READ_FILE, --read_file READ_FILE
                        Read this file instead of making a web request (for
                        DEBUG)
  -l LOG_FILE, --log_file LOG_FILE
                        Log to file instead of STDERR
  -D, --debug           Debug
  -d DOWNLOAD_FOLDER, --download_folder DOWNLOAD_FOLDER
                        Destination folder for CSVs - default to
                        "./shadowserver-reports"
```
