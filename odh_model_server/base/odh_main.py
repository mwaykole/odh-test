from odh.odhlibs.loggable import Loggable


class Odh(Loggable):
    def __init_subclass__(cls, **kwargs):
        """Automatically initialize the logger when the subclass is created."""
        super().__init_subclass__(**kwargs)
        # Initialize the logger for the test class
        cls.log = cls.create_log(name=f'{cls.__name__}Log', filename='/tmp/odh_test.log', level='DEBUG')
        cls.log.info(f"Logger initialized for {cls.__name__}")
