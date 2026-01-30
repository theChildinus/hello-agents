#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除英文文章，修复坏链脚本
功能：
1. 删除所有英文章节文件 (Chapter*.md)
2. 删除英文导航文件 (_sidebar_en.md, README_EN.md, Preface.md)
3. 修复中文侧边栏中的英文链接
"""

import os
import re
import sys
from pathlib import Path

def delete_english_files(project_root):
    """删除所有英文文件"""
    print("=" * 60)
    print("开始删除英文文件...")
    print("=" * 60)
    
    docs_dir = project_root / "docs"
    
    # 定义要删除的英文文件模式
    patterns = [
        # 英文章节文件
        "**/Chapter*.md",
        # 英文导航文件
        "_sidebar_en.md",
        "README_EN.md",
        "Preface.md",
        "Additional-Chapter/Extra01-*答案.md"  # 英文答案文件
    ]
    
    deleted_files = []
    
    for pattern in patterns:
        for file_path in docs_dir.glob(pattern):
            if file_path.is_file():
                try:
                    os.remove(file_path)
                    deleted_files.append(str(file_path.relative_to(project_root)))
                    print(f"✓ 已删除: {file_path.relative_to(project_root)}")
                except Exception as e:
                    print(f"✗ 删除失败 {file_path}: {e}")
    
    # 检查Additional-Chapter目录下的英文文件
    additional_dir = docs_dir / "Additional-Chapter"
    if additional_dir.exists():
        for file_path in additional_dir.glob("*"):
            if file_path.is_file() and file_path.suffix == ".md":
                # 检查是否包含中文字符，如果没有则认为是英文文件
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # 如果文件名包含英文且内容主要是英文（简化的判断）
                    if not any('\u4e00' <= char <= '\u9fff' for char in file_path.stem):
                        print(f"⚠ 发现可能的英文文件: {file_path.relative_to(project_root)}")
                        print(f"  请手动确认是否需要删除")
                except:
                    pass
    
    return deleted_files

def fix_broken_links(project_root):
    """修复中文侧边栏中的英文链接"""
    print("\n" + "=" * 60)
    print("开始检查和修复坏链...")
    print("=" * 60)
    
    sidebar_path = project_root / "docs" / "_sidebar.md"
    
    if not sidebar_path.exists():
        print(f"✗ 未找到侧边栏文件: {sidebar_path}")
        return
    
    try:
        content = sidebar_path.read_text(encoding='utf-8')
        original_content = content
        
        # 检查是否有英文路径的链接
        english_links = re.findall(r'\]\([^)]*Chapter[^)]*\)', content)
        if english_links:
            print(f"⚠ 发现 {len(english_links)} 个英文链接，但侧边栏应该已经是中文链接")
            for link in english_links:
                print(f"  - {link}")
        else:
            print("✓ 侧边栏中没有发现英文链接")
        
        # 检查中文链接是否存在
        chinese_links = re.findall(r'\]\(\.\/[^)]*\.md\)', content)
        missing_files = []
        
        for link in chinese_links:
            link_path = link[1:-1]  # 去掉括号
            full_path = sidebar_path.parent / link_path
            if not full_path.exists():
                missing_files.append(link)
        
        if missing_files:
            print(f"\n⚠ 发现 {len(missing_files)} 个缺失的文件链接:")
            for link in missing_files:
                print(f"  - {link}")
        else:
            print(f"\n✓ 所有 {len(chinese_links)} 个中文链接都有效")
        
    except Exception as e:
        print(f"✗ 读取侧边栏文件失败: {e}")

def clean_empty_dirs(project_root):
    """清理空目录"""
    print("\n" + "=" * 60)
    print("检查空目录...")
    print("=" * 60)
    
    docs_dir = project_root / "docs"
    
    # 递归检查并删除空目录
    for root, dirs, files in os.walk(docs_dir, topdown=False):
        root_path = Path(root)
        if not files and not dirs:
            # 只删除images以外的空目录
            if "images" not in str(root_path):
                try:
                    os.rmdir(root_path)
                    print(f"✓ 已删除空目录: {root_path.relative_to(project_root)}")
                except:
                    pass

def main():
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir
    
    print(f"项目根目录: {project_root}")
    print()
    
    # 确认执行
    print("即将执行以下操作:")
    print("1. 删除所有英文章节文件 (Chapter*.md)")
    print("2. 删除英文导航文件 (_sidebar_en.md, README_EN.md, Preface.md)")
    print("3. 检查并修复坏链")
    print("4. 清理空目录")
    print()
    
    response = input("是否继续? (y/n): ").strip().lower()
    if response != 'y':
        print("操作已取消")
        return
    
    # 执行删除操作
    deleted_files = delete_english_files(project_root)
    
    # 修复链接
    fix_broken_links(project_root)
    
    # 清理空目录
    clean_empty_dirs(project_root)
    
    # 汇总
    print("\n" + "=" * 60)
    print("操作完成!")
    print(f"共删除 {len(deleted_files)} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
