import sys
import os
from pdfrw import PdfReader, PdfWriter, PageMerge


def main(source):
    if not os.path.exists('output'):
        os.mkdir('output')

    pages = PdfReader(source).pages

    write_to_pdf('output/digital.' + os.path.basename(source), pages)


def write_to_pdf(destination, pages):
    writer = PdfWriter(destination)
    if os.path.exists(destination):
        os.remove(destination)
    writer.addpages(pages)
    writer.write()


main(sys.argv[1])
