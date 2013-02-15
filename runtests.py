#!/usr/bin/env python
# coding: utf-8

import sys
import unittest

from selenium.webdriver.common.keys import Keys

import webdriverplus

# WebElements as set

# close_on_shutdown
# default_selector
# base_url

# drag & drop

# find_all().find() is broken
# No such element exceptions need to be cleaner

run_slow_tests = '--all' in sys.argv
browser = 'firefox'


class WebDriverPlusTests(unittest.TestCase):
    extra_webdriver_kwargs = {}

    def setUp(self):
        super(WebDriverPlusTests, self).setUp()
        self.driver = webdriverplus.WebDriver(browser, reuse_browser=True,
                                              **self.extra_webdriver_kwargs)

    def tearDown(self):
        self.driver.quit()


if run_slow_tests:
    class BrowserPoolingTests(unittest.TestCase):
        # Note: We don't inherit from WebDriverPlusTests as we don't want the
        #       default reuse browser behaviour for theses tests.

        # TODO: Similar tests, but with multiple windows open.

        def setUp(self):
            webdriverplus.WebDriver._pool.pop('firefox', None)

        def tearDown(self):
            for browser, signature in webdriverplus.WebDriver._pool.values():
                browser.quit(force=True)

        def test_reuse_browser_set(self):
            browser = webdriverplus.WebDriver('firefox', reuse_browser=True)
            browser.quit()
            other = webdriverplus.WebDriver('firefox', reuse_browser=True)
            self.assertEquals(browser, other)

        def test_reuse_browser_unset(self):
            browser = webdriverplus.WebDriver('firefox')
            browser.quit()
            other = webdriverplus.WebDriver('firefox')
            self.assertNotEquals(browser, other)


class DriverTests(WebDriverPlusTests):
    def test_open(self):
        page_text = 'abc'
        self.driver.open(page_text)
        self.assertEquals(self.driver.page_text,  page_text)

    def test_find(self):
        self.driver.open(u'<h1>123</h1><h2>☃</h2><h3>789</h3>')
        self.assertEquals(self.driver.find('h2').text, u'☃')

    def test_unicode(self):
        self.driver.open('<h1>123</h1><h2>456</h2><h3>789</h3>')
        self.assertEquals(self.driver.find('h2').text, '456')


class SelectorTests(WebDriverPlusTests):
    def setUp(self):
        super(SelectorTests, self).setUp()
        snippet = """<html>
                         <h1>header</h1>
                         <ul id="mylist">
                             <li>one</li>
                             <li>two</li>
                             <li class="selected">three</li>
                             <li><a href="#">four</a></li>
                             <li><strong>hi</strong>five</li>
                             <li>six<strong>hi</strong></li>
                             <li><strong>seven</strong></li>
                             <span>one</span>
                         </ul>
                         <form>
                             <label for="username">Username:</label>
                             <input type="text" name="username" value="lucy"/>
                             <label for="password">Password:</label>
                             <input type="password" name="password" />
                         </form>
                         <form id="checkboxlist">
                             <input type="checkbox" value="red" />
                             <input type="checkbox" value="green" />
                             <input type="checkbox" value="blue" checked=yes />
                         </form>
                     </html>"""
        self.driver.open(snippet)

    def test_multiple_selectors(self):
        node = self.driver.find('li', text='one')
        self.assertEquals(node.html, '<li>one</li>')

    def test_nonexistant_multiple_selectors(self):
        """If a combination of selector doesn't match one or more
        elements, none should be returned."""
        nodes = self.driver.find('li', text='fubar')
        self.assertFalse(nodes)

    def test_multiple_named_selectors(self):
        node = self.driver.find(tag_name='li', text='one')
        self.assertEquals(node.html, '<li>one</li>')

    def test_nonexistant_multiple_named_selectors(self):
        """If a combination of named selector doesn't match one or more
        elements, none should be returned."""
        nodes = self.driver.find(tag_name='li', text='fubar')
        self.assertFalse(nodes)

    def test_id(self):
        node = self.driver.find(id='mylist')
        self.assertEquals(node.tag_name, 'ul')

    def test_class_name(self):
        node = self.driver.find(class_name='selected')
        self.assertEquals(node.text, 'three')

    def test_tag_name(self):
        node = self.driver.find(tag_name='h1')
        self.assertEquals(node.text, 'header')

    def test_name(self):
        node = self.driver.find(name='username')
        self.assertEquals(node.tag_name, 'input')
        self.assertEquals(node.value, 'lucy')

    def test_css(self):
        node = self.driver.find(css='ul li.selected')
        self.assertEquals(node.text, 'three')

    def test_xpath(self):
        node = self.driver.find(xpath='//ul/li[@class="selected"]')
        self.assertEquals(node.text, 'three')

    def test_link_text(self):
        node = self.driver.find(link_text='four')
        self.assertEquals(node.tag_name, 'a')
        self.assertEquals(node.text, 'four')

    def test_link_text_contains(self):
        node = self.driver.find(link_text_contains='ou')
        self.assertEquals(node.tag_name, 'a')
        self.assertEquals(node.text, 'four')

    def test_text(self):
        self.assertEquals(self.driver.find(text='one').index, 0)
        self.assertEquals(self.driver.find(text='two').index, 1)
        self.assertEquals(self.driver.find(text='three').index, 2)

    def test_text_contains(self):
        self.assertEquals(self.driver.find('li', text_contains='ne').index, 0)
        self.assertEquals(self.driver.find('li', text_contains='tw').index, 1)
        self.assertEquals(self.driver.find('li', text_contains='hre').index, 2)

        self.assertEquals(len(self.driver.find(text_contains='ne')), 2)
        self.assertEquals(len(self.driver.find(text_contains='tw')), 1)
        self.assertEquals(len(self.driver.find(text_contains='hre')), 1)

        self.assertEquals(len(self.driver.find('li', text_contains='ive')), 1)
        self.assertEquals(len(self.driver.find('li', text_contains='ix')), 1)
        self.assertEquals(len(self.driver.find('li', text_contains='eve')), 0)

    #def test_label(self):
    #    node = self.driver.find(label='Password:')
    #    expected = '<input type="password" name="password" />'
    #    self.assertEquals(node.html, expected)

    #def test_label_contains(self):
    #    node = self.driver.find(label_contains='Password')
    #    expected = '<input type="password" name="password" />'
    #    self.assertEquals(node.html, expected)

    def test_attribute(self):
        node = self.driver.find(attribute='checked')
        self.assertEquals(node.value, 'blue')

    def test_attribute_value(self):
        node = self.driver.find(attribute_value=('checked', 'yes'))
        self.assertEquals(node.value, 'blue')

    def test_value(self):
        node = self.driver.find(value='blue')
        self.assertEquals(node.tag_name, 'input')
        self.assertEquals(node.type, 'checkbox')
        self.assertEquals(node.value, 'blue')

    def test_type(self):
        node = self.driver.find(type='checkbox')
        self.assertEquals(node.value, 'red')

    def test_checked(self):
        elem = self.driver.find(id='checkboxlist')
        self.assertEquals(len(elem.find(checked=True)), 1)
        self.assertEquals(len(elem.find(checked=False)), 2)

    # TODO: checked=True, checked=False, selected=True, selected=False


class TraversalTests(WebDriverPlusTests):
    def setUp(self):
        super(TraversalTests, self).setUp()
        snippet = """<html>
                         <ul>
                             <li>1</li>
                             <li>2</li>
                             <li class="selected">3</li>
                             <li>4</li>
                             <li><strong>5</strong></li>
                         </ul>
                     </html>"""
        self.driver.open(snippet)

    def test_indexing(self):
        elem = self.driver.find('ul').children()[0]
        self.assertEquals(elem.html, '<li>1</li>')

    def test_slicing(self):
        elems = self.driver.find('ul').children()[0:-1]
        expected = [
            '<li>1</li>',
            '<li>2</li>',
            '<li class="selected">3</li>',
            '<li>4</li>'
        ]
        self.assertEquals([elem.html for elem in elems], expected)

    def test_children(self):
        nodes = self.driver.find('ul').children()
        text = [node.text for node in nodes]
        self.assertEquals(text, ['1', '2', '3', '4', '5'])

    def test_filtering_traversal(self):
        nodes = self.driver.find('ul').children('.selected')
        text = [node.text for node in nodes]
        self.assertEquals(text, ['3'])

    def test_parent(self):
        node = self.driver.find('.selected').parent()
        self.assertEquals(node.tag_name, 'ul')

    def test_descendants(self):
        nodes = self.driver.find('ul').descendants()
        tag_names = [node.tag_name for node in nodes]
        self.assertEquals(tag_names, ['li', 'li', 'li', 'li', 'li', 'strong'])

    def test_ancestors(self):
        nodes = self.driver.find(class_name='selected').ancestors()
        tag_names = [node.tag_name for node in nodes]
        self.assertEquals(tag_names, ['html', 'body', 'ul'])

    def test_next(self):
        node = self.driver.find('.selected').next()
        self.assertEquals(node.text, '4')

    def test_prev(self):
        node = self.driver.find('.selected').prev()
        self.assertEquals(node.text, '2')

    def test_next_all(self):
        nodes = self.driver.find('.selected').next_all()
        text = [node.text for node in nodes]
        self.assertEquals(text, ['4', '5'])

    def test_prev_all(self):
        nodes = self.driver.find('.selected').prev_all()
        text = [node.text for node in nodes]
        self.assertEquals(text, ['1', '2'])

    def test_siblings(self):
        nodes = self.driver.find('.selected').siblings()
        text = [node.text for node in nodes]
        self.assertEquals(text, ['1', '2', '4', '5'])


class FilteringTests(WebDriverPlusTests):
    def setUp(self):
        super(FilteringTests, self).setUp()
        snippet = """<ul>
                         <li>1</li>
                         <li>2</li>
                         <li class="selected">3</li>
                         <li>4</li>
                         <li class="selected">5</li>
                     </ul>"""
        self.driver.open(snippet)

    def test_filter(self):
        nodes = self.driver.find('li').filter('.selected')
        self.assertEquals([node.text for node in nodes], ['3', '5'])

    def test_exclude(self):
        nodes = self.driver.find('li').exclude('.selected')
        self.assertEquals([node.text for node in nodes], ['1', '2', '4'])


class ShortcutTests(WebDriverPlusTests):
    def setUp(self):
        super(ShortcutTests, self).setUp()
        snippet = """<ul>
                         <li>1</li>
                         <li>2</li>
                         <li class="selected">3</li>
                         <li>4</li>
                         <li>5</li>
                     </ul>"""
        self.driver.open(snippet)

    def test_index(self):
        node = self.driver.find('.selected')
        self.assertEquals(node.index, 2)

    def test_html(self):
        node = self.driver.find('.selected')
        self.assertEquals(node.html, '<li class="selected">3</li>')

    def test_inner_html(self):
        node = self.driver.find('.selected')
        self.assertEquals(node.inner_html, '3')


class InspectionTests(WebDriverPlusTests):
    def setUp(self):
        super(InspectionTests, self).setUp()
        snippet = """<html>
                         <head>
                             <style type="text/css">
                                 .selected {color: red}
                                 img {width: 100px; height: 50px;}
                             </style>
                         </head>
                         <body>
                             <img src='#' width='100px' height='50px'>
                             <ul style="color: blue">
                                 <li>1</li>
                                 <li>2</li>
                                 <li class="selected">3</li>
                                 <li>4</li>
                                 <li>5</li>
                             </ul>
                         </body>
                     </html>"""
        self.driver.open(snippet)

    def test_get_style_inline(self):
        elem = self.driver.find('ul')
        self.assertTrue(elem.style.color in (
            '#0000ff',
            'blue',
            'rgb(0, 0, 255)',
            'rgb(0,0,255)',
            'rgba(0, 0, 255, 1)',
            'rgba(0,0,255,1)',
        ))

    def test_get_style_css(self):
        elem = self.driver.find('.selected')
        self.assertTrue(elem.style.color in (
            '#ff0000',
            'red',
            'rgb(255, 0, 0)',
            'rgb(255,0,0)',
            'rgba(255, 0, 0, 1)',
            'rgba(255,0,0,1)',
        ))

    def test_set_style(self):
        elem = self.driver.find('.selected')
        elem.style.color = 'green'
        self.assertTrue(elem.style.color in (
            '#008000',
            'green',
            'rgb(0, 128, 0)',
            'rgb(0,128,0)',
            'rgba(0, 128, 0, 1)',
            'rgba(0,128,0,1)',
        ))

    def test_size(self):
        elem = self.driver.find('img')
        self.assertEquals(elem.size.width, 100)
        self.assertEquals(elem.size.height, 50)

    def test_size_unpacked(self):
        (width, height) = self.driver.find('img').size
        self.assertEquals(width, 100)
        self.assertEquals(height, 50)

    def test_attributes(self):
        elem = self.driver.find('img')
        self.assertEquals(elem.attributes,
                          {'width': '100px', 'height': '50px', 'src': '#'})
        self.assertEquals(set(elem.attributes.keys()),
                          set(['width', 'height', 'src']))
        self.assertEquals(set(elem.attributes.values()),
                          set(['100px', '50px', '#']))

    def test_get_attribute(self):
        elem = self.driver.find('img')
        self.assertEquals(elem.attributes['width'], '100px')

    def test_set_attribute(self):
        elem = self.driver.find('img')
        elem.attributes['width'] = '33px'
        self.assertEquals(elem.attributes['width'], '33px')

    def test_del_attribute(self):
        elem = self.driver.find('img')
        del elem.attributes['src']
        self.assertEquals(elem.attributes,
                          {'width': '100px', 'height': '50px'})


class FormInspectionTests(WebDriverPlusTests):
    def setUp(self):
        super(FormInspectionTests, self).setUp()
        snippet = """<html>
                         <form>
                             <select>
                                 <option selected>Walk</option>
                                 <option>Cycle</option>
                                 <option>Drive</option>
                             </select>
                             <fieldset>
                                 <input type="checkbox" value="peanuts" />
                                 I like peanuts
                             </fieldset>
                             <fieldset>
                                 <input type="checkbox" value="jam" checked />
                                 I like jam
                             </fieldset>
                         </form>
                     </html>"""
        self.driver.open(snippet)

    def test_is_selected(self):
        elem = self.driver.find('form')
        self.assertEquals(elem.find(text='Walk').is_selected, True)
        self.assertEquals(elem.find(text='Cycle').is_selected, False)
        self.assertEquals(elem.find(text='Drive').is_selected, False)

    def test_is_checked(self):
        elem = self.driver.find('form')
        self.assertEquals(elem.find(value='peanuts').is_checked, False)
        self.assertEquals(elem.find(value='jam').is_checked, True)


class ValueTests(WebDriverPlusTests):
    def setUp(self):
        super(ValueTests, self).setUp()
        snippet = """<form>
                         <input type="text" name="username" value="mike">
                     </form>"""
        self.driver.open(snippet)

    def test_get_value(self):
        pass

    def test_set_value(self):
        pass


class InputTests(WebDriverPlusTests):
    def setUp(self):
        super(InputTests, self).setUp()
        snippet = """<form>
                         <input type="text" name="username" value="mike">
                     </form>"""
        self.driver.open(snippet)

    def test_send_keys(self):
        elem = self.driver.find('input')
        elem.send_keys("hello")


class SetTests(WebDriverPlusTests):
    def setUp(self):
        super(SetTests, self).setUp()
        snippet = """<ul>
                         <li>1</li>
                         <li>2</li>
                         <li>3</li>
                         <li>4</li>
                         <li>5</li>
                     </ul>
                     <ul>
                         <li>a</li>
                         <li>b</li>
                         <li>c</li>
                     </ul>"""
        self.driver.open(snippet)

    def test_set_uniqueness(self):
        nodes = self.driver.find('li')
        self.assertEquals(len(nodes), 8)
        self.assertEquals(len(nodes.parent()), 2)


class ActionTests(WebDriverPlusTests):
    # TODO: Urg.  Refactor these
    def test_click(self):
        js = "document.getElementById('msg').innerHTML = 'click'"
        snippet = "<div id='msg'></div><a onclick=\"%s\">here</a>" % js
        self.driver.open(snippet).find('a').click()
        self.assertEquals(self.driver.find(id='msg').text, 'click')

    def test_double_click(self):
        js = "document.getElementById('msg').innerHTML = 'double click'"
        snippet = "<div id='msg'></div><a onDblclick=\"%s\">here</a>" % js
        self.driver.open(snippet).find('a').double_click()
        self.assertEquals(self.driver.find(id='msg').text, 'double click')

    def test_context_click(self):
        js = "document.getElementById('msg').innerHTML = event.button;"
        snippet = "<div id='msg'></div><a oncontextmenu=\"%s\">here</a>" % js
        self.driver.open(snippet).find('a').context_click()
        self.assertEquals(self.driver.find(id='msg').text, '2')
        # context menu stays open, so close it
        self.driver.find('body').send_keys(Keys.ESCAPE)

    def test_click_and_hold(self):
        js = "document.getElementById('msg').innerHTML = 'mouse down'"
        snippet = "<div id='msg'></div><a onMouseDown=\"%s\">here</a>" % js
        self.driver.open(snippet).find('a').click_and_hold()
        self.assertEquals(self.driver.find(id='msg').text, 'mouse down')

    def test_release(self):
        js = "document.getElementById('msg').innerHTML = 'mouse up'"
        snippet = "<div id='msg'></div><a onMouseUp=\"%s\">here</a>" % js
        elem = self.driver.open(snippet).find('a')
        elem.click_and_hold()
        self.assertEquals(self.driver.find(id='msg').text, '')
        elem.release()
        self.assertEquals(self.driver.find(id='msg').text, 'mouse up')

    def test_move_to(self):
        js = "document.getElementById('msg').innerHTML = 'mouse over'"
        snippet = "<div id='msg'></div><a onMouseOver=\"%s\">here</a>" % js
        self.driver.open(snippet).find('a').move_to()
        self.assertEquals(self.driver.find(id='msg').text, 'mouse over')

    def test_check_unchecked(self):
        snippet = "<form><input type='checkbox' id='cbx'> Checkbox</form>"
        self.driver.open(snippet).find('#cbx').check()
        self.assertEquals(self.driver.find('#cbx').get_attribute('checked'), 'true')

    def test_check_checked(self):
        snippet = "<form><input type='checkbox' id='cbx' checked='checked'> Checkbox</form>"
        self.driver.open(snippet).find('#cbx').check()
        self.assertEquals(self.driver.find('#cbx').get_attribute('checked'), 'true')

    def test_uncheck_unchecked(self):
        snippet = "<form><input type='checkbox' id='cbx'> Checkbox</form>"
        self.driver.open(snippet).find('#cbx').uncheck()
        self.assertEquals(self.driver.find('#cbx').get_attribute('checked'), None)

    def test_uncheck_checked(self):
        snippet = "<form><input type='checkbox' id='cbx' checked='checked'> Checkbox</form>"
        self.driver.open(snippet).find('#cbx').uncheck()
        self.assertEquals(self.driver.find('#cbx').get_attribute('checked'), None)

    #def test_submit(self):
    #    js = "document.getElementById('msg').innerHTML = 'submit'"
    #    snippet = "<div id='msg'></div><form onSubmit=\"%s\"><input></input></form>" % js
    #    self.driver.open(snippet).find('input').submit()
    #    self.assertEquals(self.driver.find(id='msg').text, 'submit')

    #def test_submit(self):
    #    snippet = "<form onSubmit=\"alert('submit')\"><input></input></form>"
    #    self.driver.open(snippet).find('input').submit()
    #    self.assertEquals(self.driver.alert.text, 'submit')


WAIT_SNIPPET = """<html>
    <head>
        <script type="text/javascript">
addTextLater = function() {
    setTimeout(addText, 100);
}
addText = function () {
    var txtNode = document.createTextNode("Hello World!");
    var p = document.getElementById("mypara");
    p.appendChild(txtNode);
}
        </script>
    </head>
    <body onload="addTextLater();">
        <p id="mypara"></p>
    </body>
</html>"""


class WaitTests(WebDriverPlusTests):
    extra_webdriver_kwargs = {'wait': 10}

    def setUp(self):
        super(WaitTests, self).setUp()
        snippet = WAIT_SNIPPET
        self.driver.open(snippet)

    def test_element_added_after_load_found(self):
        nodes = self.driver.find('p', text_contains='Hello World')
        self.assertEquals(len(nodes), 1)


class NoWaitTests(WebDriverPlusTests):
    def setUp(self):
        super(NoWaitTests, self).setUp()
        snippet = WAIT_SNIPPET
        self.driver.open(snippet)

    def test_element_added_after_load_not_found(self):
        nodes = self.driver.find('p', text_contains='Hello World')
        self.assertEquals(len(nodes), 0)


if __name__ == '__main__':
    try:
        sys.argv.remove('--all')
    except:
        pass

    try:
        idx = sys.argv.index('--browser')
        browser = sys.argv[idx + 1]
        sys.argv.pop(idx)
        sys.argv.pop(idx)
    except:
        pass

    # If --headless argument is given, run headless in virtual session
    # using Xvfb or Xvnc.
    try:
        sys.argv.remove('--headless')
    except ValueError:
        pass
    else:
        try:
            from pyvirtualdisplay import Display
            from easyprocess import EasyProcessCheckInstalledError
        except ImportError:
            print 'Error: --headless mode requires pyvirtualdisplay'
            sys.exit(2)
        try:
            display = Display(visible=0, size=(800, 600))
        except EasyProcessCheckInstalledError:
            print ('Error: Could not initialize virtual display. '
                   'Is either Xvfb or Xvnc installed?')
            sys.exit(2)
        print 'Running tests in headless mode.'
        display.start()

    unittest.main()

    if 'display' in locals():
        display.stop()
