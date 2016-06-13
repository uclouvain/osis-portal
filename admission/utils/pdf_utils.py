##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
"""
Utility files to manipulate pdf
"""
import os
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.utils.translation import ugettext_lazy as _
from io import BytesIO
from reportlab.lib import utils
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4 as A4
from django.conf import settings
from reportlab.lib import colors

from PyPDF2 import PdfFileMerger,  PdfFileReader, PdfFileWriter
from math import *


PAGE_SIZE = A4
MARGIN_SIZE = 15 * mm
BOTTOM_MARGIN = 18
TOP_MARGIN = 85
COLS_WIDTH = [165*mm, 15*mm]
FIRST_MERGE_PAGE = 2
MAX_NUMBER_OF_LINE_PER_TOC_PAGE = 38
ALLOWED_EXTENSIONS = ['jpg', 'jpge', 'png', 'gif']


def convert_image_to_pdf(image_file, document_type):
    filename = "%s.pdf" % document_type
    if allowed_file(image_file):
        doc = SimpleDocTemplate(filename,
                                pagesize=PAGE_SIZE,
                                rightMargin=MARGIN_SIZE,
                                leftMargin=MARGIN_SIZE,
                                topMargin=TOP_MARGIN,
                                bottomMargin=BOTTOM_MARGIN)

        image = get_image(image_file)
        content = [image]
        doc.build(content)

    return HttpResponseRedirect(reverse('home'))


def get_image(path):
    """
    Get the image ready.
    Change the dimensions if needted to fit on the page
    :param path:
    :return:
    """
    img = utils.ImageReader(path)
    xsize, ysize = img.getSize()
    width, height = A4
    width = width - (MARGIN_SIZE * 2)
    height = height - (BOTTOM_MARGIN + TOP_MARGIN)

    if xsize > ysize:  # deal with cases were xsize is bigger than ysize
        if xsize > width:
            xsize_corrected = width
            ysize_corrected = int(ysize*(xsize_corrected/xsize))
            return Image(path, width=xsize_corrected, height=ysize_corrected)
    else:  # deal with cases where ysize is bigger than xsize
        if ysize > height:
            ysize_corrected = height
            a = ysize_corrected/ysize
            xsize_corrected = xsize * a
            return Image(path, width=xsize_corrected, height=ysize_corrected)
    return Image(path)


def allowed_file(filename):
    filename = filename.lower()
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def merge_pdf():
    pdf_list = ["pdf1.pdf", "pdf2.pdf"]
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer,
                            pagesize=PAGE_SIZE,
                            rightMargin=MARGIN_SIZE,
                            leftMargin=MARGIN_SIZE,
                            topMargin=85,
                            bottomMargin=18)

    content = []

    if not pdf_list or len(pdf_list) < 2:
        exit("Please enter at least two pdfs for merging!")

    # Prepare the table of contents
    content.append(Paragraph('<br/><br/>', ParagraphStyle("Normal")))
    content.append(build_toc(pdf_list))
    doc.build(content, onFirstPage=add_header_footer)

    merger = PdfFileMerger()
    merger.setPageMode('/UseOC')
    merger.append(buffer)
    num_page = 1
    no_page = 1

    for filename in pdf_list:
        input = PdfFileReader(open(filename, 'rb'))
        number_of_page = input.getNumPages()
        lien = filename
        merger.append(input, bookmark=lien, import_bookmarks=False)
        num_page = num_page+1
        no_page = no_page + number_of_page

    output = open("output.pdf", "wb")
    merger.write(output)
    output.close()

    return HttpResponseRedirect(reverse('home'))


def build_toc(pdf_list):
    no_page = FIRST_MERGE_PAGE
    # max 38 lines in the toc on one page
    if len(pdf_list) > MAX_NUMBER_OF_LINE_PER_TOC_PAGE:
        no_page = ceil(len(pdf_list)/MAX_NUMBER_OF_LINE_PER_TOC_PAGE)+1
    data = [[_('table_contents')]]
    for filename in pdf_list:
        input = PdfFileReader(open(filename, 'rb'))
        number_of_page = input.getNumPages()
        data.append([filename, no_page])
        no_page = no_page + number_of_page

    t = Table(data, COLS_WIDTH, repeatRows=1)
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                           ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    return t


def add_header_footer(canvas, doc):
    styles = getSampleStyleSheet()
    # Save the state of our canvas so we can draw on it
    canvas.saveState()
    # Header
    header_building(canvas, doc, styles)
    # Release the canvas
    canvas.restoreState()


def header_building(canvas, doc, styles):
    a = Image(settings.LOGO_INSTITUTION_URL, width=15*mm, height=20*mm)
    p = Paragraph('''<para align=center>
                        <font size=16>%s</font>
                    </para>''' % (_('documents')), styles["Normal"])

    data_header = [[a, '%s' % _('ucl_denom_location'), p], ]

    t_header = Table(data_header, [30*mm, 100*mm, 50*mm])

    t_header.setStyle(TableStyle([]))

    w, h = t_header.wrap(doc.width, doc.topMargin)
    t_header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)




