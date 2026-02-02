#!/usr/bin/env python3
"""
Markdown图片链接修复脚本 - Extra-Chapter专用版本
功能：扫描Extra-Chapter目录下所有的markdown文件，将<div align="center"> <img src="..."/>的HTML格式
转换为标准的Markdown图片格式
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# 支持的图片扩展名
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}

def find_markdown_files(directory: str) -> List[Path]:
    """
    递归查找目录下所有的markdown文件
    
    Args:
        directory: 根目录路径
        
    Returns:
        markdown文件路径列表
    """
    md_files = []
    root_path = Path(directory)
    
    for file_path in root_path.rglob('*.md'):
        if file_path.is_file():
            md_files.append(file_path)
    
    return sorted(md_files)


def fix_image_links_in_file(file_path: Path, dry_run: bool = False) -> Tuple[int, int]:
    """
    修复单个文件中的图片链接
    
    Args:
        file_path: markdown文件路径
        dry_run: 是否只显示不实际修改
        
    Returns:
        (修复数量, 文件总数)
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配模式：<div align="center"> 包含 <img src="..."/>
        # 处理多种格式，包括div内还有其他内容的情况
        # 只匹配简单的图片div，不匹配包含复杂内容的div
        
        # 方案：匹配 <img src="..."/> 直接跟在 <div align="center"> 后面的情况
        # 然后查找最近的 </div>
        
        lines = content.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 检查是否是 div align="center" 开始
            div_match = re.search(r'<div\s+align=["\']center["\']>', line)
            
            if div_match:
                # 收集接下来的行，直到找到 </div>
                div_content = [line]
                j = i + 1
                
                while j < len(lines):
                    div_content.append(lines[j])
                    if re.search(r'</div>', lines[j]):
                        break
                    j += 1
                
                # 合并div内容
                full_div = '\n'.join(div_content)
                
                # 检查div内是否包含 img 标签
                img_match = re.search(r'<img\s+src=["\']([^"\']+)["\'][^>]*/?>', full_div)
                
                if img_match:
                    img_src = img_match.group(1)
                    
                    # 检查div内是否还有其他标签（除了img和p）
                    # 如果有其他标签，说明是复杂结构，不处理
                    other_tags = re.findall(r'<(?!img|p|/img|/p)[^>]+>', full_div)
                    
                    if other_tags:
                        # 包含其他标签，保持原样
                        result_lines.extend(div_content)
                        i = j + 1
                        continue
                    
                    # 提取所有 alt 属性
                    alt_matches = re.findall(r'alt=["\']([^"\']*)["\']', full_div)
                    img_alt = ''
                    for alt in reversed(alt_matches):
                        if alt.strip():
                            img_alt = alt
                            break
                    
                    # 查找 p 标签中的说明文字
                    p_match = re.search(r'<p>([^<]+)</p>', full_div)
                    caption_text = p_match.group(1) if p_match else ''
                    
                    # 如果有p标签的说明文字，优先使用；否则使用alt属性；如果都没有，使用空字符串
                    alt_text = caption_text.strip() if caption_text.strip() else (img_alt.strip() if img_alt.strip() else '图片')
                    
                    # 转换为markdown格式
                    result_lines.append(f'\n\n![{alt_text}]({img_src})\n\n')
                    
                    # 跳过已经处理的所有div行
                    i = j + 1
                    continue
                else:
                    # 如果没有img标签，保持原样
                    result_lines.extend(div_content)
                    i = j + 1
                    continue
            else:
                result_lines.append(line)
                i += 1
        
        # 合并结果
        new_content = '\n'.join(result_lines)
        
        # 统计修改数量
        fix_count = content != new_content
        
        if fix_count:
            print(f"✓ 修复文件: {file_path.name}")
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  已保存修改")
            else:
                print(f"  [DRY RUN] 将会修改")
        
        return (1 if fix_count else 0, 1)
        
    except Exception as e:
        print(f"✗ 处理文件失败 {file_path}: {e}")
        return (0, 0)


def check_broken_images(directory: str) -> List[Tuple[Path, str]]:
    """
    检查所有markdown文件中的图片链接是否指向存在的文件
    
    Args:
        directory: 根目录路径
        
    Returns:
        (文件路径, 图片路径) 列表，表示坏链
    """
    broken_links = []
    root_path = Path(directory)
    
    md_files = find_markdown_files(directory)
    
    # 匹配所有markdown格式的图片链接：![alt](path)
    md_img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    # 匹配HTML格式的图片：<img src="path">
    html_img_pattern = r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*/?>'
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取所有图片路径
            img_paths = []
            
            # 提取markdown格式图片
            for match in re.finditer(md_img_pattern, content):
                img_paths.append(match.group(2))
            
            # 提取HTML格式图片
            for match in re.finditer(html_img_pattern, content):
                img_paths.append(match.group(1))
            
            # 检查每个图片是否存在
            for img_path in img_paths:
                # 清理路径（移除可能的查询参数）
                img_path = img_path.split('?')[0]
                
                # 构建完整路径
                full_path = md_file.parent / img_path
                
                # 如果是相对路径，尝试从项目根目录查找
                if not full_path.exists():
                    full_path = root_path / img_path
                
                if not full_path.exists():
                    broken_links.append((md_file, img_path))
                    
        except Exception as e:
            print(f"✗ 检查文件失败 {md_file}: {e}")
    
    return broken_links


def main():
    # Extra-Chapter 目录
    extra_chapter_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Extra-Chapter')
    
    print("=" * 60)
    print("Markdown图片链接修复工具 - Extra-Chapter专用")
    print("=" * 60)
    print(f"目标目录: {extra_chapter_dir}")
    print()
    
    # 检查目录是否存在
    if not os.path.exists(extra_chapter_dir):
        print(f"✗ 目录不存在: {extra_chapter_dir}")
        return
    
    # 步骤1: 查找所有markdown文件
    print("步骤 1: 扫描markdown文件...")
    md_files = find_markdown_files(extra_chapter_dir)
    print(f"找到 {len(md_files)} 个markdown文件")
    for md_file in md_files:
        print(f"  - {md_file.name}")
    print()
    
    # 步骤2: 检查坏链
    print("步骤 2: 检查图片链接...")
    broken_links = check_broken_images(extra_chapter_dir)
    if broken_links:
        print(f"发现 {len(broken_links)} 个坏链:")
        for md_file, img_path in broken_links[:10]:  # 只显示前10个
            print(f"  - {md_file.name} -> {img_path}")
        if len(broken_links) > 10:
            print(f"  ... 还有 {len(broken_links) - 10} 个")
    else:
        print("✓ 未发现坏链")
    print()
    
    # 步骤3: 修复图片链接格式
    print("步骤 3: 修复图片链接格式...")
    print("将 <div align=\"center\"> <img src=\"...\"/> 转换为 markdown 格式")
    print()
    
    total_fixed = 0
    total_processed = 0
    
    for md_file in md_files:
        fixed, processed = fix_image_links_in_file(md_file, dry_run=False)
        total_fixed += fixed
        total_processed += processed
    
    print()
    print("=" * 60)
    print(f"修复完成！")
    print(f"处理文件数: {total_processed}")
    print(f"修复文件数: {total_fixed}")
    print("=" * 60)


if __name__ == '__main__':
    main()