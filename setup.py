from setuptools import setup

setup(
    name='simple-i18n',
    version='0.1.0',
    url='https://github.com/iDkGK/simple-i18n',
    author='iDkGK',
    author_email='1444807655@qq.com',
    maintainer='iDkGK',
    maintainer_email='1444807655@qq.com',
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=['simple_i18n'],
    requires=['pystache'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Topic :: Software Development :: Internationalization',
    ],
    keywords=['i18n', 'gettext', 'translation'],
    platforms=['MacOS X', 'Windows', 'Linux'],
    zip_safe=True,

)