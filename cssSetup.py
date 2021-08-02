from setuptools import setup

setup(
    # Either option is valid here.
    #   Either use `package_data` with enumerating the values, or
    #   set `include_package_data=True`.
    include_package_data=True,
    package_data={
        'breeze_theme': ['dist/*'],
    },
    zip_safe=False,
)
