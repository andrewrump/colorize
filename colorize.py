#!/usr/bin/python3
#
# By Andrew Rump (andrew@rump.dk) October 2019
#
# Colourize input
# Anything comming in goes out - unless not in a regex group
#
# BUGS
# - - matched using ( -)( -) are ignored
# - - matched using ( -)( )(-) miss the space
#
# TODO
# Support the current terminal
# Support bold 1, dim 2, underline 4, blink 5, reverse 7 & hidden 8

import argparse
import re

##############################################################################################

COLORS = {'grey': 30, 'red': 31, 'green': 32, 'yellow':33, 'blue': 34, 'magenta': 35, 'cyan': 36}

def light(color):
   return color + 60

def color(code = None):
   if code is None:
      return '\033[0m'
   else:
      return '\033[' + str(abs(code)) + 'm'
   
##############################################################################################

# 192.168.1.225 - - [07/Oct/2019:11:18:43 +0200] "GET /api/Test?System=Test&TimeStamp=1570439920 HTTP/1.1" 200 395 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
# 192.168.1.225 - - [08/Oct/2019:15:32:19 +0200] "-" 408 0 "-" "-"
# 192.168.1.225 - - [28/Oct/2019:08:55:23 +0100] "GET /favicon.ico HTTP/1.1" 404 494 "http://192.168.168.112/api/Test?System=test" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
WWW_LINE = r'^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})( -)( )(-|[a-z]+)' + \
           r'( \[[0-9]{2}/[A-Z][a-z]{2}/[0-9]{4}:[0-9]{2}:[0-9]{2}:[0-9]{2} (\+|\-)[0-9]{4}\])' + \
           r'( ")((DELETE|GET|INVALID|PATCH|POST|PUT) )?(-|/.+)(" )([0-9]{3})( [0-9]+)( ")(.+)(")( ")(.+)(")$'
WWW_COLORS = [light(COLORS['magenta']), light(COLORS['yellow']), light(COLORS['red']), light(COLORS['red']),
              light(COLORS['green']), light(COLORS['grey']), light(COLORS['magenta']),
              light(COLORS['yellow']), light(COLORS['grey']), light(COLORS['green']),
              light(COLORS['grey']), light(COLORS['grey']), light(COLORS['green']), light(COLORS['grey']),
              light(COLORS['grey']), COLORS['green'], light(COLORS['grey'])]

# [Mon Oct 07 11:18:43.234051 2019] [php7:notice] [pid 30304] [client 192.168.1.225:57283] PHP Notice:  Undefined index: Test in /var/www/api/mvc.php on line 94
# [Thu Oct 10 13:25:14.534758 2019] [php7:error] [pid 25126] [client 192.168.1.225:56805] PHP Fatal error:  Can't use function return value in write context in /var/www/api/Model/MVCModel.php on line 45
PHP_LINE = r'^(\[[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6} [0-9]{4}\])' + \
           r'( \[php7:.*\])( \[pid [0-9]+\])( \[client [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+\])' + \
           r'( PHP .*:  )(.+)( in .+)( on line [0-9]+)(, referer: .+)?$'
PHP_COLOR = [light(COLORS['green']), light(COLORS['yellow']), light(COLORS['green']), light(COLORS['magenta']),
             light(COLORS['yellow']), -light(COLORS['red']), light(COLORS['green']), light(COLORS['yellow']),
             light(COLORS['green'])]
# [Thu Oct 10 13:16:53.535814 2019] [php7:error] [pid 17245] [client 192.168.1.225:56748] PHP Fatal error:  Uncaught Error: Call to a member function logStatus() on null in /var/www/api/Model/MVCModel.php:36\nStack trace:\n#0 /var/www/api/Controller/MVCController.php(31): Poly\\Model\\MVCModel->listActions(Object(Poly\\Core\\Autoloader), 'Test')\n#1 /var/www/api/mvc.php(184): Poly\\Controller\\MVCController->listActions(Object(Poly\\Core\\Autoloader), 'Test')\n#2 {main}\n  thrown in /var/www/api/Model/MVCModel.php on line 36
# [Tue Oct 22 13:10:22.090057 2019] [php7:warn] [pid 20603] [client 192.168.1.225:59385] PHP Warning:  Use of undefined constant URL_DIR - assumed 'URL_DIR' (this will throw an Error in a future version of PHP) in /var/www/api/Core/ExceptionHandler/View/ExceptionClassicView.php on line 31, referer: http://192.168.168.112/api/Test?System=test
# [Mon Oct 07 16:19:24.263155 2019] [autoindex:error] [pid 1819] [client 192.168.1.225:60589] AH01276: Cannot serve directory /var/www/: No matching DirectoryIndex (index.html,index.cgi,index.pl,index.php,index.xhtml,index.htm) found, and server-generated directory index forbidden by Options directive
BAD_LINE = r'^(\[[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6} [0-9]{4}\])' + \
           r'( \[autoindex:error\])( \[pid [0-9]+\])( \[client [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+\])' + \
           r'( AH01276: Cannot serve directory /var/www/: No matching DirectoryIndex \(index.html,index.cgi,index.pl,index.php,index.xhtml,index.htm\) found, and server-generated directory index forbidden by Options directive)$'
BAD_COLOR = [light(COLORS['green']), light(COLORS['yellow']), light(COLORS['green']),
             light(COLORS['magenta']), light(COLORS['grey'])]

##############################################################################################

def match(args, line, colors, regex):
   #print(line)
   m = re.match(regex, line)
   if m:
      work_around = None
      index = -1
      for group in m.groups():
         #print('{' + group + '}')
         #if not work_around is None:
         #   print('[' + str(work_around) + '.' + group + '.' + str.strip(work_around) + ']')
         if group is None: # ()? gives None groups
            if work_around != group:
               index += 1
         elif work_around is None or work_around.find(group) == -1 or str.strip(group) == '': # Work around using ( )
            # BUG ((|)) define 2 groups not one!
            index += 1
            if index >= len(colors):
               if args.cycle_color:
                  index = 0
               else:
                  raise Exception('Ran out of colors on ' + line)
            if colors[index] < 0: # TODO BUG What???
               print(color(1), end = '')
            print(color(colors[index]) + group, end = '')
         work_around = group
      print(color())
      return True
   return False

def main(args):
   while True:
      try:
         line = input()
      except EOFError:
         break

      if not match(args, line, WWW_COLORS, WWW_LINE):
         if not match(args, line, PHP_COLOR, PHP_LINE):
            if not match(args, line, BAD_COLOR, BAD_LINE):
               if not args.default_red:
                  print(color(light(COLORS['red'])), end = '')
               print(line)
               if not args.default_red:
                  print(color(), end = '')

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description = 'Colourize input')
   parser.add_argument('-m', '--match-file', help = 'NOT IMPLEMENTED YET! Match file')
   parser.add_argument('-r', '--default_red', action = 'store_true', help = 'Color anything not recognized with red')
   parser.add_argument('-c', '--cycle_color', action = 'store_true', help = 'Cycle color if running out of colors')
   #parser.add_argument
   args = parser.parse_args()
   #print(args)
   #main(args)
   try:
      main(args)
   except KeyboardInterrupt:
      pass
   except Exception as e:
      print()
      print(color(light(COLORS['red'])), end = '')
      print(e)
      print(color(), end = '')
#Traceback (most recent call last):
#  File "./colorize.py", line 80, in <module>
#    main(args)
#  File "./colorize.py", line 65, in main
#    if not match(args, line, WWW_COLORS, WWW_LINE):
#  File "./colorize.py", line 43, in match
#    m = re.match(regex, line)
#  File "/usr/lib/python3.6/re.py", line 172, in match
#    return _compile(pattern, flags).match(string)
#  File "/usr/lib/python3.6/re.py", line 301, in _compile
#    p = sre_compile.compile(pattern, flags)
#  File "/usr/lib/python3.6/sre_compile.py", line 562, in compile
#    p = sre_parse.parse(p, flags)
#  File "/usr/lib/python3.6/sre_parse.py", line 869, in parse
#    raise source.error("unbalanced parenthesis")
#sre_constants.error: unbalanced parenthesis at position 129
