import os
import sys
import yaml # a.k.a. PyYAML
import shutil
import subprocess

from common import SCRIPTS_DIREC

def all_valid(*cmds):
    return all(shutil.which(cmd) for cmd in cmds)

def validate_dependencies():
    error_count = 0
    print('Validating necessary binaries...')
    if not all_valid('apertium', 'apertium-destxt', 'apertium-pretransfer'):
        error_count += 1
        print("Incorrectly configured (or absent) 'apertium'.")
    if not all_valid('multitrans', 'lrx-comp'):
        error_count += 1
        print("Incorrectly configured (or absent) 'apertium-lex-tools'.")
    if not all_valid('python3'):
        error_count += 1
        print("Incorrectly configured (or absent) 'python3'.")

    scripts = ['ngrams-to-rules.py',
               'biltrans-count-patterns-ngrams.py',
               'ngram-pruning-frac.py',
               'extract-alig-lrx.py',
               'biltrans-extract-frac-freq.py']
    scripts_direc_contents = os.listdir(SCRIPTS_DIREC)
    for script in scripts:
        if script not in scripts_direc_contents:
            error_count += 1
            print('Missing script {}. Did you forget to edit common.py?'.format(script))

    return error_count == 0

def read_yaml(yaml_filepath):
    try:
        with open(yaml_filepath, 'r') as f:
            config = yaml.load(f)
    except IOError as e:
        print('Error while opening as yaml file;')
        print(e)
        sys.exit()
    else:
        return config

def craft_makefile(config):
    with open('Makefile', 'w') as f, open('outro', 'r') as o:
        f.write('CORPUS={}\n'.format(config["corpus_name"]))
        f.write('DIR={}\n'.format(config["direction"]))
        f.write('DATA={}\n'.format(config["path_to_pair"]))
        f.write('AUTOBIL={}\n'.format(config["bilingual_dict"]))
        f.write('SCRIPTS={}\n'.format(SCRIPTS_DIREC))
        f.write('MODEL={}\n'.format(config["binary_model"]))
        f.write(o.read())

def validate_yaml(config):
    attrs = ['path_to_pair', 'binary_model', 'bilingual_dict', 'direction', 'corpus_name']
    try:
        for attr in attrs:
            config[attr]
    except KeyError as ke:
        print('Missing necessary configuration info:', ke)
        sys.exit()
    except TypeError:
        print('Malformed yaml file; check input specification.')
        sys.exit()

if __name__ == '__main__':
    # Validate user input.
    if len(sys.argv) != 2:
        print('Usage: python3 monolearner.py <yaml config file>')
        sys.exit()

    # Ensure necessary dependencies are installed.
    if not validate_dependencies():
        print('Please fix these problems before trying again.')
        sys.exit()

    # Validate yaml file.
    yaml_filepath = sys.argv[1]
    print('Reading config from %s...' % yaml_filepath, end=' ')
    config = read_yaml(yaml_filepath)
    print('Success!')

    # Validate yaml format.
    print('Validating format of %s...' % yaml_filepath, end=' ')
    validate_yaml(config)
    print('Success!')
    
    # Ensure that a path to the target data directory exists.
    print('Checking for valid data path...', end=' ')
    data_path = os.path.join(os.getcwd(), 'data')
    if not os.path.isdir(data_path):
        print('Not found.\nCreating data directory...', end=' ')
        os.mkdir(data_path)
        print('Success!')
    else:
        print('Found!')

    print('Generating Makefile...', end=' ')
    craft_makefile(config)
    print('Success!')

    print('Training...', end=' ')
    subprocess.call(['make'])
    print('Success!')
