# TODO:
#  1
#  args: path=xxx(default=.) log=none/csv/txt(default=txt)
from uuid import uuid1
from collections import namedtuple
import os
import csv
import glob
import time


temp_dir = str(uuid1())
DEFAULT_OUTPUT_DIR = "maff_output"
HTML_MASKS = (".htm", ".html")

INDEX_RDF = """
<?xml version="1.0"?>
<RDF:RDF xmlns:MAF="http://maf.mozdev.org/metadata/rdf#"
         xmlns:NC="http://home.netscape.com/NC-rdf#"
         xmlns:RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <RDF:Description RDF:about="urn:root">
    <MAF:indexfilename RDF:resource="index.html"/>
  </RDF:Description>
</RDF:RDF>""".lstrip()

LogRow = namedtuple(
    "LogRow", ["original_filename", "new_filename", "status", "message"]
)


class HtmlDirNotFound(Exception):
    pass


class MaffWithNameExists(Exception):
    pass


def _format_log_row_to_txt(log_tuple):
    """Format log-row to text format for print log and save to log.txt"""
    return (f"original_filename: {log_tuple.original_filename}\n"
            f"new_filename: {log_tuple.new_filename}\n"
            f"status: {log_tuple.status}\n" +
            f"message: {log_tuple.message}\n" * bool(log_tuple.message))


def _get_html_files(files_path):
    for file in glob.glob(os.path.join(files_path, "*.htm*")):
        if file.endswith((".htm", ".html")):
            yield file


def save_log(save_path, log_list, file_format="TXT"):
    """Save log to file"""
    file_format = file_format.upper()
    if file_format not in ("CSV", "TXT"):
        return

    if file_format == "TXT":
        with open(os.path.join(save_path, "log.txt"), "w") as f:
            for log in log_list:
                f.write(_format_log_row_to_txt(log))
    else:
        with open(os.path.join(save_path, "log.csv"), "w") as f:
            pass  # TODO: save CSV


if __name__ == '__main__':
    # TODO: get from args path, log format, etc.
    if not os.path.exists(DEFAULT_OUTPUT_DIR):
        os.mkdir(DEFAULT_OUTPUT_DIR)
    os.mkdir(temp_dir)

    logs = []
    for html_file in _get_html_files("test"):
        original_filename = html_file.split("\\")[-1]
        new_filename = ""
        status = "OK"
        message = ""
        # TODO: processing
        logs.append(LogRow(original_filename, new_filename, status, message))

    save_log(DEFAULT_OUTPUT_DIR, logs)
    os.removedirs(temp_dir)
