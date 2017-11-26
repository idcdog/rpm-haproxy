## 说明
用于生成haproxy rpm包
## 使用
git clone https://github.com/idcdog/rpm-haproxy.git
cd rpm-haproxy
make
## 备注
* 生成的rpm路径为rpm-haproxy/rpmbuild/RPMS/x86_64/haproxy-x.x.x-1.x86_64.rpm
* 默认生成的是1.7.9版本，如果需要其他版本，可以修改makefile中以下两个字段
> MAINVERSION=1.7  
> VERSION=1.7.9  
> 