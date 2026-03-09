#!/usr/bin/env python3
"""
增强版图片识别脚本
专门处理猎聘网截图
"""

import os
import sys
import subprocess
import tempfile
from PIL import Image
import pytesseract

def enhance_image_for_ocr(image_path):
    """
    增强图片质量，提高OCR识别率
    """
    print(f"处理图片: {image_path}")
    
    try:
        # 打开图片
        img = Image.open(image_path)
        print(f"  原始尺寸: {img.size}, 格式: {img.format}, 模式: {img.mode}")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            enhanced_path = tmp.name
        
        # 增强处理步骤
        enhancement_steps = []
        
        # 1. 转换为灰度图
        if img.mode != 'L':
            img = img.convert('L')
            enhancement_steps.append("转为灰度图")
        
        # 2. 调整对比度
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)  # 提高对比度
        enhancement_steps.append("增强对比度")
        
        # 3. 调整亮度
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.2)  # 稍微提高亮度
        enhancement_steps.append("调整亮度")
        
        # 4. 锐化
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)  # 锐化
        enhancement_steps.append("锐化处理")
        
        # 5. 调整大小（如果图片太大）
        if img.size[0] > 2000:
            new_width = 1500
            ratio = new_width / img.size[0]
            new_height = int(img.size[1] * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            enhancement_steps.append(f"调整大小: {img.size}")
        
        # 保存增强后的图片
        img.save(enhanced_path, 'JPEG', quality=95)
        print(f"  增强步骤: {', '.join(enhancement_steps)}")
        print(f"  增强后保存到: {enhanced_path}")
        
        return enhanced_path
        
    except Exception as e:
        print(f"  图片增强失败: {e}")
        return image_path  # 返回原图

def extract_text_from_image(image_path, lang='chi_sim+eng'):
    """
    从图片中提取文本
    """
    print(f"\n提取文本: {image_path}")
    
    # 增强图片
    enhanced_path = enhance_image_for_ocr(image_path)
    
    try:
        # 使用Tesseract OCR
        config = '--psm 6'  # 假设为统一的文本块
        text = pytesseract.image_to_string(enhanced_path, lang=lang, config=config)
        
        print(f"  提取文本长度: {len(text)} 字符")
        
        # 清理临时文件
        if enhanced_path != image_path and os.path.exists(enhanced_path):
            os.unlink(enhanced_path)
        
        return text
        
    except Exception as e:
        print(f"  OCR提取失败: {e}")
        return ""

def extract_key_info_from_text(text):
    """
    从OCR提取的文本中提取关键信息
    专门针对猎聘网简历格式
    """
    print(f"\n提取关键信息...")
    
    info = {
        '姓名': None,
        '年龄': None,
        '学历': [],
        '工作经验': [],
        '当前职位': None,
        '当前公司': None,
        '技能证书': []
    }
    
    lines = text.split('\n')
    
    # 常见关键词
    name_keywords = ['姓名', '名字', 'Name']
    age_keywords = ['年龄', '岁', '出生', 'Birth']
    edu_keywords = ['教育', '学历', '学校', '大学', '学院', '硕士', '博士', '本科']
    work_keywords = ['工作', '经验', '经历', '公司', '职位', '职务']
    skill_keywords = ['技能', '证书', '资格', '语言', '证书']
    
    # 提取姓名（通常是第一行有效文本）
    for line in lines[:10]:
        line = line.strip()
        if line and len(line) <= 10:
            # 简单过滤
            if any(keyword in line for keyword in ['猎聘', '简历', '个人']):
                continue
            info['姓名'] = line
            print(f"  提取到姓名: {line}")
            break
    
    # 提取学历信息
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 学历相关行
        if any(keyword in line for keyword in edu_keywords):
            # 提取接下来的几行
            edu_lines = []
            for j in range(min(5, len(lines) - i)):
                edu_line = lines[i + j].strip()
                if edu_line:
                    edu_lines.append(edu_line)
            
            edu_text = '\n'.join(edu_lines)
            
            # 检查学校
            universities = ['清华', '北大', '复旦', '上海交大', '浙大', '南京大学', 
                           '中科大', '哈工大', '西安交大', '同济', '华中科技', 
                           '中山', '武汉大学', '南开', '天津大学', '北京航空航天']
            
            for uni in universities:
                if uni in edu_text:
                    info['学历'].append(f"{uni}（检测到）")
            
            if info['学历']:
                print(f"  提取到学历信息: {info['学历']}")
            break
    
    # 提取工作信息
    in_work_section = False
    for i, line in enumerate(lines):
        line = line.strip()
        
        if any(keyword in line for keyword in work_keywords):
            in_work_section = True
        
        if in_work_section and line:
            # 简单的工作经验提取
            if '公司' in line or '职位' in line or '年' in line:
                info['工作经验'].append(line)
                
                # 尝试提取当前职位
                if '当前' in line or '现在' in line or '至今' in line:
                    if '职位' in line:
                        info['当前职位'] = line
                    elif '公司' in line:
                        info['当前公司'] = line
    
    if info['工作经验']:
        print(f"  提取到工作经验: {len(info['工作经验'])} 条")
    
    return info

def process_hunting_images(image_folder):
    """
    处理猎聘网截图文件夹
    """
    print("="*80)
    print("猎聘网截图批量处理")
    print("="*80)
    
    if not os.path.exists(image_folder):
        print(f"文件夹不存在: {image_folder}")
        return
    
    # 查找图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    image_files = []
    
    for file in os.listdir(image_folder):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(os.path.join(image_folder, file))
    
    print(f"找到 {len(image_files)} 张图片")
    
    # 处理每张图片
    results = []
    for i, image_path in enumerate(image_files, 1):
        print(f"\n{'='*40}")
        print(f"处理第 {i}/{len(image_files)} 张: {os.path.basename(image_path)}")
        print(f"{'='*40}")
        
        # 提取文本
        text = extract_text_from_image(image_path)
        
        if not text or len(text) < 50:  # 文本太短可能是识别失败
            print(f"  ⚠️ 文本提取可能失败，尝试其他方法...")
            # 可以尝试不同的psm模式
            for psm in [3, 4, 6, 11]:
                try:
                    config = f'--psm {psm}'
                    text = pytesseract.image_to_string(image_path, lang='chi_sim+eng', config=config)
                    if len(text) > 50:
                        print(f"    PSM {psm} 模式成功提取 {len(text)} 字符")
                        break
                except:
                    pass
        
        # 提取关键信息
        if text and len(text) > 50:
            info = extract_key_info_from_text(text)
            results.append({
                'file': os.path.basename(image_path),
                'text': text[:500] + '...' if len(text) > 500 else text,
                'info': info
            })
        else:
            print(f"  ❌ 无法提取有效文本")
    
    # 输出结果
    print(f"\n{'='*80}")
    print(f"处理完成")
    print(f"{'='*80}")
    
    print(f"\n📊 统计信息:")
    print(f"  总图片数: {len(image_files)}")
    print(f"  成功提取: {len(results)}")
    print(f"  失败: {len(image_files) - len(results)}")
    
    if results:
        print(f"\n📋 提取结果摘要:")
        for result in results:
            print(f"\n  文件: {result['file']}")
            if result['info']['姓名']:
                print(f"    姓名: {result['info']['姓名']}")
            if result['info']['学历']:
                print(f"    学历: {', '.join(result['info']['学历'])}")
            if result['info']['当前职位']:
                print(f"    当前职位: {result['info']['当前职位']}")
    
    # 保存结果
    output_file = os.path.join(image_folder, 'ocr_results.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("猎聘网截图OCR提取结果\n")
        f.write("="*80 + "\n\n")
        
        for result in results:
            f.write(f"文件: {result['file']}\n")
            f.write(f"提取文本:\n{result['text']}\n")
            f.write(f"关键信息:\n")
            for key, value in result['info'].items():
                if value:
                    f.write(f"  {key}: {value}\n")
            f.write("\n" + "-"*80 + "\n\n")
    
    print(f"\n✅ 详细结果已保存到: {output_file}")
    
    return results

def main():
    if len(sys.argv) < 2:
        print("用法: python 图片处理增强脚本.py <图片文件夹路径>")
        print("示例: python 图片处理增强脚本.py /path/to/images/")
        return
    
    image_folder = sys.argv[1]
    process_hunting_images(image_folder)

if __name__ == "__main__":
    main()