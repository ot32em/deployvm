import os
import errno

''' config part '''
def load_variables(filename):
    vars = {}
    execfile( filename, vars)
    del vars['__builtins__']
    return vars

def prepend( prefix, walking_seq ):
    if isinstance(walking_seq, dict):
        result = dict()
        for key in walking_seq:
            result[key] = ''.join( [prefix, walking_seq[key]] )
        return result
    elif isinstance(walking_seq, list) or isinstance(walking_seq, tuple):
        result = list()
        for v in walking_seq:
            result.append( ''.join([prefix, v]))
        return result
    raise TypeError('helper.prepend(prefix, walking_seq): walking_seq need be dict, list, or tuple. ')

def concat_path(*args):
    if len(args) < 2:
        raise AttributeError('concat_path(*args) need at least 2 arguments.')

    string = ''
    for token in args:
        if string:
            if token.startswith('/'):
                raise AttributeError('helper.concat_path(*args) only first argument can have leading slash.')
            if not string.endswith('/'):
                string = ''.join([string, '/', token])
            else:
                string = ''.join([string, token])
        else:
            string = token
    return string


def mkdir_p(path):
    '''
    @ref http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    '''
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
=======
import os
import errno

''' config part '''
def load_variables(filename):
    vars = {}
    execfile( filename, vars)
    del vars['__builtins__']
    return vars

def prepend( prefix, walking_seq ):
    if isinstance(walking_seq, dict):
        result = dict()
        for key in walking_seq:
            result[key] = ''.join( [prefix, walking_seq[key]] )
        return result
    elif isinstance(walking_seq, list) or isinstance(walking_seq, tuple):
        result = list()
        for v in walking_seq:
            result.append( ''.join([prefix, v]))
        return result
    raise TypeError('helper.prepend(prefix, walking_seq): walking_seq need be dict, list, or tuple. ')

def concat_path(*args):
    if len(args) < 2:
        raise AttributeError('concat_path(*args) need at least 2 arguments.')

    string = ''
    for token in args:
        if string:
            if token.startswith('/'):
                raise AttributeError('helper.concat_path(*args) only first argument can have leading slash.')
            if not string.endswith('/'):
                string = ''.join([string, '/', token])
            else:
                string = ''.join([string, token])
        else:
            string = token
    return string


def mkdir_p(path):
    '''
    @ref http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    '''
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise IOError("Can not make the path: %s" % path)
