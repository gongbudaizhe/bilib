#! /bin/sh
#
# sendmail.sh
# A shell wrapper of sendmail.py
#
# Copyright (C) 2014 bily <gongbudaizhe@gmail.com>
#
# Distributed under terms of the MIT license.
#

# It's normally a good idea to set -e since it will terminate as soon
# as the first error occurs which prevents errors snowballing into serious
# issues when they could have been caught earlier.
set -e

# There are about four commands to check the existence of a program
# they are which, command, type and hash. As pointed in the reference 
# it is more safe to use builtins like hash, type or command
# 
# reference: http://stackoverflow.com/questions/592620/how-to-check-if-a-program-exists-from-a-bash-script
if ! hash sendmail.py 2> /dev/null; then
   # - the -e option of the echo command enable the parsing of the escape sequences. 
   # - \e is the escape of <ESP> in Linux, \x1B is for MacOSX and \033 is for all platforms
   # - \e[31m is the escape sequence of red color
   # - the \e[0m sequence removes all attributes(formatting and coloring).It can be a good idea
   #    to add it at the end of each colored text.
   #
   # colorful display reference: http://misc.flogisoft.com/bash/tip_colors_and_formatting
   echo -e "\e[31mTo use sendmail.sh, you should put the sendmail.py in your PATH enviroment variable\e[0m" 
   exit 1;
fi

# the trap format is:
#   trap command signal[signal...]
# INT:  Interrupt, this signal is sent when someone kills the script
#       by pressing Ctrl-c
# TERM: Terminate, this signal is sent when someone sends the TERM 
#       signal using the kill command
# EXIT: this is a pseudo-signal and is triggered when your script
#       exits, either through reaching the end of the script, an 
#       exit command or by a command failing when using set -e
# 
# Reference: http://www.davidpashley.com/articles/writing-robust-shell-scripts/
trap "clean_up" EXIT
trap "terminated" INT TERM
trap "error" ERR

program=$1
attachment=$2

if [ -z $program ];then
    program=program
fi

send(){
    if [ -z $attachmen ];then
        sendmail.py "$1"
    else
        sendmail.py -a $attachment "$1" 
    fi
}

clean_up(){
    send "${program}: all work is done ^_^" 
    #echo "${program}: all work is done ^_^" 
}

terminated(){
    # we need to unset the EXIT trap otherwise it will also be triggered
    trap - EXIT
    send "${program}: terminated!!!"
    #echo "${program}: terminated!!!"
}
error(){
    trap - EXIT
    send "${program}: error occured!!!"
    #echo "${program}: error occured!!!"

}
