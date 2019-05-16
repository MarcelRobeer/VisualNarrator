from setuptools import setup, find_packages
from vn.config import __version__, author, description

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(name='visualnarrator',
      version = __version__,
      description = description,
      author = author,
      author_email = 'm.j.robeer@uu.nl',
      packages = find_packages(),
      url = 'https://github.com/marcelrobeer/VisualNarrator',
      long_description = long_description,
      long_description_content_type = 'text/markdown')