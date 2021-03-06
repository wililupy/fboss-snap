import logging
import multiprocessing
import os
import re
import shutil

import snapcraft

logger = logging.getLogger(__name__)


def _get_parallel_build_count():
    build_count = 1
    try:
        build_count = multiprocessing.cpu_count()
    except NotImplementedError:
        logger.warning('Unable to determine CPU count; disabling parallel '
                       'build')

    return build_count


def _search_and_replace_contents(file_path, search_pattern, replacement):
    with open(file_path, 'r+') as f:
        try:
            original = f.read()
        except UnicodeDecodeError:
            # This was probably a binary file. Skip it.
            return

        replaced = search_pattern.sub(replacement, original)
        if replaced != original:
            f.seek(0)
            f.truncate()
            f.write(replaced)


class XFbossPlugin(snapcraft.BasePlugin):

    @classmethod
    def schema(cls):
        return {}

    def __init__(self, name, options, project):
        super().__init__(name, options, project)

        # Most build tools are fetched by getdeps.sh, but we need to fetch the
        # source before we do anything, so we need git.
        self.build_packages.extend(['git'])

        # Run-time dependencies for folly
        self.stage_packages.extend(
            ['g++', 'automake', 'autoconf', 'autoconf-archive', 'libtool',
             'libboost-all-dev', 'libevent-dev', 'libdouble-conversion-dev',
             'libgoogle-glog-dev', 'libgflags-dev', 'liblz4-dev', 'liblzma-dev',
             'libsnappy-dev', 'make', 'zlib1g-dev', 'binutils-dev', 
             'libjemalloc-dev', 'libssl-dev', 'libunwind8-dev', 'libelf-dev',
             'libdwarf-dev', 'libiberty-dev'])

        # Run-time dependencies for fbthrift
        self.stage_packages.extend(
            ['flex', 'bison', 'libkrb5-dev', 'libsasl2-dev', 'libnuma-dev',
             'pkg-config', 'libssl-dev', 'make', 'autoconf', 'libtool', 'g++',
             'libboost-all-dev', 'libevent-dev', 'libgoogle-glog-dev', 
             'libdouble-conversion-dev', 'scons', 'libsnappy-dev'])

        # Run-time dependencies for iproute
        self.stage_packages.extend(['libdb5.3', 'libdb5.3-dev'])

        # Run-time dependencies for fboss
        self.stage_packages.extend(['libpcap0.8', 'libusb-1.0-0',
                                    'python-ipaddr', 'python-six',
                                    'python-concurrent.futures'])

    def pull(self):
        # logger.info('Obtaining FBOSS source...')

        # self.run(['git', 'clone', 'https://github.com/Facebook/fboss.git',
        #           self.sourcedir])

        logger.info('Obtaining (and building) FBOSS dependencies...')

        # This builds the dependencies right after pulling them. Not ideal for
        # the pull step, but it needs to be in the source directory so it makes
        # sense to keep it here rather than build.
        self.run(['./getdeps.sh'], cwd=self.sourcedir)

    def build(self):
        if os.path.exists(self.builddir):
            shutil.rmtree(self.builddir)
        os.mkdir(self.builddir)

        self.run(['cmake', self.sourcedir])
        self.run(['make', '-j{}'.format(_get_parallel_build_count())])

        # fboss has no install rules, so we'll need to install it all by
        # ourselves. FIXME: This should be fixed upstream.
        self._install()

    def _install(self):
        # First, install the binary
        bindir = os.path.join(self.installdir, 'bin')
        if not os.path.exists(bindir):
            os.mkdir(bindir)

        binaries = [
            os.path.join(self.builddir, 'wedge_agent'),
            os.path.join(self.sourcedir, 'fboss', 'agent', 'tools',
                         'fboss_route.py')
        ]

        for binary in binaries:
            shutil.copy(binary, bindir)

        # Now install the python modules needed by fboss_route.py
        modulesdir = self.dist_packages_dir()
        if not os.path.exists(modulesdir):
            os.mkdir(modulesdir)

        modules = [
            (os.path.join(self.builddir, 'gen', 'fboss', 'agent', 'if',
                         'gen-py', 'neteng'), 'neteng'),
            (os.path.join(self.builddir, 'gen', 'common', 'fb303', 'if',
                          'gen-py', 'fb303'), 'fb303'),
            (os.path.join(self.builddir, 'gen', 'common', 'network', 'if',
                          'gen-py', 'facebook'), 'facebook'),
            (os.path.join(self.sourcedir, 'external', 'fbthrift', 'thrift',
                         'lib', 'py'), 'thrift')
        ]

        for module in modules:
            shutil.copytree(module[0], os.path.join(modulesdir, module[1]))

        # Finally, install the external libraries
        libdir = os.path.join(self.installdir, 'lib')
        if not os.path.exists(libdir):
            os.mkdir(libdir)

        external_dir = os.path.join(self.sourcedir, 'external')

        libraries = [
            os.path.join(external_dir, 'folly', 'folly', '.libs',
                         'libfolly.so.57'),
            os.path.join(external_dir, 'fbthrift', 'thrift', 'lib', 'cpp',
                         '.libs', 'libthrift.so.32'),
            os.path.join(external_dir, 'fbthrift', 'thrift', 'lib', 'cpp2',
                         '.libs', 'libthriftcpp2.so.32'),
            os.path.join(external_dir, 'fbthrift', 'thrift', 'lib', 'cpp2',
                         '.libs', 'libthriftprotocol.so'),
            os.path.join(external_dir, 'OpenNSL', 'bin', 'wedge-trident',
                         'libopennsl.so.1')
        ]

        for library in libraries:
            shutil.copy(library, libdir)

    def dist_packages_dir(self):
        return os.path.join(self.installdir, 'usr', 'lib',
                            self.python_version(), 'dist-packages')

    def python_version(self):
        return self.run_output(['pyversions', '-d'])
