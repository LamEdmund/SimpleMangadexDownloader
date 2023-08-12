import downloader
import argparse

if __name__ == '__main__':
    argParser = argparse.ArgumentParser(prog='ProgramName',
                    description='What the program does')
    
    required = argParser.add_argument_group('Required arguements')
    optional = argParser.add_argument_group('Optional arguements')

    # required arguements
    required.add_argument('-u', '--url',
                           dest = 'url',
                           required = False,
                           nargs = 1,
                           default = None,
                           help = 'Target Mangadex manga url') 
    required.add_argument('-i', '--ID',
                           dest = 'ID',
                           required = False,
                           nargs = 1,
                           default = None,
                           help = 'Target Mangadex manga id') 
    
    # optional arguements
    optional.add_argument('-q', '--quality',
                           dest = 'quality',
                           required = False,
                           type = int,
                           choices = [0, 1], 
                           default = 1,
                           help = "Choose image quality to get. 0 = data, 1 = data-saver")
    optional.add_argument('-s', '--skip',
                          dest='skip',
                          action = argparse.BooleanOptionalAction,
                          required = False,
                          choices = [True, False],
                          default = True,
                          help = 'Skip existing page. Is True by default.'
                          )

    args = argParser.parse_args()
    print(args)
    
    if args.url == None and args.ID == None:
        print('No url or ID specified, exiting.')
    else:
        pass