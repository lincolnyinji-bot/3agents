#!/usr/bin/env python3
"""
真实OCR分析截图内容
"""

import subprocess
import tempfile
import os

def extract_text_from_image(image_path):
    """真正使用OCR提取文本"""
    print(f"处理图片: {os.path.basename(image_path)}")
    
    try:
        # 使用tesseract提取文本
        result = subprocess.run(
            ['tesseract', image_path, 'stdout', '-l', 'chi_sim+eng'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            text = result.stdout.strip()
            print(f"  提取文本长度: {len(text)} 字符")
            
            # 显示前200字符
            preview = text[:200].replace('\n', ' ')
            print(f"  预览: {preview}...")
            
            return text
        else:
            print(f"  ⚠️ 无法提取文本")
            return None
            
    except Exception as e:
        print(f"  ❌ OCR失败: {e}")
        return None

def main():
    print("="*80)
    print("真实OCR分析 - 查看截图实际内容")
    print("="*80)
    
    # 列出所有截图
    import glob
    image_files = glob.glob("/root/.openclaw/media/inbound/*.jpg")
    print(f"找到 {len(image_files)} 张截图")
    
    # 分析每张图片
    for i, image_path in enumerate(image_files[:3], 1):  # 先看前3张
        print(f"\n{'='*40}")
        print(f"截图 {i}: {os.path.basename(image_path)}")
        print(f"{'='*40}")
        
        text = extract_text_from_image(image_path)
        
        if text:
            # 简单分析内容
            lines = text.split('\n')
            print(f"  总行数: {len(lines)}")
            
            # 找关键词
            keywords = ['姓名', '教育', '学校', '大学', '经验', '投资', '基金', '工作']
            found_keywords = []
            
            for line in lines[:20]:  # 前20行
                for keyword in keywords:
                    if keyword in line:
                        found_keywords.append(f"{keyword}: {line.strip()}")
                        break
            
            if found_keywords:
                print(f"  发现关键词:")
                for item in found_keywords[:5]:  # 显示前5个
                    print(f"    • {item}")
        
        print(f"\n  建议: 需要更好的OCR预处理或手动查看图片内容")

if __name__ == "__main__":
    main()