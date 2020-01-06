# -*- coding: utf-8 -*-
import logging
import re
import sys
from pdfminer.pdfdevice import PDFTextDevice
from pdfminer.pdffont import PDFUnicodeNotDefined
from pdfminer.layout import LTContainer
from pdfminer.layout import LTPage
from pdfminer.layout import LTText
from pdfminer.layout import LTLine
from pdfminer.layout import LTRect
from pdfminer.layout import LTCurve
from pdfminer.layout import LTFigure
from pdfminer.layout import LTChar
from pdfminer.layout import LTTextLine
from pdfminer.layout import LTTextBox
from pdfminer.layout import LTTextGroup
from pdfminer.utils import apply_matrix_pt
from pdfminer.utils import mult_matrix
from pdfminer.utils import enc
from pdfminer.utils import bbox2str
import pdfminer.utils as utils

import six  # Python 2+3 compatibility

log = logging.getLogger(__name__)

##  PDFLayoutAnalyzer
##
class PDFLayoutAnalyzer(PDFTextDevice):

    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFTextDevice.__init__(self, rsrcmgr)
        self.pageno = pageno
        self.laparams = laparams
        self._stack = []
        return

    def begin_page(self, page, ctm):
        (x0, y0, x1, y1) = page.mediabox
        (x0, y0) = apply_matrix_pt(ctm, (x0, y0))
        (x1, y1) = apply_matrix_pt(ctm, (x1, y1))
        mediabox = (0, 0, abs(x0-x1), abs(y0-y1))
        self.cur_item = LTPage(self.pageno, mediabox)
        return

    def end_page(self, page):
        assert not self._stack, str(len(self._stack))
        assert isinstance(self.cur_item, LTPage), str(type(self.cur_item))
        if self.laparams is not None:
            self.cur_item.analyze(self.laparams)
        self.pageno += 1
        self.receive_layout(self.cur_item)
        return

    def begin_figure(self, name, bbox, matrix):
        self._stack.append(self.cur_item)
        self.cur_item = LTFigure(name, bbox, mult_matrix(matrix, self.ctm))
        return

    def end_figure(self, _):
        fig = self.cur_item
        assert isinstance(self.cur_item, LTFigure), str(type(self.cur_item))
        self.cur_item = self._stack.pop()
        self.cur_item.add(fig)
        return

    def paint_path(self, gstate, stroke, fill, evenodd, path):
        shape = ''.join(x[0] for x in path)
        if shape == 'ml':
            # horizontal/vertical line
            (_, x0, y0) = path[0]
            (_, x1, y1) = path[1]
            (x0, y0) = apply_matrix_pt(self.ctm, (x0, y0))
            (x1, y1) = apply_matrix_pt(self.ctm, (x1, y1))
            if x0 == x1 or y0 == y1:
                self.cur_item.add(LTLine(gstate.linewidth, (x0, y0), (x1, y1),
                    stroke, fill, evenodd, gstate.scolor, gstate.ncolor))
                return
        if shape == 'mlllh':
            # rectangle
            (_, x0, y0) = path[0]
            (_, x1, y1) = path[1]
            (_, x2, y2) = path[2]
            (_, x3, y3) = path[3]
            (x0, y0) = apply_matrix_pt(self.ctm, (x0, y0))
            (x1, y1) = apply_matrix_pt(self.ctm, (x1, y1))
            (x2, y2) = apply_matrix_pt(self.ctm, (x2, y2))
            (x3, y3) = apply_matrix_pt(self.ctm, (x3, y3))
            if ((x0 == x1 and y1 == y2 and x2 == x3 and y3 == y0) or
                (y0 == y1 and x1 == x2 and y2 == y3 and x3 == x0)):
                self.cur_item.add(LTRect(gstate.linewidth, (x0, y0, x2, y2),
                    stroke, fill, evenodd, gstate.scolor, gstate.ncolor))
                return
        # other shapes
        pts = []
        for p in path:
            for i in range(1, len(p), 2):
                pts.append(apply_matrix_pt(self.ctm, (p[i], p[i+1])))
        self.cur_item.add(LTCurve(gstate.linewidth, pts, stroke, fill,
            evenodd, gstate.scolor, gstate.ncolor))
        return

    def render_char(self, matrix, font, fontsize, scaling, rise, cid, ncs, graphicstate):
        try:
            text = font.to_unichr(cid)
            assert isinstance(text, six.text_type), str(type(text))
        except PDFUnicodeNotDefined:
            text = self.handle_undefined_char(font, cid)
        textwidth = font.char_width(cid)
        textdisp = font.char_disp(cid)
        item = LTChar(matrix, font, fontsize, scaling, rise, text, textwidth, textdisp, ncs, graphicstate)
        self.cur_item.add(item)
        return item.adv

    def handle_undefined_char(self, font, cid):
        log.info('undefined: %r, %r', font, cid)
        return '(cid:%d)' % cid

    def receive_layout(self, ltpage):
        return

##  PDFConverter
##
class PDFConverter(PDFLayoutAnalyzer):

    def __init__(self, rsrcmgr, outfp, codec='utf-8', pageno=1, laparams=None):
        PDFLayoutAnalyzer.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        self.outfp = outfp
        self.codec = codec
        if hasattr(self.outfp, 'mode'):
            if 'b' in self.outfp.mode:
                self.outfp_binary = True
            else:
                self.outfp_binary = False
        else:
            import io
            if isinstance(self.outfp, io.BytesIO):
                self.outfp_binary = True
            elif isinstance(self.outfp, io.StringIO):
                self.outfp_binary = False
            else:
                try:
                    self.outfp.write(u"é")
                    self.outfp_binary = False
                except TypeError:
                    self.outfp_binary = True
        return

##  TextConverter
##
class TextConverter(PDFConverter):

    def __init__(self, rsrcmgr, outfp, codec='utf-8', pageno=1, laparams=None,
                showpageno=False):
        PDFConverter.__init__(self, rsrcmgr, outfp, codec=codec, pageno=pageno, laparams=laparams)
        self.showpageno = showpageno
        return

    def write_text(self, text):
        text = utils.compatible_encode_method(text, self.codec, 'ignore')
        if six.PY3 and self.outfp_binary:
            text = text.encode()
        self.outfp.write(text)
        return

    def receive_layout(self, ltpage):
        def render(item):
            if isinstance(item, LTContainer):
                for child in item:
                    render(child)
            elif isinstance(item, LTText):
                self.write_text(item.get_text())
            if isinstance(item, LTTextBox):
                self.write_text('\n')
        if self.showpageno:
            self.write_text('Page %s\n' % ltpage.pageid)
        render(ltpage)
        self.write_text('\f')
        return

    def paint_path(self, gstate, stroke, fill, evenodd, path):
        return

##  HTMLConverter
##
class HTMLConverter(PDFConverter):

    RECT_COLORS = {
        #'char': 'green',
        'figure': 'yellow',
        'textline': 'magenta',
        'textbox': 'cyan',
        'textgroup': 'red',
        'curve': 'black',
        'page': 'gray',
    }

    TEXT_COLORS = {
        'textbox': 'blue',
        'char': 'black',
    }

    def __init__(self, rsrcmgr, outfp, codec='utf-8', pageno=1, laparams=None,
                scale=1, fontscale=1.0, layoutmode='normal', showpageno=True,
                pagemargin=50, debug=0,
                rect_colors={'curve': 'black', 'page': 'gray'},
                text_colors={'char': 'black'}):
        PDFConverter.__init__(self, rsrcmgr, outfp, codec=codec, pageno=pageno, laparams=laparams)
        self.scale = scale
        self.fontscale = fontscale
        self.layoutmode = layoutmode
        self.showpageno = showpageno
        self.pagemargin = pagemargin
        self.rect_colors = rect_colors
        self.text_colors = text_colors
        if debug:
            self.rect_colors.update(self.RECT_COLORS)
            self.text_colors.update(self.TEXT_COLORS)
        self._yoffset = self.pagemargin
        self._font = None
        self._fontstack = []
        self.write_header()
        return

    def write(self, text):
        if self.codec:
            text = text.encode(self.codec)
        if sys.version_info < (3, 0):
            text = str(text)
        self.outfp.write(text)
        return

    def write_header(self):
        self.write('<!doctype html>\n<html>\n\t<head>\n')
        if self.codec:
            self.write('\t\t<meta http-equiv="Content-Type" content="text/html; charset=%s">\n' % self.codec)
        else:
            self.write('\t\t<meta http-equiv="Content-Type" content="text/html">\n')
        self.write('\t</head>\n\t<body>\n')
        return

    def write_footer(self):
        self.write('\t\t<div style="position:absolute; top:0px;">Page: %s</div>\n' %
                ', '.join('<a href="#%s">%s</a>' % (i, i) for i in range(1, self.pageno)))
        self.write('\t</body>\n</html>\n')
        return

    def write_text(self, text):
        self.write(enc(text, None))
        return

    def place_rect(self, color, borderwidth, x, y, w, h):
        color = self.rect_colors.get(color)
        if color is not None:
            self.write('\t\t<span style="position:absolute; border: %s %dpx solid; '
                        'left:%dpx; top:%dpx; width:%dpx; height:%dpx;"></span>\n' %
                        (color, borderwidth,
                        x*self.scale, (self._yoffset-y)*self.scale,
                        w*self.scale, h*self.scale))
        return

    def place_border(self, color, borderwidth, item):
        self.place_rect(color, borderwidth, item.x0, item.y1, item.width, item.height)
        return

    def place_text(self, color, text, x, y, size):
        color = self.text_colors.get(color)
        if color is not None:
            self.write('\t\t<span style="position:absolute; color:%s; left:%dpx; top:%dpx; font-size:%dpx;">' %
                       (color, x*self.scale, (self._yoffset-y)*self.scale, size*self.scale*self.fontscale))
            self.write_text(text)
            self.write('\t\t</span>\n')
        return

    def begin_div(self, color, borderwidth, x, y, w, h, writing_mode=False):
        self._fontstack.append(self._font)
        self._font = None
        self.write('\t\t<div style="position:absolute; border: %s %dpx solid; writing-mode:%s; '
                    'left:%dpx; top:%dpx;">' % (color, borderwidth, writing_mode,
                                                                    x*self.scale, (self._yoffset-y)*self.scale))
        return

    def end_div(self, color):
        if self._font is not None:
            self.write('</span>\n')
        self._font = self._fontstack.pop()
        self.write('\t\t</div>\n')
        return

    def put_text(self, text, fontname, fontsize):
        font = (fontname, fontsize)

        def Enco(fontname):
            fname=''
            for i in range(len(fontname)):
                if fontname[i] == '-':
                    fname = fontname[:i]
                    break
                if i == len(fontname) - 1:
                    fname = fontname
            for i in range(len(fname)):
                if i == len(fontname) - 1:
                    fname = fontname
                elif 'Italic' in fname:
                    fname = fname.replace('Italic', '')
                elif 'Bold' in fname:
                    fname = fname.replace('Bold', '')
            import re
            # return re.sub(r"(\w)([A-Z])", r"\1 \2", fname)
            return fname

        fname = Enco(fontname)   
        if 'Italic' in fontname:
            fstyle = 'italic'
        else:
            fstyle = 'normal'
        if 'Bold' in fontname:
            fweight= 'bold'
        else:
            fweight = 'normal'

        if font != self._font:
            if self._font is not None:
                self.write('</span>')
            self.write('\n\t\t\t<span style="font-style: %s; font-weight: %s; font-family: %s; font-size:%dpx">\n\t\t\t\t' %
                       (fstyle, fweight, fname, fontsize * self.scale * self.fontscale))
            self._font = font
        self.write_text(text)
        return

    def put_newline(self):
        self.write('\t\t\t<br>')
        return

    def receive_layout(self, ltpage):
        def show_group(item):
            if isinstance(item, LTTextGroup):
                self.place_border('textgroup', 1, item)
                for child in item:
                    show_group(child)
            return

        def render(item):
            if isinstance(item, LTPage):
                self._yoffset += item.y1
                self.place_border('page', 1, item)
                if self.showpageno:
                    self.write('\t\t<div style="position:absolute; top:%dpx;">' %
                            ((self._yoffset-item.y1)*self.scale))
                    self.write('\n\t\t\t<a name="%s">Page %s</a>\n\t\t</div>\n' % (item.pageid, item.pageid))
                for child in item:
                    render(child)
                if item.groups is not None:
                    for group in item.groups:
                        show_group(group)
            elif isinstance(item, LTCurve):
                self.place_border('curve', 1, item)
            elif isinstance(item, LTFigure):
                self.begin_div('figure', 1, item.x0, item.y1, item.width, item.height)
                for child in item:
                    render(child)
                self.end_div('figure')
            else:
                if self.layoutmode == 'exact':
                    if isinstance(item, LTTextLine):
                        self.place_border('textline', 1, item)
                        for child in item:
                            render(child)
                    elif isinstance(item, LTTextBox):
                        self.place_border('textbox', 1, item)
                        self.place_text('textbox', str(item.index+1), item.x0, item.y1, 20)
                        for child in item:
                            render(child)
                    elif isinstance(item, LTChar):
                        self.place_border('char', 1, item)
                        self.place_text('char', item.get_text(), item.x0, item.y1, item.size)
                else:
                    if isinstance(item, LTTextLine):
                        for child in item:
                            render(child)
                        if self.layoutmode != 'loose':
                            self.put_newline()
                    elif isinstance(item, LTTextBox):
                        self.begin_div('textbox', 1, item.x0, item.y1, item.width, item.height,
                                    item.get_writing_mode())
                        for child in item:
                            render(child)
                        self.end_div('textbox')
                    elif isinstance(item, LTChar):
                        self.put_text(item.get_text(), item.fontname, item.size)
                    elif isinstance(item, LTText):
                        self.write_text(item.get_text())
            return
        render(ltpage)
        self._yoffset += self.pagemargin
        return

    def close(self):
        self.write_footer()
        return