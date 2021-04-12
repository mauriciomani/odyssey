from setuptools import find_packages, setup

def read_requirements():
    with open("requirements.txt") as req:
        content = req.read()
        requirements = content.split("\n")
    return(requirements)

setup(
    name='odyssey',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    entry_points='''
        [console_scripts]
        odyssey=odyssey.cli:cli
    ''',
    version='0.0.1',
    description='Cloud Machine Learning using AWS, Azure, GCP, etc. Just needed train and serve scripts.',
    author='mauriciomani',
    license='MIT',
)
