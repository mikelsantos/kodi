import xbmc, xbmcaddon
import sys, tempfile, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))
from tstream import navigation

ADDON = xbmcaddon.Addon()
CLEANUP = bool(ADDON.getSetting('cleanup'))
TORRENT_TEMP_DIR = ADDON.getSetting('temp_dir_path')

xbmc.log('TORRENT_TEMP_DIR IS %s' % TORRENT_TEMP_DIR)

if not TORRENT_TEMP_DIR:
    try:
        TORRENT_TEMP_DIR = tempfile.gettempdir()
        ADDON.setSetting('temp_dir_path', TORRENT_TEMP_DIR)
    except Exception as e:
        xbmc.log(str(e))
        pass

if TORRENT_TEMP_DIR and not TORRENT_TEMP_DIR.endswith('torrent-stream'):
    try:
        download_path = os.path.join(TORRENT_TEMP_DIR, 'torrent-stream')
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        ADDON.setSetting('temp_dir_path', download_path)
    except Exception as e:
        xbmc.log(str(e))
        pass

if TORRENT_TEMP_DIR and TORRENT_TEMP_DIR.endswith('torrent-stream') and CLEANUP:
    try:
        import shutil
        xbmc.log('REMOVING: %s' % TORRENT_TEMP_DIR)
        shutil.rmtree(TORRENT_TEMP_DIR, True)
        xbmc.log('REMOVAL OK')
    except Exception as e:
        xbmc.log('REMOVAL FAILED')
        xbmc.log(str(e))
        pass

navigation.run()
