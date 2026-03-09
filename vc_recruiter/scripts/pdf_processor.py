#!/usr/bin/env python3
"""
PDF简历处理器
支持中文PDF文本提取
"""

import subprocess
import os
import tempfile
import re

def pdf_to_text(pdf_path, lang='chi_sim'):
    """
    将PDF转换为文本
    """
    print(f"处理PDF文件: {pdf_path}")
    
    # 方法1: 使用pdftotext（纯文本提取）
    try:
        print("方法1: 使用pdftotext提取文本...")
        result = subprocess.run(
            ['pdftotext', '-layout', pdf_path, '-'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            text = result.stdout
            print(f"成功提取文本，长度: {len(text)} 字符")
            return text
    except Exception as e:
        print(f"pdftotext失败: {e}")
    
    # 方法2: 使用OCR（针对扫描件）
    print("方法2: 使用OCR处理...")
    try:
        # 将PDF转换为图像
        with tempfile.TemporaryDirectory() as tmpdir:
            # 先转换为PNG
            image_prefix = os.path.join(tmpdir, "page")
            subprocess.run(
                ['pdftoppm', '-png', '-r', '300', pdf_path, image_prefix],
                capture_output=True,
                timeout=30
            )
            
            # 获取生成的图像文件
            images = []
            for i in range(1, 20):  # 假设最多20页
                img_path = f"{image_prefix}-{i:06d}.png"
                if os.path.exists(img_path):
                    images.append(img_path)
                else:
                    break
            
            # 对每张图像进行OCR
            all_text = []
            for img in images:
                txt_path = f"{img}.txt"
                subprocess.run(
                    ['tesseract', img, img.replace('.png', ''), '-l', lang],
                    capture_output=True,
                    timeout=30
                )
                
                if os.path.exists(txt_path):
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        all_text.append(f.read())
            
            if all_text:
                text = "\n".join(all_text)
                print(f"OCR提取成功，长度: {len(text)} 字符")
                return text
    except Exception as e:
        print(f"OCR处理失败: {e}")
    
    return None

def extract_education_info(text):
    """从文本中提取教育信息"""
    print("\n提取教育信息...")
    
    education_info = {
        '本科学校': None,
        '本科专业': None,
        '硕士学校': None,
        '硕士专业': None,
        '博士学校': None,
        '博士专业': None
    }
    
    # 常见关键词
    edu_keywords = [
        '教育背景', '学历', '教育经历', 
        '本科', '学士', '大学', 
        '硕士', '研究生', '硕士生',
        '博士', '博士生', '博士研究生'
    ]
    
    # 查找教育部分
    edu_start = -1
    for keyword in edu_keywords:
        if keyword in text:
            edu_start = text.find(keyword)
            if edu_start != -1:
                break
    
    if edu_start == -1:
        print("未找到教育背景部分")
        return education_info
    
    # 提取教育部分内容（取500字符）
    edu_section = text[edu_start:edu_start+500]
    print(f"教育部分内容:\n{edu_section[:200]}...")
    
    # 简单解析
    lines = edu_section.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 本科识别
        if '本科' in line or '学士' in line:
            # 提取学校
            for univ in ['清华大学', '北京大学', '复旦大学', '上海交通大学', 
                         '浙江大学', '南京大学', '中国科学技术大学', '哈尔滨工业大学',
                         '西安交通大学', '同济大学', '华中科技大学', '中山大学', '武汉大学']:
                if univ in line:
                    education_info['本科学校'] = univ
                    break
            
            # 提取专业
            major_keywords = ['专业', '方向', '系']
            for keyword in major_keywords:
                if keyword in line:
                    parts = line.split(keyword)
                    if len(parts) > 1:
                        education_info['本科专业'] = parts[1].strip()
                        break
        
        # 硕士识别
        elif '硕士' in line or '研究生' in line:
            for univ in ['清华大学', '北京大学', '复旦大学', '上海交通大学', 
                         '浙江大学', '南京大学', '中国科学技术大学', '哈尔滨工业大学',
                         '西安交通大学', '同济大学', '华中科技大学', '中山大学', '武汉大学']:
                if univ in line:
                    education_info['硕士学校'] = univ
                    break
            
            # 提取专业
            major_keywords = ['专业', '方向', '系']
            for keyword in major_keywords:
                if keyword in line:
                    parts = line.split(keyword)
                    if len(parts) > 1:
                        education_info['硕士专业'] = parts[1].strip()
                        break
    
    return education_info

def extract_basic_info(text):
    """提取基本信息"""
    print("\n提取基本信息...")
    
    basic_info = {
        '姓名': None,
        '性别': None,
        '年龄': None,
        '出生年月': None,
        '当前职位': None,
        '当前公司': None
    }
    
    # 姓名提取（通常是第一行或第二行）
    lines = text.split('\n')
    for line in lines[:10]:  # 前10行找姓名
        line = line.strip()
        if line and len(line) <= 10 and '姓名' not in line and '简历' not in line:
            # 可能是姓名
            basic_info['姓名'] = line
            break
    
    # 关键词提取
    for line in lines:
        if '性别' in line:
            basic_info['性别'] = line.replace('性别', '').strip()
        elif '年龄' in line:
            basic_info['年龄'] = line.replace('年龄', '').strip()
        elif '出生' in line:
            basic_info['出生年月'] = line.replace('出生', '').replace('年月', '').strip()
        elif '职位' in line and '当前' in line:
            basic_info['当前职位'] = line.replace('当前职位', '').replace('职位', '').strip()
        elif '公司' in line:
            basic_info['当前公司'] = line.replace('公司', '').strip()
    
    return basic_info

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python pdf_processor.py <pdf文件路径>")
        return
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        return
    
    # 处理PDF
    text = pdf_to_text(pdf_path)
    
    if not text:
        print("无法提取文本")
        return
    
    # 提取信息
    print("\n" + "="*50)
    print("简历信息提取结果")
    print("="*50)
    
    # 基本信息
    basic_info = extract_basic_info(text)
    print(f"\n📋 基本信息:")
    for key, value in basic_info.items():
        if value:
            print(f"  {key}: {value}")
    
    # 教育信息
    edu_info = extract_education_info(text)
    print(f"\n🎓 教育背景:")
    for key, value in edu_info.items():
        if value:
            print(f"  {key}: {value}")
    
    # 保存提取的文本
    output_txt = pdf_path.replace('.pdf', '.txt')
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"\n✅ 文本已保存到: {output_txt}")
    print(f"总文本长度: {len(text)} 字符")

if __name__ == "__main__":
    main()