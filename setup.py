from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
       license = f.read()

setup(
    name='Food Sense',
    version='0.4.0',
    description='DT08 Food Sense',
    long_description=readme,
    author='Derrick Patterson and Mavroidis Mavroidis',
    author_email='DT08FoodSense@gmail.com',
    url='https://github.com/foodsense/foodsense',
    license=license,
    packages=find_packages()
)
