from .core import PageOne


def get(page, **kw):
    """
    simplified interface
    """
    kw['page'] = page
    return PageOne(**kw).links(**kw)
