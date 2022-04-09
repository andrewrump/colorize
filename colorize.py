#!/usr/bin/python3
#
# By Andrew Rump 2019 andrew@rump.dk
#
# Colourize input
# Anything comming in goes out - unless not in a regex group
#
# TODO
# Support the current terminal
# Support bold 1, dim 2, underline 4, blink 5, reverse 7 & hidden 8

import argparse
import re

##############################################################################################

GREY = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
MAGENTA = 35
CYAN = 36

def light(color):
   return color + 60

##############################################################################################

# 192.168.1.225 - - [07/Oct/2019:11:18:43 +0200] "GET /api/Test?System=Test&TimeStamp=1570439920 HTTP/1.1" 200 395 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
WWW_LINE = r'^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})( -)( (-|[a-z]+))' + \
           r'( \[[0-9]{2}/[A-Z][a-z]{2}/[0-9]{4}:[0-9]{2}:[0-9]{2}:[0-9]{2} \+0200\])' + \
           r'( ")((DELETE|GET|PATCH|POST|PUT) )(/.+)(" )([0-9]{3})( [0-9]+)( "-")( ")(.+)(")$'
WWW_COLORS = [light(MAGENTA), light(YELLOW), light(RED), light(GREEN), light(GREY),
              light(MAGENTA), light(YELLOW), light(GREY), light(GREEN), light(GREY),
              light(MAGENTA), light(GREY), GREEN, light(GREY)]

# [Mon Oct 07 11:18:43.234051 2019] [php7:notice] [pid 30304] [client 192.168.1.225:57283] PHP Notice:  Undefined index: Test in /var/www/api/mvc.php on line 94
PHP_LINE = r'^(\[[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6} [0-9]{4}\])' + \
           r'( \[php7:notice\])( \[pid [0-9]+\])( \[client [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+\])' + \
           r'( PHP Notice:  )(.+)( on line [0-9]+)$'
PHP_COLOR = [light(GREEN), light(YELLOW), light(GREEN), light(MAGENTA), light(YELLOW), -light(RED), light(YELLOW)]

# [Mon Oct 07 16:19:24.263155 2019] [autoindex:error] [pid 1819] [client 192.168.1.225:60589] AH01276: Cannot serve directory /var/www/: No matching DirectoryIndex (index.html,index.cgi,index.pl,index.php,index.xhtml,index.htm) found, and server-generated directory index forbidden by Options directive
BAD_LINE = r'^(\[[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6} [0-9]{4}\])' + \
           r'( \[autoindex:error\])( \[pid [0-9]+\])( \[client [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+\])' + \
           r'( AH01276: Cannot serve directory /var/www/: No matching DirectoryIndex \(index.html,index.cgi,index.pl,index.php,index.xhtml,index.htm\) found, and server-generated directory index forbidden by Options directive)$'
BAD_COLOR = [light(GREEN), light(YELLOW), light(GREEN), light(MAGENTA), light(GREY)]

##############################################################################################

def match(args, line, colors, regex):
   #print(line)
   m = re.match(regex, line)
   if m:
      work_around = None
      index = -1
      for group in m.groups():
         #if not work_around is None:
         #   print('[' + str(work_around) + '.' + group + '.' + str.strip(work_around) + ']')
         if work_around is None or len(work_around) == len(group) or \
            str.strip(work_around) != group:
            work_around = group # BUG ((|)) define 2 groups not one!
            index += 1
            if index >= len(colors):
               if args.cycle_color:
                  index = 0
               else:
                  raise Exception('Ran out of colors on ' + line)
            if colors[index] < 0: # TODO
               print('\033[1m', end = '')
            print('\033[' + str(abs(colors[index])) + 'm', end = '')
            print(group, end = '')
      print('\033[0m')
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
                  print('\033[' + str(light(RED)) + 'm', end = '')
               print(line)
               if not args.default_red:
                  print('\033[0m', end = '')

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description = 'Colourize input')
   parser.add_argument('-m', '--match-file', help = 'NOT IMPLEMENTED YET! Match file')
   parser.add_argument('-r', '--default_red', action = 'store_true', help = 'Color anything not recognized with red')
   parser.add_argument('-c', '--cycle_color', action = 'store_true', help = 'Cycle color if running out of colors')
   #parser.add_argument
   args = parser.parse_args()
   #print(args)
   main(args)
   #try:
   #   main(args)
   #except Exception as e:
   #   print()
   #   print('\033[' + str(light(RED)) + 'm', end = '')
   #   print(e)
   #   print('\033[0m', end = '')
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
