"""
Helper methods for dealing with Polarion XML files before
sending them to the Polarion Importer.
"""

import xml.etree.ElementTree as ElTree
from typing import List


class PolarionXmlUtils(object):
    """
    Provides utility methods for manipulating specific elements
    on a Polarion XML file that is being prepared to be sent out to
    Polarion importer.
    """

    @staticmethod
    def new_linked_work_item(
            linked_work_item_parent: ElTree.Element,
            workitem_id: str,
            role_id: str = 'verifies') -> None:
        """
        Creates sub-element named 'linked-work-item' within the given
        'linked-work-items' parent. It will also set the 'workitem-id'
        property using the id value provided.
        :param linked_work_item_parent:
        :param workitem_id:
        :param role_id:
        :return:
        """
        if workitem_id is None:
            return
        sub_elem = ElTree.SubElement(linked_work_item_parent,
                                     'linked-work-item')
        sub_elem.set('workitem-id', workitem_id)
        sub_elem.set('lookup-method', 'id')
        sub_elem.set('role-id', role_id)

    @staticmethod
    def new_custom_field(custom_fields_parent: ElTree.Element,
                         id_field: str, content: str) -> None:
        """
        Creates sub-element named 'custom-field' within the given 'custom-fields' parent.
        It will also set the 'id' and 'content' attributes on the 'custom-field' element.
        TODO Generalize and use dictionary
        :param custom_fields_parent:
        :param id_field:
        :param content:
        :return:
        """
        if content is None:
            return
        sub_elem = ElTree.SubElement(custom_fields_parent, 'custom-field')
        sub_elem.set('id', id_field)
        sub_elem.set('content', content)

    @staticmethod
    def new_test_step(test_steps_parent: ElTree.Element,
                      step: str, result: str) -> None:
        """
        Create a test-step element within the provided test-steps (parent) and inside of
        it, two child elements named test-step-column will be created. The first one with
        id = "step" and the second with id = "expectedResult". The value of each element
        will be populated accordingly.
        TODO Generalize and use dictionary
        :param test_steps_parent:
        :param step:
        :param result:
        :return:
        """
        if step is None:
            return

        # The test-step that holds step and expectedResult
        test_step = ElTree.SubElement(test_steps_parent, 'test-step')

        # Step element
        step_elem = ElTree.SubElement(test_step, 'test-step-column')
        step_elem.set('id', 'step')
        step_elem.text = step

        # Expected result element
        result_elem = ElTree.SubElement(test_step, 'test-step-column')
        result_elem.set('id', 'expectedResult')
        result_elem.text = result

    @staticmethod
    def new_test_step_params(test_steps_parent: ElTree.Element,
                             params: List[str], scope: str = "local") -> None:
        if params is None:
            return

        # The test-step that holds all test parameters
        test_step = ElTree.SubElement(test_steps_parent, 'test-step')

        # Step element
        step_elem = ElTree.SubElement(test_step, 'test-step-column', id='step')
        step_elem.text = 'Parameters: '
        for (idx, param) in enumerate(params):
            param_elem = ElTree.Element("parameter", name=param, scope=scope)
            if idx > 0:
                step_elem.text += ", "
            step_elem.text += param
            step_elem.append(param_elem)
        step_elem.text += " => "

    @staticmethod
    def new_property_sub_element(parent: ElTree.Element, name: str, value: str) -> None:
        """
        Creates sub-element named 'property' within the given parent.
        It will also set the 'name' and 'value' attributes on the 'property' element.
        :param parent:
        :param name:
        :param value:
        :return:
        """
        if value is None:
            return
        sub_elem = ElTree.SubElement(parent, 'property')
        sub_elem.set('name', name)
        sub_elem.set('value', value)
