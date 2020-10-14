import sys
import os
from pdfrw import PdfReader, PdfWriter, PageMerge

QUIRE_SIZE = 16


def main(source):
    if not os.path.exists('output'):
        os.mkdir('output')

    pages = PdfReader(source).pages
    split_pages = split_all(pages)
    ordered_pages = put_back_cover_last(split_pages)
    printable_pages = get_printable_quire_pages(ordered_pages)

    digital_pages = [ordered_pages[0]] + pages[1:] + [ordered_pages[-1]]
    write_to_pdf('output/digital.' + os.path.basename(source), digital_pages)

    write_to_pdf('output/print.' + os.path.basename(source), printable_pages)


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


def get_printable_quire_pages(pages):
    number_of_pages = len(pages)

    assert number_of_pages % QUIRE_SIZE == 0

    quire_pages = list()
    for index_quire_sheet in range(int(number_of_pages / QUIRE_SIZE)):
        recto_quire_page, verso_quire_page = get_quire_sheet(index_quire_sheet, pages)

        quire_pages.append(recto_quire_page)
        quire_pages.append(verso_quire_page)

    return quire_pages


##
# recto
# +---+---+---+---+
# |i+7|n-7| n | i |
# +---+---+---+---+
# |i+4|n-4|n-3|i+3|
# +---+---+---+---+
#
# verso
# +---+---+---+---+
# |i+5|n-5|n-2|i+2|
# +---+---+---+---+
# |i+6|n-6|n-1|i+1|
# +---+---+---+---+
#
# the bottom row is rotated 180 degrees
def get_quire_sheet(index_quire_sheet, pages):
    i = int(index_quire_sheet * QUIRE_SIZE / 2)
    n = int(len(pages) - (QUIRE_SIZE / 2 * index_quire_sheet) - 1)

    recto_pages = [
        pages[i + 7],
        pages[n - 7],
        pages[n],
        pages[i],

        pages[i + 4],
        pages[n - 4],
        pages[n - 3],
        pages[i + 3]
    ]

    verso_pages = [
        pages[i + 5],
        pages[n - 5],
        pages[n - 2],
        pages[i + 2],

        pages[i + 6],
        pages[n - 6],
        pages[n - 1],
        pages[i + 1]
    ]

    recto_page = get_single_side_quire_page(recto_pages)
    verso_page = get_single_side_quire_page(verso_pages)

    return recto_page, verso_page


##
# pages
# +---+---+---+---+
# | 0 | 1 | 2 | 3 |
# +---+---+---+---+
# | 4 | 5 | 6 | 7 |
# +---+---+---+---+
def get_single_side_quire_page(pages):
    number_of_pages = len(pages)

    assert number_of_pages == round(QUIRE_SIZE / 2)

    half_index = round(number_of_pages / 2)

    rotate_all(180, pages[half_index:])

    result = PageMerge() + (x for x in pages if x is not None)

    width = result[0].w
    height = result[0].h

    for i in range(half_index):
        dx = i * width
        dy = height
        result[i].x += dx
        result[i].y += dy

    for i in range(half_index, number_of_pages):
        dx = (i - half_index) * width
        dy = 0
        result[i].x += dx
        result[i].y += dy

    return result.render()


def rotate_all(degrees, pages):
    for page in pages:
        rotate(degrees, page)


def rotate(degrees, page):
    page.Rotate = (int(page.inheritable.Rotate or
                       0) + degrees) % 360


def write_to_pdf(destination, pages):
    writer = PdfWriter(destination)
    if os.path.exists(destination):
        os.remove(destination)
    writer.addpages(pages)
    writer.write()


main(sys.argv[1])
