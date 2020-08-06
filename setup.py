from setuptools import setup

setup(name='realtrends',
      version='1.0',
      description='Package to scrape google trends for '
                  'real and relative search volumes. '
                  'Data is returned as a DataFrame.',
      url='',
      author='Robert Chambers',
      author_email='1robertchambers@gmail.com',
      license='MIT',
      packages=['realtrends'],
      install_requires=[
            'python-dateutil',
            'pandas',
            'pycurl'
      ],
      zip_safe=False)