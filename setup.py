from setuptools import find_packages, setup

# TODO: Min. Python Version: 3.5
# TODO: Proper package data finding
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
        'async_timeout',
        'YURL',

        # Bonuses to aiohttp
        'cchardet',
        'aiodns',
        # TODO: Platform-specific requirements.
        # Most of this is from https://github.com/r0x0r/pywebview/blob/master/setup.py
        # Windows: pythonnet or pywin32 (via pypiwin32)
        # Linux: PyGObject or PyQt4 (actually installable through pip)
        # Mac: PyObjC or PyQt4
    ],
    entry_points={
        'gui_scripts': [
            'smol = smol.__main__:main'
        ]
    },
    # zip_safe=False,
)
