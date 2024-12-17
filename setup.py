from setuptools import setup, find_packages

setup(
    name="sqlmap-gui",
    version="1.0.0",
    description="SQLMap的图形化界面工具 - 零漏安全出品",
    author="无垢",
    author_email="hanyan711@qq.com",
    packages=find_packages(include=['src', 'src.*']),
    package_dir={'': '.'},
    include_package_data=True,
    install_requires=[
        'PyQt5>=5.15.9',
        'PyQtChart>=5.15.6',
        'requests>=2.31.0',
        'psutil>=5.9.5',
        'PySocks>=1.7.1',
        'matplotlib>=3.7.1',
    ],
    entry_points={
        'console_scripts': [
            'sqlmap-gui=main:main',
        ],
    },
    python_requires='>=3.7',
) 