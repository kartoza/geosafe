# coding=utf-8
import os
import unittest
from distutils.util import strtobool

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
# available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from geosafe.app_settings import settings
from geosafe.helpers.utils import GeoSAFEIntegrationLiveServerTestCase


# available since 2.26.0


def selenium_flag_ready():
    """Flag to tell that selenium test is setup."""
    selenium_unit_test_flag = os.environ.get(
        'SELENIUM_UNIT_TEST_FLAG', 'False')
    selenium_unit_test_flag = strtobool(selenium_unit_test_flag)
    return settings.SELENIUM_DRIVER and selenium_unit_test_flag


class SeleniumTest(GeoSAFEIntegrationLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(SeleniumTest, cls).setUpClass()
        # Create a new instance of the driver
        try:
            cls.driver = webdriver.Remote(
                command_executor=settings.SELENIUM_DRIVER,
                desired_capabilities=DesiredCapabilities.FIREFOX)
            cls.driver.implicitly_wait(60)
            cls.url = settings.SITEURL
        except BaseException:
            pass

    @classmethod
    def tearDownClass(cls):
        try:
            cls.driver.quit()
        except BaseException:
            pass
        super(SeleniumTest, cls).tearDownClass()


class TestGeoSAFETemplate(SeleniumTest):

    @unittest.skipUnless(
        selenium_flag_ready(),
        'Selenium test was not setup')
    def test_topbar_added(self):
        driver = self.driver

        driver.get(self.url)

        navbar = driver.find_element_by_id('navbar')

        geosafe_menu = navbar.find_element_by_partial_link_text('GeoSAFE')

        self.assertTrue(geosafe_menu)

    @unittest.skipUnless(
        selenium_flag_ready(),
        'Selenium test was not setup')
    def test_create_analysis_tooltip(self):
        driver = self.driver

        driver.get(self.url)

        navbar = driver.find_element_by_id('navbar')

        geosafe_menu = navbar.find_element_by_link_text('GeoSAFE')

        geosafe_menu.click()

        create_analysis = navbar.find_element_by_link_text(
            'Create Analysis')

        create_analysis.click()

        # Wait url changes
        WebDriverWait(driver, 10).until(EC.url_changes)
        # Make sure tooltip shown
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'options-panel'), "Select Hazard")
        )
