# -*- coding: utf8 -*-

import os
from mock import MagicMock

from ..utility import QtTest, click_button
from ...model.DioptasModel import DioptasModel
from ...widgets.ConfigurationWidget import ConfigurationWidget

unittest_path = os.path.dirname(__file__)
data_path = os.path.join(unittest_path, '../data')
jcpds_path = os.path.join(data_path, 'jcpds')


class ConfigurationWidgetTest(QtTest):
    def setUp(self):
        self.config_widget = ConfigurationWidget()
        self.model = DioptasModel()

    def test_one_configuration(self):
        self.config_widget.update_configurations(self.model.configurations, 0)
        self.assertEqual(len(self.config_widget.configuration_btns), 1)

    def test_multiple_configurations(self):
        self.model.add_configuration()
        self.model.add_configuration()
        self.model.add_configuration()
        self.config_widget.update_configurations(self.model.configurations, 1)

        self.assertEqual(len(self.config_widget.configuration_btns), 4)
        self.assertFalse(self.config_widget.configuration_btns[0].isChecked())
        self.assertFalse(self.config_widget.configuration_btns[2].isChecked())
        self.assertFalse(self.config_widget.configuration_btns[3].isChecked())
        self.assertTrue(self.config_widget.configuration_btns[1].isChecked())

    def test_configuration_selected_signal(self):
        self.config_widget.configuration_selected = MagicMock()
        self.model.add_configuration()
        self.model.add_configuration()
        self.model.add_configuration()
        self.config_widget.update_configurations(self.model.configurations, 0)

        click_button(self.config_widget.configuration_btns[3])
        self.config_widget.configuration_selected.emit.assert_called_once_with(3, True)

        self.assertFalse(self.config_widget.configuration_btns[0].isChecked())
        self.assertFalse(self.config_widget.configuration_btns[1].isChecked())
        self.assertFalse(self.config_widget.configuration_btns[2].isChecked())
        self.assertTrue(self.config_widget.configuration_btns[3].isChecked())
