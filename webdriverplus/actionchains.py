from selenium.webdriver.common.action_chains import ActionChains as _ActionChains


class WebElementCompat(object):
    """ WebElement wrapper to expose the (selenium) id property

        action chains only need the id property and nothing else
    """

    def __init__(self, element):
        try:
            self._id = element._first._id  # WebElementSet
        except AttributeError:
            self._id = element._id  # WebElement

    @property
    def id(self):
        return self._id


class ActionChains(_ActionChains):
    """ WebElement hides the "id" property of elements (with the html id)
        so we need to manually unhide this to use action chains
    """

    def move_to_element(self, to_element):
        wrapped_el = WebElementCompat(to_element)
        return super(ActionChains, self).move_to_element(wrapped_el)

    def move_to_element_with_offset(self, to_element, xoffset, yoffset):
        wrapped_el = WebElementCompat(to_element)
        return super(ActionChains, self).move_to_element_with_offset(
            wrapped_el, xoffset, yoffset)


