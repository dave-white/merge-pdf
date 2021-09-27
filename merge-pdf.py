#!/usr/bin/env python3

import os
import shutil
import argparse
from pathlib import Path

def main() :
    arg_parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='For each immdediate child directory of specified parent directory (or current if\n'
                      + 'none specified) merges all PDFs in child into <child-name>.mrg.pdf within child.\n'
                      + 'If graphicsmagick present, also first converts jp(e)g and png into single\n'
                      + 'temporary PDF to be merged with others.\n\n'
                + 'Dependencies \n'
                + '------------ \n'
                + 'Required: python3 >= 3.6, \n'
                + '          ghostscript (available in TeXLive) \n'
                + 'Optional: graphicsmagick (available from Homebrew) \n \n'
            )

    arg_parser.add_argument('-q', '--quiet',
            action='store_true',
            dest='quiet',
            help='Suppresses progress messages.')

    arg_parser.add_argument('-p', '--parent-dir=',
            nargs='?',
            default='',
            metavar='PARENT DIRECTORY',
            dest='par_dir',
            help = 'Relative or absolute path to the source directory of the pdf and img files to be merged. \n'
                 + 'Default: current working directory.'
        )

    # Check for ghostscript exe (gs).
    # If not found, abort.
    if shutil.which('gs') == None :
        print('Ghostscript executable, gs, not found. Aborting.')
        return

    # Parse cmd line arguments.

    args = arg_parser.parse_args()

    # Unless --quiet specified at cmd line, print status msgs
    quiet = False
    quiet = args.quiet

    # Set parent directory.
    # Use cwd if none specified at cmd line.
    par_dir = Path.cwd()

    str_par_dir = args.par_dir.strip()
    if not str_par_dir == '' :
        par_dir = Path(str_par_dir)

    if not quiet :
        print("Parent directory set to " + str(par_dir.resolve()) + ".")
    
    # Merge/conversion process.

    # Check whether graphicsmagick is available for image conversion
    can_do_img = False
    if not shutil.which('gm') == None :
        if not quiet :
            print('graphicsmagick detected. Will attempt to merge image files.')

        can_do_img = True

    cwd = os.getcwd()
    for fldr in par_dir.iterdir() :
        os.chdir(fldr)
        # Convert image files into a single temporary PDF via graphicsmagick (gm)
        if can_do_img :
            l_img_files = list(fldr.glob('*.jpg'))
            l_img_files.extend(fldr.glob('*.jpeg'))
            l_img_files.extend(fldr.glob('*.png'))
            str_img_lst = ''
            for img in list(l_img_files) :
                str_img_lst += img.name + ' '

            tmp_img_fname = fldr.name + '-img-tmp.pdf'
            os.system('gm convert ' + str_img_lst + tmp_img_fname)

        # Merge PDFs via ghostscript (gs)
        str_pdf_lst = ''
        for pdf in list(fldr.glob('*.pdf')) :
            str_pdf_lst += ' ' + pdf.name

        os.system('gs -dNOPAUSE -sDEVICE=pdfwrite -sOUTPUTFILE=' + fldr.name + '.mrg.pdf -dBATCH' + str_pdf_lst)
        if not quiet :
            print('Created merge file ' + fldr.name + '.mrg.pdf')

        # Clean up temporary files
        os.system('rm ' + tmp_img_fname)

    os.chdir(cwd)

    return

if __name__ == '__main__':
    main()

