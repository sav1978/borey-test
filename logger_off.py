# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
        except TimeoutException:
            return
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
        borey = self.tree.xpath("/Boreys/Borey[@ipAddress='" + ip + "']")
        for node in borey:
            if (not ("backup" in node.attrib)) or (node.attrib["backup"] != "1"):
                driver = self.driver
                driver.get("http://" + ip + "/logon.html?next=%2Fadmin%2F")
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "username"))
                    )
                except TimeoutException:
                    print '[ERROR] No response from Borey with ip {}'.format(ip)
                    return False
                driver.find_element_by_id("username").clear()
                driver.find_element_by_id("username").send_keys("root")
                driver.find_element_by_id("password").clear()
                driver.find_element_by_id("password").send_keys("root")
                driver.find_element_by_id("submit").click()
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "body > footer > span.admin-backup"))
                    )
                except TimeoutException:
                    print '[ERROR] Can not login to Borey with ip {}'.format(ip)
                    return False
                driver.find_element_by_css_selector("body > footer > span.admin-backup").click()
                driver.find_element_by_xpath("/html/body/footer/ul/li[1]").click()
                driver.find_element_by_xpath("//*[@id='jquery-dialog-window']/div[3]/button[1]").click()
                try:
                    WebDriverWait(driver, 180).until(lambda element: element.find_element_by_xpath("//*[@id='jquery-dialog-window']/div[3]/button[contains(text(),'Продолжить работу')]"))
                except TimeoutException:
                    return
                driver.find_element_by_xpath("//*[@id='jquery-dialog-window']/div[3]/button[contains(text(),'Продолжить работу')]").click()
                driver.find_element_by_css_selector("body > footer > span.admin-backup").click()
                driver.find_element_by_xpath("/html/body/footer/ul/li[4]").click()
                time.sleep(5)
                node.attrib["backup"] = "1"
                return True
            else:
                print '[INFO] No need to backup Borey with ip {}. Backup already created'.format(ip)
                return False


    def test_logger_off(self):
        for ip in self.ips:
            print 'Making backup of Borey with ip {}'.format(ip)
            if self.make_backup(ip):
                print '[OK] Backup of Borey with ip {} MAKED and SAVED!'.format(ip)
                f = open("boreys.xml", "w")
                f.write(et.tostring(self.tree, pretty_print=True, xml_declaration=True, encoding='utf-8'))
                f.close()

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
