from distutils.core import setup
import py2exe
import pygame
import os
import sys
import glob
 
sys.argv.append('py2exe')

# The filename of the script you use to start your program.
target_file = 'pirates.py'
 
# The root directory containing your assets, libraries, etc.
assets_dir = '.\\'
 
# Filetypes not to be included in the above.
excluded_file_types = ['py','pyc','project','pydevproject', 'bat']

PYGAMEDIR = os.path.split(pygame.base.__file__)[0]
 
SDL_DLLS = glob.glob(os.path.join(PYGAMEDIR,'*.dll'))
 
if os.path.exists('dist/'): shutil.rmtree('dist/')
 
extra_files = [ 
                ("data",glob.glob(os.path.join('data','*.dat'))),
                ("gfx",glob.glob(os.path.join('gfx','*.jpg'))),
                ("gfx",glob.glob(os.path.join('gfx','*.png'))),
                ("fonts",glob.glob(os.path.join('fonts','*.ttf'))),
                ("music",glob.glob(os.path.join('music','*.ogg'))),
                ("snd",glob.glob(os.path.join('snd','*.wav')))
              ]

 
def get_data_files(base_dir, target_dir, list=[]):
    """
    " * get_data_files
    " *    base_dir:    The full path to the current working directory.
    " *    target_dir:  The directory of assets to include.
    " *    list:        Current list of assets. Used for recursion.
    " *
    " *    returns:     A list of relative and full path pairs. This is 
    " *                 specified by distutils.
    """
    for file in os.listdir(base_dir + target_dir):
 
        full_path = base_dir + target_dir + file
        if os.path.isdir(full_path):
            get_data_files(base_dir, target_dir + file + '\\', list)
        elif os.path.isfile(full_path):
            if (len(file.split('.')) == 2 and file.split('.')[1] not in excluded_file_types):
                list.append((target_dir, [full_path]))
 
    return list
 
# The directory of assets to include.
my_files = get_data_files(os.path.dirname(os.path.realpath(__file__)) + '\\', assets_dir)

my_files += get_data_files(PYGAMEDIR + '\\', assets_dir);
 
# Build a dictionary of the options we want.
opts = { 'py2exe': {
  'ascii':'True',
  'excludes':['_ssl','_hashlib', 'numpy'],
  'includes' : ['pygame'],
  'bundle_files':'1',
  'compressed':'True',
  'optimize': 0,
  'dll_excludes':['w9xpopen.exe', 'build.bat'],
  'packages': ['encodings'],
  #'packages': ['ctypes', '_ctypes', 'pygame', 'pygame.mixer', 'requests', 'encodings'],
}}
 
# Run the setup utility.
setup(console=[target_file], data_files=my_files, zipfile=None, options=opts);
