from ftw.labels.interfaces import ILabelJar
from ftw.labels.interfaces import ILabelRoot
from ftw.labels.interfaces import ILabelSupport
from ftw.labels.interfaces import ILabeling
from ftw.labels.testing import ADAPTERS_ZCML_LAYER
from ftw.testing import MockTestCase
from zope.annotation import IAttributeAnnotatable
from zope.component import queryAdapter


class TestLabeling(MockTestCase):
    layer = ADAPTERS_ZCML_LAYER

    def setUp(self):
        super(TestLabeling, self).setUp()
        self.root = self.providing_stub([ILabelRoot, IAttributeAnnotatable])
        self.document = self.providing_stub([ILabelSupport,
                                             IAttributeAnnotatable])
        self.set_parent(self.document, self.root)
        self.replay()
        self.jar = ILabelJar(self.root)

    def test_adapter(self):
        self.assertTrue(
            queryAdapter(self.document, ILabeling),
            'The labeling adapter is not registered for ILabeling')

    def test_available_labels(self):
        self.jar.add('Question', '#00FF00')
        labeling = ILabeling(self.document)
        self.assertEqual(
            [{'label_id': 'question',
             'title': 'Question',
             'color': '#00FF00',
             'active': False}],
            list(labeling.available_labels()))

    def test_available_labels_empty(self):
        labeling = ILabeling(self.document)
        self.assertEqual([], list(labeling.available_labels()))

    def test_activate_label(self):
        self.jar.add('Question', '#00FF00')
        labeling = ILabeling(self.document)

        labeling.activate('question')
        self.assertEqual(
            [{'label_id': 'question',
              'title': 'Question',
              'color': '#00FF00',
              'active': True}],
            list(labeling.available_labels()))

    def test_activate_multiple_labels(self):
        self.jar.add('Question', '')
        self.jar.add('Bug', '')
        self.jar.add('Duplicate', '')
        labeling = ILabeling(self.document)

        labeling.activate('question', 'duplicate')
        self.assertItemsEqual(
            [{'label_id': 'question',
              'title': 'Question',
              'color': ''},
             {'label_id': 'duplicate',
              'title': 'Duplicate',
              'color': ''}],
            list(labeling.active_labels()))

    def test_activate_raises_LookupError_when_label_not_in_jar(self):
        self.assertEqual(0, len(self.jar.list()))
        labeling = ILabeling(self.document)
        with self.assertRaises(LookupError) as cm:
            labeling.activate('something')

        self.assertEqual(
            'Cannot activate label: the label'
            ' "something" is not in the label jar.',
            str(cm.exception))

    def test_deactivate_label(self):
        self.jar.add('Question', '')
        labeling = ILabeling(self.document)

        labeling.activate('question')
        self.assertEqual(1, len(labeling.active_labels()))

        labeling.deactivate('question')
        self.assertEqual(0, len(labeling.active_labels()))

    def test_deactivate_multiple_labels(self):
        self.jar.add('Question', '')
        self.jar.add('Bug', '')
        self.jar.add('Duplicate', '')
        labeling = ILabeling(self.document)

        labeling.activate('question', 'bug', 'duplicate')
        self.assertEqual(3, len(labeling.active_labels()))

        labeling.deactivate('question', 'bug')
        self.assertEqual(1, len(labeling.active_labels()))

    def test_active_labels(self):
        self.jar.add('Question', '')
        self.jar.add('Bug', '')
        self.jar.add('Duplicate', '')

        labeling = ILabeling(self.document)
        labeling.activate('bug')
        self.assertEqual(
            [{'label_id': 'bug',
              'title': 'Bug',
              'color': ''}],
            labeling.active_labels())

    def test_active_labels_is_sorted(self):
        self.jar.add('Zeta', '')
        self.jar.add('alpha', '')
        self.jar.add('\xc3\x84lpha', '')
        self.jar.add('Alpha', '')
        self.jar.add('\xc3\xa4lpha', '')

        labeling = ILabeling(self.document)
        labeling.activate(
            'zeta',
            'zeta-1',
            'alpha',
            'alpha-1',
            'alpha-2',
            'a-lpha',
            )

        self.assertEqual(
            [
                'alpha',
                '\xc3\xa4lpha',
                'Alpha',
                '\xc3\x84lpha',
                'zeta',
                'Zeta'
            ],
            [label.get('title') for label in labeling.active_labels()])
