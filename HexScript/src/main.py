# coding=utf-8
import time
import os
import sys
import shutil
import subprocess
import platform

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys, '_enablelegacywindowsfsencoding'):
        sys._enablelegacywindowsfsencoding()

def printm(m: str):
    log_msg = f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}::{m}"
    print(log_msg, flush=True)
    if platform.system() == 'Windows':
        with open("HexScript运行日志.txt", "a", encoding='utf-8') as f:
            f.write(log_msg + "\n")

def detect_compiler():
    printm("开始搜索编译器")
    candidates = ['g++', 'clang++', 'cl', 'c++']
    for c in candidates:
        printm(f"正在搜索编译器: {c}")
        if shutil.which(c):
            printm(f"检测到编译器: {c}")
            return c
    raise RuntimeError("未检测到任何可用的 C/C++ 编译器，请先安装 g++/clang++/MSVC 等。")

def detect_objcopy():
    printm("开始搜索 objcopy 工具")
    candidates = ['objcopy', 'llvm-objcopy', 'x86_64-w64-mingw32-objcopy']
    
    if platform.system() == 'Windows':
        candidates.extend(['objcopy.exe', 'llvm-objcopy.exe'])
    
    for tool in candidates:
        printm(f"正在搜索工具: {tool}")
        if shutil.which(tool):
            printm(f"检测到工具: {tool}")
            return tool
    
    printm("警告: 未找到 objcopy 工具，将跳过 HEX 转换步骤")
    return None

def auto_compile(source_path, output_path=None):
    source_path = os.path.abspath(source_path)
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"源文件不存在: {source_path}")
    
    ext = os.path.splitext(source_path)[1].lower()
    if ext not in ['.cpp', '.c', '.cxx']:
        raise RuntimeError(f"仅支持编译 .cpp/.c/.cxx 文件，当前文件类型: {ext}")
    
    compiler = detect_compiler()
    
    if not output_path:
        base = os.path.splitext(source_path)[0]
        if platform.system() == 'Windows':
            output_path = base + '.exe'
        else:
            output_path = base + '.out'
    output_path = os.path.abspath(output_path)
    
    if compiler == 'cl':
        cmd = [compiler, '/Fe:' + output_path, source_path, '/O2', '/nologo']
    else:
        cmd = [compiler, source_path, '-o', output_path, '-O2']
    
    printm(f"执行编译命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            shell=False
        )
        if result.returncode != 0:
            raise RuntimeError(f"编译失败: {result.stderr}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"编译失败: {e}")
    except Exception as e:
        raise RuntimeError(f"编译异常: {str(e)}")
    
    if not os.path.exists(output_path):
        raise RuntimeError(f"编译后未生成可执行文件: {output_path}")
    
    return output_path

def to_hex(executable_path, hex_path=None):
    executable_path = os.path.abspath(executable_path)
    objcopy = detect_objcopy()
    
    if not objcopy:
        printm("跳过 HEX 转换: 未找到 objcopy 工具")
        return executable_path  
    
    if not hex_path:
        base = os.path.splitext(executable_path)[0]
        hex_path = base + '.hex'  
    hex_path = os.path.abspath(hex_path)
    
    cmd = [objcopy, '-O', 'ihex', executable_path, hex_path]
    
    printm(f"执行转换命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.returncode != 0:
            raise RuntimeError(f"HEX转换失败: {result.stderr}")
    except subprocess.CalledProcessError as e:
        printm(f"警告: HEX 转换失败: {e}")
        return executable_path
    except Exception as e:
        printm(f"警告: HEX 转换异常: {str(e)}")
        return executable_path
    
    if os.path.exists(hex_path):
        printm(f"HEX 文件已生成: {hex_path}")
        return hex_path
    else:
        printm("警告: HEX 文件生成失败")
        return executable_path

def main():
    if len(sys.argv) < 2:
        printm("错误: 请将 .cpp/.c 文件拖拽到本程序上运行！")
        if platform.system() == 'Windows':
            os.system("pause")
        sys.exit(1)
    
    source_file = sys.argv[1]
    run_after = sys.argv[2] if len(sys.argv) > 2 else "0"
    
    if run_after not in ["0", "1"]:
        printm("错误: 运行参数仅支持 '1'(运行) 或 '0'(不运行)，已自动设为0")
        run_after = "0"
    
    start_time = time.time()
    printm("="*50)
    printm("HexScript开始运行->编译CPP")
    printm(f"待编译文件: {source_file}")
    printm(f"运行标记: {'运行' if run_after == '1' else '不运行'}")
    printm("="*50)
    
    try:
        executable_path = auto_compile(source_file)
        printm(f"✅ 二进制可执行文件已生成: {executable_path}")
        
        final_output = to_hex(executable_path)
        printm(f"✅ 最终输出文件: {final_output}")
        
        if run_after == "1":
            printm(f"🔄 自动运行可执行文件: {executable_path}")
            try:
                if final_output.endswith('.hex'):
                    printm("⚠️ 注意: .hex 文件无法直接执行，跳过运行步骤")
                else:
                    run_result = subprocess.run(
                        [executable_path],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        shell=False
                    )
                    if run_result.returncode != 0:
                        printm(f"❌ 运行失败: {run_result.stderr}")
                    else:
                        printm(f"✅ {executable_path} 已运行完成")
                        if run_result.stdout:
                            printm(f"运行输出: {run_result.stdout}")
            except PermissionError:
                printm("❌ 权限错误: 无法执行文件，可能需要添加执行权限")
            except Exception as e:
                printm(f"❌ 运行异常: {str(e)}")
        else:
            printm(f"ℹ️ {executable_path} 未运行（默认配置）")
            
    except Exception as e:
        printm(f"❌ 执行错误: {str(e)}")
    
    end_time = time.time()
    printm("="*50)
    printm("✅ 过程结束")
    printm(f"⏱️  过程耗时: {end_time - start_time:.2f}秒")
    printm("📄 运行日志已保存至: HexScript运行日志.txt")
    printm("="*50)
    
    if platform.system() == 'Windows':
        printm("\n按任意键退出...")
        os.system("pause >nul")

if __name__ == "__main__":
    printm("")
    main()