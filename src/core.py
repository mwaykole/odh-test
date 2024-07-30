from src.carteplex import Carteplex
from src.colorfiable import Colorfiable
from src.configurable import Configurable
from src.loggable import Loggable


class OdhAssess(Colorfiable, Loggable, Configurable, Carteplex):
    # Templatable, Unittestable, Restable, Rpycable, Carteplex):
    """The locker for all things odh."""
    # TODO: figure out how we want to do this with cli options
    # TODO: call this after configs are read to be more effective
    # TODO: do this by default or force to be from main() or other importer
    # create default log
    log = Loggable.create_log()
