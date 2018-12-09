 # coding: latin-1
import xbmc
from tstream import provider

PROVIDER_NAME = 'NewPCT1'
WEB_PAGE_BASE = 'http://descargas2020.com'

ITEM_PATTERN = r'<li>\t(.+?)</li>'
ITEM_SEARCH_PATTERN = r'<li(?:>\t| style)(.+?)</div> ?</li>'
LABEL_PATTERN = r'title="(?:Serie\ subtitulada|Serie |Descarga Serie HD |Ver online |Ver en linea |Descargar (?!Pelicula)|)(.+?)(?: gratis|torrent)?"'
TORRENT_PATTERN = r'<a\ href="(.+?)"'
REALTORRENT_PATTERN = r'window.location.href = "(.+?)";' #r'"(http://newpct1.com/descargar-torrent/.+?)"' #"<span id='content-torrent'>\t*<a href='(.+?)'"
ICON_PATTERN = 'img src="(.+?)"'
THUMBNAIL_PATTERN = 'img src="(.+?)"'
RATING_PATTERN = '<span property="v:average">(.+?)%</span>'
YEAR_PATTERN = '(?:A&ntilde;o: *(.+?)\.|A&ntilde;o<br />(.+?)<br />)'
COUNTRY_PATTERN = 'Pa&iacute;s: *(.+?)\.'
CAST_PATTERN = '(?:Interpretaci&oacute;n: *(.+?)\.|Reparto<br />(.+?)<br />)'
DIRECTOR_PATTERN = '(?:Direcci&oacute;n: *(.+?)\.|Director<br />(.+?)<br />)'
WRITER_PATTERN = '(?:Gui&oacute;n: ?(.+?)\.|Gui&oacute;n<br />(.+?)</div>)'
ORIGINALTITLE_PATTERN = 'T&iacute;tulo original: *(.+?)\.'
GENRE_PATTERN = '(?:G&eacute;nero: ?(.+?)\.|G&eacute;nero<br />(.+?)<br />)'
PLOT_PATTERN = "(?:Sinopsis<br /> *(.+?)|<div class='sinopsis'> *(.+?))</div>"
PLOTOUTLINE_PATTERN = "(?:Sinopsis<br /> *(.+?)|<div class='sinopsis'> *(.+?))</div>"

SEARCH_URI_BASE = 'POST@%s/buscar?q=%s' % (WEB_PAGE_BASE, '%s')
MOVIE_URI_BASE = '%s/peliculas/pg/1' % WEB_PAGE_BASE
TV_URI_BASE = '%s/series/' % WEB_PAGE_BASE
TV_HD_URI_BASE = '%s/series-hd/' % WEB_PAGE_BASE
TV_VO_URI_BASE = '%s/series-vo/' % WEB_PAGE_BASE

URI_PAGE_PATTERN = r'/pg/(\d+)'
URI_PAGE_PATTERN_EPISODES = r'/pg/(\d+)'
RESULTS_PER_PAGE = 79

def name():
    return PROVIDER_NAME

def init():
    items = []
    items.append(provider.getMenuItem('Buscar', '_input_search', SEARCH_URI_BASE))
    items.append(provider.getMenuItem('Series', 'init_tv', TV_URI_BASE))
    items.append(provider.getMenuItem('Peliculas', 'init_movies', MOVIE_URI_BASE))
     
    return items

def search(uri):
    xbmc.log('search: %s' % uri)
    patterns = {'item':ITEM_SEARCH_PATTERN, 'path':TORRENT_PATTERN, 'label':LABEL_PATTERN, 'icon':ICON_PATTERN, 'thumbnail':THUMBNAIL_PATTERN}
    items = provider.getItemsFromPattern(uri, patterns, URI_PAGE_PATTERN, False, 'get_torrent_search')
    #if len(items)>0 and len(items)<=30: items=items[:-1]
    
    if items:
        for item in items:
            if item['thumbnail'].find('/c/minis/')>=0:
                item['thumbnail'] = item['thumbnail'].replace('/c/minis/','/c/')
    
    return items
    
def init_tv(uri):
    items = []
    items.append(provider.getMenuItem('Series', 'init_tv_next', TV_URI_BASE))
    items.append(provider.getMenuItem('Series HD', 'init_tv_next_hd', TV_HD_URI_BASE))
    items.append(provider.getMenuItem('Series VO', 'init_tv_next_vo', TV_VO_URI_BASE))
        
    return items
    
def init_tv_next(uri):
    items = []
    items.append(provider.getMenuItem('A-Z', 'get_tv_az', uri))
    items.extend(get_tv(uri))
    return items

def init_tv_next_hd(uri):
    items = []
    items.append(provider.getMenuItem('A-Z', 'get_tv_hd_az', uri))
    items.extend(get_tv_hd(uri))
    return items

def init_tv_next_vo(uri):
    items = []
    items.append(provider.getMenuItem('A-Z', 'get_tv_vo_az', TV_VO_URI_BASE))
    items.extend(get_tv_vo(uri))
    return items
        
def init_movies(uri):
    items = []
    items.append(provider.getMenuItem('A-Z', 'get_movies_az', MOVIE_URI_BASE))
    items.extend(get_movies(MOVIE_URI_BASE))
    
    return items
    
def _get_tv(uri, pattern):
    patterns = {'item':ITEM_PATTERN, 'path':TORRENT_PATTERN, 'label':LABEL_PATTERN, 'icon':ICON_PATTERN, 'thumbnail':THUMBNAIL_PATTERN}
    items = provider.getItemsFromPattern(uri, patterns, URI_PAGE_PATTERN, False, pattern)
    #if len(items)>0 and len(items)<=RESULTS_PER_PAGE: items=items[:-1]
    
    return items
    
def get_tv(uri):
    return _get_tv(uri, 'get_tv_episodes')

def get_tv_hd(uri):
    return _get_tv(uri, 'get_tv_hd_episodes')
    
def get_tv_vo(uri):
    return _get_tv(uri, 'get_tv_vo_episodes')
    
def _get_tv_episodes(uri, pattern):
    xbmc.log('get_episodes: %s' % uri)
    if uri.find('/pg/')<0:
        uri = '%s/pg/1' % uri
    patterns = {'item':ITEM_SEARCH_PATTERN, 'path':TORRENT_PATTERN, 'label':LABEL_PATTERN, 'icon':ICON_PATTERN, 'thumbnail':THUMBNAIL_PATTERN}
    xbmc.log('URI IS %s NOW PATTERNS' % uri)
    items = provider.getItemsFromPattern(uri, patterns, URI_PAGE_PATTERN_EPISODES, True, 'get_torrent')
	
    return items
    
def get_tv_episodes(uri):
    xbmc.log('get_tv_episodes: %s' % uri)    	
    return _get_tv_episodes(uri, 'series')

def get_tv_hd_episodes(uri):
    xbmc.log('get_tv_hd_episodes: %s' % uri)    	
    return _get_tv_episodes(uri, 'series-hd')
    
def get_tv_vo_episodes(uri):
    xbmc.log('get_tv_vo_episodes: %s' % uri)    	
    return _get_tv_episodes(uri, 'series-vo')
 
def get_movies(uri):
    xbmc.log('get_movies: %s' % uri)
    patterns = {'item':ITEM_PATTERN, 'path':TORRENT_PATTERN, 'label':LABEL_PATTERN, 'icon':ICON_PATTERN, 'thumbnail':THUMBNAIL_PATTERN}
    items = provider.getItemsFromPattern(uri, patterns, URI_PAGE_PATTERN, True, 'get_torrent')
    #if len(items)>0 and len(items)<=RESULTS_PER_PAGE: items=items[:-1]
    
    return items
  
def get_torrent_search(path):
    xbmc.log('get_torrent_search: %s' % path)
    if '/series/' in path:
        return get_tv_episodes(path)
    if '/series-hd/' in path:
        return get_tv_hd_episodes(path)
    if '/series-vo/' in path:
        return get_tv_vo_episodes(path)
    
    return [provider.getItem(label='Play', path=path, isPlayable=True, callback='get_torrent', args=path)]
  
def get_torrent(path):        
    xbmc.log('URL ARGS: %s' % path)
    link = path #'%s/descarga-torrent%s' % (WEB_PAGE_BASE, path[path.find(WEB_PAGE_BASE)+len(WEB_PAGE_BASE):])
    xbmc.log('NEW URL ARGS: %s' % link)
    response = provider.GET(link)
    if response:
        link = provider.reSearch(response.data, REALTORRENT_PATTERN)
        #link = provider.reSearch(response.data, '"(http://tumejor.+?)"')
        xbmc.log('LINK: %s' % link)
    return link
    
def get_az(uri, pattern):
    items = []
    for letter in 'abcdefghijklmnopqrstuvwxyz':        
        link = '%s/%s/letter/%s/pg/1' % (WEB_PAGE_BASE, pattern, letter)
        items.append(provider.getItem(label=letter.upper(), path=link, callback='get_tv', args=link))
    
    return items
    
def get_tv_az(uri):
    return get_az(uri, 'series')

def get_tv_hd_az(uri):
    return get_az(uri, 'series-hd')    

def get_tv_vo_az(uri):
    return get_az(uri, 'series-vo')
   
def get_movies_az(uri):
    items = []
    for letter in 'abcdefghijklmnopqrstuvwxyz':        
        link = '%s/peliculas/letter/%s/pg/1' % (WEB_PAGE_BASE, letter)
        items.append(provider.getItem(label=letter.upper(), path=link, callback='get_movies', args=link))
    
    return items
    
def infoLabels(arg):
    patterns = {'rating':RATING_PATTERN, 'director':DIRECTOR_PATTERN, 'writer':WRITER_PATTERN, 'plot':PLOT_PATTERN, 'plotoutline':PLOTOUTLINE_PATTERN, 'year':YEAR_PATTERN, 'genre':GENRE_PATTERN, 'cast':CAST_PATTERN, 'orginaltitle':ORIGINALTITLE_PATTERN}
    
    return provider.getInfoLabelsFromPattern(arg, patterns)
    
def getInfoLabels(items):
    result = []
    try:
        from multiprocessing.pool import cpu_count
        from multiprocessing.pool import ThreadPool
        pool_size = cpu_count()*2
        pool = ThreadPool(processes=pool_size)
        args = []
        for item in items: args.append(item['path'])
        result = pool.map(infoLabels, args)
        pool.close()
        pool.join()
    except:    
        pass
    finally:        
        for i, infoLabel in enumerate(result):            
            items[i]['infoLabels'] = infoLabel
    
    return items