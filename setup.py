from setuptools import setup

setup(name='realtrends',
      version = '0.1',
      description = 'Package to scrape google trends for '
                  'real and relative search volumes. '
                    'Data is returned as a DataFrame.',
      url = '',
      author = 'Robert Chambers',
      author_email = '1robertchambers@gmail.com',
      license = 'MIT',
      packages = ['realtrends'],
      install_requires = [
            'pandas',
            'pycurl'
      ],
      zip_safe = False)