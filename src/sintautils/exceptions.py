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

class InvalidLoginCredentialException(SintaException):
    """ Error raised when the wrong credentials are passed to the login functions in the scraper. """
    def __repr__(self):
        return 'InvalidLoginCredentialException: Either your username or password cannot be used to perform the necessary login.'
    
    __str__ = __repr__

class NonStringParameterException(SintaException):
    """ Error raised when non-string parameters are passed to the login function. """
    def __repr__(self):
        return 'NonStringParameterException: You can only pass variables of type str to the method.'
    
    __str__ = __repr__

class NoLoginCredentialsException(SintaException):
    """ Error raised when a `sintautils.scraper.AV` object is created without providing the necessary credential information. """
    def __repr__(self):
        return 'NoLoginCredentialsException: You must provide username and password in order to use the AV scraper.'

    __str__ = __repr__
