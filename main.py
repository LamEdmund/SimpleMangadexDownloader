import downloader as dlr
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
                           type = str,
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
                           type = str,
                           choices = ['data', 'data-saver'], 
                           default = 'data-saver',
                           help = "Choose image quality to get, data or data-saver")
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
    elif args.url != None:
        dlr.downloadManga(dlr.getMangaId(args.url), args.quality, args.skip)
    elif args.ID != None:
        dlr.downloadManga(args.ID, args.quality, args.skip)