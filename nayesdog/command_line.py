#!/usr/bin/env python2

# Commandline tool

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-browser', default=False, type=bool, help='Do not open web interface in browser')
    parser.add_argument('--config', type=str, default='', help='Use alternative config folder')
    args = parser.parse_args()
    import os
    import webbrowser
    from facelib import run
    from config import get_pars_for_facelib as get_pars

    if args.config != '' and os.path.isfile(args.config):
        pars = get_pars(file_path=args.config)
    else:
        pars = get_pars()

    if not args.no_browser:
        webbrowser.open('http://{}:{}'.format(*pars['server_address']))

    run(**pars)
    #run()

if __name__ == '__main__':
    main()
