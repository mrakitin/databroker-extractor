#assumes tunnel is setup
from metadatastore.mds import MDS
from filestore.fs import FileStore
from databroker import Broker, get_events, get_images

##### Some initial setup for databroker and FS
# Port used for tunneling (CHX' mongodb port is 27017)
TUNNELPORT = 27019
# old chx root directory for EIGER files and other filestore stuff
OLDROOTS = ["/XF11ID/data", "/xf11id/data"]
# new root directory for EIGER files and other filestore stuff
NEWROOT = "/media/xray/NSLSII_Data/CHX"


# This an example. You'll need to know your local configuration.
mds = MDS({
            'host': 'localhost',
            'port': TUNNELPORT,
            'database': 'datastore',
            'timezone': 'US/Eastern',
             }, auth=False)

# This an example. You'll need to know your local configuration.
fs = FileStore({
        'host': 'localhost',
                  'port': TUNNELPORT,
                  'database': 'filestore'})

chxdb = Broker(mds, fs)
print("Set up the chx database at `chxdb`. Please test if connection is"
      "successful by running chxdb[-1]")

#### Setup of the handlers
import h5py
from detector.eiger import EigerImages2

def changerootdir(oldroots, newroot):
    ''' returns a decorator that acts on function in a class.
        changes substring oldroots to newroot in filepaths
    '''
    def f_outer(f):
        def f_inner(self, fpath, images_per_file):
            for oldroot in oldroots:
                fpath = fpath.replace(oldroot, newroot)
            return f(self, fpath, images_per_file)
        return f_inner
    return f_outer


class EigerHandler2:
    EIGER_MD_LAYOUT = {
        'y_pixel_size': 'entry/instrument/detector/y_pixel_size',
        'x_pixel_size': 'entry/instrument/detector/x_pixel_size',
        'detector_distance': 'entry/instrument/detector/detector_distance',
        'incident_wavelength': 'entry/instrument/beam/incident_wavelength',
        'frame_time': 'entry/instrument/detector/frame_time',
        'beam_center_x': 'entry/instrument/detector/beam_center_x',
        'beam_center_y': 'entry/instrument/detector/beam_center_y',
        'count_time': 'entry/instrument/detector/count_time',
        'pixel_mask': 'entry/instrument/detector/detectorSpecific/pixel_mask',
    }
    specs = {'AD_EIGER2'}
    @changerootdir(OLDROOTS, NEWROOT)
    def __init__(self, fpath, images_per_file):
        # create pims handler
        self._base_path = fpath
        self._images_per_file = images_per_file

    def __call__(self, seq_id):
        master_path = '{}_{}_master.h5'.format(self._base_path, seq_id)
        with h5py.File(master_path, 'r') as f:
            md = {k: f[v].value for k, v in self.EIGER_MD_LAYOUT.items()}
        # the pixel mask from the eiger contains:
        # 1  -- gap
        # 2  -- dead
        # 4  -- under-responsive
        # 8  -- over-responsive
        # 16 -- noisy
        pixel_mask = md['pixel_mask']
        #pixel_mask[pixel_mask>0] = 1
        #pixel_mask[pixel_mask==0] = 2
        #pixel_mask[pixel_mask==1] = 0
        #pixel_mask[pixel_mask==2] = 1
        md['binary_mask'] = (md['pixel_mask'] == 0)
        md['framerate'] = 1./md['frame_time']
        # TODO Return a multi-dimensional PIMS seq.
        return EigerImages2(master_path, self._images_per_file, md=md)

from eiger_io.fs_handler import LazyEigerHandler
#  TODO needs to be made a decorator llike chgrootdir later...
def LazyEigerHandler2(fpath, frame_per_point, mapping=None):
    for oldroot in OLDROOTS:
        fpath = fpath.replace(oldroot, NEWROOT)
    return LazyEigerHandler(fpath, frame_per_point, mapping=mapping)

chxdb.fs.register_handler('AD_EIGER2', EigerHandler2)
chxdb.fs.register_handler('AD_EIGER', LazyEigerHandler2)

print("Registered the Eiger Handler")
