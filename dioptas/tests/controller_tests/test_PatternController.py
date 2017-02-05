# -*- coding: utf8 -*-

import os

import numpy as np

from ..utility import QtTest, click_button, delete_if_exists
from mock import MagicMock

from qtpy import QtWidgets

from ...widgets.integration import IntegrationWidget
from ...controller.integration.PatternController import PatternController
from ...controller.integration.BackgroundController import BackgroundController
from ...model.DioptasModel import DioptasModel
from ...model.util.calc import convert_units

unittest_data_path = os.path.join(os.path.dirname(__file__), '../data')


class PatternControllerTest(QtTest):
    def setUp(self):
        self.working_dir = {'image': '', 'spectrum': ''}

        self.widget = IntegrationWidget()
        self.model = DioptasModel()

        self.controller = PatternController(
            working_dir=self.working_dir,
            widget=self.widget,
            dioptas_model=self.model)

    def tearDown(self):
        delete_if_exists(os.path.join(unittest_data_path, "test.xy"))

    def test_changing_units(self):
        self.model.img_model.load(os.path.join(unittest_data_path, 'CeO2_Pilatus1M.tif'))
        self.model.calibration_model.load(os.path.join(unittest_data_path, 'CeO2_Pilatus1M_2.poni'))

        click_button(self.widget.spec_q_btn)
        self.assertEqual(self.widget.pattern_widget.spectrum_plot.getAxis('bottom').labelString(),
                         "<span style='color: #ffffff'>Q (A<sup>-1</sup>)</span>")

        click_button(self.widget.spec_tth_btn)
        self.assertEqual(self.widget.pattern_widget.spectrum_plot.getAxis('bottom').labelString(),
                         u"<span style='color: #ffffff'>2θ (°)</span>")

        click_button(self.widget.spec_d_btn)
        self.assertEqual(self.widget.pattern_widget.spectrum_plot.getAxis('bottom').labelString(),
                         u"<span style='color: #ffffff'>d (A)</span>")

    def test_changing_units_with_background_subtraction(self):
        self.background_controller = BackgroundController(self.working_dir, self.widget, self.model)


        self.model.calibration_model.load(os.path.join(unittest_data_path, 'CeO2_Pilatus1M.poni'))
        self.model.img_model.load(os.path.join(unittest_data_path, 'CeO2_Pilatus1M.tif'))

        click_button(self.widget.qa_bkg_spectrum_btn)

        self.assertTrue(self.model.pattern.auto_background_subtraction)

        old_roi = self.model.pattern.auto_background_subtraction_roi
        old_x, old_y = self.model.pattern.data

        ######################
        click_button(self.widget.spec_q_btn)


        new_roi = self.model.pattern.auto_background_subtraction_roi
        new_x, new_y = self.model.pattern.data

        self.assertEqual(new_roi[0], convert_units(old_roi[0], self.model.calibration_model.wavelength,
                                                   '2th_deg', 'q_A^-1'))

        self.assertEqual(new_roi[1], convert_units(old_roi[1], self.model.calibration_model.wavelength,
                                                   '2th_deg', 'q_A^-1'))

        ######################
        click_button(self.widget.spec_tth_btn)
        old_roi_2 = self.model.pattern.auto_background_subtraction_roi
        old_x_2, old_y_2 = self.model.pattern.data
        self.assertEqual(old_roi_2[0], convert_units(new_roi[0], self.model.calibration_model.wavelength,
                                                     'q_A^-1', '2th_deg' ))
        self.assertAlmostEqual(old_roi_2[1], convert_units(new_roi[1], self.model.calibration_model.wavelength,
                                                           'q_A^-1', '2th_deg'), delta=0.01)
        self.assertAlmostEqual(0.0, np.sum(old_y-old_y_2))

    def test_configuration_selected_changes_active_unit_btn(self):
        self.model.add_configuration()
        click_button(self.widget.spec_q_btn)
        self.model.add_configuration()
        click_button(self.widget.spec_d_btn)

        self.model.select_configuration(0)
        self.assertTrue(self.widget.spec_tth_btn.isChecked())
        self.assertFalse(self.widget.spec_q_btn.isChecked())
        self.assertFalse(self.widget.spec_d_btn.isChecked())

        self.assertEqual(self.widget.pattern_widget.spectrum_plot.getAxis('bottom').labelString(),
                         u"<span style='color: #ffffff'>2θ (°)</span>")

        self.model.select_configuration(1)
        self.assertTrue(self.widget.spec_q_btn.isChecked())

        self.assertEqual(self.widget.pattern_widget.spectrum_plot.getAxis('bottom').labelString(),
                         "<span style='color: #ffffff'>Q (A<sup>-1</sup>)</span>")

        self.model.select_configuration(2)
        self.assertTrue(self.widget.spec_d_btn.isChecked())
        self.assertEqual(self.widget.pattern_widget.spectrum_plot.getAxis('bottom').labelString(),
                         u"<span style='color: #ffffff'>d (A)</span>")

    def test_save_pattern_without_background(self):
        QtWidgets.QFileDialog.getSaveFileName = MagicMock(return_value=os.path.join(unittest_data_path, "test.xy"))
        self.model.calibration_model.create_file_header = MagicMock(return_value="None")
        click_button(self.widget.qa_save_spectrum_btn)

        self.assertTrue(os.path.exists(os.path.join(unittest_data_path, "test.xy")))
