#! /bin/sh
#
# test_sendmail.sh
# Copyright (C) 2014 bily <bily@mclab>
#
# Distributed under terms of the MIT license.
#

#######################################
# CASE 1
# fails with attachment 
#######################################

# you can even pass parameters to sourced script, which is,
# astonishing!!!
. ./sendmail.sh bily.lee@qq.com sendmail.sh


#######################################
# CASE 2
# there is an error
#######################################

#. ./sendmail.sh bily.lee@qq.com 
#false


#######################################
# CASE 3
# run successfully without attachment
#######################################

#. ./sendmail.sh bily.lee@qq.com

