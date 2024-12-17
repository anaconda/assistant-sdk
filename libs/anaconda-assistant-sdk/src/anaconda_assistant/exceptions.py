class AnacondaAssistantError(Exception):
    pass


class NotAcceptedTermsError(AnacondaAssistantError):
    pass


class UnspecifiedAcceptedTermsError(AnacondaAssistantError):
    pass


class UnspecifiedDataCollectionChoice(AnacondaAssistantError):
    pass
