from setuptools import setup, find_packages

setup(
    name='glamkit-fallbackserve',
    author='Wil Tan',
    author_email='wil@interaction.net.au',
    version='0.1',
    description='Makes your life easier when dealing with media during the development of Django apps',
    url='http://github.com/glamkit/glamkit-fallbackserve',
    packages=find_packages(),
    package_data={},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)