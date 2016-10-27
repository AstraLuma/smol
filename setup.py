from setuptools import find_packages, setup

setup(
    name='smol',
    version='0.0.1',
    description='The Small MOdpack minecraft Launcher',
    platforms=['POSIX'],
    packages=find_packages(),
    package_data={
        '': ['templates/*.html', 'static/*.*']
    },
    include_package_data=True,
    install_requires=[
        'pywebview',
        'aiohttp',
        'pyyaml',
        'aiohttp_jinja2',

        # Bonuses to aiohttp
        'cchardet',
        'aiodns',
    ],
    # zip_safe=False,
)