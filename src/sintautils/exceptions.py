"""
sintautils
Created by: Samarthya Lykamanuella
Establishment year: 2025

LICENSE NOTICE:
===============

This file is part of sintautils.

sintautils is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

sintautils is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along
with sintautils. If not, see <https://www.gnu.org/licenses/>.
"""


class SintaException(Exception):
    """ The super-class for all exceptions related to sintautils. This exception should not be called directly. """


class AuthorIDNotFoundException(SintaException):
    """ Error raised when the author ID specified is not found in the SINTA database. """
    
    def __init__(self, arg: str = ''):
        self.arg = arg
    
    def __repr__(self):
        return f'Cannot locate author ID {self.arg}.'
    
    __str__ = __repr__


class EmptyFieldException(SintaException):
    """ Error raised when there is no field selection in the scraper function passed. """

    def __init__(self, arg: str = ''):
        self.arg = arg

    def __repr__(self):
        return f'You must specify at least one of the following fields: {self.arg}. Use "*" to select all fields.'

    __str__ = __repr__


class InvalidAuthorIDException(SintaException):
    """ Error raised when the user specifies an invalid (i.e., non-numerical) author ID. """

    def __init__(self, arg: str = ''):
        self.arg = arg

    def __repr__(self):
        return f'Invalid author ID: {self.arg}. You must specify a valid, numerical author ID.'
    
    __str__ = __repr__


class InvalidLoginCredentialException(SintaException):
    """ Error raised when the wrong credentials are passed to the login functions in the scraper. """
    def __repr__(self):
        return 'Either your username or password cannot be used to perform the necessary login.'
    
    __str__ = __repr__


class InvalidParameterException(SintaException):
    """ Error raised when a function's parameter setting is not obeyed. """
    
    def __init__(self, arg: str = ''):
        self.arg = arg
    
    def __repr__(self):
        return f'Invaled parameter passed: {self.arg}.'
    
    __str__ = __repr__


class NonStringParameterException(SintaException):
    """ Error raised when non-string parameters are passed to the login function. """
    def __repr__(self):
        return 'You can only pass variables of type str to the method.'
    
    __str__ = __repr__


class NoLoginCredentialsException(SintaException):
    """ Error raised when a `sintautils.scraper.AV` object is created without providing the necessary credential
    information."""
    def __repr__(self):
        return 'You must provide username and password in order to use the AV scraper.'

    __str__ = __repr__


class MalformedDOMException(SintaException):
    """ DOM-related error raised when, e.g., there is an item element
    that does not have a particular property every other item has."""
    
    def __init__(self, arg: str = ''):
        self.arg = arg
    
    def __repr__(self):
        return f'Malformed DOM on URL: {self.arg}.'
    
    __str__ = __repr__
