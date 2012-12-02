import pygments
import pygments.formatters
import pygments.lexers


class CodeHtmlFormatter(pygments.formatters.HtmlFormatter):
    def __init__(self, lineno_class_func=None,  **kwargs):
        super(CodeHtmlFormatter, self).__init__(**kwargs)
        self.lineno_class_func = lineno_class_func

    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        lineno = 0
        for i, t in source:
            if i == 1:
                lineno += 1
                yield 0, '<div class="line %s">' % self.lineno_class_func(lineno)

            yield i, t

            if i == 1:
                yield 0, '</div>'

def format_code(filename, code, func):
    try:
        lexer = pygments.lexers.get_lexer_for_filename(filename)
    except pygments.util.ClassNotFound:
        try:
            lexer = pygments.lexers.guess_lexer(code)
        except pygments.util.ClassNotFound:
            return '<pre>' + code + '</pre>'
        

    formatter = CodeHtmlFormatter(linenos='inline', lineno_class_func=func)
    return pygments.highlight(code, lexer, formatter)
