# coding: latin-1
import xbmc
from tstream import provider

PROVIDER_NAME = 'ZonaTorrent'
WEB_PAGE_BASE = 'https://zonatorrent.tv'

ITEM_PATTERN = r'<li class="TPostMv">(.+?)</li>'
LABEL_PATTERN = r'<div class="Title">(.+?)(Español Torrent|Online Torrent)?</div>'
TORRENT_PATTERN = r'<a href="(.+?)" rel="bookmark">'
ICON_PATTERN = 'src="(.+?)"'
THUMBNAIL_PATTERN = 'src="(.+?)"'
LINK_PATTERN = '<a rel="nofollow" target="_blank" href="(.+?\.torrent)" class="Button STPb torrent-movie">Download</a>'

SERIES_ITEM_PATTERN = r'<tr><td>(.+?)</td></tr>'
SERIES_LABEL_PATTERN = r'<td class="MvTbTtl"><a href=".+?">(.+?)</a>'
SERIES_TORRENT_PATTERN = r'<td class="MvTbTtl"><a href="(.+?)">'
SERIES_ICON_PATTERN = 'src="(.+?)"'
SERIES_THUMBNAIL_PATTERN = 'src="(.+?)"'

PLOT_PATTERN = '<div class="Description"><p>(.+?)</p>'
PLOTOUTLINE_PATTERN = '<div class="Description"><p>(.+?)</p>'

SEARCH_URI_BASE = '%s/?s=%s' % (WEB_PAGE_BASE, '%s')
TV_URI_BASE = '%s/serie/page/1' % WEB_PAGE_BASE
MOVIE_URI_BASE = '%s/pelicula/page/1' % WEB_PAGE_BASE

URI_PAGE_PATTERN = r'.+/page/(\d+)$'
RESULTS_PER_PAGE = 20

def name():
    return PROVIDER_NAME

def init():
    items = []
    items.append(provider.getMenuItem('Buscar', '_input_search', SEARCH_URI_BASE))
    items.append(provider.getMenuItem('Series', 'get_tv', TV_URI_BASE))
    items.append(provider.getMenuItem('Peliculas', 'search', MOVIE_URI_BASE))
    
    return items
    
def search(args):
    patterns = {'item':ITEM_PATTERN, 'path':TORRENT_PATTERN, 'label':LABEL_PATTERN, 'icon':ICON_PATTERN, 'thumbnail':THUMBNAIL_PATTERN}
    items = provider.getItemsFromPattern(args, patterns, URI_PAGE_PATTERN, True, 'get_torrent')
    if len(items)<=RESULTS_PER_PAGE: items=items[:-1]

    if items:
        for item in items:
            if item['icon'].startswith('//'):
                item['icon'] = 'https://%s' % item['icon'][2:]
            if item['thumbnail'].startswith('//'):
                item['thumbnail'] = 'https://%s' % item['thumbnail'][2:]
	
    return items

def get_tv(uri):
    xbmc.log('get_tv: %s' % uri)
    patterns = {'item':ITEM_PATTERN, 'path':TORRENT_PATTERN, 'label':LABEL_PATTERN, 'icon':ICON_PATTERN, 'thumbnail':THUMBNAIL_PATTERN}
    items = provider.getItemsFromPattern(uri, patterns, URI_PAGE_PATTERN, False, 'get_episodes')
    if len(items)<=RESULTS_PER_PAGE: items=items[:-1]

    if items:
        for item in items:
            if item['icon'].startswith('//'):
                item['icon'] = 'https://%s' % item['icon'][2:]
            if item['thumbnail'].startswith('//'):
                item['thumbnail'] = 'https://%s' % item['thumbnail'][2:]
	
    return items
    
def get_episodes(uri):
    xbmc.log('get_episodes: %s' % uri)
    patterns = {'item':SERIES_ITEM_PATTERN, 'path':SERIES_TORRENT_PATTERN, 'label':SERIES_LABEL_PATTERN, 'icon':SERIES_ICON_PATTERN, 'thumbnail':SERIES_THUMBNAIL_PATTERN}
    items = provider.getItemsFromPattern(uri, patterns, URI_PAGE_PATTERN, True, 'get_torrent')
    
    return items

def get_torrent(path):    
    xbmc.log('URL ARGS: %s' % path)
    link = path
    response = provider.GET(link)
    if response:
        link = provider.reSearch(response.data, LINK_PATTERN)
        xbmc.log('LINK: %s' % link)
    
    return link
    
def infoLabels(arg):
    patterns = {'plot':PLOT_PATTERN, 'plotoutline':PLOTOUTLINE_PATTERN}
    return provider.getInfoLabelsFromPattern(arg, patterns)