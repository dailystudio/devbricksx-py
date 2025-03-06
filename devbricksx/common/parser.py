import os
import imghdr
from devbricksx.development.log import *

__ACCEPT_IMAGE_TYPES__ = ['png', 'jpeg', 'bmp']


def append_common_developer_options_to_parse(ap):
    ap.add_argument("-v", "--verbose", action='store_true',
                    default=False,
                    help="print more development information")
    ap.add_argument("-s", "--silent", action='store_true',
                    default=False,
                    help="silent only some critical outputs remained")


def append_common_dir_options_to_parse(ap):
    dir_opts_group = ap.add_argument_group('input and output arguments')
    dir_opts_group.add_argument("-id", "--input-directory",
                                required=True,
                                help="input directory with image files")
    dir_opts_group.add_argument("-od", "--output-directory",
                                help="output directory with image files")


def append_common_file_options_to_parse(ap, group_required=False, enable_od=True):
    file_opts_group = ap.add_argument_group('input and output arguments')
    group = file_opts_group.add_mutually_exclusive_group(required=group_required)
    group.add_argument("-if", "--input-file",
                       help="input image file")
    group.add_argument("-id", "--input-directory",
                       help="input directory with image files")

    if not enable_od:
        file_opts_group.add_argument("-of", "--output-file",
                                     help="output image file")
    else:
        group = file_opts_group.add_mutually_exclusive_group(required=False)
        group.add_argument("-of", "--output-file",
                           help="output image file")
        group.add_argument("-od", "--output-directory",
                           help="output directory with image files")


def check_consistency_of_file_options(args):
    if args.output_directory is not None and args.input_directory is None:
        exit('Invalid arguments: --output_directory should be used with --input_directory')

    if args.output_file is not None and args.input_file is None:
        exit('Invalid arguments: --output_file should be used with --input_file')


def extract_files_from_args(args):
    files = []

    if args.input_directory is not None:
        input_dir = args.input_directory
        debug("selected directories:{}".format(input_dir))
        files_in_dir = os.listdir(input_dir)
        for f in files_in_dir:
            file_path = os.path.join(input_dir, f)
            image_type = imghdr.what(file_path)
            if image_type in __ACCEPT_IMAGE_TYPES__:
                files.append(file_path)
            else:
                info('skip file [%s] with file type (%s) is not accepted. It SHOULD be one of [%s].'
                     % (f, image_type, ','.join(str(t) for t in __ACCEPT_IMAGE_TYPES__)))
    else:
        debug("selected file:{}".format(args.input_file))
        files.append(args.input_file)

    return files
