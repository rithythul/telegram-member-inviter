import PyInstaller.__main__

PyInstaller.__main__.run([
    'bot.py',
    '--onefile',
    '--console',
    '-n',
    'telegram-member-inviter',
    '--clean',
])
