
import configobj
from configobj import ConfigObjError

configobj.DEFAULT_INDENT_TYPE = '\t'


class Config(configobj.ConfigObj):
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, list_values=False, **kwargs)
        self.indent_type = None

    def section(self, name, side=None):
        if side is not None:
            if '"' in side:
                raise ConfigObjError('Side %r cannot be quoted.' % side)
            name = '%s "%s"' % (name, side)
        if name not in self:
            self[name] = {}
        return self[name]
