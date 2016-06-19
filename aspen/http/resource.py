from ..output import Output
from ..request_processor import dispatcher
from ..simplates.simplate import Simplate, SimplateException


class Static(object):
    """Model a static HTTP resource.
    """

    def __init__(self, request_processor, fspath, raw, media_type):
        assert type(raw) is bytes  # sanity check
        self.raw = raw
        self.media_type = media_type
        if media_type == 'application/json':
            self.media_type = request_processor.media_type_json
        self.charset = None
        if request_processor.charset_static:
            try:
                raw.decode(request_processor.charset_static)
                self.charset = request_processor.charset_static
            except UnicodeDecodeError:
                pass

    def render(self, context):
        return Output(body=self.raw, media_type=self.media_type, charset=self.charset)


class Dynamic(Simplate):
    """Model a dynamic HTTP resource using simplates.

       Make .request_processor available as it has been historically.

       Figure out which accept header to use.

    """

    def __init__(self, request_processor, fs, raw, default_media_type):
        self.request_processor = request_processor
        defaults = request_processor.simplate_defaults
        super(Dynamic, self).__init__(defaults, fs, raw, default_media_type)


    def render(self, state):
        accept = dispatch_accept = state['dispatch_result'].extra.get('accept')
        if accept is None:
            accept = state.get('accept_header')
        try:
            return super(Dynamic, self).render(accept, state)
        except SimplateException as e:
            # find an Accept header
            if dispatch_accept is not None:  # indirect negotiation
                raise dispatcher.IndirectNegotiationFailure()
            else:                            # direct negotiation
                message = "Couldn't satisfy %s. The following media types are available: %s."
                message %= (accept, ', '.join(e.available_types))
                raise dispatcher.DirectNegotiationFailure(message.encode('US-ASCII'))
