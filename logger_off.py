# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from lxml import etree as et
import unittest, time


class LoggerOff(unittest.TestCase):
    def setUp(self):
        print "Hello!"
        # To prevent download dialog
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)  # custom location
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir', r'd:\NeyrossBackups')
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')

        self.driver = webdriver.Firefox(profile)
        self.driver.implicitly_wait(50)
        print "Firefox started!"
        self.ips = []
        self.tree = et.parse("boreys.xml")
        boreys = self.tree.xpath("/Boreys/Borey[@configured='0']")
        for borey in boreys:
            self.ips.append(borey.get("ipAddress"))
        print "Read list of " + str(len(self.ips)) + " ip addresses ..."
        self.verificationErrors = []
        self.accept_next_alert = True

    def turn_off_logs(self, ip):
        driver = self.driver
        driver.get("http://" + ip + "/logon.html?next=%2Flog-ui%2F")
        driver.find_element_by_id("username").clear()
        driver.find_element_by_id("username").send_keys("root")
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys("root")
        driver.find_element_by_id("submit").click()
        driver.implicitly_wait(15)
        driver.find_element_by_xpath("//ul[@id='log-tabs']/li[2]").click()
        self.setup_logger(driver, "cyclic-extra")
        self.setup_logger(driver, "cyclic")
        borey = self.tree.xpath("/Boreys/Borey[@ipAddress='" + ip + "']")
        for node in borey:
            node.attrib["configured"] = "1"
        driver.get("http://" + ip + "/admin/")
        #driver.find_element_by_xpath("/html/body/footer/span[3]").click()
        #driver.find_element_by_xpath("/html/body/footer/ul/li[1]").click()
        #driver.find_element_by_xpath("//*[@id='jquery-dialog-window']/div[3]/button[1]").click()
        #WebDriverWait(driver, 10).until()
        #driver.find_element_by_xpath("//*[@id='jquery-dialog-window']/div[3]/button[contains(text(),'Продолжить работу')]").click()

    def setup_logger(self, driver, logger):
        Select(driver.find_element_by_id("appender-select")).select_by_visible_text(logger)
        alldivs = driver.find_elements_by_xpath(u"//a[contains(text(),'удалить')]")
        first = True
        for div in alldivs:
            if first:
                first = False
                continue
            else:
                div.click()
        Select(driver.find_element_by_xpath(
            u"//*[@id='appender-filter']/div/div[1]/div[2]/select")).select_by_visible_text("ERROR")
        driver.find_element_by_xpath(u"//*[@id='appender-form']/button").click()
        self.assertEqual(u"Сохранено", self.close_alert_and_get_its_text())

    def make_backup(self, ip):
        driver = self.driver
        driver.get("http://" + ip + "/logon.html?next=%2Fadmin%2F")
        driver.find_element_by_id("username").clear()
        driver.find_element_by_id("username").send_keys("root")
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys("root")
        driver.find_element_by_id("submit").click()
        driver.implicitly_wait(15)
        driver.find_element_by_css_selector("body > footer > span.admin-backup").click()
        driver.find_element_by_xpath("/html/body/footer/ul/li[1]").click()
        driver.find_element_by_xpath("//*[@id='jquery-dialog-window']/div[3]/button[1]").click()
        try:
            WebDriverWait(driver, 90).until(lambda element: element.find_element_by_xpath("//*[@id='jquery-dialog-window']/div[3]/button[contains(text(),'Продолжить работу')]"))
        except:
            return
        driver.find_element_by_xpath("//*[@id='jquery-dialog-window']/div[3]/button[contains(text(),'Продолжить работу')]").click()
        driver.find_element_by_css_selector("body > footer > span.admin-backup").click()
        driver.find_element_by_xpath("/html/body/footer/ul/li[4]").click()
        time.sleep(5)


    def test_logger_off(self):
        self.make_backup("10.0.30.44")
        #  for ip in self.ips:
        #      self.turn_off_logs(ip)
        #      f = open("boreys.xml", "w")
        #      f.write(et.tostring(self.tree, pretty_print=True, xml_declaration=True, encoding='utf-8'))
        #      f.close()

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
