import libtorrent as lt
import time
import sys

ses = lt.session()
baseport = 6881
baseport2 = 6891
ses.listen_on(6881,6891)

info = lt.torrent_info(sys.argv[1])
h = ses.add_torrent({'ti': info, 'save_path': './'})
print 'starting', h.name()

seeding_timer = 30
while (not h.is_seed() or seeding_timer > 0):
    s = h.status()

    state_str = ['queued', 'checking', 'downloading metadata', \
        'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
    print '\r%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
        (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
        s.num_peers, state_str[s.state]),
    sys.stdout.flush()

    if h.is_seed() :
        seeding_timer = seeding_timer - 1

    time.sleep(1)


print h.name(), 'complete'
