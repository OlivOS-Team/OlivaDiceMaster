# -*- encoding: utf-8 -*-
r"""
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/

@File      :   data.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2026, OlivOS-Team
@Desc      :   None
"""

OlivaDiceMaster_ver = '3.0.35'
OlivaDiceMaster_svn = 36
OlivaDiceMaster_ver_short = '%s(%s)' % (str(OlivaDiceMaster_ver), str(OlivaDiceMaster_svn))

OlivaDiceMaster_oopm_host = 'http://api.dice.center/OlivaDiceVer'

globalProc = None

backupPath = './plugin/data/'

# OlivOS 插件目录，.oopm 安装/更新时在其中递归查找已有插件（支持子文件夹）
pluginAppDir = './plugin/app'

exportPath = './plugin/export'
