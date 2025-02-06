# Please `cd` into the root folder of this repository
# before running this test script.

from getpass import getpass
import os

from src.sintautils import AV

env_keys = list(dict(os.environ).keys())
key_u = 'sintautils_av_username'
key_p = 'sintautils_av_password'

u = os.environ[key_u] if key_u in env_keys else input('AV Username: ')
p = os.environ[key_p] if key_p in env_keys else getpass('AV Password: ')
id_1 = input('Specify Author ID 1: ')
id_2 = input('Specify Author ID 2: ')

x = AV(u, p)
x.verbosity = 2
x.login()
x.dump_author(id_1, fields='scopus')
x.dump_author(id_2, fields='ipr', use_fullname_prefix=False)
