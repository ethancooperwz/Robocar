from setuptools import setup, find_packages

setup(
    name = 'speech',
    version = '1.1',
    packages=find_packages(),
    description = 'speech library',
    author = 'aidenwei',
    include_package_data=True,
    package_data={
        'speech': ['**/*'],
    },
)
