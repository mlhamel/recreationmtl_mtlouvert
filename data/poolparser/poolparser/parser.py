import StringIO
import BeautifulSoup
import csv

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.cmapdb import CMapDB

from pdfminer.layout import LAParams

from pdfminer.converter import HTMLConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, process_pdf

codec = 'utf-8'
laparams = LAParams()
outfile = None
outtype = None
outdir = None
pagenos = set((0,))
maxpages = 1
password = ''
caching = True
layoutmode = 'normal'
scale = 1

X_COLUMN_2 = '167'
X_COLUMN_3_1 = '284'
X_COLUMN_3_2 = '288'
X_COLUMN_4 = '362'

class PoolParser(object):

    def __init__(self, filename, debug=False):
        self.filename = filename
        self.outfp = StringIO.StringIO()
        self.content = None
        self.fp = None
        self.rsrcmgr = None
        self.device = None

        PDFDocument.debug = debug
        PDFParser.debug = debug
        CMapDB.debug = debug
        PDFResourceManager.debug = debug
        PDFPageInterpreter.debug = debug
        PDFDevice.debug = debug

    def __enter__(self):
        self.__call__()
        return self.content

    def __exit__(self, type, value, traceback):
        self.fp.close()
        return isinstance(value, TypeError)

    def __len__(self):
        return len(self.column2)
            
    def __call__(self):
        self.execute()
        for x in self.column2:
            pool = self.merge(x, self.column3, self.column4)
            if len(pool) >= 3 and len(pool) <= 4:
                yield pool        

    def execute(self):
        self.content = self.parse()

    def parse(self):
        self.fp = open(self.filename, 'rb')
        self.rsrcmgr = PDFResourceManager(caching=caching)        
        self.device = HTMLConverter(self.rsrcmgr, self.outfp, codec=codec, scale=scale,
                               layoutmode=layoutmode, laparams=laparams, outdir=outdir)
        process_pdf(self.rsrcmgr, self.device, self.fp, pagenos, maxpages=maxpages, password=password,
                    caching=caching, check_extractable=True)
        self.outfp.seek(0)
        return BeautifulSoup.BeautifulSoup("".join(self.outfp.readlines()))
        

    @property
    def column_list(self):
        return [x for x in self.content.findAll('div')]

    @property
    def column2(self):
        return [x for x in self.content.findAll('div') \
                    if X_COLUMN_2 in dict(x.attrs).get('style', '')]

    @property
    def column3(self):
        return [x for x in self.content.findAll('div') \
                    if X_COLUMN_3_1 in dict(x.attrs).get('style', '') \
                    or X_COLUMN_3_2 in dict(x.attrs).get('style', '')]

    @property
    def column4(self):
        return [x for x in self.content.findAll('div') \
                    if X_COLUMN_4 in dict(x.attrs).get('style', '')]

    def top(self, source):
        return dict([x.strip().split(":") \
                         for x in dict(source.attrs).get('style', '').split(';') \
                         if x]).get('top','')

    def merge(self, source, *lsts):
        elem = [source.text.encode('utf-8')]
        source_top = self.top(source) 
        if source_top != "":
            for lst in lsts:
                for x in lst:                
                    x_top = self.top(x)
                    if source_top == x_top:
                        elem.append(x.text.encode('utf-8'))
        return elem


def pinfo():
    """extract informations from the pdf print it on the std"""
    import argparse
    parser = argparse.ArgumentParser(description='Montreal pools informations')
    parser.add_argument('source', type=str)
    parser.add_argument('output', type=str, nargs="?")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--list', action='store_true')
    args = parser.parse_args()

    output_filename = getattr(args, 'destination', None)
    output_delimiter = ','
    output_mode = 'wb'
    output = None

    use_csv = output_filename is not None

    parser = PoolParser(args.source, args.debug)
    if args.list:
        parser.execute()
        print parser.column_list
    else:
        try:
            if use_csv:
                output = open(output_filename, output_mode)
                poolWriter = csv.writer(output, delimiter=output_delimiter)
            for line in parser():
                if use_csv:
                    poolWriter.writerow(line)
                else:
                    print(line)
        finally:
            if output is not None:
                output.close()
