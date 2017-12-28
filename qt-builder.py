#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    用于编译QT源码的脚本，可以在有tk支持的python环境中直接编译QT源码， 或者按照指定
    配置生成无需tk支持（无界面）的编译脚本
"""
import tkinter.filedialog
import tkinter.font
import tkinter.messagebox
import tkinter as tk

import subprocess
import sys
import os
import threading
import platform
import enum
import copy
import functools
import shutil
import re
import ctypes

"""
    QT 模块类型：
        qtbase   : 基础框架，没他就没QT
        suggested: 推荐组件，非常有用
        osspec   : 系统组件，只能在特定操作系统上使用
        optional : 可选组件，提供特定功能，按需选择
        unknown  : 未知组件，不在QT5.10.0的源码包中
"""
class ModuleType(enum.IntEnum) :
    QTBASE    = 0
    SUGGESTED = 1
    OSSPEC    = 2
    OPTIONAL  = 3
    UNKNOWN   = 4
    
    def __str__(self) :
        nameList = (
            "基础框架", "推荐组件", "系统组件", 
            "可选组件", "未知组件"
        )
        return nameList[self.value]

"""
    QT 模块描述信息, 由作者（kayven）本人按照个人需求与喜好主观认定
    目前版本为QT 5.10.0
"""
KNOWN_MODULES = { 
    # 基础框架，没他就没QT
    'qtbase'            : {
        'name'          : 'qtbase',
        'description'   : '核心模块, 提供QT的核心功能和基础框架. 必须构建或者'
                          '存在于\"安装路径\"指定的位置',
        'type'          : ModuleType.QTBASE,
        'os'            : 'all',
        'selected'      : True,
        'dependence'    : []
    },
    # 重要的QT模块，功能完善，非常有用
    'qtdeclarative'     : {
        'name'          : 'qtdeclarative',
        'description'   : 'QML引擎,所有QML模块都需要它才能编译,没它就没QML',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase']   
    },
    'qtquickcontrols'   : {
        'name'          : 'qtquickcontrols',
        'description'   : 'QML控件库-V1,提供了基础的QML界面控件',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtquickcontrols2'  : {
        'name'          : 'qtquickcontrols2',
        'description'   : 'QML控件库-V2,提供了更好看和更多的QML界面控件. '
                          '建议编译',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase','qtdeclarative']   
    },
    'qtimageformats'    : {
        'name'          : 'qtimageformats',
        'description'   : '提供多种图像格式的支持(包括JPG，PNG等等)',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase']   
    },
    'qtmultimedia'      : {
        'name'          : 'qtmultimedia',
        'description'   : '提供基本的音视频编解码支持,可以用来做简单的影视片播放'
                          '和图像处理. ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase','qtdeclarative']   
    },
    'qtserialport'      : {
        'name'          : 'qtserialport',
        'description'   : '提供比较完善的串口设备访问支持. ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase']   
    },
    'qtsvg'             : {
        'name'          : 'qtsvg',
        'description'   : '提供了不完善但是基本可用的SVG图像格式支持. ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase']   
    },
    'qtxmlpatterns'     : {
        'name'          : 'qtxmlpatterns',
        'description'   : 'XML扩展支持模块(包括XPath, XSLT, XQuery等). ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase']   
    },
    'qtdoc'             : {
        'name'          : 'qtdoc',
        'description'   : '用于处理和生成QT格式文档(qdoc)的工具库. ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase']   
    },
    'qttools'           : {
        'name'          : 'qttools',
        'description'   : 'QT开发辅助工具(assist，designer和linguist). ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase','qtdeclarative']   
    },
    'qttranslations'    : {
        'name'          : 'qttranslations',
        'description'   : 'QT多语言支持. ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase']   
    },
    'qt3d'              : {
        'name'          : 'qt3d',
        'description'   : 'QT 3D绘图/渲染支持库. ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtcharts'          : {
        'name'          : 'qtcharts',
        'description'   : 'QT 2D图表库,相当有用. ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtcanvas3d'        : {
        'name'          : 'qtcanvas3d',
        'description'   : 'QT/QML 3D绘图/渲染支持库, 提供canvas标准接口. ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtdatavis3d'       : {
        'name'          : 'qtdatavis3d',
        'description'   : 'QT 3D图表库, 不太完善但基本可用. ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtwebsockets'      : {
        'name'          : 'qtwebsockets',
        'description'   : 'QT WebSocket支持库. ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtgraphicaleffects': {
        'name'          : 'qtgraphicaleffects',
        'description'   : 'QML图形变换效果支持库. ',
        'type'          : ModuleType.SUGGESTED,
        'os'            : 'all',
        'selected'      : True , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    # 只能在特定操作系统上编译/运行的模块 
    'qtactiveqt'        : {
        'name'          : 'qtactiveqt',
        'description'   : 'QT ActiveX控件支持，只能用于Windows系统. ',
        'type'          : ModuleType.OSSPEC,
        'os'            : 'windows',
        'selected'      : False    , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtwinextras'       : {
        'name'          : 'qtwinextras',
        'description'   : '提供windows特有的界面功能. ',
        'type'          : ModuleType.OSSPEC,
        'os'            : 'windows',
        'selected'      : False    , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtx11extras'       : {
        'name'          : 'qtx11extras',
        'description'   : '提供x11窗口系统特有的界面功能. ',
        'type'          : ModuleType.OSSPEC,
        'os'            : 'linux/posix',
        'selected'      : False        , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtandroidextras'   : {
        'name'          : 'qtandroidextras',
        'description'   : '提供android特有的界面功能. ',
        'type'          : ModuleType.OSSPEC,
        'os'            : 'android',
        'selected'      : False    , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtmacextras'       : {
        'name'          : 'qtmacextras',
        'description'   : '提供mac os特有的界面功能. ',
        'type'          : ModuleType.OSSPEC,
        'os'            : 'mac os x',
        'selected'      : False     , 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtserialbus'       : {
        'name'          : 'qtserialbus',
        'description'   : '官方说用于Linux/BootToQT的一个模块, 不知道干嘛的. ',
        'type'          : ModuleType.OSSPEC,
        'os'            : 'linux',
        'selected'      : False  , 
        'dependence'    : ['qtbase']   
    },
    # 比较鸡肋的模块, 用处不大麻烦不少 
    'qtvirtualkeyboard' : {
        'name'          : 'qtvirtualkeyboard',
        'description'   : 'QT虚拟键盘模块, 商业许可证, 而且不好用. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtconnectivity'    : {
        'name'          : 'qtconnectivity',
        'description'   : '蓝牙/NFC等连接支持, 不完善. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtgamepad'         : {
        'name'          : 'qtgamepad',
        'description'   : '游戏手柄, 摇杆, 虚拟摇杆等支持, 不完善. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']
    },
    'qtlocation'        : {
        'name'          : 'qtlocation',
        'description'   : 'QT地理位置支持模块，不完善但基本可用. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtremoteobjects'   : {
        'name'          : 'qtremoteobjects',
        'description'   : '5.10新增，不知道干嘛的. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtpurchasing'      : {
        'name'          : 'qtpurchasing',
        'description'   : 'QT交易市场库，莫名其妙，不建议用. '
                          '建议放弃',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtnetworkauth'     : {
        'name'          : 'qtnetworkauth',
        'description'   : '似乎是网络认证支持, 没用过, 不知道. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtscxml'           : {
        'name'          : 'qtscxml',
        'description'   : 'scxml支持模块，不完善而且没啥用. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtsensors'         : {
        'name'          : 'qtsensors',
        'description'   : '传感器支持，不完善而且需要特定硬件. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtspeech'          : {
        'name'          : 'qtspeech',
        'description'   : 'QT也有TTS, 你敢信? 你敢用? ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtwebchannel'      : {
        'name'          : 'qtwebchannel',
        'description'   : '没用过, 不知道干嘛的. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtwayland'         : {
        'name'          : 'qtwayland',
        'description'   : 'QT导航支持, 不完善, 不好用. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtwebglplugin'     : {
        'name'          : 'qtwebglplugin',
        'description'   : '没用过, 不知道干嘛的. 估计还需要WebEngine. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtwebview'         : {
        'name'          : 'qtwebview',
        'description'   : '在智能手机平台上还行(使用手机浏览器作为后端), '
                          '桌面操作系统上需要WebEngine. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    },
    'qtscript'          : {
        'name'          : 'qtscript',
        'description'   : '被放弃的QML引擎, 早就被qtdeclarative取代了. ',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase']   
    },
    'qtwebengine'       : {
        'name'          : 'qtwebengine',
        'description'   : '使用chromium作为后端的web浏览器模块, 其实还算'
                          '挺好用的, 就是编译太麻烦了...',
        'type'          : ModuleType.OPTIONAL,
        'os'            : 'all',
        'selected'      : False, 
        'dependence'    : ['qtbase', 'qtdeclarative']   
    }
}

def queryModuleList (path) :
    try:
        dirList = os.scandir(path)
    except:
        return []

    modList = []
    for it in dirList :
        if len(it.name) <= 2 or it.name[0:2] != "qt" or not it.is_dir():
            continue 
        if it.name not in KNOWN_MODULES :
            info = {
                'name'       : it.name,
                'description': '未知模块',
                'type'       : ModuleType.UNKNOWN,
                'os'         : '未知',
                'selected'   : False , 
                'dependence' : ['qtbase']
            }
        else:
            info = KNOWN_MODULES[it.name]
        mod = type('QtModule', (object,), copy.deepcopy(info))
        
        modList.append(mod)

    def modcmp(a, b) :
        if b.name in a.dependence:
            return  1
        if a.name in b.dependence:
            return -1
        return a.type - b.type
    
    modList.sort(key = functools.cmp_to_key(modcmp))
    return modList
def centerWindow    (top ) :
    top.update_idletasks()
    x = (top.winfo_screenwidth () - top.winfo_reqwidth ()) // 2
    y = 200
    w = top.winfo_reqwidth ()
    h = top.winfo_reqheight()
    g = "{w}x{h}+{x}+{y}".format(x = x,
                                 y = y,
                                 w = w,
                                 h = h)
    top.geometry(g)
def updateGeometry  (top ) :
    r = "(\d+)x(\d+)[-+](\d+)[-+](\d+)"
    m = re.match(r,top.geometry())
    x = int(m.groups()[2])
    y = int(m.groups()[3])

    top.update_idletasks()
    w = top.winfo_reqwidth ()
    h = top.winfo_reqheight()
    g = "{w}x{h}+{x}+{y}".format(x = x, 
                                 y = y,
                                 w = w, 
                                 h = h)
    top.geometry(g)
def copyTree        (src , dst) :
    for root, dirs, files in os.walk(src):
        for file in files:
            relpath = root.replace(src , '').lstrip(os.sep)
            srcpath = root
            dstpath = os.path.join(dst , relpath)
            if not os.path.isdir(dstpath):
                os.makedirs(dstpath)
            srcpath = os.path.join(srcpath, file)
            dstpath = os.path.join(dstpath, file)
            shutil.copyfile(srcpath, dstpath)
def preventHibernate(top ) :
    if platform.system() == "Windows" :
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    top.after(10 * 1000, lambda: preventHibernate(top))

class CfgArgsDlg(tk.Frame) :
    def __init__(self, args = "", master = None) :
        tk.Frame.__init__(self, master, relief = tk.FLAT)

        toplevel = tk.Toplevel(self.master)
        toplevel.title("修改配置参数")
        toplevel.protocol("WM_DELETE_WINDOW", 
                          self.onCancel)
        toplevel.grab_set()

        w = tk.Text (toplevel, width = 80, height = 20)
        w.config(wrap = 'word')
        w.insert('end',args)
        w.focus_set()
        w.grid(row        = 0,
               column     = 0, 
               columnspan = 5,
               padx       = 4, 
               pady       = 4)
        self.textedit = w

        w = tk.Button(toplevel, 
                      command = self.onOk,
                      width   = 8,
                      text    = "确定")
        w.grid(row    = 1, 
               column = 1, 
               pady   = 4)

        w = tk.Button(toplevel, 
                      command = self.onCancel,
                      width   = 8,
                      text    = "取消")
        w.grid(row    = 1, 
               column = 3,
               pady   = 4)

        self.toplevel = toplevel
        self.cfgargs  = args
        self.accepted = False

        toplevel.resizable(False, False)
    
    def onCancel(self) :
        self.accepted = False
        self.cfgargs  = ""
        self.toplevel.grab_release()
        self.toplevel.destroy()
    def onOk    (self) :
        args = self.textedit.get("0.0", "end")
        args = args.replace('\n', ' ')
        args = args.replace('\t', ' ')
        self.accepted = True
        self.cfgargs  = args
        self.toplevel.grab_release()
        self.toplevel.destroy()
    def doModal (self) :
        self.toplevel.withdraw ()
        updateGeometry(self.toplevel)
        centerWindow  (self.toplevel)
        self.toplevel.deiconify()
        self.toplevel.wait_window()

class ModuleView(tk.Frame) :
    def __init__(self, path = "", master = None) :
        tk.Frame.__init__(self, master, relief=tk.FLAT)

        self.groupViews = {}
        self.moduleList = queryModuleList(path)
        for it in self.moduleList :
            self.createModuleItem(it)

        for it in list(ModuleType) :
            if it not in self.groupViews:
                continue
            view = self.groupViews[it]
            view.pack(fill = 'x')

    def createModuleItem(self, info) :
        if info.type not in self.groupViews :
            self.createGroupView(info.type)

        view = self.groupViews[info.type]
        item = tk.Checkbutton(view, text = info.name)
        item.modinfo = info
        info.checked = tk.IntVar()
        info.widget  = item
        item.config(justify  = 'left',
                    variable = info.checked)

        def showDesc(e) :
            desc = e.widget.modinfo.description
            self.master.setStatusText(desc)
        def hideDesc(e) :
            self.master.setStatusText("")

        item.bind("<Enter>", showDesc)
        item.bind("<Leave>", hideDesc)

        if info.selected : 
            item.select()
        
        count = len(view.children.values()) - 1
        row   = count // 3
        col   = count %  3
        item.grid(row    = row,
                  column = col,
                  sticky = 'W')
    def createGroupView (self, type) :
        view = tk.LabelFrame(self, text = str(type))
        view.columnconfigure(0, minsize=150, weight = 1)
        view.columnconfigure(1, minsize=150, weight = 1)
        view.columnconfigure(2, minsize=150, weight = 1)

        self.groupViews[type] = view
    def selectModuleList(self) :
        modList = []
        for it in self.moduleList :
            if it.checked.get() :
                modList.append(it)
        return modList

class QTBuilder :
    def __init__(self, mainWindow) :
        self.ui = mainWindow
 
    def buildQt (self, **args) :
        self.srcpath = args['srcpath']
        self.dstpath = args['dstpath']
        self.confarg = args['confarg']
        self.makecmd = args['makecmd']
        self.makearg = args['makearg']
        self.makedoc = args['makedoc']
        self.skiperr = args['skiperr']
        self.modlist = args['modlist']

        self.retcode = False

        worker = threading.Thread(target = self.qtBuildThread,
                                  name   = 'worker')
        worker.start()
    
    def setupBuildEnv(self) :
        self.ui.writeBrief("准备编译环境......")
        #1. 保存并设置path环境变量    
        self.oldpath = os.environ['PATH']
        if platform.system() == "Windows" :
            path  = self.srcpath + ';/gnuwin32/bin'
            path += self.dstpath + ';/bin'
            path += ";C:\\mingw\\x64\\bin"
        else:
            path  = self.dstpath + ':/bin'
        os.environ['PATH'] += path
        
        #2. 创建用于进行shadow build的目录
        try :
            if os.path.exists("build") :
                shutil.rmtree("build")
            os.mkdir("build")
            os.chdir("build")
        except:
            self.ui.writeBrief ("失败\n")
            err  = str(sys.exc_info())
            err += "\n"
            self.ui.writeDetail(err)
            return False
        self.ui.writeBrief("成功\n")
        return True
    def clearBuildEnv(self) :
        os.environ['PATH'] = self.oldpath
        os.chdir('..')
    def buildQtMods  (self) :
        total = len(self.modlist)
        self.ui.writeBrief("\n开始编译QT功能模块(共 {0} 个)\n\n", total)

        count = 1
        for it in self.modlist :
            desc = it.description
            name = it.name

            self.ui.writeBrief("[{0:02d} of {1:02d}] {2}\n",
                               count,
                               total,
                               name )
            self.ui.writeBrief("{0}: {1}\n",
                               str(it.type),
                               desc )
                            
            if (not self.buildMod(it)) and (not self.skiperr) :
                return False
            count = count + 1
        return True
    def buildMod     (self, mod) :
        self.ui.clearDetail()

        os.mkdir(mod.name)
        os.chdir(mod.name)

        self.ui.writeBrief("配置模块......")
        if mod.type == ModuleType.QTBASE :
            cmdline = "{0}/qtbase/configure -prefix {1} {2} "
            cmdline = cmdline.format(self.srcpath,
                                     self.dstpath,
                                     self.confarg)
        else:
            cmdline = "{0}/bin/qmake {1}/{2}"
            cmdline = cmdline.format(self.dstpath, 
                                     self.srcpath, 
                                     mod.name   )
        if self.runCommand(cmdline) != 0 :
            self.ui.writeBrief("失败\n")
            os.chdir('..')
            return False
        self.ui.writeBrief("成功\n")

        self.ui.writeBrief("编译模块......")
        cmdline = "{0} {1}"
        cmdline = cmdline.format(self.makecmd, self.makearg)
        if self.runCommand(cmdline) != 0 :
            self.ui.writeBrief("失败\n")
            os.chdir('..')
            return False
        self.ui.writeBrief("成功\n")

        self.ui.writeBrief("安装模块......")
        cmdline = "{0} install"
        cmdline = cmdline.format(self.makecmd)
        if self.runCommand(cmdline) != 0 :
            self.ui.writeBrief("失败\n")
            os.chdir('..')
            return False
        self.ui.writeBrief("成功\n")

        src = "{0}/{1}/examples"
        src = src.format(self.srcpath, mod.name)
        dst = "{0}/examples"
        dst = dst.format(self.dstpath)
        if not os.path.exists(src) :
            os.chdir('..')
            return True

        self.ui.writeBrief("安装示例......")
        try :
            copyTree(src,dst)
        except:
            self.ui.writeBrief("失败\n")
            err = str(sys.exc_info())
            self.ui.writeDetail(err  + "\n")
            os.chdir('..')
            return False
        self.ui.writeBrief("成功\n")

        os.chdir('..')
        return True
    def buildQtDocs  (self) :
        total = len(self.modlist)
        self.ui.writeBrief("\n开始生成QT模块文档(共 {0} 个)\n\n", total)

        count = 1
        for it in self.modlist :
            desc = it.description
            name = it.name

            self.ui.writeBrief("[{0:02d} of {1:02d}] {2}\n",
                               count,
                               total,
                               name )
            if (not self.buildDoc(it)) and (not self.skiperr) :
                return False
            count = count + 1
        return True
    def buildDoc     (self, mod) :
        self.ui.clearDetail()

        os.chdir(mod.name)

        self.ui.writeBrief("生成文档......")
        cmdline = "{0} docs"
        cmdline = cmdline.format(self.makecmd)
        if self.runCommand(cmdline) != 0 :
            self.ui.writeBrief("失败\n")
            os.chdir('..')
            return False
        self.ui.writeBrief("成功\n")

        self.ui.writeBrief("安装文档......")
        cmdline = "{0} install_docs"
        cmdline = cmdline.format(self.makecmd)
        if self.runCommand(cmdline) != 0:
            self.ui.writeBrief("失败\n")
            os.chdir('..')
            return False
        self.ui.writeBrief("成功\n")

        os.chdir('..')
        return True
    def qtBuildThread(self) :
        self.ui.onBuildStarted()

        if self.modlist[0].type != ModuleType.QTBASE :
            coremsg  = ('*** ' +
                        '注意: QT基础框架(qtbase)不在'
                        '编译列表中，请确认 '
                        ' {0} 存在正确可用的QT基础框架'
                        '*** '
                        '\n\n')
            self.ui.writeBrief(coremsg, self.dstpath)

        while True :
            self.retcode = False
            if not self.setupBuildEnv() : 
                break
            if not self.buildQtMods  () :
                break
            if not self.makedoc         :
                self.retcode = True
                break
            if not self.buildQtDocs  () :
                break
            self.retcode = True
            break

        self.clearBuildEnv()
        self.ui.onBuildStopped()
    def runCommand   (self, cmd) :
        self.ui.writeDetail("{0}\n", cmd)
        proc = subprocess.Popen(cmd,
                                stdout  = subprocess.PIPE  ,
                                stderr  = subprocess.STDOUT,
                                shell   = True,
                                bufsize = 1,
                                universal_newlines = True)
        while proc.poll() is None:
            line = proc.stdout.readline()
            if not line:
                break
            logf = open("./qt-build.log", 'at')
            logf.write(line)
            logf.close()
            self.ui.writeDetail(line)
        line = proc.communicate()[0]
        if line :
            logf = open("./qt-build.log", 'at')
            logf.write(line)
            logf.close()
            self.ui.writeDetail(line)
        return proc.poll()

QT_CONFIGS = {
    'winnt-mingw': {
        'confarg': '-opensource -confirm-license -nomake examples '
                   '-opengl desktop '
                   '-plugin-sql-odbc -silent ',
        'makecmd': 'mingw32-make',
        'makearg': '-j4',
        'makedoc': 1,
        'skiperr': 0,
        'message': ''
    },
    'winnt-msvc' : {
        'confarg': '-opensource -confirm-license -nomake examples '
                   '-opengl desktop '
                   '-plugin-sql-odbc -silent -mp ',
        'makecmd': 'nmake',
        'makedoc': 1,
        'skiperr': 0,
        'makearg': '',
        'message': ''
    },
    'winxp-mingw': {
        'confarg': '-opensource -confirm-license -nomake examples '
                   '-opengl desktop '
                   '-plugin-sql-odbc -no-angle ',
        'makecmd': 'mingw32-make',
        'makedoc': 1,
        'skiperr': 1,
        'makearg': '-j4',
        'message': 'Windows XP上只能使用QT 5.7.1或者以下的版本'
    },
    'linux-g++'  : {
        'confarg': '-opensource -confirm-license -nomake examples '
                   '-opengl desktop -static'
                   '-silent -qt-xcb -fontconfig ',
        'makecmd': 'make',
        'makedoc': 1,
        'skiperr': 0,
        'makearg': '-j4',
        'message': '在Linux上使用缺省配置编译QT，请确认以下支持库已被安装：\n'
                   '    * mesa-common-dev    \n'
                   '    * libgl1-mesa-dev    \n'
                   '    * libglu1-mesa-dev   \n'
                   '    * freeglut3-dev      \n'
                   '    * libfontconfig1-dev   '
    }
}

class MainWindow(tk.Frame) :
    def __init__(self,  master = None) :
        tk.Frame.__init__(self, master, relief = tk.FLAT)

        welcome = "欢迎使用QT构建工具......"

        self.sourcePath = tk.StringVar()
        self.targetPath = tk.StringVar()
        self.makeCmd    = tk.StringVar()
        self.makeArgs   = tk.StringVar()
        self.configArgs = tk.StringVar()
        self.makeDoc    = tk.IntVar   (value = 1)
        self.skipError  = tk.IntVar   (value = 1)

        self.showDetail = tk.IntVar   (value = 0)
        self.moduleView = None
        self.statusText = tk.StringVar(value = welcome)
        self.detailView = self.createDetailPane()
        self.optWidgets = []
        self.qtBuilder  = QTBuilder(self)
        
        pane = self.createOptionPane()
        pane.grid(row    = 0, 
                  column = 0, 
                  pady   = 4, 
                  sticky = ("W","E"))
        self.optionPane = pane

        self.columnconfigure(0, weight = 10)

        pane = self.createStatusPane()
        pane.grid(row    = 2, 
                  column = 0, 
                  pady   = 0, 
                  sticky = ("W","E"))
        self.statusPane = pane

    def onBrowseSourcePath(self) :
        path = tk.filedialog.askdirectory()
        if not path :
            return
        if not self.setQtSourcePath(path) :
            return
        self.sourcePath.set(path)
    def onBrowseTargetPath(self) :
        path = tk.filedialog.askdirectory()
        if not path : 
            return
        self.targetPath.set (path)
    def onChangeSourcePath(self) :
        path = self.sourcePath.get()
        self.setQtSourcePath(path)        
    def onChangeConfigArgs(self) :
        dlg = CfgArgsDlg(self.configArgs.get(), self)
        dlg.doModal()
        if dlg.accepted:
            self.configArgs.set(dlg.cfgargs)
        updateGeometry(self.master)
    def onShowDetailWindow(self) :
        top = self.detailView.master
        if  self.showDetail.get() :
            self.updateDetailWindow()
            top.deiconify()
        else:
            top.withdraw ()
    def onHideDetailWindow(self) :
        top = self.detailView.master
        top.withdraw ()
        self.showDetail.set(0)
    def onBuildQt         (self) :
        if not self.checkUserInput() :
            return
        self.showDetail.set(1)

        srcpath = self.sourcePath.get()
        dstpath = self.targetPath.get()
        makecmd = self.makeCmd   .get()
        makearg = self.makeArgs  .get()
        confarg = self.configArgs.get()
        makedoc = self.makeDoc   .get()
        skiperr = self.skipError .get()
        modlist = self.moduleView.selectModuleList()

        self.qtBuilder.buildQt(srcpath = srcpath, 
                               dstpath = dstpath, 
                               makecmd = makecmd,
                               makearg = makearg,
                               confarg = confarg,
                               makedoc = makedoc,
                               skiperr = skiperr,
                               modlist = modlist)
    def onSaveBuildScript (self) :
        if not self.checkUserInput() :
            return
    def onBuildStarted    (self) :
        for it in self.moduleView.moduleList :
            widget = it.widget
            widget.config(state = 'disabled')
        for it in self.optWidgets :
            it.config(state = 'disabled')
        
        self.clearBrief ()
        self.clearDetail()

        self.showDetail.set(1)    
        self.onShowDetailWindow()
    def onBuildStopped    (self) :
        for it in self.moduleView.moduleList :
            widget = it.widget
            widget.config(state = 'normal')
        for it in self.optWidgets :
            it.config(state = 'normal')

        if not self.qtBuilder.retcode :
            msg = "编译QT时发生错误，请查看详细信息窗口以确认错误原因"
            tk.messagebox.showerror("发生错误", msg)
            self.showDetail.set(1)    
            self.onShowDetailWindow()
        else :
            msg = "QTSDK已经成功编译并安装"
            tk.messagebox.showinfo ("编译完成", msg)

    def createOptionPane  (self) :
        pane = tk.Frame(self, relief = 'flat')
        pane.columnconfigure(1, weight  = 10 , minsize = 100)
        pane.columnconfigure(3, weight  = 10 , minsize = 100)
        pane.rowconfigure   (0, minsize = 30 )
        pane.rowconfigure   (1, minsize = 30 )
        pane.rowconfigure   (2, minsize = 30 )
        pane.rowconfigure   (3, minsize = 30 )
        
        # 1. “源码位置”，输入框，按钮-浏览
        w = tk.Label(pane, text="源码位置：")
        w.grid(row        = 0, 
               column     = 0, 
               sticky     = ("W", "E"),
               padx       = 4)

        w = tk.Entry(pane, textvariable = self.sourcePath)
        w.bind("<Return>", 
               lambda e: self.onChangeSourcePath())
        w.grid(row        = 0, 
               column     = 1, 
               sticky     = ("W", "E"),
               columnspan = 3)
        self.optWidgets.append(w)

        w = tk.Button(pane, text = "浏览", relief  = 'flat')
        w.config(command  = self.onBrowseSourcePath)
        w.grid(row        = 0,
               column     = 4, 
               sticky     = ("W"), 
               padx       = 4)
        self.optWidgets.append(w)

        # 2. “安装位置”，输入框，按钮-浏览
        w = tk.Label(pane, text = "安装位置：")
        w.grid(row        = 1, 
               column     = 0, 
               sticky     = ("W", "E"),
               padx       = 4)
        
        w = tk.Entry(pane, textvariable = self.targetPath)
        w.grid(row        = 1, 
               column     = 1, 
               sticky     = ("W", "E"),
               columnspan = 3)
        self.optWidgets.append(w)
        
        w = tk.Button(pane, text = "浏览", relief  = 'flat')
        w.config(command  = self.onBrowseTargetPath)
        w.grid(row        = 1, 
               column     = 4, 
               sticky     = ("W"), 
               padx       = 4) 
        self.optWidgets.append(w)

        # 3. “编译命令：”，输入框-编译命令
        w = tk.Label(pane, text = "编译命令：")
        w.grid(row        = 2, 
               column     = 0, 
               sticky     = ("W", "E"),
               padx       = 4)

        w = tk.Entry(pane, textvariable = self.makeCmd   )
        w.grid(row        = 2, 
               column     = 1, 
               sticky     = ("W", "E"))
        self.optWidgets.append(w)

        w = tk.Label(pane, text = "编译参数：")
        w.grid(row        = 2, 
               column     = 2, 
               sticky     = ("W", "E"),
               padx       = 4)

        w = tk.Entry(pane, textvariable = self.makeArgs  )
        w.grid(row        = 2, 
               column     = 3, 
               sticky     = ("W", "E"))
        self.optWidgets.append(w)

        # 4. “配置参数：”，标签-配置参数，按钮-修改
        w = tk.Label(pane, text = "配置参数：")
        w.grid(row        = 3, 
               column     = 0, 
               sticky     = ('N', 'S', "W", "E"),
               padx       = 4)
        w.config(anchor='nw')

        def autowrap(e) :
            w = e.widget
            w.config(wraplength = e.width - 10)

        w = tk.Label(pane, textvariable = self.configArgs)
        w.config(justify    = 'left',
                 fg         = 'blue',
                 anchor     = 'nw'  ,
                 wraplength = 400   )
        w.bind("<Configure>", autowrap)
        w.grid(row        = 3, 
               column     = 1, 
               sticky     = ('N', 'S', "W", "E"),
               columnspan = 3)
        
        w = tk.Button(pane, text = "修改", relief  = 'flat')
        w.config(command  = self.onChangeConfigArgs)
        w.grid(row        = 3, 
               column     = 4, 
               sticky     = ("NW"), 
               padx       = 4) 
        self.optWidgets.append(w)
        
        # 5. 预设参数菜单
        argmenu = tk.Menu(self, tearoff = 0)

        if platform.system() == "Windows" :
            cfgname = "winnt-mingw"
            menucmd = lambda: self.loadConfig("winnt-mingw")
            argmenu.add_command(label   = cfgname,
                                command = menucmd)
            cfgname = "winnt-msvc"
            menucmd = lambda: self.loadConfig("winnt-msvc" )
            argmenu.add_command(label   = cfgname,
                                command = menucmd)
            cfgname = "winxp-mingw"
            menucmd = lambda: self.loadConfig("winxp-mingw")
            argmenu.add_command(label   = cfgname,
                                command = menucmd)
        if platform.system() == "Linux"   :
            cfgname = "linux-g++"
            menucmd = lambda: self.loadConfig("linux-g++"  )
            argmenu.add_command(label   = cfgname,
                                command = menucmd)

        # 6. 按钮-开始编译, 按钮-生成脚本, 复选按钮-详细信息
        f = tk.Frame(pane)
        itemList = []

        w = tk.Button     (f, text = "预设参数")
        w.config(relief = 'flat')
        w.pack(side = 'right', padx = 4)
        self.optWidgets.append(w)
        menubtn = w
        def showMenu() :
            x = menubtn.winfo_rootx ()
            y = menubtn.winfo_rooty ()
            w = menubtn.winfo_width ()
            h = menubtn.winfo_height()
            y = y + h
            argmenu.post(x, y)
        menubtn.config(command=showMenu)


        w = tk.Checkbutton(f, text = "详细信息")
        w.config(command  = self.onShowDetailWindow ,
                 variable = self.showDetail)
        w.pack(side = 'right', padx = 4)
        itemList.append(w)
        
        w = tk.Checkbutton(f, text = "强制构建")
        w.config(variable = self.skipError )
        w.pack(side = 'right', padx = 4)
        itemList.append(w)
        self.optWidgets.append(w)

        w = tk.Checkbutton(f, text = "生成文档")
        w.config(variable = self.makeDoc   )
        w.pack(side = 'right', padx = 4)
        itemList.append(w)
        self.optWidgets.append(w)

        w = tk.Button     (f, text = "生成脚本")
        w.config(command  = self.onSaveBuildScript  ,
                 relief   = 'flat')
        w.pack(side = 'right', padx = 4)
        itemList.append(w)

        w = tk.Button     (f, text = "开始构建")
        w.config(command  = self.onBuildQt          , 
                 relief   = 'flat')
        w.pack(side = 'right', padx = 4)
        itemList.append(w)
        self.optWidgets.append(w)

        for it in reversed(itemList) :
            it.lift()

        f.grid(row        = 4, 
               column     = 0, 
               columnspan = 5, 
               sticky     = ("W", "E"))

        return pane
    def createStatusPane  (self) :
        pane = tk.Label(self,
                        textvariable = self.statusText,
                        wraplength   = 400,
                        borderwidth  = 1,
                        padx         = 4, 
                        relief       = 'flat', 
                        anchor       = 'nw', 
                        justify      = 'left')

        def autowrap(e) :
            w = e.widget
            w.config(wraplength = e.width - 10)
        pane.bind("<Configure>", autowrap)

        return pane
    def createDetailPane  (self) :
        top   = tk.Toplevel(self.master)
        top.protocol("WM_DELETE_WINDOW", self.onHideDetailWindow)
        top.withdraw()

        pane  = tk.Frame(top, relief = tk.FLAT)

        frame = tk.LabelFrame(pane, text = "主要信息")
        sbar  = tk.Scrollbar(frame)
        view  = tk.Text(frame, width = 80, height = 15)
        view.configure(state = 'disabled')
        view.configure(yscrollcommand = sbar.set)
        sbar.configure(command = view.yview)

        view .pack(side = 'left', fill = 'both', expand = True)
        sbar .pack(side = 'left', fill = 'y')
        frame.pack(fill = 'both', expand = True)
        
        pane.brief   = view

        frame = tk.LabelFrame(pane, text = "详细信息")
        sbar  = tk.Scrollbar(frame)
        view  = tk.Text(frame, width = 80, height = 30)
        view.configure(state = 'disabled')
        view.configure(yscrollcommand = sbar.set)
        sbar.configure(command = view.yview)

        view.pack(side = 'left', fill = 'both', expand = True)
        sbar.pack(side = 'left', fill = 'y')
        frame.pack(fill = 'both', expand = True)
        
        pane.detail = view
        
        pane.pack(expand = True, fill='both')
        
        return pane

    def updateDetailWindow(self) :
        top = self.master
        r = "(\d+)x(\d+)[-+](\d+)[-+](\d+)"
        m = re.match(r,top.geometry())
        x = int(m.groups()[2]) + int(m.groups()[0])
        y = int(m.groups()[3])

        top = self.detailView.master
        w   = top.winfo_reqwidth ()
        h   = top.winfo_reqheight()
        g   = "{w}x{h}+{x}+{y}".format(x = x,
                                       y = y,
                                       w = w,
                                       h = h)
        top.geometry(g)

    def setQtSourcePath   (self, path) :
        view = ModuleView(path, self)
        if not view.moduleList :
            view.destroy()
            tk.messagebox.showerror("错误", "无效的源码路径")
            return False

        if self.moduleView : 
            self.moduleView.destroy()

        view.grid(row    = 1, 
                  column = 0, 
                  pady   = 4, 
                  sticky = ("W","E","N","S"))
        view.lift()
        updateGeometry(self.master)

        self.moduleView = view
        return True
    def loadConfig        (self, name) :
        if name not in QT_CONFIGS :
            return

        cfg = QT_CONFIGS[name]
        msg = cfg.get('message', '')
        if msg:
            tk.messagebox.showinfo("注意", msg)

        self.configArgs.set(cfg['confarg'])
        self.makeCmd   .set(cfg['makecmd'])
        self.makeArgs  .set(cfg['makearg'])
        self.makeDoc   .set(cfg['makedoc'])
        self.skipError .set(cfg['skiperr'])
        
    def setStatusText     (self, text) :
        self.statusText.set(text)
        updateGeometry(self.master)
    def checkUserInput    (self) :
        if not self.sourcePath.get() :
            tk.messagebox.showerror("错误", "无效的源码路径")
            return False
        if not self.moduleView       :
            tk.messagebox.showerror("错误", "无效的源码路径")
            return False
        if not self.targetPath.get() :
            tk.messagebox.showerror("错误", "无效的安装路径")
            return False
        if not self.makeCmd   .get() :
            tk.messagebox.showerror("错误", "请输入编译命令")
            return False
        if not self.configArgs.get() :
            tk.messagebox.showerror("错误", "请输入编译参数")
            return False
        return True
    def writeDetail       (self, text, *args, **kwargs) :
        if   args and kwargs :
            text = text.foramt(*args, **kwargs)
        elif args   :
            text = text.format(*args)
        elif kwargs :
            text = text.format(**kwargs)

        view = self.detailView.detail
        view.config(state = 'normal'  )
        view.insert('end', text)
        view.see('end')
        view.config(state = 'disabled')
    def writeBrief        (self, text, *args, **kwargs) :
        if   args and kwargs :
            text = text.foramt(*args, **kwargs)
        elif args   :
            text = text.format(*args)
        elif kwargs :
            text = text.format(**kwargs)

        view = self.detailView.brief
        view.config(state = 'normal'  )
        view.insert('end', text)
        view.see('end')
        view.config(state = 'disabled')
    def clearDetail       (self) :
        view = self.detailView.detail
        view.configure(state = 'normal'  )
        view.delete('0.0', 'end')
        view.see('end')
        view.configure(state = 'disabled')
    def clearBrief        (self) :
        view = self.detailView.brief
        view.configure(state = 'normal'  )
        view.delete('0.0', 'end')
        view.see('end')
        view.configure(state = 'disabled')

root = tk.Tk()
root.withdraw()
root.title("QT构建工具")
app  = MainWindow(root)
app.pack(expand = True, fill='both')
root.wm_minsize(640, 0)
root.resizable(False, False)
centerWindow(root)
root.deiconify()


preventHibernate(root)
root.mainloop()
