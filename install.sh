#!/bin/sh -e
#
# install script
#
#   (c) 2021 Yoichi Tanibayashi
#
############################################################
help() {
    cat <<'END'

[インストール後のディレクトリ構造]

 $HOME/ ... ホームディレクトリ
    |
    +- bin/ .. BINDIR シェルスクリプトなど
    |   |
    |   +- Ytsched .. WRAPPER_SCRIPT
    |   +- boot-Ytsched.sh .. 起動スクリプト
    |
    +- ytsched/ .. WORKDIR
    |   |
    |   +- log/ .. LOGDIR
    |   |
    |   +- webroot/ .. WEBROOT
    |   |   |
    |   |   +- templates/
    |   |   +- static/
    |   |       |
    |   |       +- css/
    |   |       +- js/
    |   |       +- images/
    |   |       :
    |   |
    |   +- upload/
    |   +- data/ .. DATADIR
    |   :   |
    |   :   +- todo.txt
    |   :   +- 2021/
    |   :   :
    |
    +- env1/ .. python3 Virtualenv(venv) 【ユーザが作成する】
        |
        +- ytsched2/ .. MYDIR
        |   |
        |   +- build/ .. BUILD_DIR
        |
        +- subpackage1/
        |
        :

END
}

############################################################
MYNAME=`basename $0`
cd `dirname $0`
MYDIR=`pwd`
echo "MYDIR=$MYDIR"


MY_PKG="ytsched"
WRAPPER_SCRIPT="Ytsched"


echo "MY_PKG=$MY_PKG"
echo "WRAPPER_SCRIPT=$WRAPPER_SCRIPT"

WRAPPER_SRC="$WRAPPER_SCRIPT.src"
echo "WRAPPER_SRC=$WRAPPER_SRC"

BINDIR="$HOME/bin"
mkdir -pv $BINDIR

WORKDIR="$HOME/$MY_PKG"
echo "WORKDIR=$WORKDIR"

WEBROOT="$WORKDIR/webroot"
echo "WEBROOT=$WEBROOT"

LOGDIR="$WORKDIR/log"
echo "LOGDIR=$LOGDIR"

DATADIR="$WORKDIR/data"
echo "DATADIR=$DATADIR"

PKGS_TXT="pkgs.txt"

GITHUB_TOP="git@github.com:ytani01"

CUILIB_PKG="cuilib"
CUILIB_DIR="CuiLib"
CUILIB_GIT="${GITHUB_TOP}/${CUILIB_DIR}.git"

BUILD_DIR="$MYDIR/build"

INSTALLED_FILE="$BUILD_DIR/installed"

FAST_MODE=0

#
# fuctions
#
cd_echo() {
    cd $1
    echo "### [ `pwd` ]"
    echo
}

install_python_pkg_from_git() {
    _PKG=$1
    _DIR=$2
    _GIT=$3

    cd_echo $VIRTUAL_ENV

    echo "### install/update $_PKG"
    echo

    if [ ! -d $_DIR ]; then
        git clone $_GIT || exit 1
    fi

    cd_echo ./$_DIR
    git pull
    pip install .
    echo
}

usage() {
    echo
    echo "  Usage: $MYNAME [-u] [-h]"
    echo
    echo "    -f  fastmode"
    echo "    -u  uninstall"
    echo "    -c  clean"
    echo "    -h  show this usage"
    echo
}

uninstall() {
    cd_echo $MYDIR

    echo "### uninstall my python package"
    echo
    pip uninstall -y $MY_PKG
    echo

    echo "### remove installed files"
    echo
    rm -f `cat $INSTALLED_FILE`
    echo

    echo "### remove build/"
    echo
    rm -rfv build
    echo

    echo "### $WORKDIR"
    echo
    if [ -d $WORKDIR ]; then
        # rm -rfv $WORKDIR
        echo "WORKDIR=$WORKDIR: exists"
    fi
    echo
    
}

clean() {
    cd_echo $MYDIR

    echo "### clean"
    echo

    rm -rfv build dist *.egg-info
}

#
# main
#
cd_echo $MYDIR

while getopts fuch OPT; do
    case $OPT in
        f) FAST_MODE=1;echo "FAST_MODE=$FAST_MODE";;
        u) uninstall; exit 0;;
        c) clean; exit 0;;
        h) help; echo "#####"; usage; exit 0;;
        *) usage; exit 1;;
    esac
    shift
done

#
# install Linux packages
#
if [ -f $PKGS_TXT ]; then
    PKGS=`cat $PKGS_TXT`
    if [ ! -z $PKGS ]; then
        echo "### install Linux packages"
        echo
        sudo apt install `cat $PKGS_TXT`
        echo
    fi
fi

#
# venv
#
if [ -z $VIRTUAL_ENV ]; then
    while [ ! -f ./bin/activate ]; do
        cd ..
        if [ `pwd` = "/" ]; then
            echo
            echo "ERROR: Please create and activate Python3 Virtualenv(venv) and run again"
            echo
            echo "\$ cd ~"
            echo "\$ python -m venv env1"
            echo "\$ . ~/env1/bin/activate"
            echo
            exit 1
        fi
    done
    echo "### activate venv"
    . ./bin/activate
fi
cd_echo $VIRTUAL_ENV

#
# version
#
cd_echo $MYDIR
MY_VERSION=`python setup.py --version`
echo "MY_VERSION=$MY_VERSION"
echo

#
# make $WRAPPER_SCRIPT
#
cd_echo $MYDIR

mkdir -pv $BUILD_DIR
echo -n > $INSTALLED_FILE
echo

echo "### build $WRAPPER_SCRIPT"

sed -e "s?%%% MY_PKG %%%?$MY_PKG?" \
    -e "s?%%% MY_VERSION %%%?$MY_VERSION?" \
    -e "s?%%% VENVDIR %%%?$VIRTUAL_ENV?" \
    -e "s?%%% WORKDIR %%%?$WORKDIR?" \
    -e "s?%%% WEBROOT %%%?$WEBROOT?" \
    -e "s?%%% DATADIR %%%?$DATADIR?" \
    $WRAPPER_SRC > $BUILD_DIR/$WRAPPER_SCRIPT

chmod +x $BUILD_DIR/$WRAPPER_SCRIPT
echo $BUILD_DIR/$WRAPPER_SCRIPT >> $INSTALLED_FILE

echo '-----'
cat $BUILD_DIR/$WRAPPER_SCRIPT | sed -n -e '1,/\#* main/p'
echo '  :'
echo '-----'
echo

#
# install scripts
#
echo "### install scripts"
echo
cp -fv $BUILD_DIR/$WRAPPER_SCRIPT $BINDIR
echo $BINDIR/$WRAPPER_SCRIPT >> $INSTALLED_FILE
echo

#
# work dir
#
for d in $WORKDIR $WEBROOT $LOGDIR; do
    echo "### $d"
    echo
    if [ ! -d $d ]; then
        mkdir -pv $d
        echo
    fi
done

if [ ! -z $WEBROOT ]; then
    cd_echo $MYDIR/webroot
    cp -rfv * $WEBROOT
    echo
fi

#
# update pip, setuptools, and wheel
#
if [ $FAST_MODE -lt 1 ]; then
    echo "### insall/update pip etc. .."
    echo
    pip install -U pip setuptools wheel
    hash -r
    echo
    pip -V
    echo
fi

#
# install my python packages
#
#if [ $FAST_MODE -lt 1 ]; then
#    install_python_pkg_from_git $CUILIB_PKG $CUILIB_DIR $CUILIB_GIT
#fi

#
# install my package
#
cd_echo $MYDIR
echo "### install my python package"
echo
pip install .
echo

#
# display usage
#
echo "### usage"
echo
$WRAPPER_SCRIPT -h
echo
