from distutils.core import setup

setup(
    name='libdlb',
    version='0.1dev',
    packages=['libdlb',],
    license='',
    long_description=open('README.md').read(),
    install_requires=[
        'torch>=0.4.1',
        "jsonnet==0.10.0 ; sys.platform != 'win32'",
        'overrides',
        'boto3',
        'requests>=2.18',
        'tqdm>=4.19',
        'termcolor',
    ],
    scripts=["bin/libdlb-run"],
)
