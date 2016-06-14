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
import io

PAGE_SIZE = A4
MARGIN_SIZE = 15 * mm
BOTTOM_MARGIN = 18
TOP_MARGIN = 85
COLS_WIDTH = [165*mm, 15*mm]
FIRST_MERGE_PAGE = 2
MAX_NUMBER_OF_LINE_PER_TOC_PAGE = 38
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']


def convert_image_to_pdf(image_file, filename):
    """
    :param image_file: path to image file.  (expected : gif, jpg, jpeg, png)
    :param filename: filename with pdf extention (ex : test2.pdf)
    :return:
    """
    if filename.lower().endswith('.pdf') and allowed_file(image_file) and os.path.isfile(image_file):
        doc = SimpleDocTemplate(filename,
                                pagesize=PAGE_SIZE,
                                rightMargin=MARGIN_SIZE,
                                leftMargin=MARGIN_SIZE,
                                topMargin=TOP_MARGIN,
                                bottomMargin=BOTTOM_MARGIN)

        image = resize_image(image_file)
        if image:
            content = [image]
            doc.build(content)

            return doc

    return None


def resize_image(image_file):
    """
    Get the image ready.
    Change the dimensions if needed to fit on the page
    :param image_file:
    :return:
    """
    if os.path.isfile(image_file):
        try:
            img = utils.ImageReader(image_file)
            xsize, ysize = img.getSize()
            width, height = A4
            width = width - (MARGIN_SIZE * 2)
            height = height - (BOTTOM_MARGIN + TOP_MARGIN)

            if xsize > ysize:  # deal with cases were xsize is bigger than ysize
                if xsize > width:
                    xsize_corrected = width
                    ysize_corrected = int(ysize*(xsize_corrected/xsize))
                    return Image(image_file, width=xsize_corrected, height=ysize_corrected)
            else:  # deal with cases where ysize is bigger than xsize
                if ysize > height:
                    ysize_corrected = height
                    a = ysize_corrected/ysize
                    xsize_corrected = xsize * a
                    return Image(image_file, width=xsize_corrected, height=ysize_corrected)
            return Image(image_file)
        except OSError:
            return None
    return None


def allowed_file(filename):
    filename = filename.lower()
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_pdf_with_cover(document_list, pdf_files_to_merge, noma):
    pdf_cover = create_cover_sheet(document_list, noma)
    pdf_files = []
    if pdf_cover:
        pdf_files.append(pdf_cover)
    if pdf_files_to_merge and len(pdf_files_to_merge) > 0:
        pdf_files.extend(pdf_files_to_merge)
    if len(pdf_files) > 0:
        return merge_pdfs(pdf_files)
    return None


def create_cover_sheet(document_list, noma):
    cover_file_name = "cover.pdf"
    doc = SimpleDocTemplate(cover_file_name,
                            pagesize=PAGE_SIZE,
                            rightMargin=MARGIN_SIZE,
                            leftMargin=MARGIN_SIZE,
                            topMargin=85,
                            bottomMargin=18)
    content = []
    # Prepare the table of contents
    if noma:
        content.append(Paragraph('<br/><br/>', ParagraphStyle("Normal")))
        content.append(Paragraph('%s : %s' % (_('student'), noma), ParagraphStyle("Normal")))
    if document_list and len(document_list) > 0:
        content.append(Paragraph('<br/><br/>', ParagraphStyle("Normal")))
        content = build_toc(content, document_list)
    if len(content) > 0:
        doc.build(content, onFirstPage=add_header)
        return cover_file_name
    return None


def merge_pdfs(pdf_files):
    filename = "%s.pdf" % _('scores_sheet')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    if not pdf_files or len(pdf_files) == 0:
        return None

    merger = PdfFileMerger()
    merger.setPageMode('/UseOC')

    merged_file = 0
    for filename in pdf_files:
        if filename.lower().endswith('.pdf') and os.path.isfile(filename):
            input = PdfFileReader(open(filename, 'rb'))
            merger.append(input, bookmark=filename, import_bookmarks=False)
            merged_file = merged_file + 1

    if merged_file > 0:
        output = open("output.pdf", "wb")
        merger.write(output)
        output.close()
        return output
    return None


def build_toc(content, document_list):
    if document_list:
        content.append(Paragraph('<br/>', ParagraphStyle("Normal")))
        for document in document_list:
            content.append(Paragraph('%s' % document, ParagraphStyle("Normal")))
    return content


def add_header(canvas, doc):
    styles = getSampleStyleSheet()
    canvas.saveState()
    header_building(canvas, doc, styles)
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




