import sys
import os
from pdfrw import PdfReader, PdfWriter, PageMerge


def main(source):
    if not os.path.exists('output'):
        os.mkdir('output')

    pages = PdfReader(source).pages
    split_pages = split_all(pages)
    ordered_pages = put_back_cover_last(split_pages)

    digital_pages = [ordered_pages[0]] + pages[1:] + [ordered_pages[-1]]
    write_to_pdf('output/digital.' + os.path.basename(source), digital_pages)


def split_all(pages):
    split_pages = list()
    for page in pages:
        left_page, right_page = split(page)
        split_pages.append(left_page)
        split_pages.append(right_page)
    return split_pages


def split(page):
    x, y, width, height = page.MediaBox
    if width > height:
        for x_pos in (0, 0.5):
            yield PageMerge().add(page, viewrect=(x_pos, 0, 0.5, 1)).render()
    else:
        yield page


def put_back_cover_last(pages):
    back_cover = pages[0]
    ordered_pages = pages[1:] + [back_cover]
    return ordered_pages


def write_to_pdf(destination, pages):
    writer = PdfWriter(destination)
    if os.path.exists(destination):
        os.remove(destination)
    writer.addpages(pages)
    writer.write()


main(sys.argv[1])
