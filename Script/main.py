from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
import os

from pdfconverter import TextConverter, HTMLConverter

def convert_pdf(path, format='text', codec='utf-8', password=''):
    rsrcmgr = PDFResourceManager() # Resources to be reused
    retstr = BytesIO()
    laparams = LAParams() # Use for layout analysis
    if format == 'text':
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'html':
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    else:
        raise ValueError('Please provide format, either text or html!')
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device) # Processor for the content of a page
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=0, password=password,caching=True, check_extractable=True):
        interpreter.process_page(page)
    
    text = retstr.getvalue().decode()
    fp.close()
    device.close()
    retstr.close()
    return text

def convertMultiple(pdfDir):
    if pdfDir == "":
        pdfDir = os.getcwd() + "\\"

    for pdf in os.listdir(pdfDir):
        fileExtension = pdf.split(".")[-1]

        if fileExtension == "pdf":
            pdfFilename = pdfDir + pdf 
            str = convert_pdf(pdfFilename, format='text')
            txtDir = pdfFilename + '.txt'
            txtDir = txtDir.replace('.pdf', '')
            if os.path.exists(txtDir):
                os.remove(txtDir)
            textFile = open(txtDir, "a")
            textFile.write(str)
            textFile.close()

            str = convert_pdf(pdfFilename, format='html')
            htmlDir = pdfFilename + '.html'
            htmlDir = htmlDir.replace('.pdf', '')
            if os.path.exists(htmlDir):
                os.remove(htmlDir)
            htmlFile = open(htmlDir, "a")
            htmlFile.write(str)
            htmlFile.write('\t</body>\n</html>')
            htmlFile.close()

def convertPDF(pdfName):
    str = convert_pdf(pdfName, format='text')
    txtDir = pdfName + '.txt'
    txtDir = txtDir.replace('.pdf', '')
    if os.path.exists(txtDir):
        os.remove(txtDir)
    textFile = open(txtDir, "a")
    textFile.write(str)
    textFile.close()

    str = convert_pdf(pdfName, format='html')
    htmlDir = pdfName + '.html'
    htmlDir = htmlDir.replace('.pdf', '')
    if os.path.exists(htmlDir):
        os.remove(htmlDir)
    htmlFile = open(htmlDir, "a")
    htmlFile.write(str)
    htmlFile.write('\t</body>\n</html>')
    htmlFile.close()
