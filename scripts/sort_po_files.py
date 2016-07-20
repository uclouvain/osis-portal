#!/usr/bin/env python3
##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
# Sort the "filename_to_be_sorted" located in "dir_path".
# The file to be sorted must be a ".po" file used in django for translation.
# Call the script with:  python -c 'import sort_po_files; sort_po_files.sort_and_replace()'

import os


key_keyword = "msgid"
value_keyword = "msgstr"

filename_to_be_sorted= "django.po"
filename_sorted = "django_ordered.po"

dir_path = "./admission/locale/en/LC_MESSAGES/"


# ******************************** MAIN FUNCTIONS *********************
def sort_po_file(relative_dir_path):
    """
    Create a file "filename_sorted" which is the sorted version of the file
    "filename_to_be_sorted".
    :param relative_dir_path: path of the directory containing the file to be sorted.
    """
    with open(relative_dir_path+filename_to_be_sorted) as f:
        d, header = parse_file(f)

        list_keys = list(d.keys())
        list_keys.sort()

    with open(relative_dir_path+filename_sorted, "w") as new_f:
        header_to_file(header, new_f)
        dic_to_file(list_keys, d, new_f)


def replace_file(old_file, new_file):
    """
    Replace "old_file" by "new_file".
    :param old_file: file to be replaced
    :param new_file: file which replaced
    """
    files_exist = os.path.isfile(old_file) and \
                  os.path.isfile(new_file)
    if not files_exist:
        return
    # Rename replace dst by src if dst exists
    os.rename(src=new_file, dst=old_file)


# ******************************** UTILITY FUNCTIONS *********************


def dic_to_file(key_order, d, f):
    """
    Writes in the file "f" lines of the form:
        "key_keyword"   "key"
        "value_keyword" "value"
    :param key_order: list of order of the keys to write
    :param d: dictionary
    :param f: file to write
    """
    for key in key_order:
        f.write(key_keyword + "\t" + key)
        f.write(value_keyword + "\t" + d[key])
        f.write("\n")


def parse_file(file):
    """
    Parse the file by keeping the header and by adding the other lines in a dictionnary.
    :param file: a .po object file.
    :return: A dictionary and header lines.
    """
    d = {}
    header = ""
    for line in file:
        if not is_header_line(line):
            dic_from_file(file, d)
            return d, header
        header = header + line;
    return d, header


def dic_from_file(file, d):
    """
        Creates a dictionary containing all pairs "key_keyword" - "value_keyword".
        Ex: msgid "professional"
            msgstr "Professional"
            Will return d = {"professional": "Professional}
        :param file: a .po object file.
        :param d:  a dictionary
        :return: A dictionary
    """
    key = ""
    for line in file:
        if line.startswith(key_keyword):
            key = msg_after_prefix(line, key_keyword)
        elif line.startswith(value_keyword):
            value = msg_after_prefix(line, value_keyword)
            # Add an entry to the dict "d" with key "key" and value "value"
            d[key] = value
        elif line.strip('\n') != "":
            d[key] = d[key] + line

    return d


def header_to_file(header, f):
    f.write(header);


def is_header_line(line):
    """
    A line is header if it is a comment, indicates the mime-type, etc.
    Ex: "Project-Id-Version: PACKAGE VERSION\n"
        "Report-Msgid-Bugs-To: \n"
    :param line: a string representing a line of a ."po" file
    :return: a truth value if the line is header
    """
    prefixes = ["#", '"Project-Id-Version:', '"Report-Msgid-Bugs-To:', '"POT-Creation-Date:',
              '"PO-Revision-Date:', '"Last-Translator:', '"Language-Team:', '"Language:',
              '"MIME-Version:', '"Content-Type:', '"Content-Transfer-Encoding:', 'msgid ""',
                'msgstr ""']

    for prefix in prefixes:
        if line.startswith(prefix):
            return True
    return False


def msg_after_prefix(s, prefix):
    """
    Return a stripped string which is equal to "s" without it's "prefix".
    :param s: a string
    :param prefix: a string which is the prefix of "s"
    :return:
    """
    msg = s.split(prefix)[1]
    msg = msg.strip('\n\r')
    return msg+"\n"

# *********************** SORT AND REPLACE FILE *******************************


def sort_and_replace():
    sort_po_file(dir_path)
    replace_file(dir_path + filename_to_be_sorted, dir_path + filename_sorted)
