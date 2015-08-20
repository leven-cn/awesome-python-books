#!/usr/bin/env python3

# Copyright (c) 2015 Li Yun <leven.cn@gmail.com>
# All Rights Reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''重建Python 3环境 (root 权限)

支持操作系统：

- CentOS 7.0

'''

import sys
import platform
import subprocess
import argparse


def shell_output(cmd):
    '''Run a shell command and return the result string.

    @param cmd shell command
    @return result string
    '''
    return subprocess.check_output(cmd, shell=True).decode('utf-8')


def cpu_cores():
    '''Get the CPU cores.

    @return a tuple of (physical cores, logical cores)
    '''
    # 查看CPU物理核数
    #     cat /proc/cpuinfo | grep "physical id" | uniq | wc -l
    physical_cores = int(shell_output('cat /proc/cpuinfo | grep "physical id" | uniq | wc -l'))

    # 查看CPU逻辑核数
    #     cat /proc/cpuinfo| grep "processor" | uniq | wc -l
    logical_cores = int(shell_output('cat /proc/cpuinfo | grep "processor" | uniq | wc -l'))
    return physical_cores, logical_cores


def build_python_from_source(logical_cpu_cores=1):
    '''Build python from the source code.

    @param logical_cpu_cores number of CPU logical cores
    '''
    subprocess.check_call('./configure --prefix=/usr', shell=True)
    subprocess.check_call('make -j{}'.format(logical_cpu_cores), shell=True)
    subprocess.check_call('sudo make install', shell=True)


def install_or_update_pip_pkgs():
    '''Install or update python extension packages with pip.

    $ sudo pip3 install --upgrade <python-pkg ...>
    '''
    subprocess.check_call('sudo pip3 install --upgrade pip pep8', shell=True)


if __name__ == '__main__':
    if platform.system() != 'Linux':
        sys.exit('Only support Linux')

    parser = argparse.ArgumentParser(description='Rebuild Pythn 3 environment.')
    parser.add_argument('commands', metavar='command', type=str, nargs='+',
                   help='a command to be executed, one of "upgrade-python", "upgrade-pip"')
    parser.add_argument('--foo', help='foo help')

    # 解析命令行参数
    _upgrade_python = False
    _upgrade_pip = False
    args = parser.parse_args()
    if 'upgrade-pip' in args.commands:
        _upgrade_pip = True
    if 'upgrade-python' in args.commands:
        _upgrade_python = True
        _upgrade_pip = True

    # 更新依赖包
    os_name, os_version,  _ = platform.dist()
    if os_name == 'centos':
        if os_version > '7.0':
            # 更新Yum
            subprocess.check_call('sudo yum install yum yum-utils deltarpm', shell=True)

            # 更新核心组件
            subprocess.check_call('sudo yum install bash bash-completion sudo python coreutils \
                    binutils vim openssh openssh-server gcc gcc-c++ openssl-devel', shell=True)

            # 更新Python依赖包
            if _upgrade_python:
                subprocess.check_call('sudo yum install sqlite-devel', shell=True)

    
    # 源码编译并安装
    if _upgrade_python:
        logical_cpu_cores, _ = cpu_cores()
        build_python_from_source(logical_cpu_cores)

    # 安装拓展包
    if _upgrade_pip:
        install_or_update_pip_pkgs()
