from pybuilder.core import use_plugin, init, Author

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("copy_resources")

name = "simple-container-runtime"

authors = [Author("Marco Hoyer", "marco_hoyer@gmx.de")]
description = "Simple-Container-Runtime - simply run docker containers"
license = "APACHE LICENSE, VERSION 2.0"
summary = "Simple-Container-Runtime - simply run docker containers"
url = "https://github.com/cfn-sphere/simple-container-runtime"
version = "0.1.1"

default_task = "publish"


@init
def set_properties(project):
    project.depends_on("sh")
    project.depends_on("click")
    project.depends_on("requests")
    project.depends_on("boto3")
    project.depends_on("PyYAML")
    project.build_depends_on("unittest2")
    project.build_depends_on("mock")

    project.set_property("copy_resources_target", "$dir_dist")
    project.get_property("copy_resources_glob").extend(["setup.cfg"])

    project.set_property("install_dependencies_upgrade", True)
    project.set_property("coverage_break_build", False)

    project.get_property('filter_resources_glob').extend(['**/cfn_sphere/__init__.py'])
    project.set_property('distutils_console_scripts', ['cf=simple_container_runtime.cli:main'])