# -*- mode: python -*-

block_cipher = None


a = Analysis(['avenew.py'],
             pathex=['D:\\avenew'],
             binaries=[],
             datas=[],
             hiddenimports=["anymail.apps", "anymail.inbound", "anymail.message", "anymail.signals", "Cookie", "django.contrib.sessions.apps", "django.contrib.sites.apps", "django.contrib.staticfiles.apps", "django.template.loader_tags", "django.template.defaulttags", "evennia.commands.command", "evennia.commands.cmdparser", "evennia.prototypes.protfuncs", "evennia.server.inputfuncs", "evennia.settings_default", "evennia.web.webclient", "evennia.web.website", "evennia_wiki", "os.path", "requests", "sekizai", "twisted.scripts.twistd", "web.builder", "web.evapp", "web.help_system", "web.mailgun.apps", "web.text", "world.prototypes"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='avenew',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='avenew')
