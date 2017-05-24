import numpy as np
import skimage.io as io
import tensorflow as tf
import os, sys

CODE_2_MEANING = 'Code 2: invalid arguements'
CODE_1_MEANING = 'Code 1: Absent Data'


def _float_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))

def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def main(args=None):
    """
    :param args: List of arguments
    :arg -d file path to the data output directory of skynet-data, required. The <manifest>.tfrecords file will also be put in this directory.
    :arg -m the manifest file, usually train.txt or val.txt, required.
    :returns: Nothing
    side effects: writes file tfrecords file <dataDir>/<manifest>.tfrecords containing training data
    """
    tfrecords_filename = '.tfrecords'
    dataDir = ""
    process = False
    if args == None:
        args = sys.argv
    if isinstance(args, str):
        args = args.split(' ')
    if len(args) == 1 or args[1] == '--help':
        print("Usage:")
        print("python read_skynet_data.py -d path/to/skynet-data/output [-f]")
        sys.exit(0)

    i = 1
    while i < len(args):
        arg = args[i]
        if arg == '-p':
            process = True
        elif arg == '-d':
            i += 1
            arg = args[i]
            dataDir = arg
        elif arg == '-m':
            i += 1
            arg = args[i]
            manifest = arg
        else:
            print('Unrecognized flag ' + arg)
            print(CODE_2_MEANING)
            sys.exit(2)
        i += 1
    if dataDir == "":
        print('You must provide the location of the training data with the -d arg')
        print(CODE_2_MEANING)
        sys.exit(2)
    if manifest == "":
        print('You must provide the location of the manifest with the -m arg')
        print(CODE_2_MEANING)
        sys.exit(2)
    if not os.path.isdir(dataDir):
        print('The data directory you supplied with the -d arg does not exist or is not a directory')
        print(CODE_2_MEANING)
        sys.exit(2)
    tfrecords_filename = manifest[:-4] + tfrecords_filename
    writer = tf.python_io.TFRecordWriter(tfrecords_filename)

    train = open(dataDir + '/' + manifest, 'r')
    trainLabels = []
    trainImages = []
    for line in train:
        line = line.split(' ')
        imagePath = line[0]
        labelPath = line[1]
        #remove the /data, which is redundant to dataDir
        imagePath = dataDir + imagePath[5:]
        #also remove the newling
        labelPath = dataDir + labelPath[5:-1]
        image = io.imread(imagePath, as_grey=True)
        image = np.array(image)
        image = (image*255).astype('byte') #scale to fit byte data type
        height = image.shape[0]
        width = image.shape[1]
        imgRaw = image.tostring()

        labelAr = io.imread(labelPath, as_grey=True)
        labelAr = np.array(labelAr)
        #so the really weird thing is that the data values are zero and the nodata values are nonzero?
        #hence the following line
        label = width*height - np.count_nonzero(labelAr)

        pair = tf.train.Example(features=tf.train.Features(feature={
            'height': _int64_feature(height),
            'width': _int64_feature(width),
            'image_raw': _bytes_feature(imgRaw),
            'label_raw': _int64_feature(label)}))
        writer.write(pair.SerializeToString())


def read_data(loc, manifestName):
    print("reading " + manifestName)
    main("read_skynet_data.py -d " + loc + " -m " + manifestName + '.txt')


#test main("read_skynet_data.py -d /Users/devmcdevlin/skynet-data/data -m train.txt")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt):
        exit('Received Ctrl + C... Exiting', 1)