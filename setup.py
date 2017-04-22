from setuptools import setup

setup(
    name='lcd_restful',
    packages=['lcd_restful'],
    version='0.1.0',
    description=(
        "RESTful controller for HD44780 Character Panel LCD " +
        "on the Raspberry Pi. Supports testing on non-Rpi systems"),
    author='Ryan Farley',
    author_email='rfarley3@gmu.edu',
    # url='https://github.com/rfarley3/lcd-restful',
    # download_url='https://github.com/rfarley3/lcd_restful/tarball/0.1.0',
    keywords=['lcd', 'rpi', 'hd44780'],
    classifiers=[],
    install_requires=[
        'rplcd',
        'rpifake',
        'requests',
        'bottle',
        'jsonpickle'
    ],
    entry_points={
        'console_scripts': [
            'lcd_server = lcd_restful.__main__:main_serv',
        ]
    },
    include_package_data=True,
)
