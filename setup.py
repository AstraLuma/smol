from setuptools import find_packages, setup

# TODO: Min. Python Version: 3.5
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
        'aiofiles',

        # Bonuses to aiohttp
        'cchardet',
        'aiodns',
    ],
    entry_points={
        'gui_scripts': [
            'smol = smol.__main__:main'
        ]
    },
    # zip_safe=False,
)