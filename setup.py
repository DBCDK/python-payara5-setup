from setuptools import find_packages, setup

setup(
    name='payara5-setup',
    version='0.9',
    packages=['xmltools'],
    package_dir={'xmltools': 'xmltools'},
    options={
        'build_exe': {
            'packages': find_packages(exclude=['tests', 'README.md'])
        }
    },
    scripts=['payara5-setup', 'payara-log-setup', 'payara-logback-setup', 'payara-admin-password'],
    url='https://github.com/kosmisk-dk/payara5-setup',
    license='gpl3',
    author='kosmisk-dk',
    author_email='source@kosmisk.dk',
    description="Configuration of payara5's domain.xml before 1st launch",
    long_description="""Designed for simplified configuration of payara5-full, given a number of
configuration specs. It can manipulate the config.xml, on a basic xpath like level, or on an
abstract resource like level, i.e. jms/jdbc/resource/custom-resource/..."""
)
