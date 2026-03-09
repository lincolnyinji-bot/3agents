#!/usr/bin/env python3
# PDF简历解析器
# 从PDF简历中提取结构化信息

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

class PDFResumeParser:
    def __init__(self):
        # 学校数据库
        self.load_schools()
        # 关键词模式
        self.patterns = {
            'name': r'(?:姓名|名字|Name)[：:\s]*([^\n]+)',
            'phone': r'(?:电话|手机|Phone|Tel)[：:\s]*([+\d\s\-()]+)',
            'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'education': r'(?:教育背景|教育经历|Education)[：:\s]*(.+?)(?=\n\s*\n|\n\s*[^\s])',
            'experience': r'(?:工作经历|工作经验|Experience)[：:\s]*(.+?)(?=\n\s*\n|\n\s*[^\s])',
            'skills': r'(?:技能|专长|Skills)[：:\s]*(.+?)(?=\n\s*\n|\n\s*[^\s])',
            'salary': r'(?:期望薪资|薪资要求|期望薪水)[：:\s]*([^\n]+)',
            'university': r'(?:大学|学院|学校|University|College)[：:\s]*([^\n]+)',
            'major': r'(?:专业|Major)[：:\s]*([^\n]+)',
            'degree': r'(?:学历|学位|Degree)[：:\s]*([^\n]+)'
        }
        
    def load_schools(self):
        """加载学校数据库"""
        try:
            with open('../data/schools.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.top_schools = set(data['985_universities'] + data['qs_top_100'])
                self.stem_programs = set(data['理工科_programs'])
                self.business_programs = set(data['商科_programs'])
        except:
            # 默认学校列表
            self.top_schools = {'清华大学', '北京大学', '浙江大学', '上海交通大学', '复旦大学'}
            self.stem_programs = {'计算机', '软件工程', '人工智能', '电子信息', '数学', '统计'}
            self.business_programs = {'金融', '经济', '工商管理', '会计'}
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        从PDF提取文本
        注意：需要安装pdfplumber或PyPDF2
        """
        text = ""
        
        # 方法1: 尝试使用pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except ImportError:
            pass
        
        # 方法2: 尝试使用PyPDF2
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except ImportError:
            pass
        
        # 方法3: 使用系统工具pdftotext
        try:
            import subprocess
            result = subprocess.run(
                ['pdftotext', pdf_path, '-'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode == 0:
                return result.stdout
        except:
            pass
        
        # 如果所有方法都失败，返回空字符串
        print(f"警告: 无法解析PDF文件 {pdf_path}")
        print("请安装: pip install pdfplumber 或 apt-get install poppler-utils")
        return ""
    
    def parse_resume(self, pdf_path: str) -> Dict:
        """解析单份PDF简历"""
        # 提取文本
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return self._create_empty_result(pdf_path)
        
        # 基本信息提取
        result = {
            'file_name': os.path.basename(pdf_path),
            'raw_text': text[:1000] + "..." if len(text) > 1000 else text,
            '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 提取各个字段
        result.update(self._extract_basic_info(text))
        result.update(self._extract_education(text))
        result.update(self._extract_experience(text))
        result.update(self._extract_skills(text))
        
        return result
    
    def _extract_basic_info(self, text: str) -> Dict:
        """提取基本信息"""
        info = {}
        
        # 姓名
        name_match = re.search(self.patterns['name'], text, re.IGNORECASE)
        if name_match:
            info['姓名'] = name_match.group(1).strip()
        else:
            # 尝试从文件名提取
            info['姓名'] = "未知"
        
        # 电话
        phone_match = re.search(self.patterns['phone'], text)
        if phone_match:
            info['电话'] = phone_match.group(1).strip()
        
        # 邮箱
        email_match = re.search(self.patterns['email'], text)
        if email_match:
            info['邮箱'] = email_match.group(1).strip()
        
        # 期望薪资
        salary_match = re.search(self.patterns['salary'], text, re.IGNORECASE)
        if salary_match:
            info['期望薪资'] = salary_match.group(1).strip()
        
        return info
    
    def _extract_education(self, text: str) -> Dict:
        """提取教育背景"""
        edu_info = {
            '本科学历': '',
            '本科专业': '',
            '硕士学历': '',
            '硕士专业': ''
        }
        
        # 查找教育背景部分
        edu_match = re.search(self.patterns['education'], text, re.IGNORECASE | re.DOTALL)
        if not edu_match:
            return edu_info
        
        edu_text = edu_match.group(1)
        
        # 提取学校和专业信息
        lines = edu_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否包含学校信息
            for school in self.top_schools:
                if school in line:
                    if '硕士' in line or '研究生' in line or 'Master' in line:
                        edu_info['硕士学历'] = school
                    elif '本科' in line or '学士' in line or 'Bachelor' in line:
                        edu_info['本科学历'] = school
                    elif not edu_info['本科学历']:
                        edu_info['本科学历'] = school  # 默认设为本科
            
            # 检查是否包含专业信息
            for major in self.stem_programs.union(self.business_programs):
                if major in line:
                    if '硕士' in line or '研究生' in line:
                        edu_info['硕士专业'] = major
                    elif '本科' in line or '学士' in line:
                        edu_info['本科专业'] = major
                    elif not edu_info['本科专业']:
                        edu_info['本科专业'] = major
        
        return edu_info
    
    def _extract_experience(self, text: str) -> Dict:
        """提取工作经验"""
        exp_info = {
            '当前职位': '',
            '当前公司': '',
            '工作经验': '',
            '投资经验': '',
            '项目经验': ''
        }
        
        # 查找工作经验部分
        exp_match = re.search(self.patterns['experience'], text, re.IGNORECASE | re.DOTALL)
        if not exp_match:
            return exp_info
        
        exp_text = exp_match.group(1)
        exp_info['项目经验'] = exp_text[:500]  # 截取前500字符
        
        # 尝试提取投资相关经验
        investment_keywords = ['投资', 'VC', 'PE', '风投', '股权', '基金', '资本']
        vc_companies = ['红杉', 'IDG', '高瓴', '启明', '经纬', '源码', '晨兴', '今日资本']
        
        lines = exp_text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # 检查是否投资相关职位
            if any(keyword in line_lower for keyword in ['投资经理', '分析师', '投资总监', 'associate', 'vp']):
                # 提取职位
                for keyword in ['投资经理', '分析师', '投资总监', 'Associate', 'VP']:
                    if keyword in line:
                        exp_info['当前职位'] = keyword
                        break
                
                # 提取公司
                for company in vc_companies:
                    if company in line:
                        exp_info['当前公司'] = company
                        break
                
                # 提取年限
                year_match = re.search(r'(\d+)\s*年', line)
                if year_match:
                    exp_info['投资经验'] = f"{year_match.group(1)}年"
        
        # 估算总工作经验
        year_matches = re.findall(r'(\d+)\s*年', exp_text)
        if year_matches:
            max_years = max([int(y) for y in year_matches if y.isdigit()])
            exp_info['工作经验'] = f"{max_years}年"
        
        return exp_info
    
    def _extract_skills(self, text: str) -> Dict:
        """提取技能信息"""
        skills_info = {'技能关键词': ''}
        
        # 查找技能部分
        skills_match = re.search(self.patterns['skills'], text, re.IGNORECASE | re.DOTALL)
        if skills_match:
            skills_text = skills_match.group(1)
            skills_info['技能关键词'] = skills_text[:300]  # 截取前300字符
        else:
            # 从全文提取技能关键词
            vc_skills = ['行研', '行业研究', '项目挖掘', '尽职调查', '尽调', 'DD', 
                        '交易执行', '投后管理', '财务分析', '估值', '谈判']
            found_skills = []
            for skill in vc_skills:
                if skill in text:
                    found_skills.append(skill)
            if found_skills:
                skills_info['技能关键词'] = '、'.join(found_skills)
        
        return skills_info
    
    def _create_empty_result(self, pdf_path: str) -> Dict:
        """创建空结果"""
        return {
            'file_name': os.path.basename(pdf_path),
            '姓名': '未知',
            '电话': '',
            '邮箱': '',
            '本科学历': '',
            '本科专业': '',
            '硕士学历': '',
            '硕士专业': '',
            '当前职位': '',
            '当前公司': '',
            '工作经验': '',
            '投资经验': '',
            '期望薪资': '',
            '技能关键词': '',
            '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '解析状态': '失败'
        }
    
    def batch_parse(self, pdf_directory: str) -> List[Dict]:
        """批量解析PDF简历"""
        results = []
        
        if not os.path.exists(pdf_directory):
            print(f"目录不存在: {pdf_directory}")
            return results
        
        pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
        
        print(f"发现 {len(pdf_files)} 个PDF文件")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_directory, pdf_file)
            print(f"正在解析: {pdf_file}")
            
            result = self.parse_resume(pdf_path)
            results.append(result)
        
        return results
    
    def save_to_csv(self, results: List[Dict], output_file: str):
        """保存为CSV格式"""
        if not results:
            print("没有数据可保存")
            return
        
        # 获取所有字段
        all_fields = set()
        for result in results:
            all_fields.update(result.keys())
        
        field_order = [
            'file_name', '姓名', '电话', '邮箱', 
            '本科学历', '本科专业', '硕士学历', '硕士专业',
            '当前职位', '当前公司', '工作经验', '投资经验',
            '期望薪资', '技能关键词', '提取时间', '解析状态'
        ]
        
        # 确保字段顺序
        fields = [f for f in field_order if f in all_fields]
        fields += [f for f in all_fields if f not in field_order]
        
        import csv
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"已保存到: {output_file}")

def main():
    """主函数"""
    print("=" * 60)
    print("PDF简历解析器 v1.0")
    print("=" * 60)
    
    parser = PDFResumeParser()
    
    # 测试解析第一份简历
    test_pdf = "/root/.openclaw/media/inbound/王谟松-简历---7c095a4e-cada-4adf-a58b-ae4ef85b22c6.pdf"
    
    if os.path.exists(test_pdf):
        print(f"正在解析测试文件: {test_pdf}")
        result = parser.parse_resume(test_pdf)
        
        print("\n解析结果:")
        print("-" * 40)
        for key, value in result.items():
            if key not in ['raw_text']:  # 不显示原始文本
                print(f"{key}: {value}")
        
        # 保存结果
        output_dir = "../data/parsed"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "parsed_resumes.csv")
        parser.save_to_csv([result], output_file)
        
        print(f"\n结果已保存到: {output_file}")
    else:
        print(f"测试文件不存在: {test_pdf}")
        print("\n使用说明:")
        print("1. 将PDF简历放入 data/raw_pdfs/ 目录")
        print("2. 运行: python pdf_parser.py --batch")
        print("3. 结果保存到 data/parsed/ 目录")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()