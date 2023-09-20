import sys

import PyInstaller.__main__

PyInstaller.__main__.run([
    '__main__.py',
    '--onefile',
    '--console',
    '-n',
    f'telegram-member-inviter-{sys.platform}',
    '--clean',
])
