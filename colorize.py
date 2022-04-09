#!/usr/bin/python3
#
# By Andrew Rump (andrew@rump.dk) October 2019-2021
#
# Colourize input depending on the format of the input
# Anything comming in goes out - unless not in a regex group
#
# BUGS:
# In case of errors read the rest of the input before terminating
## Bug - the bugfix cause the program to hang on keyboard input!?!
# Ran out of colors does not clear the input buffer
# XML/HTML miss the last > character
# 144,145d104 does not change color correctly
# - - matched using ( -)( -) are ignored
# - - matched using ( -)( )(-) miss the space
# Input without echo
#
# TODO:
# Implement self test
# Group matches and raise exception if match switches group
# Implicit ^$ instead of explicit - or vice versa
# DONE? COLORS depending on match (200, 404, ...)
# Dynamic fields, e.g., W3C field definitions
##Fields: date time s-ip cs-method cs-uri-stem cs-uri-query s-port cs-username c-ip cs(User-Agent) sc-status sc-substatus sc-win32-status time-taken
# Isn't black color missing?
# Add XML/HTML support
# Support free (XML/HTML) format, i.e., repeating pattern (use findall()/finditer()? & start()/end()/span())
# Multiline support (probably require a total rewrite)
# compile RE
# If changes are diffs, i.e., + & - and minimal mark the differences using color and not the whole line
# + Handle -w (which ignores any whitespace)
#   8c8
#   <          <Reference URI="#idf656943cc2d2480eb03dd00f39312992">
#   ---
#   > <Reference URI="#id1f54b9ffa67c448790f84608bfff27a7">
# Implement leading detection and/or naming of filters as part of arguments as some input are too easy to catch, e.g. copy
# Support reading files
# Detect if color (and other) codes are send through the pipe and either abort or support it
# Support the current terminal settings
# Support bold 1, dim 2, underline 4, blink 5, reverse 7 & hidden 8
#
# DONE:
# Color field depending on value, i.e., 200 or 2.. green, 4.. red, ...
# Is adding [..., []] to an array end up adding two elements - a Python bug or a Python misunderstanding? => mis

import argparse
import re

##############################################################################################

VERSION = "Version: 1.20 (" + '__FILEDATE__' + ")"
AUTHOR = "Copyright: Andrew Rump, andrew@rump.dk, 2019-2021"

##############################################################################################

COLORS = {'grey': 30, 'red': 31, 'green': 32, 'yellow':33, 'blue': 34, 'magenta': 35, 'cyan': 36}

def light(color):
   return color + 60

def color_code(code = None, blank = False):
   if blank:
      return ''
   if code is None:
      return '\033[0m'
   else:
      return '\033[' + str(abs(code)) + 'm'
   
##############################################################################################

matches = [] # When adding (not extending) the list of matches make sure to add an array of arrays [[]]

# Web log
# TODO Colorsplit HTTP/1\.(01) from URL
# 192.168.1.225 - - [07/Oct/2019:11:18:43 +0200] "GET /api/Test?System=Test&TimeStamp=1570439920 HTTP/1.1" 200 395 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
# 192.168.1.225 - - [08/Oct/2019:15:32:19 +0200] "-" 408 0 "-" "-"
# 192.168.1.225 - - [28/Oct/2019:08:55:23 +0100] "GET /favicon.ico HTTP/1.1" 404 494 "http://192.168.168.112/api/Test?System=test" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
#::1 - - [09/Dec/2019:09:54:32 +0000] "OPTIONS * HTTP/1.0" 200 126 "-" "Apache/2.4.25 (Debian) (internal dummy connection)"
#192.168.168.169 - - [13/Jan/2020:10:42:16 +0100] "HEAD /pleje_development/Resource/html5/phantom/svg/zonesScreen1.svg HTTP/1.1" 200 292 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362"

matches += [[r'^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|::1)( -)( )(-|[a-z]+)' + \
             r'( \[[0-9]{2}/[A-Z][a-z]{2}/[0-9]{4}:[0-9]{2}:[0-9]{2}:[0-9]{2} (\+|\-)[0-9]{4}\])' + \
             r'( ")((DELETE|GET|HEAD|INVALID|OPTIONS|PATCH|POST|PUT) )?(-|\* HTTP/1\.0|/.* HTTP/1\.[01])(" )([0-9]{3})( [0-9]+)( ")(.+)(")( ")(.+)(")$',
             [light(COLORS['magenta']), light(COLORS['yellow']), light(COLORS['red']), light(COLORS['red']),
              light(COLORS['green']), light(COLORS['grey']), light(COLORS['magenta']),
              light(COLORS['yellow']), light(COLORS['grey']), 0,
              light(COLORS['grey']), light(COLORS['grey']), light(COLORS['green']), light(COLORS['grey']),
              light(COLORS['grey']), COLORS['green'], light(COLORS['grey'])],
              [(r'^[12][0-9]{2}$', light(COLORS['green'])), (r'3[0-9]{2}$', light(COLORS['yellow'])),
               (r'^408$', COLORS['green']), (r'^[45][0-9]{2}$', light(COLORS['red']))]
           ]]

# PHP Web log
# [Mon Oct 07 11:18:43.234051 2019] [php7:notice] [pid 30304] [client 192.168.1.225:57283] PHP Notice:  Undefined index: Test in /var/www/api/mvc.php on line 94
# [Thu Oct 10 13:25:14.534758 2019] [php7:error] [pid 25126] [client 192.168.1.225:56805] PHP Fatal error:  Can't use function return value in write context in /var/www/api/Model/MVCModel.php on line 45
# [Thu Oct 10 13:16:53.535814 2019] [php7:error] [pid 17245] [client 192.168.1.225:56748] PHP Fatal error:  Uncaught Error: Call to a member function logStatus() on null in /var/www/api/Model/MVCModel.php:36\nStack trace:\n#0 /var/www/api/Controller/MVCController.php(31): Poly\\Model\\MVCModel->listActions(Object(Poly\\Core\\Autoloader), 'Test')\n#1 /var/www/api/mvc.php(184): Poly\\Controller\\MVCController->listActions(Object(Poly\\Core\\Autoloader), 'Test')\n#2 {main}\n  thrown in /var/www/api/Model/MVCModel.php on line 36
# [Thu Feb 06 09:06:49.415526 2020] [php7:warn] [pid 7042] [client 192.168.168.169:64321] PHP Warning:  Invalid argument supplied for foreach() in /var/www/pleje_development/Controller/MenuController.php on line 387, referer: https://www.pleje.net/demo112/75d00129a99a1668b5323a4e80bf238a/MVC/Alpha/?Action=getAlpha&svr=0
# [Tue Oct 22 13:10:22.090057 2019] [php7:warn] [pid 20603] [client 192.168.1.225:59385] PHP Warning:  Use of undefined constant URL_DIR - assumed 'URL_DIR' (this will throw an Error in a future version of PHP) in /var/www/api/Core/ExceptionHandler/View/ExceptionClassicView.php on line 31, referer: http://192.168.168.112/api/Test?System=test
matches += [[r'^(\[[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6} [0-9]{4}\])' + \
             r'( \[php7:.+\])( \[pid [0-9]+\])( \[client [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+\])' + \
             r'( PHP .+:  )(.+)( in .+)( on line [0-9]+)(, referer: .+)?$',
             [light(COLORS['green']), light(COLORS['yellow']), light(COLORS['green']), light(COLORS['magenta']),
              light(COLORS['yellow']), light(COLORS['red']), light(COLORS['green']), light(COLORS['yellow']),
              light(COLORS['green'])]]]

# PHP log
# [Mon Oct 07 16:19:24.263155 2019] [autoindex:error] [pid 1819] [client 192.168.1.225:60589] AH01276: Cannot serve directory /var/www/: No matching DirectoryIndex (index.html,index.cgi,index.pl,index.php,index.xhtml,index.htm) found, and server-generated directory index forbidden by Options directive
#[Wed Jan 15 13:18:59.095275 2020] [autoindex:error] [pid 6908] [client 192.168.1.128:54837] AH01276: Cannot serve directory /var/www/julia/pleje_test/: No matching DirectoryIndex (index.html,index.cgi,index.pl,index.php,index.xhtml,index.htm) found, and server-generated directory index forbidden by Options directive
matches += [[r'^(\[[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6} [0-9]{4}\])' + \
             r'( \[autoindex:error\])( \[pid [0-9]+\])( \[client [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+\])' + \
             r'( AH01276: Cannot serve directory )(.*)(: No matching DirectoryIndex \(index.html,index.cgi,index.pl,index.php,index.xhtml,index.htm\) found, and server-generated directory index forbidden by Options directive)$',
             [light(COLORS['green']), light(COLORS['yellow']), light(COLORS['green']),
              light(COLORS['magenta']), light(COLORS['yellow']), light(COLORS['red']), light(COLORS['yellow'])]]]

#[Tue Jan 14 14:13:59.450034 2020] [php7:error] [pid 30623] [client 192.168.168.169:64941] script '/var/www/pleje_development/wp-login.php' not found or unable to stat
matches += [[r'^(\[[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6} [0-9]{4}\])' + \
             r'( \[php7:error\])( \[pid [0-9]+\])( \[client [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+\])' + \
             r'( script \'.*\' not found or unable to stat)$',
             [light(COLORS['green']), light(COLORS['yellow']), light(COLORS['green']),
              light(COLORS['magenta']), light(COLORS['red'])]]]

# Apache2 log
#[Fri Dec 06 13:13:31.319105 2019] [mpm_prefork:notice] [pid 594] AH00169: caught SIGTERM, shutting down
#[Fri Dec 06 06:09:01.217027 2019] [mpm_prefork:notice] [pid 594] AH00163: Apache/2.4.25 (Debian) configured -- resuming normal operations
#[Fri Dec 06 06:09:01.217045 2019] [core:notice] [pid 594] AH00094: Command line: '/usr/sbin/apache2'
matches += [[r'^(\[[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6} [0-9]{4}\])' + \
             r'( \[(core|mpm_prefork):notice\])( \[pid [0-9]+\])' + \
             r'( AH[0-9]+: .+)$',
             [light(COLORS['green']), light(COLORS['yellow']), light(COLORS['grey']), light(COLORS['magenta'])]]]

# SimpleSAMLphp web log
#[Mon Dec 09 09:54:24.626515 2019] [php7:notice] [pid 11588] [client 192.168.1.214:55251] SimpleSAMLphp ERR [c383cf2251] Missing default-enable or default-disable file for the module authfacebook
#[Mon Dec 09 09:54:24.626541 2019] [php7:notice] [pid 11588] [client 192.168.1.214:55251] SimpleSAMLphp ERR [c383cf2251] SimpleSAML\\Error\\CriticalConfigurationError: The configuration is invalid: The configuration (/var/simplesamlphp/config/config.php) is invalid: syntax error, unexpected ''timezone'' (T_CONSTANT_ENCAPSED_STRING), expecting ']'
#[Mon Dec 09 09:54:24.626548 2019] [php7:notice] [pid 11588] [client 192.168.1.214:55251] SimpleSAMLphp ERR [c383cf2251] Backtrace:
#[Mon Dec 09 09:54:24.626554 2019] [php7:notice] [pid 11588] [client 192.168.1.214:55251] SimpleSAMLphp ERR [c383cf2251] 1 /var/simplesamlphp.versions/simplesamlphp-1.18.2/www/_include.php:60 (require_once)
#[Mon Dec 09 09:54:24.626560 2019] [php7:notice] [pid 11588] [client 192.168.1.214:55251] SimpleSAMLphp ERR [c383cf2251] 0 /var/simplesamlphp.versions/simplesamlphp-1.18.2/www/index.php:3 (N/A)
#[Mon Dec 09 09:54:24.626566 2019] [php7:notice] [pid 11588] [client 192.168.1.214:55251] SimpleSAMLphp ERR [c383cf2251] Error report with id 72c8c6cf generated.
#[Mon Dec 09 09:54:24.631282 2019] [php7:notice] [pid 11588] [client 192.168.1.214:55251] SimpleSAMLphp DEBUG [c383cf2251] Localization: using old system
#[Mon Dec 09 09:54:24.634692 2019] [php7:notice] [pid 11588] [client 192.168.1.214:55251] SimpleSAMLphp DEBUG [c383cf2251] Translate: Reading dictionary [/var/simplesamlphp.versions/simplesamlphp-1.18.2/dictionaries/errors]
matches += [[r'^(\[[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6} [0-9]{4}\])' + \
             r'( \[php7:.+\])( \[pid [0-9]+\])( \[client [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+\])' + \
             r'( SimpleSAMLphp (DEBUG|ERR))( \[[0-9a-f]{10}\] )' + \
             r'((.+)$)',
             [light(COLORS['green']), light(COLORS['yellow']), light(COLORS['green']), light(COLORS['magenta']),
              light(COLORS['green']), light(COLORS['yellow']), light(COLORS['red'])]]]
# SimpleSAMLphp web log
#Dec 09 13:11:49 simplesamlphp DEBUG [f103537713] Session: Valid session found with 'admin'.
#Dec 09 13:11:49 simplesamlphp DEBUG [f103537713] Localization: using old system
matches += [[r'^([A-Z][a-z]{2} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})' + \
             r'( simplesamlphp (DEBUG|ERR|INFO|NOTICE STAT))( \[[0-9a-f]{10}\] )' + \
             r'((' + \
               r'Loading state: \'.+frontpage_welcome.php\'' + r'|' + \
               r'User \'admin\' successfully authenticated from [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' + r'|' + \
               r'Deleting state: \'_[0-9a-z]+\'' + r'|' + \
               r'Session: doLogin\("admin"\)' + r'|' + \
               r'Session: Valid session found with \'admin\'.' + r'|' + \
               r'Localization: using old system' + r'|' + \
               r'Translate: Reading dictionary \[/var/simplesamlphp.versions/simplesamlphp\-1.18.2/dictionaries/.+\]' + r'|' + \
               r'Translate: Reading dictionary \[/var/simplesamlphp.versions/simplesamlphp\-1.18.2/modules/.+/dictionaries/.+\]' + r'|' + \
               r'Saved state: \'_.+\'' + r'|' + \
               r'idpDisco.saml: Accessing discovery service.' + r'|' + \
               r'idpDisco.saml: returnIdParam initially set to \[idpentityid\]' + r'|' + \
               r'idpDisco.saml: isPassive initially set to \[FALSE\]' + r'|' + \
               r'idpDisco.saml: getSelectedIdP\(\) returned null' + r'|' + \
             r')$)',
             #' + r'|' + \
             [light(COLORS['green']), light(COLORS['yellow']), light(COLORS['magenta']), light(COLORS['green'])]]]

# diff
matches += [[r'^.*([0-9]+(,[0-9]+)?)([acd])([0-9]+(,[0-9]+)?)$',
             [light(COLORS['red']), COLORS['red'], COLORS['red'], COLORS['yellow'], COLORS['green'], COLORS['green']]]]
matches += [[r'^(---)$', [COLORS['yellow']]]]
matches += [[r'^(< *)(.+)$', [COLORS['red'], light(COLORS['red'])]]]
matches += [[r'^(> *)(.+)$', [COLORS['green'], light(COLORS['green'])]]]
matches += [[r'^([\+\-])([^ ].+)$', [COLORS['red'], COLORS['green']]]]
matches += [[r'^(\\ No newline at end of file)$', [COLORS['yellow']]]]
matches += [[r'^(Only in )(.+)(:)(.+)$',
             [light(COLORS['red']), light(COLORS['yellow']), light(COLORS['red']), light(COLORS['yellow'])]]]
matches += [[r'^(Binary files )(.+)( and )(.+)( differ)$',
             [light(COLORS['yellow']), light(COLORS['red']), light(COLORS['yellow']), light(COLORS['green']),
              light(COLORS['yellow'])]]]
matches += [[r'^(diff -r )(.+)( )(.+)$',
             [light(COLORS['yellow']), light(COLORS['red']), COLORS['green'], light(COLORS['green'])]]]

## copy
#matches += [[r'^sending incremental file list$', [light(COLORS['grey'])]]]
#matches += [[r'^(sent )([0-9]+)( bytes  received )([0-9]+)( bytes  [0-9]+\.[0-9]+ bytes/sec)$',
#             [light(COLORS['grey']), COLORS['green'], light(COLORS['grey']), COLORS['green'], light(COLORS['grey'])]]]
#matches += [[r'^.+\.php'], [light(COLORS['green'])]]]
#matches += [[r'^(total size is )([0-9]+)(  speedup is [0-9]+\.[0-9]+)$',
#             [light(COLORS['grey']), COLORS['green'], light(COLORS['grey'])]]]

# XML/HTML
#matches += [[r'^(( *)(</?)([^>]+)(/?>)(([^<]+)?(<)([^>]+)(/?>))?)+$',
#matches += [[r'^(( *)((<)(.+?)(>)((.+?)?(<)(.+?)(/?>))?|(<)(.+?)(/>)|(</)(.+?)(>)))+$',
matches += [[r'^( *?)(<)(.+?)(>)((.*?)(<)(.+?)(/?>))?$',
            [COLORS['grey'], light(COLORS['red']), COLORS['green'], light(COLORS['red']),
             light(COLORS['green']),
             COLORS['grey'], light(COLORS['red']), COLORS['green'], light(COLORS['red'])]]]

# W3C IIS
#2021-09-17 08:05:28 192.169.169.41 POST /cpr2.asp - 8080 - 192.168.168.193 - 200 0 0 452
#2021-09-17 08:05:34 192.169.169.41 GET /dgws_cpr.asp System=Test&ResponseId=0|251|800a01f4|Variable_is_undefined:_'orgAnswer'|25|80004005|[MySQL][ODBC_5.1_Driver]Unknown_database_'basislaege' 8080 - 192.169.169.41 Mozilla/5.0+(Windows+NT+6.1;+Win64;+x64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/93.0.4577.63+Safari/537.36 500 0 0 52
#2021-09-17 08:05:56 192.169.169.41 GET /EDI_in.dt - 8080 - 192.168.168.72 Mozilla/4.0+(compatible;+Win32;+WinHttp.WinHttpRequest.5) 200 0 0 78
#2021-09-17 08:06:53 192.169.169.41 GET /dgws_cpr.asp System=Test&ResponseId=0|256|800a01f4|Variable_is_undefined:_'boldXML'|25|80004005|[MySQL][ODBC_5.1_Driver]Unknown_database_'basislaege' 8080 - 192.169.169.41 Mozilla/5.0+(Windows+NT+6.1;+Win64;+x64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/93.0.4577.63+Safari/537.36 500 0 0 168
#2021-09-17 08:06:55 192.169.169.41 GET /dgws_cpr.asp System=Test&ResponseId=0|256|800a01f4|Variable_is_undefined:_'boldXML'|25|80004005|[MySQL][ODBC_5.1_Driver]Unknown_database_'basislaege' 8080 - 192.169.169.41 Mozilla/5.0+(Windows+NT+6.1;+Win64;+x64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/93.0.4577.63+Safari/537.36 500 0 0 130
#Software: Microsoft Internet Information Services 7.5
#Version: 1.0
#Date: 2017-03-05 13:29:48
#Fields: date time s-ip cs-method cs-uri-stem cs-uri-query s-port cs-username c-ip cs(User-Agent) sc-status sc-substatus sc-win32-status time-taken
#2017-03-05 13:29:48 192.169.169.41 GET /testkk.asp - 8080 - 192.169.169.130 Mozilla/5.0+(Windows+NT+6.1;+WOW64;+rv:51.0)+Gecko/20100101+Firefox/51.0 200 0 0 249
#2017-03-05 13:29:48 192.169.169.41 GET /favicon.ico - 8080 - 192.169.169.130 Mozilla/5.0+(Windows+NT+6.1;+WOW64;+rv:51.0)+Gecko/20100101+Firefox/51.0 404 0 2 202
#2017-03-05 13:29:51 192.169.169.41 GET /testkk.asp - 8080 - 192.169.169.130 Mozilla/5.0+(Windows+NT+6.1;+WOW64;+rv:51.0)+Gecko/20100101+Firefox/51.0 200 0 0 218
#2017-03-05 13:29:52 192.169.169.41 GET /testkk.asp - 8080 - 192.169.169.130 Mozilla/5.0+(Windows+NT+6.1;+WOW64;+rv:51.0)+Gecko/20100101+Firefox/51.0 200 0 0 218
#2017-03-05 13:36:31 192.169.169.41 GET /testkk.asp - 8080 - 192.168.1.126 Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10.12;+rv:51.0)+Gecko/20100101+Firefox/51.0 200 0 0 0
#2017-03-05 13:36:31 192.169.169.41 GET /favicon.ico - 8080 - 192.168.1.126 Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10.12;+rv:51.0)+Gecko/20100101+Firefox/51.0 404 0 2 15
#2017-03-05 13:45:11 192.169.169.41 GET /testkk.asp - 8080 - 81.19.251.35 Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_12_3)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/56.0.2924.87+Safari/537.36 200 0 0 0
#2017-03-05 13:45:11 192.169.169.41 GET /favicon.ico - 8080 - 81.19.251.35 Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_12_3)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/56.0.2924.87+Safari/537.36 404 0 2 0
#2017-03-05 13:51:40 192.169.169.41 GET /testkk.asp - 8080 - 192.168.1.126 Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10.12;+rv:51.0)+Gecko/20100101+Firefox/51.0 200 0 0 15
#2017-03-05 13:53:41 192.169.169.41 GET /testkk.asp - 8080 - 192.168.168.110 Mozilla/5.0+(X11;+Ubuntu;+Linux+x86_64;+rv:20.0)+Gecko/20100101+Firefox/20.0 200 0 0 0
#2017-03-05 13:53:41 192.169.169.41 GET /favicon.ico - 8080 - 192.168.168.110 Mozilla/5.0+(X11;+Ubuntu;+Linux+x86_64;+rv:20.0)+Gecko/20100101+Firefox/20.0 404 0 2 0
#2017-03-05 13:53:41 192.169.169.41 GET /favicon.ico - 8080 - 192.168.168.110 Mozilla/5.0+(X11;+Ubuntu;+Linux+x86_64;+rv:20.0)+Gecko/20100101+Firefox/20.0 404 0 2 15
##Software: Microsoft Internet Information Services 7.5
##Version: 1.0
##Date: 2017-03-05 14:12:25
##Fields: date time s-ip cs-method cs-uri-stem cs-uri-query s-port cs-username c-ip cs(User-Agent) sc-status sc-substatus sc-win32-status time-taken
#2017-03-05 14:12:25 192.169.169.41 GET /testkk.asp - 8080 - 81.19.251.35 Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_12_3)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/56.0.2924.87+Safari/537.36 200 0 0 0
#2017-03-05 14:15:43 192.169.169.41 GET /testkk.asp - 8080 - 81.7.167.150 Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_12_3)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/56.0.2924.87+Safari/537.36 200 0 0 15
#2017-03-05 14:15:45 192.169.169.41 GET /testkk.asp - 8080 - 81.7.167.150 Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_12_3)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/56.0.2924.87+Safari/537.36 200 0 0 15
#2017-03-05 14:15:56 192.169.169.41 GET /testkk.asp - 8080 - 81.7.167.150 Mozilla/5.0+(Windows+NT+6.1;+WOW64;+rv:51.0)+Gecko/20100101+Firefox/51.0 200 0 0 218
#2017-03-05 14:16:01 192.169.169.41 GET /favicon.ico - 8080 - 81.7.167.150 Mozilla/5.0+(Windows+NT+6.1;+WOW64;+rv:51.0)+Gecko/20100101+Firefox/51.0 404 0 2 218
#2017-03-05 14:16:04 192.169.169.41 GET /testkk.asp - 8080 - 81.7.167.150 Mozilla/5.0+(Windows+NT+6.1;+WOW64;+rv:51.0)+Gecko/20100101+Firefox/51.0 200 0 0 202
#2017-03-05 14:16:06 192.169.169.41 GET /testkk.asp - 8080 - 81.7.167.150 Mozilla/5.0+(Windows+NT+6.1;+WOW64;+rv:51.0)+Gecko/20100101+Firefox/51.0 200 0 0 218
#2017-03-05 14:17:06 192.169.169.41 GET /testkk.asp - 8080 - 81.7.167.150 Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_12_3)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/56.0.2924.87+Safari/537.36 200 0 0 0
#2017-03-05 14:17:14 192.169.169.41 GET /testkk.asp - 8080 - 81.7.167.150 Mozilla/5.0+(Windows+NT+6.1;+WOW64;+rv:51.0)+Gecko/20100101+Firefox/51.0 200 0 0 218
#2017-03-05 14:17:16 192.169.169.41 GET /testkk.asp - 8080 - 81.7.167.150 Mozilla/5.0+(Windows+NT+6.1;+WOW64;+rv:51.0)+Gecko/20100101+Firefox/51.0 200 0 0 218
#2017-03-05 14:17:17 192.169.169.41 GET /testkk.asp - 8080 - 81.7.167.150 Mozilla/5.0+(Windows+NT+6.1;+WOW64;+rv:51.0)+Gecko/20100101+Firefox/51.0 200 0 0 218
#2017-03-05 14:17:42 192.169.169.41 GET /testkk.asp - 8080 - 81.7.167.150 Mozilla/5.0+(X11;+Ubuntu;+Linux+x86_64;+rv:20.0)+Gecko/20100101+Firefox/20.0 200 0 0 0
#2017-03-05 14:17:42 192.169.169.41 GET /favicon.ico - 8080 - 81.7.167.150 Mozilla/5.0+(X11;+Ubuntu;+Linux+x86_64;+rv:20.0)+Gecko/20100101+Firefox/20.0 404 0 2 0
#

matches += [[r'^#Software: Microsoft Internet Information Services [0-9]+\.[0-9]+$',
            [COLORS['green']]]]
matches += [[r'^#Version [0-9]+\.[0-9]+$',
            [COLORS['green']]]]
matches += [[r'^#Date: [0-9]{2}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$',
            [COLORS['green']]]]
matches += [[r'^#Fields: date time s-ip cs-method cs-uri-stem cs-uri-query s-port cs-username c-ip cs(User-Agent) sc-status sc-substatus sc-win32-status time-taken$',
            [COLORS['green']]]]
matches += [[r'^([0-9]{4}-[0-9]{2}-[0-9]{2})( )([0-9]{2}:[0-9]{2}:[0-9]{2})( )' + \
             r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})( )(GET|POST)( )' + \
             r'(/[a-zA-Z0-9_]+\.(asp|dt|ico))( )(-)( )([0-9]+)( )(-)( )' + \
             r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})( )(.+)( )' + \
             r'([0-9]{3})( )(0)( )(0)( )([0-9]+)$',
            [COLORS['green'], COLORS['grey'], COLORS['blue'], COLORS['grey'],
             COLORS['magenta'], COLORS['grey'], COLORS['green'], COLORS['grey'],
             light(COLORS['grey']), COLORS['green'], COLORS['grey'],
             COLORS['red'], light(COLORS['green']), COLORS['grey'], COLORS['red'], COLORS['grey'],
             COLORS['green'], COLORS['grey'], COLORS['red'], COLORS['grey'],
             COLORS['green'], COLORS['grey'], COLORS['red'],
             [(r'^[12][0-9]{2}$', light(COLORS['green'])), (r'3[0-9]{2}$', light(COLORS['yellow'])),
              (r'^408$', COLORS['green']), (r'^[45][0-9]{2}$', light(COLORS['red']))], COLORS['grey'],
             COLORS['magenta'], COLORS['grey'], COLORS['green']]]]

##############################################################################################

exception = False

##############################################################################################

def match(args, line, regex, colors, local):
   m = re.match(regex, line)
   if m:
      work_around = None
      index = -1
      for group in m.groups():
         if args.verbose:
            if group is None:
               print('{ None }', end = '')
            else:
               print('{' + group + '}', end = '')
         #if args.verbose and not work_around is None:
         #   print('[' + str(work_around) + '.' + group + '.' + str.strip(work_around) + ']')
         if group is None: # ()? gives None groups
            #print(group, work_around)
            if work_around != group: # BUGGY If the same value turn up twice this is not detected
               index += 1
         elif work_around is None or work_around.find(group) == -1 or str.strip(group) == '': # Work around using ( )
            # BUG ((|)) define 2 groups not one!
            index += 1
            if index >= len(colors):
               if args.cycle_color:
                  index = 0
               else:
                  exception = True
                  raise Exception('Ran out of colors on ' + line)
            if colors[index] > 0: # BUG TODO DONE BUG What???
               print(color_code(colors[index], args.blank) + group, end = '')
            else:
               found = False
               for pattern in local:
                  for regex, color in pattern:
                     if args.verbose:
                        print(regex, color)
                     m = re.match(regex, group)
                     if m:
                        found = True
                        print(color_code(color, args.blank) + group, end = '')
                        break
                  if not found:
                     if args.abort_no_match:
                        exception = True
                        raise Exception('Could not match group')
                     print(color_code(light(COLORS['red']), args.blank) + group, end = '')
               #if args.verbose:
               #   print(color_code(light(COLORS['green']), args.blank) + group, end = '')
         work_around = group
      if not args.blank:
         print(color_code(blank = args.blank))
      else:
         print()
      if (index != len(colors) - 3 and index != len(colors) - 2 and index != len(colors) - 1) and args.abort_color:
        exception = True
        raise Exception('Number of colors does not match') # BUG problem with 1,2c3,4
      return True
   return False

##############################################################################################

def main(args):
   print(__file__ + ' ' + VERSION + ' ' + AUTHOR)
   while True:
      try:
         line = input()
      except EOFError:
         break

      matched = False
      for (regex, colors, *local) in matches:
         matched = match(args, line, regex, colors, local)
         if matched:
            break
      if not matched:
         if not args.blank and not args.default_not_red:
            print(color_code(light(COLORS['red']), args.blank), end = '')
         print(line, end = '')
         if not args.blank and not args.default_not_red:
            print(color_code(blank = args.blank), end = '')
         print()
         if args.abort_no_match:
            break

##############################################################################################

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description = 'Colourize input')
   parser.add_argument('-m', '--match_file', help = 'NOT IMPLEMENTED YET! Match file')
   parser.add_argument('-d', '--read_file', help = 'NOT IMPLEMENTED YET! Read file') # Multiple
   parser.add_argument('-r', '--default_not_red', action = 'store_true',
                       help = 'Don''t color anything not recognized with red')
   parser.add_argument('-v', '--verbose', action = 'store_true', help = 'Verbose')
   parser.add_argument('-b', '--blank', action = 'store_true', help = 'Blank - no color')
   parser.add_argument('-e', '--raise_exception', action = 'store_true', help = '(Re)Raise exceptions to shell')
   parser.add_argument('-c', '--cycle_color', action = 'store_true', help = 'Cycle color if running out of colors')
   parser.add_argument('-a', '--abort_no_match', action = 'store_true', help = 'Abort if no match')
   parser.add_argument('-n', '--abort_color', action = 'store_true', help = 'Abort if number of colors don''t match')
   args = parser.parse_args()

   main(args)
   try:
      main(args)
   except KeyboardInterrupt:
      pass
   except Exception as e:
      if exception:
         while True:
            try:
               line = input() # Empty the input buffer
            except EOFError:
               break
      if args.raise_exception:
         raise
      else:
         print()
         print(color_code(light(COLORS['red']), args.blank), end = '')
         print(e)
         print(color_code(blank = args.blank), end = '')
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
