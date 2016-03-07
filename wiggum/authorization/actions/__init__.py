
class WiggumActionContext(object):
    """ Object where actions will return and pass through the chain actions
        This object will say when the chain needs to break.
    """

    def __init__(self, request, response, extra_context=None,
                 break_chain=False):
        self.request = request
        self.response = response
        if not extra_context:
            extra_context = {}
        self.extra_context = extra_context
        self.break_chain = break_chain
