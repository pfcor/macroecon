import setuptools

setuptools.setup(
    name="macroecon",
    version="0.1.2a",
    url="https://github.com/pfcor/macroecon.git",

    author="Pedro Correia",
    author_email="pedrocorreia.rs@gmail.com",

    description="Interface with macroeconomic data sources from Brasil, such as IPEA.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[
        'requests',
        'beautifulsoup4',
        'pandas'
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ],
)
