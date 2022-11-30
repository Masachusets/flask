import pydantic


class HttpError(Exception):

    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


def validate(data_to_validate: dict, validation_class):
    try:
        data_after_validate = validation_class(**data_to_validate).dict(exclude_none=True)
        return data_after_validate
    except pydantic.ValidationError as err:
        raise HttpError(400, err.errors())
