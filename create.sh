#!/bin/bash
# spec文件参考
# https://git.centos.org/blob/rpms!haproxy.git/c7/SPECS!haproxy.spec
# https://github.com/haproxy/haproxy/blob/master/examples/haproxy.spec


if [[ $# -ne 1 ]];then
    echo "请给定要编译的版本号,比如1.7.9"
    exit 1
fi

LongVersion=$1
ShortVersion=`echo $LongVersion|awk -F"." '{print $1"."$2}'`
SourceURL="http://www.haproxy.org/download/${ShortVersion}/src/haproxy-${LongVersion}.tar.gz"
HomeDir="$HOME/rpmbuild"
function check_result() {
    if [[ $1 != 0 ]];then
        echo "`date` $2 失败"
        if [[ $3 == 999 ]];then
            echo "程序退出"
            exit 1
        fi
    else
        echo "`date` $2 成功"
    fi
}

function install_req(){
	echo "检查依赖软件"
	REQ_PKGS='rpmdevtools rpm-build gcc gcc-c++ make openssl openssl-devel wget'
	rpm -V $REQ_PKGS || yum install -y $REQ_PKGS
}
install_req
mkdir -p $HOME/rpmbuild && /bin/rpmdev-setuptree
check_result $? '创建相关目录' 999

# cd $HOME/rpmbuild/SOURCES && wget $SourceURL
# check_result $? '获取源码文件' 999
/bin/cp -rf SPECS SOURCES $HomeDir && cd $HomeDir
check_result $? '拷贝源文件' 999

sed -i "s/^Version: .*/Version: $LongVersion/" SPECS/haproxy.spec && sed -i "s#^Source0: .*#Source0: $SourceURL#" SPECS/haproxy.spec
check_result $? '修改SPEC文件' 999

rpmbuild -bb SPECS/haproxy.spec
check_result $? '生成rpm' 999


