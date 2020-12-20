# This is the class you derive to create a plugin
from airflow import configuration
from airflow.plugins_manager import AirflowPlugin

from flask import Blueprint
from flask_admin.base import MenuLink
from flask_admin import BaseView as AdminBaseview, expose as admin_expose
from flask_appbuilder import expose as app_builder_expose, BaseView as AppBuilderBaseView, has_access


# Importing base classes that we need to derive
from airflow.hooks.base_hook import BaseHook
from airflow.models import BaseOperator
from airflow.models.baseoperator import BaseOperatorLink
# from airflow.operators.gcs_to_s3 import GoogleCloudStorageToS3Operator
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.executors.base_executor import BaseExecutor

import logging



rbac_authentication_enabled = configuration.getboolean("webserver", "RBAC")

# Will show up under airflow.hooks.test_plugin.PluginHook
class PluginHook(BaseHook):
    pass

# Will show up under airflow.operators.test_plugin.PluginOperator
class PluginOperator(BaseOperator):
    pass

# Will show up under airflow.sensors.test_plugin.PluginSensorOperator
class PluginSensorOperator(BaseSensorOperator):
    pass

# Will show up under airflow.executors.test_plugin.PluginExecutor
class PluginExecutor(BaseExecutor):
    pass

# Will show up under airflow.macros.test_plugin.plugin_macro
# and in templates through {{ macros.test_plugin.plugin_macro }}
def plugin_macro():
    pass

def get_baseview():
    if rbac_authentication_enabled == True:
        return AppBuilderBaseView
    else:
        return AdminBaseview

# Creating a flask BaseView
class TestView(get_baseview()):
	if rbac_authentication_enabled == True:
		@app_builder_expose('/')
		def list(self):
			logging.info("TestView.list() called")
			return self.render_template("test_plugin/test.html",
			                            baseview="AppBuilderBase")
	else:
		@admin_expose('/')
		def test(self):
			logging.info("TestView.test() called")
			return self.render("test_plugin/test.html",
		                      baseview="AdminBase")

# Creating View to be used by Plugin
if rbac_authentication_enabled == True:
    v = {"category": "Test Plugin",
               "name": "Test View Plugin",  "view": TestView()}
else:
    v = TestView(category="Test Plugin", name="Test View Plugin")


# Creating a flask blueprint to integrate the templates and static folder
bp = Blueprint(
    "test_plugin", __name__,
    template_folder='templates', # registers airflow/plugins/templates as a Jinja template folder
    static_folder='static',
    static_url_path='/static/test_plugin')

ml = MenuLink(
    category='Test Plugin',
    name='Test Menu Link',
    url='https://airflow.apache.org/')


# Creating a flask appbuilder Menu Item
appbuilder_mitem = {"name": "Google",
                    "category": "Search",
                    "category_icon": "fa-th",
                    "href": "https://www.google.com"}

class GoogleLink(BaseOperatorLink):
    name = "Google"

    def get_link(self, operator, dttm):
        return "https://www.google.com"


# Defining the plugin class
class AirflowTestPlugin(AirflowPlugin):
    name = "test_plugin"
    operators = [PluginOperator]
    sensors = [PluginSensorOperator]
    hooks = [PluginHook]
    executors = [PluginExecutor]
    macros = [plugin_macro]
    admin_views = [v]
    flask_blueprints = [bp]
    menu_links = [ml]
    appbuilder_views = [v]
    appbuilder_menu_items = [appbuilder_mitem]
    global_operator_extra_links = [GoogleLink(),]
    operator_extra_links = []