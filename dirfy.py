#!/usr/bin/python3
#
# dirfy
# an async webpath scanner based on asyhttp
#
# Version: 0.1
# Author: pyno
#

import sys, getopt
from asyhttp import loop
from dye import *
import threading

ver = "0.1"
global_progress = 0
global_total = 0
progress_lock = threading.BoundedSemaphore()
LOG_ENABLED = True
logfile = None

def read_file(filepath):
    try:
        with open(filepath, "r") as file:
            return [f for f in file.readlines()]
    except Exception as e:
        print(e)    

def print_help():
    print("  Usage:")
    print("    -u <url>                   :- target URL")
    print("    -e <extensions>            :- comma separated extension list")
    print("    -p <proxy>                 :- proxy string (e.g. http://myproxy:8080)")
    print("    -d <dict_file>             :- dictionary file (default is list.txt)")
    print("    -f <false_positives_file>  :- file containing strings that indicate false positives")
    print("    -c <max_concurrent>        :- maximum number of concurrent requests (default 1000)")
    print("    -r                         :- follow redirects")
    print("    -n                         :- disable logging")

def main(argv):
    arg_exts = ""
    arg_proxy_url = ""
    arg_ext_list = ""
    wordlist_path = "./list.txt"
    arg_max_concurrent = 1000
    arg_allow_redirects = False
    fps = []
    fps_file = ""

    sys.stdout.write(" ----------------------\n")
    sys.stdout.write("  dirfy v{}".format(ver)+"\n")
    sys.stdout.write(" ----------------------\n")

    try:
        opts, args = getopt.getopt(argv,"hu:e:p:d:f:c:rn",[
                                                        "url=","extensions=","proxy=",
                                                        "dict=","false-positives=,max-concurrent=",
                                                        "follow-redirects", "disable-log"
                                                        ])
    except getopt.GetoptError as goe:
        print(fg.RED+' [!] '+str(goe)+'\n'+fg.RESET)
        print_help()
        sys.exit(2)

    if(opts == []):
        print_help()
        sys.stdout.write(" ----------------------\n")
        sys.exit(0)

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-u", "--url"):
            arg_url = arg
        elif opt in ("-p", "--proxy"):
            arg_proxy_url = arg
        elif opt in ("-e", "--extensions"):
            arg_exts = arg
            arg_ext_list = arg_exts.split(",")
        elif opt in ("-d", "--dict"):
            wordlist_path = arg
        elif opt in ("-f", "--false-positives"):
            fps_file = arg
            fps = [fp[:-1] for fp in  open(fps_file,'r').readlines()]
        elif opt in ("-c", "--max-concurrent"):
            arg_max_concurrent = int(arg)
        elif opt in ("-r", "--follow-redirects"):
            arg_allow_redirects = True
        elif opt in ("-n" "--disable-log"):
            global LOG_ENABLED
            LOG_ENABLED=False
            
    if LOG_ENABLED:
        global logfile
        logfile = open('./log.txt','a')
            
    path_list = [d for d in read_file(wordlist_path)]
    target=arg_url+"/{}"

    url_dict_list = []
    for path in path_list:
        if "%EXT%" in path:
            for ext in arg_ext_list:
                repl_path = path.replace('%EXT%',ext)
                url_dict = {}
                url_dict["url"] = target.format(repl_path[:-1])
                url_dict["method"] = "GET"
                url_dict_list.append(url_dict)
        else:
            url_dict = {}
            url_dict["url"] = target.format(path[:-1])
            url_dict["method"] = "GET"
            url_dict_list.append(url_dict)

    global global_total
    global_total = len(url_dict_list)

    sys.stdout.write(fg.HBLUE+" [i] tARGET                  {}{}\n".format(fg.RESET,arg_url))
    sys.stdout.write(fg.HBLUE+" [i] eXTENSIONS              "+fg.RESET+"{}".format(arg_ext_list)+"\n")
    sys.stdout.write(fg.HBLUE+" [i] pROXY                   "+fg.RESET+"{}".format(arg_proxy_url)+"\n")
    sys.stdout.write(fg.HBLUE+" [i] wORDLIST                "+fg.RESET+"{} ({})".format(wordlist_path, 
                                                                                           len(url_dict_list))+"\n")
    if len(fps) > 0:
        sys.stdout.write(fg.HBLUE+" [i] fALSE pOSITIVES         "+fg.RESET+"{} ({})".format(fps_file, 
                                                                                        len(fps))+"\n")
    else:
        sys.stdout.write(fg.HBLUE+" [i] fALSE pOSITIVES         "+fg.RESET+"\n")
    sys.stdout.write(fg.HBLUE+" [i] mAX cONCURRENT rEQUESTS "+fg.RESET+"{}".format(arg_max_concurrent)+"\n")
    sys.stdout.write(fg.HBLUE+" [i] aLLOW rEDIRECTS         "+fg.RESET+"{}".format(arg_allow_redirects)+"\n")
    input("\n [+] pRESS a kEY tO cONTINUE..")
    print("\n")

    try:
        loop(url_dict_list,process_out=process_output, proxy=arg_proxy_url, redirects=arg_allow_redirects,
                max_concurrent=arg_max_concurrent,
                usrdata={'false_positives':fps})
    except KeyboardInterrupt as ki:
        sys.stdout.write(fg.RED+"\n\n [!] eXITING"+fg.RESET)
        sys.stdout.flush()

    if LOG_ENABLED:
        logfile.flush()
        logfile.close()

    sys.stdout.write("\n [+] bYE")
    sys.stdout.write("\n")

def show_progress():
    global global_progress
    global global_total
    global progress_lock

    reqs_for_a_block = global_total / 20

    # critical section
    progress_lock.acquire()
    global_progress += 1
    num_blocks = int(global_progress / reqs_for_a_block)
    progress_lock.release()
    # end critical section

    sys.stdout.write("\r [+] |{}{}| - {}/{} ".format(bg.GREEN+" "*(num_blocks)+bg.RESET, 
                                                            " "*(20-num_blocks), 
                                                            global_progress, global_total))
    sys.stdout.flush()


def is_fp(resp, fps):
    for fp in fps:
        try:
            if fp in resp.decode("UTF-8"):
                return True
        except UnicodeDecodeError as ude:
            return False
    return False

def LOG(s):
    if LOG_ENABLED:
        logfile.write(s)
        logfile.flush()

        logfile.write(s)
        logfile.flush()

def process_output(url,return_code,reason,resp_body, usrdata):
    show_progress()
    #if return_code == 404:
    resp_length = len(resp_body)
    if return_code == 200 and not is_fp(resp_body, usrdata['false_positives']) and resp_length > 0:
        sys.stdout.write("\r  "+fg.HYELLOW+'{:<6}'.format(resp_length)+fg.RESET+" [ "+str(return_code)+" - "+reason+" ]")
        sys.stdout.write(fg.BLUE+' {:<40}'.format(url)+fg.RESET)
        sys.stdout.write("\n")
    LOG("  {:<6}".format(resp_length)+" [ "+str(return_code)+" - "+reason+" ]" + ' {:<40}\n'.format(url))
    #LOG(' {:<40}\n'.format(url))

if __name__ == "__main__":
    main(sys.argv[1:])


