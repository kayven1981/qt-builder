# qt-builder 图形化QT源码编译工具

用于编译QT源码的图形化工具

## 1. QT 与 Windows XP 

---
### 支持Windows XP 的 QT 版本

  官方说在**QT 5.6.2** 以后的版本都不支持WindowsXP，但实际上 **QT 5.7.1**也是可以的。推荐使用5.7.1，至少他提供了QuickControls2的基本支持

---
### 编译器与编译选项
  - 尽量使用MingW编译器进行编译, 目前测试可用的版本有
    > **MinGW-5.3.0** 的32和64位版本
    > **MinGW-7.2.0** 的32和64位版本

  - 如果一定要用Visual C++，那最好用MSVC2010
    > QT 5.7.1 的configure脚本已经不再支持 **-target xp** 参数，MSVC2012以上
    > 版本会在你部署的时候给你带来一些的麻烦(工具链问题)

  - 编译时使用 **-opengl desktop** 参数
    > **不要使用 -opengl dynamic 或者 -opengl es2**
  - 添加 -no-angle以阻止QT使用ANGLE库：
    > ANGLE很久以前就不支持Windows XP了
    > 我曾经通过修改代码的方式强行编译成功，然而没有什么卵用：运行结果和狗屎一样
---
### Qt Quick 2D Render
  QT 5.7.1的Qt Quick环境使用OpenGL 2.x 作为渲染引擎，而Windows XP只支持 1.x。 如果想要在Windows XP上相对正常的使用Qt Quick，你必须编译并安装 Qt Quick 2D Render模块

  这个模块其实是一个用软件渲染（GUI渲染）来代替OpenGL渲染的 Qt scene graph render plugin

  如果想要使用Qt Quick 2D Render（如果你已经正确的安装了他），只需要修改一下的环境变量即可：
  > export QMLSCENE_DEVICE=softwarecontext（Linux）
  > set QMLSCENE_DEVICE=softwarecontext （Windows）

  Qt Quick 2D Render的代码并没有整合在Qt 5.7.1 中，需要单独code.qt.io克隆：
  > git clone https://code.qt.io/qt/qtdeclarative-render2d.git

  获取源码以后，像一个普通的Qt module一样编译并安装他就可以。
  > 需要注意的是，你用来编译Qt Quick 2D Render代码的Qt SDK本身必须配置了opengl支持
   
  Qt Quick 2D Render有很多使用上的限制
  > 具体请看Qt的官方说明：<http://doc.qt.io/QtQuick2DRenderer>

  最后说点没用的：
  > Qt 5.8.0以上的版本，已经内置支持了Qt Quick 2D Render。不止是可以使用软件渲染，还可以使用Direct3D 12来替代OpenGL进行渲染，真是牛逼啊！然而还是没有什么卵用，Qt 5.8.0以后的版本已经不支持Windows XP了
   