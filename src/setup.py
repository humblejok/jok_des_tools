from distutils.core import setup

import des_tools

setup(
      name='DES tools for Python',
      version='.'.join(map(str, des_tools.__version__)),
      description='Utility code for DES and Python 2.5 or higher',
      author='De Jonckheere Stephane',
      author_email='humble.jok@gmail.com',
      packages=['des_tools',],
)