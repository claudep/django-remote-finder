try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-remote-finder',
    version='0.4',
    author='Jim Garrison',
    description='Keep various javascript/css libraries updated within a Django package',
    url='https://github.com/claudep/django-remote-finder',
    packages=[
        'remote_finder',
    ],
    install_requires=['Django'],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
