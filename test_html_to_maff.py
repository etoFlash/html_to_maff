from html_to_maff import _get_html_files, _format_log_row_to_txt, LogRow


def test_get_html_files():
    expected = 5
    actual = len(list(_get_html_files("test_html_to_maff")))

    assert actual == expected


def test_format_log_row_to_txt():
    expected = ("Original filename: file.html\n"
                "New filename: file.maff\n"
                "Status: OK\n\n")

    log_row = LogRow("file.html", "file.maff", "OK", "")
    actual = _format_log_row_to_txt(log_row)

    assert actual == expected