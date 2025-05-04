from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from django.test import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

MAX_WAIT = 10

class NewVisitorTest(LiveServerTestCase):
    
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

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

    def test_can_start_a_list_and_retrieve_it_later(self):

        # 张三听说有一个在线待办事项的应用
        # 他去看了这个应用的首页
        self.browser.get(self.live_server_url)  # (1)
        # self.browser.get('http://localhost:8000')  # (1)

        # 他注意到网页的标题和头部都包含了“To-Do”这个单词
        self.assertIn('To-Do', self.browser.title)  
        header_text = self.browser.find_element(By.TAG_NAME, 'h1').text  # (1)
        self.assertIn('To-Do', header_text)

        # 应用有一个输入框来添加待办事项的文本输入框
        inputbox = self.browser.find_element(By.ID, 'id_new_item')  # (1)
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # 他在文本输入框中输入了“Buy flowers”
        inputbox.send_keys('Buy flowers')  # (2)

        # 他按了回车键后，页面更新了
        # 待办事项表格中显示了“1:Buy flowers”
        inputbox.send_keys(Keys.ENTER)  # (3)
        self.wait_for_row_in_list_table('1:Buy flowers')

        #table = self.browser.find_element(By.ID, 'id_list_table')
        #rows = table.find_elements(By.TAG_NAME, 'tr')  # (1)
        #self.assertIn('1:Buy flowers', [row.text for row in rows])

        # 页面中又显示了一个文本输入框，可以再输入其他的待办事项
        # 他输入了“Give a gift to Lisi”
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Give a gift to Lisi')
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # 页面再次更新，他的清单中显示了这两个待办事项
        #table = self.browser.find_element(By.ID, 'id_list_table')
        #rows = table.find_elements(By.TAG_NAME, 'tr')
        #self.assertIn('1:Buy flowers', [row.text for row in rows])
        #self.assertIn('2:Give a gift to Lisi', [row.text for row in rows])
        self.wait_for_row_in_list_table('1:Buy flowers')
        self.wait_for_row_in_list_table('2:Give a gift to Lisi')



        # 张三想知道这个网站是否会记住他的清单
        # 他看到网站为他生成了一个唯一的URL
        """ self.fail('Finish the test!') """

    def test_multiple_uesrs_start_a_lists_at_different_urls(self):
        # 张三开始了一个新清单，并看到有一个唯一的URL
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy flowers')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:Buy flowers')

        # 他注意到他的清单URL中包含了一个唯一的编号
        zhangsan_list_url = self.browser.current_url
        self.assertRegex(zhangsan_list_url, '/lists/.+')    # (1)

        # 现在一个新用户王五访问网站
        # 我们使用一个新的浏览器会话来确保cookie不共享，确保张三的信息不会泄露
        self.browser.quit()
        self.browser = webdriver.Chrome()

        # 王五访问首页，看不到张三的清单
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('Buy flowers', page_text)
        self.assertNotIn('Give a gift to Lisi', page_text)

        # 王五开始一个新清单，他输入一个不同的待办事项

        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy milk')

        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:Buy milk')

        # 王五获得了一个唯一的URL
        wangwu_list_url = self.browser.current_url
        self.assertRegex(wangwu_list_url, '/lists/.+')
        self.assertNotEqual(wangwu_list_url, zhangsan_list_url)

        # 这个页面没有张三的清单
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('Buy flowers', page_text)
        self.assertIn('Buy milk', page_text)

        # 两个人都很满意




""" if __name__ == '__main__':
    unittest.main() """