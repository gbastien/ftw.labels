from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.labels.interfaces import ILabelJar
from ftw.labels.interfaces import ILabelRoot
from plone.app.portlets.portlets.base import Renderer


class Renderer(Renderer):
    render = ViewPageTemplateFile('labeljar.pt')

    @property
    def available(self):
        return ILabelRoot.providedBy(self.context)

    @property
    def labels(self):
        return ILabelJar(self.context).list()
