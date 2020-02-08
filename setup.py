from setuptools import setup, find_packages
setup(
    name='swampsat2',
    version='1.0.10',
    packages=find_packages("lib"),
    package_dir={'': 'lib'},
    url='http://github.com/ralent/swampsat2',
    license='MIT',
    author='Ralen Toledo',
    description='Parse SwampSat II Beacon (UF CubeSat)',
    scripts=["lib/swampsat2.py"],
    install_requires=["docopt"],
    include_package_data=True,
    entry_points={
        'console_scripts': ['swampsat2=swampsat2:main'],
    },
)
