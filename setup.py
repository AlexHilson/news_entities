from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='news_entities',
    version='0.0.1',
    install_requirements=requirements,
    packages=['news_entities']
)