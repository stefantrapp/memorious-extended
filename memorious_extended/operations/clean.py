from banal import ensure_dict, ensure_list, is_mapping

from ..exceptions import MetaDataError
from ..util import casted_dict


def clean(context, data, emit=True):
    """
    clean and validate metadata and make sure it is as it is supposed to be

    params: (all optional)
        drop: <list of keys to delete>
        defaults:  # set some defaults if keys are empty
            key: value
        values: # rewrite some values in the data dict
            key:
                old value: new value
                ...
            another_key: <string to format from data dict>
        typing:
            ignore: <list of keys to not attempt type casting>
            dateparserkwargs: ...
        required: <list of keys to be required in data>
    """

    # drop keys
    for key in ensure_list(context.params.get("drop")):
        if key in data:
            del data[key]

    # set defaults
    for key, value in ensure_dict(context.params.get("defaults")).items():
        if key not in data:
            data[key] = value

    # rewrite values
    for key, values in ensure_dict(context.params.get("values")).items():
        if is_mapping(values):
            if data.get(key) in values:
                data[key] = values[data[key]]
        elif isinstance(values, str):
            data[key] = values.format(**data)

    # validate required
    for key in ensure_list(context.params.get("required")):
        if key not in data:
            context.emit_warning(MetaDataError(f"`{key}` not in data but required."))

    # typing
    typing = ensure_dict(context.params.get("typing"))
    if typing:
        data = casted_dict(
            data,
            ignore_keys=ensure_list(typing.get("ignore")),
            **ensure_dict(typing.get("dateparserkwargs")),
        )

    # emit to next stage or return
    if emit:
        context.emit(data=data)
    else:
        return data
