from setuptools import setup

setup(
    author='Victor Leikehman',
    author_email='victorlei@gmail.com',
    description='Matlab to Python compiler',
    license='MIT',
    keywords='matlab octave python compiler',
    name='smop',
    version='0.23',
    entry_points={'console_scripts': ['smop = smop.main:main', ], },
    packages=['smop'],
    install_requires=['numpy', 'scipy'],
)
