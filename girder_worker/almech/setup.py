from setuptools import setup, find_packages

setup(name='almech',
      version='0.1.0',
      description='The girder worker plugin for albany mechanics simulations',
      author='Patrick Avery',
      author_email='patrick.avery@kitware.com',
      license='Apache v2',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: Apache Software License'
          'Topic :: Scientific/Engineering :: GIS',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Programming Language :: Python'
      ],
      entry_points={
          'girder_worker_plugins': [
              'almech = almech:AlMechPlugin',
          ]
      },
      packages=find_packages(),
      zip_safe=False)
