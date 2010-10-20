from setuptools import setup

setup(
    name = 'pubbot',
    version = '0.1',
    author = 'John Carr',
    author_email = 'john.carr@unrouted.co.uk',

    zip_safe = True,
    packages = ['pubbot', 'twisted.plugins'],
    install_requires = [
        'Twisted',
    ],
    package_data={'twisted': ['plugins/pubbot.py']},
)
