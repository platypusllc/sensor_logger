from setuptools import setup

package_name = 'sensor_logger'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Chris Tomaszewski',
    maintainer_email='chris@senseplatypus.com',
    description='ROS2 logging package for Atlas Scientific Sensors',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'atlas = sensor_logger.atlas:main'
        ],
    },
)
