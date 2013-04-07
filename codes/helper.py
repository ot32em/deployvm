import os
''' config part '''
def load_config( config_filename ):
    config={}
    if not os.path.exists( config_filename ) :
        raise ConfigFileNotFoundError()
    execfile(config_filename, config)
    del config['__builtins__']
    validate_config( config ) 
    config['prototype_uris'] = prepend( config['repository_prototype_url'], config['prototype_filenames'] )
    config['kernel_uris'] = prepend( config['repository_kernel_url'], config['kernel_filenames'] )

    config['os_types'] = config['prototype_filenames'].keys()
    config['kernel_types'] = config['kernel_filenames'].keys()

    return config

def load_test_config( test_config_filename, original_config_filename ):
    ''' overwrite original config with some test data '''
    c = load_config( original_config_filename )
    t = {}
    execfile( test_config_filename, t )
    del t['__builtins__']
    c.update(t)
    return c
    

def prepend( prefix, walking_dict ):
    dest_dict = dict()
    for key in walking_dict:
        dest_dict[key] = prefix + walking_dict[key]
    return dest_dict

def validate_config(config):
    required_keys = ['download_method', 'deploy_root','deploy_user_data_dir', 'download_dir', 'repository_url','repository_prototype_url', 'repository_kernel_url', 'prototype_filenames','kernel_filenames']
    for key in required_keys :
        if not config.has_key( key ) :
            raise PareConfigError("key: %s is required..." % key )


    

class ConfigError(Exception):
    pass
class ConfigFileNotFoundError(ConfigError):
    pass
class ParseConfigError(ConfigError):
    pass


