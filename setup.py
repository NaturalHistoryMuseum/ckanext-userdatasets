from setuptools import setup, find_packages

version = '0.1'

setup(
	name='ckanext-userdatasets',
	version=version,
	description="CKAN extension to allow users to edit their dataset only",
    url='https://github.com/NaturalHistoryMuseum/ckanext-userdatasets',
	packages=find_packages(),
	namespace_packages=['ckanext', 'ckanext.userdatasets'],
	entry_points="""
        [ckan.plugins]
            userdatasets = ckanext.userdatasets.plugin:UserDatasetsPlugin
	""",
)
