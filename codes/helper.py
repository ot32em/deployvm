import os
''' config part '''
def load_variables( filename ):
    vars = {}
    execfile( filename, vars)
    del vars['__builtins__']
    return vars



def prepend( prefix, walking_dict ):
    dest_dict = dict()
    for key in walking_dict:
        dest_dict[key] = prefix + walking_dict[key]
    return dest_dict



