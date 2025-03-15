import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name="smam",              
        version="0.0.1",          
        description="A simple script that manages multiple Signal Desktop accounts on Linux.",
        author="Stan",
        package_dir={"": "src"},
        packages=setuptools.find_packages(where="src"),
        entry_points={
            "console_scripts": [
                "smam=smam_package.smam:main",
            ],
        },
    )