import pygments
import pygments.formatters
import pygments.lexers


class CodeHtmlFormatter(pygments.formatters.HtmlFormatter):
    def __init__(self, highlight_data, blank_data,  **kwargs):
        super(CodeHtmlFormatter, self).__init__(**kwargs)
        self.highlight_data = highlight_data
        self.blank_data = blank_data

    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def lineno_cls(self, lineno):
        return 'highlight' if lineno in self.highlight_data else 'reg'

    def _wrap_code(self, source):
        lineno = 1
        for i, t in source:
            if i == 1:
                for _ in xrange(self.blank_data[lineno]):
                    yield 0, '<div class="blank">&nbsp;</div>'
                yield 0, '<div class="line %s">' % self.lineno_cls(lineno)

            yield i, t

            if i == 1:
                yield 0, '</div>'
                lineno += 1

def format_code(filename, code, highlight_data, blank_data):
    try:
        lexer = pygments.lexers.get_lexer_for_filename(filename)
    except pygments.util.ClassNotFound:
        try:
            lexer = pygments.lexers.guess_lexer(code)
        except pygments.util.ClassNotFound:
            return '<pre>' + code + '</pre>'
        

    formatter = CodeHtmlFormatter(highlight_data, blank_data, linenos='inline')
    return pygments.highlight(code, lexer, formatter)
