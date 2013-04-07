import urllib2 as ul
import libtorrent as lt
import time
import sys
import tempfile
import shutil


def unicast_download( url, save_dir='./', chunk_size=10*1024*1024 ): # 10 MB chunk size for default setting
    filename = url.split('/')[-1]
    fullpath = save_dir + filename
    try:
        req = urllib2.urlopen( url )
        total_size = int( req.info().getheader('Content-Length').strip() )
        downloaded = 0
        with open( fullpath, 'w' ) as fp:
            while True:
                chunk = req.read( chunk_size )
                downloaded += len( chunk )
                if not chunk :
                    break
                progress_bar( downloaded/1000, total_size/1000, 'KB')
                fp.write(chunk)
        return True

    except ValueError as e:
        print("URL Error: %s" % url )
        return False
    except urllib2.HTTPError as r:
        print("HTTP Error: %s [%s]" % (r.reason, url))
        return False
    except urllib2.URLError as r:
        print("HTTP Error: %s [%s]" % (r.reason, url))
        return False


def bt_download( torrent_location, save_dir='./', seeding_time=0, debug=False, verbose=False ):
    is_url = False
    tmp_dir = None
    try:
        req = ul.urlopen( torrent_location ) # assume it is url
        tmp_dir = tempfile.mkdtemp()
        filename = tmp_dir + '/' + torrent_location.split('/')[-1]
        content = req.read()
        req.close()
        with open( filename, 'w' ) as f :
            f.write(content)
        is_url = True
    except ValueError: # torrent_location is not url
        filename = torrent_location
            

    ses = lt.session()
    ses.listen_on(6881,6891)

    info = lt.torrent_info( filename )
    h = ses.add_torrent({'ti': info, 'save_path': save_dir })

    if debug || verbose :
        print( 'starting', h.name() )

    while (not h.is_seed() or seeding_time > 0):
        s = h.status()

        if debug || verbose :
            state_str = ['queued', 'checking', 'downloading metadata', \
                'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
            print( '\r%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
                (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
                s.num_peers, state_str[s.state])),
            sys.stdout.flush()

        if h.is_seed() :
            seeding_time = seeding_time - 1

        time.sleep(1)

    if debug || verbose :
        print( h.name(), 'complete' )

    if is_url and os.path.exists( tmp_dir ):
        shutil.rmtree( tmp_dir )

    return True
        

def progress_bar( current, total, unit='', bar_width=30):
    if current > 1 :
        unit = unit + 's'
    import sys
    head_symbol='>'
    done_symbol='='
    left_symbol=' '
    done_percent = (current * 100.0) / total  
    done_width = int( bar_width * done_percent ) / 100
    left_width = bar_width - done_width - 1 # left 1 for head symbol

    sys.stdout.write("\r")
    sys.stdout.flush()
    sys.stdout.write('[' + done_symbol * done_width + head_symbol + left_width * left_symbol + ']')
    sys.stdout.write(' %3.2f %%, %i %s/ %i %s' % ( done_percent, current, unit, total, unit ) )
    sys.stdout.flush()
    if current == total :
        sys.stdout.write("\n")
        sys.stdout.flush()

def get_size(url):   
    req = urllib2.urlopen(url)
    size = int( req.info().getheader('Content-Length').strip() )
    req.close()
    return size


