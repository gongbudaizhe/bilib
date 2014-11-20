#! /bin/sh
#
# %FFILE%
# Copyright (C) %YEAR% %USER% <%MAIL%>
#
# Distributed under terms of the %LICENSE% license.
#

# log and sendmail utilities
set -e

trap "terminated " INT TERM
trap "error" ERR
trap "clean_up" EXIT

if ! hash sendmail.py 2> /dev/null; then
    echo -e "\e[31mTo use sendmail.sh, you should put the sendmail.py in your PATH enviroment variable\e[0m" 
    echo -e "diable the sendmail utility"
    use_mail=false
else
    use_mail=true
fi

program=`basename $0`
time=`date +%Y%m%d-%H%M%S`
logname=log.$program.$time.txt

send(){
    $use_mail && sendmail.py -su $program -a $logname "$1"
}
clean_up(){
    send "all work is done ^_^"  
    exit 0
}
terminated(){
    trap - EXIT
    send " terminated!!!" 
    exit -1
}
error(){
    trap - EXIT
    send "error occured!!!"
    exit -2
}

###############################################################################
###             MAIN
###############################################################################
main(){
    %HERE% 
}
main &> $logname
