from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement as _WebElement

from webdriverplus.actionchains import ActionChains
from webdriverplus.selectors import SelectorMixin
from webdriverplus.utils import get_terminal_size
from webdriverplus.wrappers import Style, Attributes, Size, Location

import os
import sys


class ParentProxy(object):
    """ We want to use the name 'parent', for traversal, but this hides
        the default WebElement property. We use a proxy so that _calling
        parent does the traversal while allowing _WebElement to use parent
        to access the WebDriver
    """
    def __init__(self, _webelement):
        self._webelement = _webelement

    def __call__(self, *args, **kwargs):
        return self._webelement._traversal_parent(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._webelement._parent, name)


class WebElement(SelectorMixin, _WebElement):
    @property
    def _xpath_prefix(self):
        return './/*'

    @property
    def parent(self):
        """
        Note: We're overriding the default WebElement.parent behaviour here.
        (Normally .parent is a property that returns the WebDriver object.)
        """
        return ParentProxy(self)

    # Traversal
    def _traversal_parent(self, *args, **kwargs):
        ret = self.find(xpath='..')
        return ret.filter(*args, **kwargs)

    def children(self, *args, **kwargs):
        ret = self.find(xpath='./*')
        return ret.filter(*args, **kwargs)

    def descendants(self):
        return self.find(xpath='./descendant::*')

    def ancestors(self, *args, **kwargs):
        ret = self.find(xpath='./ancestor::*')
        return ret.filter(*args, **kwargs)

    def next(self, *args, **kwargs):
        ret = self.find(xpath='./following-sibling::*[1]')
        return ret.filter(*args, **kwargs)

    def prev(self, *args, **kwargs):
        ret = self.find(xpath='./preceding-sibling::*[1]')
        return ret.filter(*args, **kwargs)

    def next_all(self, *args, **kwargs):
        ret = self.find(xpath='./following-sibling::*')
        return ret.filter(*args, **kwargs)

    def prev_all(self, *args, **kwargs):
        ret = self.find(xpath='./preceding-sibling::*')
        return ret.filter(*args, **kwargs)

    def siblings(self, *args, **kwargs):
        ret = self.prev_all() | self.next_all()
        return ret.filter(*args, **kwargs)

    # Inspection & Manipulation
    @property
    def id(self):
        return self.get_attribute('id')

    @property
    def type(self):
        return self.get_attribute('type')

    @property
    def value(self):
        return self.get_attribute('value')

    @property
    def is_checked(self):
        return self.get_attribute('checked') is not None

    @property
    def is_selected(self):
        return super(WebElement, self).is_selected()

    @property
    def is_displayed(self):
        return super(WebElement, self).is_displayed()

    @property
    def is_enabled(self):
        return super(WebElement, self).is_enabled()

    @property
    def inner_html(self):
        return self.get_attribute('innerHTML')

    @property
    def html(self):
        # http://stackoverflow.com/questions/1763479/how-to-get-the-html-for-a-dom-element-in-javascript
        script = """
            var container = document.createElement("div");
            container.appendChild(arguments[0].cloneNode(true));
            return container.innerHTML;
        """
        return self._parent.execute_script(script, self)

    @property
    def index(self):
        return len(self.prev_all())

    @property
    def style(self):
        return Style(self)

    @property
    def size(self):
        val = super(WebElement, self).size
        return Size(val['width'], val['height'])

    @property
    def location(self):
        val = super(WebElement, self).location
        return Location(val['x'], val['y'])

    @property
    def attributes(self):
        return Attributes(self)

    def javascript(self, script):
        script = "return arguments[0].%s;" % script
        return  self._parent.execute_script(script, self)

    def jquery(self, script):
        script = "return $(arguments[0]).%s;" % script
        return  self._parent.execute_script(script, self)

    # Actions...
    def double_click(self):
        ActionChains(self._parent).double_click(self).perform()

    def context_click(self):
        ActionChains(self._parent).context_click(self).perform()

    def click_and_hold(self):
        ActionChains(self._parent).click_and_hold(self).perform()

    def release(self):
        ActionChains(self._parent).release(self).perform()

    def move_to(self):
        ActionChains(self._parent).move_to_element(self).perform()

    def check(self):
        if not self.is_checked:
            self.click()

    def uncheck(self):
        if self.is_checked:
            self.click()

    def __repr__(self):
        try:
            if os.isatty(sys.stdin.fileno()):
                try:
                    width = get_terminal_size()[0]
                except:
                    width = 80
            else:
                width = 80

            ret = self.html
            ret = ' '.join(ret.split())
            ret = ret.encode('utf-8')

            if len(ret) >= width - 2:
                ret = ret[:width - 5] + '...'
            #self.style.backgroundColor = '#f9edbe'
            #self.style.borderColor = '#f9edbe'
            #self.style.outline = '1px solid black'
            return ret
        except StaleElementReferenceException:
            return '<StaleElement>'

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        return self._id == other._id
