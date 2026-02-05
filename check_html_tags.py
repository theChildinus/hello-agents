#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 Markdown 文件中使用的所有 HTML 标签

使用方法:
    python check_html_tags.py <目录路径>

示例:
    python check_html_tags.py /Users/kong/obsidian-vault/hello-agents
"""

import os
import re
from collections import defaultdict, Counter
from pathlib import Path


def extract_html_tags(content):
    """
    从内容中提取所有 HTML 标签
    
    Returns:
        list: 标签名称列表，包含开始标签和结束标签
    """
    # 匹配所有 HTML 标签
    # 匹配格式: <tag> 或 </tag> 或 <tag ...>
    pattern = r'</?([a-zA-Z][a-zA-Z0-9]*)'
    tags = re.findall(pattern, content)
    return tags


def get_tag_contexts(content, tag_name, max_examples=3):
    """
    获取某个标签的使用上下文示例
    
    Args:
        content: 文件内容
        tag_name: 标签名称
        max_examples: 最大示例数量
    
    Returns:
        list: 标签使用示例列表
    """
    # 匹配标签及其内部内容
    pattern = rf'<{tag_name}(?:[^>]*)>(.*?)</{tag_name}>'
    matches = re.findall(pattern, content, flags=re.DOTALL)
    
    examples = []
    for match in matches[:max_examples]:
        # 清理示例，移除多余的空白
        cleaned = ' '.join(match.split())
        # 截断过长的示例
        if len(cleaned) > 100:
            cleaned = cleaned[:100] + "..."
        examples.append(f"<{tag_name}>{cleaned}</{tag_name}>")
    
    return examples


def analyze_markdown_file(file_path):
    """
    分析单个 Markdown 文件中的 HTML 标签
    
    Returns:
        tuple: (标签计数器, 标签示例字典)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tags = extract_html_tags(content)
        tag_counter = Counter(tags)
        
        # 获取每个标签示例
        tag_examples = {}
        for tag_name in tag_counter.keys():
            examples = get_tag_contexts(content, tag_name)
            if examples:
                tag_examples[tag_name] = examples
        
        return tag_counter, tag_examples
        
    except Exception as e:
        print(f"✗ 错误读取文件: {file_path}")
        print(f"  {str(e)}")
        return Counter(), {}


def main():
    """主函数"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python check_html_tags.py <目录路径>")
        print("示例: python check_html_tags.py /Users/kong/obsidian-vault/hello-agents")
        sys.exit(1)
    
    # 获取目标目录
    target_dir = Path(sys.argv[1])
    
    if not target_dir.exists():
        print(f"错误: 目录不存在: {target_dir}")
        sys.exit(1)
    
    if not target_dir.is_dir():
        print(f"错误: 不是目录: {target_dir}")
        sys.exit(1)
    
    # 收集所有 Markdown 文件
    md_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(('.md', '.markdown')):
                md_files.append(Path(root) / file)
    
    if not md_files:
        print(f"未找到 Markdown 文件在目录: {target_dir}")
        sys.exit(0)
    
    print(f"正在扫描 {len(md_files)} 个 Markdown 文件...\n")
    print("=" * 70)
    
    # 汇总所有文件的标签统计
    total_tag_counter = Counter()
    tag_file_counts = defaultdict(set)
    all_tag_examples = defaultdict(list)
    
    # 分析每个文件
    for md_file in sorted(md_files):
        tag_counter, tag_examples = analyze_markdown_file(md_file)
        
        if tag_counter:
            # 更新总计数
            total_tag_counter.update(tag_counter)
            
            # 记录使用该标签的文件
            for tag_name in tag_counter:
                tag_file_counts[tag_name].add(md_file.name)
            
            # 收集标签示例
            for tag_name, examples in tag_examples.items():
                all_tag_examples[tag_name].extend(examples)
    
    # 输出结果
    if total_tag_counter:
        print(f"\n📊 HTML 标签统计结果（按使用频率排序）：\n")
        print("=" * 70)
        print(f"{'标签':<20} {'出现次数':<10} {'涉及文件':<10} {'使用示例'}")
        print("-" * 70)
        
        # 按使用次数排序
        sorted_tags = sorted(total_tag_counter.items(), key=lambda x: x[1], reverse=True)
        
        for tag_name, count in sorted_tags:
            file_count = len(tag_file_counts[tag_name])
            
            # 获取示例（去重）
            examples = list(dict.fromkeys(all_tag_examples[tag_name]))[:2]
            example_str = ' | '.join(examples) if examples else ""
            
            print(f"{tag_name:<20} {count:<10} {file_count:<10} {example_str}")
        
        print("=" * 70)
        print(f"\n总计发现 {len(sorted_tags)} 种不同的 HTML 标签")
        print(f"总共出现 {sum(total_tag_counter.values())} 次")
        
        # 分类展示标签
        print("\n" + "=" * 70)
        print("📝 标签分类建议：\n")
        
        # 常见的 Obsidian 支持/不需要替换的标签
        obsidian_tags = ['div', 'span', 'br', 'hr']
        # 需要替换为 Markdown 语法的标签
        replace_tags = ['strong', 'em', 'b', 'i', 'u', 's', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        # 代码相关标签
        code_tags = ['code', 'pre']
        # 列表相关标签
        list_tags = ['ul', 'ol', 'li']
        # 链接和图片标签
        media_tags = ['a', 'img']
        # 表格标签
        table_tags = ['table', 'tr', 'td', 'th', 'thead', 'tbody']
        
        categories = {
            '⚠️ 需要替换为 Markdown 语法': replace_tags,
            '💻 代码相关': code_tags,
            '📋 列表相关': list_tags,
            '🔗 链接和图片': media_tags,
            '📊 表格相关': table_tags,
            '✅ Obsidian 支持（可保留）': obsidian_tags,
        }
        
        for category_name, category_tags in categories.items():
            found_tags = [tag for tag in category_tags if tag in total_tag_counter]
            if found_tags:
                print(f"{category_name}:")
                for tag in found_tags:
                    count = total_tag_counter[tag]
                    print(f"  - <{tag}> ({count} 次)")
                print()
        
        # 其他标签
        other_tags = [tag for tag in total_tag_counter 
                     if tag not in sum(categories.values(), [])]
        if other_tags:
            print(f"❓ 其他标签:")
            for tag in other_tags:
                count = total_tag_counter[tag]
                print(f"  - <{tag}> ({count} 次)")
        
    else:
        print("\n✓ 未发现任何 HTML 标签")


if __name__ == "__main__":
    main()
