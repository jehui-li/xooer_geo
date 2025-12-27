#!/usr/bin/env python3
"""
验证项目基础设施是否设置正确
运行此脚本前，请先安装依赖: pip install -r requirements.txt
"""

import sys
from pathlib import Path

def check_structure():
    """检查项目目录结构"""
    required_dirs = [
        "src",
        "src/connectors",
        "src/analyzers",
        "src/scorers",
        "src/probes",
        "src/strategists",
        "config",
        "utils",
        "tests",
        "logs",
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ 缺少目录: {', '.join(missing_dirs)}")
        return False
    else:
        print("✅ 项目目录结构完整")
        return True

def check_files():
    """检查必需文件"""
    required_files = [
        "requirements.txt",
        ".env.example",
        "config/settings.py",
        "utils/logger.py",
        "README.md",
        ".gitignore",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少文件: {', '.join(missing_files)}")
        return False
    else:
        print("✅ 必需文件完整")
        return True

def check_imports():
    """检查模块导入"""
    try:
        from config.settings import settings
        print("✅ 配置模块导入成功")
        
        from utils.logger import logger
        print("✅ 日志模块导入成功")
        
        # 测试配置
        print(f"   日志级别: {settings.log_level}")
        print(f"   应用环境: {settings.app_env}")
        print(f"   Temperature 列表: {settings.temperature_list}")
        
        # 测试日志
        logger.info("日志系统测试 - INFO 级别")
        logger.debug("日志系统测试 - DEBUG 级别")
        
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("   请先安装依赖: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("GEO Agent 基础设施验证")
    print("=" * 50)
    print()
    
    results = []
    results.append(("目录结构", check_structure()))
    print()
    results.append(("文件检查", check_files()))
    print()
    results.append(("模块导入", check_imports()))
    print()
    
    print("=" * 50)
    if all(result[1] for result in results):
        print("✅ 所有检查通过！基础设施搭建完成。")
        return 0
    else:
        print("❌ 部分检查未通过，请查看上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())

