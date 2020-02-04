from uuid import uuid1
from collections import namedtuple
import os
import csv
import glob
import time
import shutil


DEFAULT_OUTPUT_DIR = "maff_output"
TXT_LOG_NAME = "log.txt"
INDEX_HTML_PREFIX = "index"
INDEX_HTML_POSTFIX = ".html"
DIR_FILES_POSTFIX = "_files"
INDEX_RDF_FILENAME = "index.rdf"

TEMP_DIR = str(uuid1())

ERR_DIR_NOT_FOUND = "Dir not found for html: '{}'"
ERR_MAFF_EXISTS = "MAFF-file this with name already exists: '{}'"
ERR_EMPTY_FILENAME = "Empty filename after remove reserved chars"

HTML_MASKS = (".htm", ".html")
RESERVED_CHAR = "/\\%<>:\"?* |."

INDEX_RDF_DATA = """
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


def _format_log_row_to_txt(log_tuple):
    """Format log-row to text format for print log and save to TXT_LOG_NAME"""
    return (f"Original filename: {log_tuple.original_filename}\n"
            f"New filename: {log_tuple.new_filename}\n"
            f"Status: {log_tuple.status}\n"
            + f"Message: {log_tuple.message}\n" * bool(log_tuple.message) + "\n")


def _get_html_files(files_path, file_prefix="*"):
    for file in glob.glob(os.path.join(files_path, f"{file_prefix}.htm*")):
        if file.endswith((".htm", ".html")):
            yield file


def pack_to_maff(inp_file_with_path, out_path=DEFAULT_OUTPUT_DIR, temp_path=TEMP_DIR) -> str:
    # 1) get dates +
    # 2) copy to temp +
    # 3) rename file +
    # 4) rename url in file
    # 5) pack to maff (zip) to output
    # - # 6) copy
    # 7) set dates
    # 8) clean temp
    stat = os.stat(inp_file_with_path)
    inp_file = inp_file_with_path.split(os.path.sep)[-1]
    out_filename = "".join(filter(lambda c: c not in RESERVED_CHAR,
                                  inp_file[:inp_file.rfind(".")]))[:145]
    assert len(out_filename) > 0, ERR_EMPTY_FILENAME
    out_filename = out_filename[:145] + ".maff"
    dir_files = inp_file_with_path[:inp_file_with_path.rfind(".")] + DIR_FILES_POSTFIX
    assert os.path.isdir(dir_files), ERR_DIR_NOT_FOUND.format(dir_files)
    shutil.copy(inp_file_with_path, os.path.join(temp_path, INDEX_HTML_PREFIX + INDEX_HTML_POSTFIX))
    shutil.copytree(dir_files, os.path.join(temp_path, INDEX_HTML_PREFIX + DIR_FILES_POSTFIX))

    return out_filename


def save_log(save_path, log_list, file_format="txt"):
    """Save log to file"""
    file_format = file_format.lower()
    if file_format not in ("csv", "txt"):
        return

    if file_format == "txt":
        with open(os.path.join(save_path, TXT_LOG_NAME), "w") as f:
            for log in log_list:
                f.write(_format_log_row_to_txt(log))
    else:
        with open(os.path.join(save_path, "log.csv"), "w") as f:
            pass  # TODO: save CSV


if __name__ == '__main__':
    # TODO: get from args path, log format, etc.
    if not os.path.exists(DEFAULT_OUTPUT_DIR):
        os.mkdir(DEFAULT_OUTPUT_DIR)
    os.mkdir(TEMP_DIR)
    with open(os.path.join(TEMP_DIR, INDEX_RDF_FILENAME), "w") as f:
        f.write(INDEX_RDF_DATA)

    logs = []
    for html_file in _get_html_files("test"):
        original_filename = html_file.split(os.path.sep)[-1]
        status, message, new_filename = "OK", "", ""
        try:
            new_filename = pack_to_maff(html_file)
        except Exception as e:
            status = "Failure"
            message = e
        logs.append(LogRow(original_filename, new_filename, status, message))
        print(_format_log_row_to_txt(logs[-1]), end="")

    save_log(DEFAULT_OUTPUT_DIR, logs)
    input("press enter")
    shutil.rmtree(TEMP_DIR)
