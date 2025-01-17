#!/usr/bin/env python2
# encoding: utf-8
"""
This script generates index.html files to every directory and subdirectory
starting from the specified directory. Every html file consist of a table
with the following columns:
icon file_name last_modification_time file_size open_url description

It is designed to look like the output of apache web server.
"""

from __future__ import (absolute_import, division, print_function)

import os
import re
import utils
import config
import operator
import argparse
from unipath import Path
from time import gmtime, strftime
from jinja2 import Environment, FileSystemLoader

TEMPLATE_ENVIRONMENT = Environment(autoescape=False,
                                   loader=FileSystemLoader('templates'),
                                   trim_blocks=False)


def create_ipynb_link(filename):
    link = 'http://nbviewer.ipython.org/urls/'

    if config.DROPBOX_BASE_URL.startswith('https://'):
        link = link + config.DROPBOX_BASE_URL[8:]
    elif config.DROPBOX_BASE_URL.startswith('http://'):
        link = link + config.DROPBOX_BASE_URL[7:]

    findex = filename.find('Public')
    link = link + filename[findex + 6:]

    return link


def get_open_url(filename):
    # TODO: this should be updated to reflect correct external url
    link = []

    if os.path.isfile(filename):
        ext = os.path.splitext(filename)[1]
        if ext == '.ipynb':
            link.append(create_ipynb_link(filename))
            link.append('nbview')
    else:
        link.append('')
        link.append('')

    return link


def sizeof_fmt(filesize_in_bytes):
    """Converts file size to human readable format."""

    num = float(filesize_in_bytes)
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']:
        if num < 1024.0 and x == 'bytes':
            return int(num)
        elif num < 1024.0:
            return "{0:.2f}&nbsp;{1}".format(num, x)
        num /= 1024.0


def get_icon_name(filename):
    """Returns the name of the icon that belongs to the file or directory."""

    if filename == "../index.html":
        return "back.gif"
    elif os.path.isdir(filename):
        return "folder.gif"
    else:
        for extension, icon in config.extensions.items():
            # if the file extension is recognised return the correct icon
            match = re.search(extension + "$", filename)
            if match:
                return icon

    # unknown filename extension
    return "unknown.gif"


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def get_context(datas, root, current_directory, relpath):
    """returns the context dictionary, to be used by template.html"""
    return {
        'datas': datas,
        'root': root,
        'current_directory': current_directory,
        'font': ("monospace" if config.MONOSPACED_FONTS else ""),
        'SHOW_SERVER_INFO': config.SHOW_SERVER_INFO,
        'server_info': config.SERVER_INFO,
        'index_of': ("" if relpath == "." else relpath),
        'link_to_icons': os.path.relpath(config.icon_dir, current_directory)
    }


def create_index_html(root, recurse=True):
    """Creates an index.html file in every directory and subdirectory."""

    total_processed_files = 0
    total_processed_dirs = 0
    total_generated_index_htmls = 0

    depth_from_root = 0
    for dirpath, dirnames, filenames in os.walk(root):
        if not recurse and depth_from_root > 0:
            break

        if config.HIDE_HIDDEN_ENTRIES and os.path.basename(dirpath).startswith("."):
            continue

        filter_names(dirnames, filenames)
        if recurse:
            dirs = get_entries(dirpath, dirnames)
        else:
            dirs = []
        files = get_entries(dirpath, filenames)

        context = get_context(datas=dirs + files,
                              root=root,
                              current_directory=dirpath,
                              relpath=os.path.relpath(dirpath, root))

        rendered_template = render_template('template.html', context)
        index_html = os.path.join(dirpath, "index.html")

        if os.path.exists(index_html):
            print('Skipping as index.html already exist: ' + index_html)
        else:
            write_to_disk(rendered_template, index_html)
            total_generated_index_htmls += 1

        depth_from_root += 1
        total_processed_dirs += len(dirs)
        total_processed_files += len(files)

    total_processed_items = total_processed_dirs + total_processed_files
    print("Total processed files and directories: {count}".format(count=total_processed_items))
    print("Total index.html files generated: {count}".format(count=total_generated_index_htmls))


def filter_names(dirnames, filenames):
    """Filter files and directories based on config"""
    if config.HIDE_INDEX_HTML_FILES and "index.html" in filenames:
        filenames.remove("index.html")

    if config.HIDE_ICONS_FOLDER and config.TARGET_ICON_FOLDER_NAME in dirnames:
        dirnames.remove(config.TARGET_ICON_FOLDER_NAME)

    if config.HIDE_HIDDEN_ENTRIES:
        remove_hiddens(dirnames)
        remove_hiddens(filenames)

    for ext in config.ignore_exts:
        filenames[:] = [x for x in filenames if not x.endswith(ext)]


def remove_hiddens(name_list):
    name_list[:] = [x for x in name_list if not x.startswith(".")]


def get_entries(dirpath, names):
    """Returns Entry object for each element of names"""
    paths = []
    for name in names:
        paths.append(get_entry(Path(dirpath, name)))

    paths.sort(key=operator.attrgetter('name'))
    return paths


def get_entry(path):
    assert isinstance(path, Path), "path is not a Path object"

    name = path.name
    date = strftime("%Y-%m-%d&nbsp;%H:%M", gmtime(60 * 60 + path.mtime()))
    size = sizeof_fmt(path.size())
    icon = get_icon_name(path)
    open_url = get_open_url(os.path.abspath(path))

    if path.isdir():
        url = os.path.join(name, "index.html")
    else:
        url = name

    return Entry(name, date, size, icon, url, open_url)


class Entry():
    def __init__(self, name, date, size, icon, url, open_url):
        self.name = name
        self.date = date
        self.size = size
        self.icon = icon
        self.url = url
        self.open_url = open_url


def file_differs_from_content(filename, content):
    is_different = True

    if os.path.exists(filename):
        with open(filename) as f:
            if f.read().strip() == content.strip():
                is_different = False

    return is_different


def write_to_disk(template, destination):
    with open(destination, "w") as f:
        f.write(template)


def main():
    parser = argparse.ArgumentParser(description="Apache web-server style static HTML file generator")
    parser.add_argument("location",
                        help="path to the Public folder of your Dropbox folder.")

    parser.add_argument("--clean",
                        action="store_true",
                        help="cleans your Dropbox directory by deleting index.html files.")

    parser.add_argument("--no-recurse",
                        action="store_true",
                        help="Disables recursive traversal.")

    parser.add_argument('--ignore-exts', nargs='+', required=False,
                        help='File extensions to ignore', default=[])

    args = parser.parse_args()

    target_dir = os.path.realpath(args.location)
    recurse = not args.no_recurse
    config.ignore_exts = args.ignore_exts

    if args.clean:
        utils.cleanup(target_dir)
        exit(0)

    icon_dir = utils.install_icons(target_dir)
    config.icon_dir = icon_dir  # make it available globally!
    create_index_html(target_dir, recurse=recurse)




#############################################################################

if __name__ == "__main__":
    main()
