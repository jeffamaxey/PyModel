"""
pymodel configuration: rebind WebModel StateFilter
"""

import WebModel

def OneUserLoggedIn():
    return WebModel.usersLoggedIn in [[], [ 'VinniPuhh' ]]

WebModel.StateFilter = OneUserLoggedIn
