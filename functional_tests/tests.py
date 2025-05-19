from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import os

MAX_WAIT = 10


class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        real_server = os.environ.get('REAL_SERVER')
        if real_server:
            self.live_server_url = 'http://' + real_server

    def tearDown(self):
        self.browser.quit()

    # ---------- 辅助函数 ----------
    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element(By.ID, 'id_list_table')
                rows = table.find_elements(By.TAG_NAME, 'tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    # ---------- 功能测试 1 ----------
    def test_can_start_a_list_and_retrieve_it_later(self):
        # 访问首页
        self.browser.get(self.live_server_url)

        # 标题与页眉包含“To-Do”
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, 'h1').text
        self.assertIn('To-Do', header_text)

        # 输入第 1 条
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        self.assertEqual(inputbox.get_attribute('placeholder'), 'Enter a to-do item')
        inputbox.send_keys('Buy flowers')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:Buy flowers')

        # 输入第 2 条
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Give a gift to Lisi')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:Buy flowers')
        self.wait_for_row_in_list_table('2:Give a gift to Lisi')

    # ---------- 功能测试 2 ----------
    def test_multiple_uesrs_start_a_lists_at_different_urls(self):
        # 张三的清单
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy flowers')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:Buy flowers')
        zhangsan_list_url = self.browser.current_url
        self.assertRegex(zhangsan_list_url, '/lists/.+')

        # 启动新浏览器会话（王五）
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # 王五访问，不应看到张三的数据
        self.browser.get(self.live_server_url)
        body_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('Buy flowers', body_text)
        self.assertNotIn('Give a gift to Lisi', body_text)

        # 王五添加自己的条目
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:Buy milk')

        wangwu_list_url = self.browser.current_url
        self.assertRegex(wangwu_list_url, '/lists/.+')
        self.assertNotEqual(wangwu_list_url, zhangsan_list_url)

        body_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('Buy flowers', body_text)
        self.assertIn('Buy milk', body_text)

    # ---------- 功能测试 3 ----------
    def test_layout_and_styling(self):
        # 首页居中
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )

        # 提交后仍居中
        inputbox.send_keys('testing')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:testing')
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )
