# CPP_to_hex
可以调用系统的编译器，编译为 .hex 文件，建议搭配 "https://github.com/swswswswwsc/RunHex" 使用。较为轻量。
EXE 可执行文件由nuitka编译，比较原生速度来说十分快。
可以选择拖放开启，或是命令行开启。
1.拖放，将目标CPP文件（C也行）拖到此应用的图标上，他会自动生成 .hex 文件，不自动运行
2.命令行，按照以下格式（exe可执行文件的上层目录必须在系统Path中）:
"CPP_to_hex [你的目标文件路径] [1/0]" 
其中，1表示自动运行；0表示不自动运行。
各项声明请看 src中的声明

# CPP_to_hex
It can invoke the system compiler to compile files into .hex format. It is recommended to use it in conjunction with "https://github.com/swswswswwsc/RunHex". This tool is relatively lightweight.
The EXE executable file is compiled with Nuitka, which runs extremely fast compared to the native execution speed.
You can launch it either by drag-and-drop or via the command line:
1. Drag-and-drop: Drag the target CPP file (C files are also supported) onto the icon of this application, and it will automatically generate a .hex file without running it automatically.
2. Command line: Use the following format (the parent directory of the EXE executable must be added to the system Path):
"CPP_to_hex [your target file path] [1/0]" 
Where: 1 means run automatically; 0 means do not run automatically.
For all declarations, please refer to the statements in the src directory.
