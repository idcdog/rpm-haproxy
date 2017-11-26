HOME=$(shell pwd)
MAINVERSION=1.7
VERSION=1.7.9
RELEASE=1

all: build

install_prereq:
	sudo yum install -y pcre-devel pcre-devel make gcc openssl-devel rpm-build rpmdevtools gcc openssl-devel wget

clean:
	rm -f ./SOURCES/haproxy-${VERSION}.tar.gz
	rm -rf ./rpmbuild
	mkdir -p ./rpmbuild/SPECS/ ./rpmbuild/SOURCES/ ./rpmbuild/RPMS/ ./rpmbuild/SRPMS/

download-upstream:
	test -f ./SOURCES/haproxy-${VERSION}.tar.gz || wget http://www.haproxy.org/download/${MAINVERSION}/src/haproxy-${VERSION}.tar.gz -O ./SOURCES/haproxy-${VERSION}.tar.gz 

build: install_prereq clean download-upstream
	cp -r ./SPECS/* ./rpmbuild/SPECS/ || true
	cp -r ./SOURCES/* ./rpmbuild/SOURCES/ || true
	rpmbuild -ba SPECS/haproxy.spec \
	--define "version ${VERSION}" \
	--define "release ${RELEASE}" \
	--define "_topdir %(pwd)/rpmbuild" \
	--define "_builddir %{_topdir}/BUILD" \
	--define "_buildroot %{_topdir}/BUILDROOT" \
	--define "_rpmdir %{_topdir}/RPMS" \
	--define "_srcrpmdir %{_topdir}/SRPMS"