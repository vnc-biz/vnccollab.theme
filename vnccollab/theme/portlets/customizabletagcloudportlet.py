from collective.vaporisation.portlets.customizabletagcloudportlet import Renderer as BaseRenderer
from vnccollab.theme import messageFactory as _


class Renderer(BaseRenderer):
    def Title(self):
        print type(self.data.name), self.data.name, _(self.data.name)
        return _(self.data.name)
