# -*- coding: utf-8 -*-
import os
import sys
import shutil

'''
    [Usage]
    Chans and Foton files copy to userapps.

    chans_foton_copying_to_userapps(optics)
    or each to
    chans_copying_to_userapps(optics)
    foton_copying_to_userapps(optics)
'''

### Source file path
# /opt/rtcds/kamioka/k1/chans/K1(optics).txt
chans_src_fullpath = '/opt/rtcds/kamioka/k1/chans/K1VIS%s.txt'

# /opt/rtcds/kamioka/k1/target/k1vis(optics)/k1vis(optics)epics/burt/'
# aligned.snap, misaligned.snap, safe.snap
foton_src_dir = '/opt/rtcds/kamioka/k1/target/k1vis%s/k1vis%sepics/burt/'
aligned_src_fullpath = foton_src_dir + 'aligned.snap'
misaligned_src_fullpath = foton_src_dir + 'misaligned.snap'
safe_src_fullpath = foton_src_dir + 'safe.snap'

### Dist directory
dst_fullpath = '/opt/rtcds/userapps/release/vis/k1/'
chans_dst_fullpath = dst_fullpath + 'snapfiles/'
foton_dst_fullpath = dst_fullpath + 'fotonfiles/k1vis%s/'

'''
    Common Function
'''
def common_copying_to_userapps(src, dst):
    if os.path.isdir(dst) == False:
        print('Directpry not found: ' + dst)
        return False

    if os.path.isfile(src) == True:
        print('Copy from '+src+' to '+dst)
        shutil.copy2(src, dst)
    else:
        print('File not found: ' + src)
        return False

    return True

'''
    Copying the chans file to userapps directory
'''
def chans_copying_to_userapps(optics):
    print('Start chans file copy')
    src = chans_src_fullpath % optics.upper()
    dst = chans_dst_fullpath
    return common_copying_to_userapps(src, dst)

'''
    Copying the foton files to userapps directory
'''
def foton_copying_to_userapps(optics):
    print('Start foton file copy')
    dst = foton_dst_fullpath % optics.lower()
    if os.path.isdir(dst) == False:
        print('mkdir ' + dst)
        os.mkdir(dst)

    src = aligned_src_fullpath % (optics.lower(), optics.lower())
    result = common_copying_to_userapps(src, dst)
    if result == False:
        return False

    src = misaligned_src_fullpath % (optics.lower(), optics.lower())
    result = common_copying_to_userapps(src, dst)
    if result == False:
        return False

    src = safe_src_fullpath % (optics.lower(), optics.lower())
    result = common_copying_to_userapps(src, dst)
    if result == False:
        return False

    return True

'''
    Copying the chans and foton files to userapps directory
'''
def chans_foton_copying_to_userapps(optics):
    if chans_copying_to_userapps(optics) == False:
        return False
    
    if foton_copying_to_userapps(optics) == False:
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Chans and Foton files copy to userapps.')
        print('$ libviscopy [optics]')
        print(' optics: etmxp or ETMXP...')
        sys.exit(1)

    optics = sys.argv[1]
    print('optics', optics)
    chans_foton_copying_to_userapps(optics)
