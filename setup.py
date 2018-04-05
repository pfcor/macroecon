import setuptools

setuptools.setup(
    name="macroecon",
    version="0.1.0",
    url="https://github.com/pfcor/macroecon.git",

    author="Pedro Correia",
    author_email="pedrocorreia.rs@gmail.com",

    description="Interface with macroeconomic data sources from Brasil, such as IPEA.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
