from banal import ensure_dict
from memorious.operations.store import directory as memorious_store

from ..incremental import skip_incremental


def store(context, data):
    """
    an extended store to be able to set skip_incremental
    """
    memorious_store(context, data)
    incremental = ensure_dict(data.get("skip_incremental"))
    if incremental.get("target") == context.stage.name:
        if incremental.get("key") is not None:
            context.set_tag(incremental["key"], True)
    # during testing mode, this will end the scraper, if store stage is set as target
    skip_incremental(context, data)
