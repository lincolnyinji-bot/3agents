#!/usr/bin/env python3
"""
批量简历处理系统
用于处理20份推荐报告，进行批量评估和数据分析
"""

import os
import csv
import json
import re
from datetime import datetime
from typing import List, Dict, Any
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.resume_filter_enhanced import ResumeFilterEnhanced

class BatchResumeProcessor:
    """批量简历处理器"""
    
    def __init__(self, input_dir: str = "../data/batch_processing/input", 
                 output_dir: str = "../data/batch_processing/output"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.filter = ResumeFilterEnhanced()
        
        # 创建目录
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # 子目录
        self.raw_dir = os.path.join(input_dir, "raw_reports")
        self.csv_dir = os.path.join(input_dir, "csv")
        self.eval_dir = os.path.join(output_dir, "evaluations")
        self.stats_dir = os.path.join(output_dir, "statistics")
        
        for dir_path in [self.raw_dir, self.csv_dir, self.eval_dir, self.stats_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def parse_recommendation_report(self, report_text: str) -> Dict[str, Any]:
        """
        解析推荐报告文本，提取结构化信息
        基于已有的推荐报告格式进行解析
        """
        data = {
            "姓名": "",
            "性别": "",
            "年龄": "",
            "家庭状况": "",
            "目前状态": "",
            "现居地": "",
            "当前职位": "",
            "当前公司": "",
            "工作经验": "",
            "投资经验": "",
            "本科学历": "",
            "本科专业": "",
            "硕士学历": "",
            "硕士专业": "",
            "当前年薪(万)": "",
            "期望年薪(万)": "",
            "项目经验": "",
            "投成案例数": "0",
            "推荐理由": ""
        }
        
        # 基础信息提取
        lines = report_text.split('\n')
        for line in lines:
            line = line.strip()
            
            # 姓名
            if "姓名：" in line or "姓名:" in line:
                data["姓名"] = line.split("：")[-1].split(":")[-1].strip()
            
            # 年龄
            elif "年龄：" in line or "年龄:" in line:
                age_match = re.search(r'\d+', line)
                if age_match:
                    data["年龄"] = age_match.group()
            
            # 当前职位和公司
            elif "目前状态：" in line or "目前状态:" in line:
                if "在职" in line:
                    # 尝试从后续行提取职位和公司
                    pass
            
            # 教育背景
            elif "学历" in line and ("本科" in line or "硕士" in line):
                # 简化处理，实际需要更复杂的解析
                pass
            
            # 薪资
            elif "薪资" in line or "收入" in line:
                # 提取薪资数字
                salary_match = re.search(r'(\d+)K|(\d+)万|(\d+)k', line)
                if salary_match:
                    for group in salary_match.groups():
                        if group:
                            if "当前" in line or "薪资结构" in line:
                                data["当前年薪(万)"] = group
                            elif "期望" in line or "希望" in line:
                                data["期望年薪(万)"] = group
            
            # 投成案例数（从推荐理由推断）
            elif "投成" in line or "投资" in line:
                # 提取数字
                case_match = re.search(r'(\d+)\s*个(?:项目|案例|投成)', line)
                if case_match:
                    data["投成案例数"] = case_match.group(1)
        
        # 如果投成案例数未提取到，尝试从项目描述推断
        if data["投成案例数"] == "0" and "项目" in report_text:
            # 简化推断逻辑
            project_count = report_text.count("项目")
            if project_count > 0:
                data["投成案例数"] = str(min(project_count, 10))
        
        return data
    
    def convert_report_to_csv(self, report_file: str) -> str:
        """将推荐报告转换为CSV格式"""
        with open(report_file, 'r', encoding='utf-8') as f:
            report_text = f.read()
        
        # 解析报告
        resume_data = self.parse_recommendation_report(report_text)
        
        # 生成CSV文件名
        name = resume_data["姓名"] or "unknown"
        csv_filename = f"{name}_resume.csv"
        csv_path = os.path.join(self.csv_dir, csv_filename)
        
        # 写入CSV
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=resume_data.keys())
            writer.writeheader()
            writer.writerow(resume_data)
        
        return csv_path
    
    def process_batch(self, batch_size: int = 20) -> Dict[str, Any]:
        """处理一批简历"""
        print("=" * 70)
        print("批量简历处理系统")
        print("=" * 70)
        
        # 查找原始报告文件
        raw_files = []
        if os.path.exists(self.raw_dir):
            for file in os.listdir(self.raw_dir):
                if file.endswith(('.txt', '.md', '.pdf')):
                    raw_files.append(os.path.join(self.raw_dir, file))
        
        if not raw_files:
            print(f"未找到原始文件，请在 {self.raw_dir} 中放置简历文件")
            return {"status": "no_files"}
        
        print(f"找到 {len(raw_files)} 个原始文件")
        
        # 处理每个文件
        all_results = []
        successful = 0
        failed = 0
        
        for i, raw_file in enumerate(raw_files[:batch_size], 1):
            try:
                print(f"\n处理文件 {i}/{len(raw_files)}: {os.path.basename(raw_file)}")
                
                # 转换为CSV
                csv_file = self.convert_report_to_csv(raw_file)
                
                # 读取CSV数据
                with open(csv_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    row = next(reader)
                
                # 评估简历
                result = self.filter.evaluate_enhanced(row)
                
                # 添加处理信息
                result['原始文件'] = os.path.basename(raw_file)
                result['处理时间'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                all_results.append(result)
                successful += 1
                
                print(f"  ✓ 评估完成: {result['姓名']} - {result['评估级别']} - {result['总分']}分")
                
            except Exception as e:
                print(f"  ✗ 处理失败: {str(e)}")
                failed += 1
        
        # 保存结果
        if all_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.eval_dir, f"batch_evaluation_{timestamp}.csv")
            
            # 写入完整结果
            with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
                fieldnames = list(all_results[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_results)
            
            # 生成统计信息
            stats = self.generate_statistics(all_results)
            
            # 保存统计信息
            stats_file = os.path.join(self.stats_dir, f"batch_stats_{timestamp}.json")
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            print(f"\n{'='*70}")
            print("批量处理完成！")
            print(f"{'='*70}")
            print(f"成功处理: {successful} 份")
            print(f"处理失败: {failed} 份")
            print(f"推荐率: {stats['recommendation_rate']:.1f}%")
            print(f"平均分数: {stats['average_score']:.1f}")
            print(f"最高分: {stats['max_score']} ({stats['top_candidate']})")
            print(f"最低分: {stats['min_score']}")
            print(f"\n详细结果保存至: {output_file}")
            print(f"统计信息保存至: {stats_file}")
            
            return {
                "status": "success",
                "successful": successful,
                "failed": failed,
                "output_file": output_file,
                "stats_file": stats_file,
                "statistics": stats
            }
        
        return {"status": "no_results"}
    
    def generate_statistics(self, results: List[Dict]) -> Dict[str, Any]:
        """生成统计信息"""
        if not results:
            return {}
        
        scores = [r['总分'] for r in results]
        recommended = [r for r in results if r['状态'] == '推荐']
        
        # 按级别分组
        levels = {}
        for result in results:
            level = result['评估级别']
            levels[level] = levels.get(level, 0) + 1
        
        # 按分数段分组
        score_brackets = {
            "S级 (90+)": len([s for s in scores if s >= 90]),
            "A级 (80-89)": len([s for s in scores if 80 <= s < 90]),
            "B级 (70-79)": len([s for s in scores if 70 <= s < 80]),
            "C级 (60-69)": len([s for s in scores if 60 <= s < 70]),
            "D级 (<60)": len([s for s in scores if s < 60]),
        }
        
        # 找到最高分候选人
        top_result = max(results, key=lambda x: x['总分'])
        
        stats = {
            "total_candidates": len(results),
            "recommended_count": len(recommended),
            "recommendation_rate": len(recommended) / len(results) * 100,
            "average_score": sum(scores) / len(scores),
            "max_score": max(scores),
            "min_score": min(scores),
            "top_candidate": top_result['姓名'],
            "top_score": top_result['总分'],
            "top_level": top_result['评估级别'],
            "level_distribution": levels,
            "score_distribution": score_brackets,
            "processing_time": datetime.now().isoformat()
        }
        
        return stats
    
    def analyze_algorithm_performance(self, results: List[Dict]) -> Dict[str, Any]:
        """分析算法性能，识别需要优化的地方"""
        analysis = {
            "score_components": {
                "education_avg": 0,
                "experience_avg": 0,
                "salary_avg": 0,
                "skills_avg": 0,
                "cases_avg": 0
            },
            "common_issues": [],
            "recommendations": []
        }
        
        if not results:
            return analysis
        
        # 计算各维度平均分
        components = ['学历评分', '经验评分', '薪资评分', '技能评分', '案例评分']
        for comp in components:
            scores = [r.get(comp, 0) for r in results]
            analysis["score_components"][f"{comp[:2]}_avg"] = sum(scores) / len(scores)
        
        # 识别常见问题
        low_skill = [r for r in results if r.get('技能评分', 0) < 5]
        high_salary_expectation = [r for r in results if r.get('薪资评分', 0) < 5]
        
        if low_skill:
            analysis["common_issues"].append(f"{len(low_skill)} 位候选人技能评分偏低(<5)")
        
        if high_salary_expectation:
            analysis["common_issues"].append(f"{len(high_salary_expectation)} 位候选人薪资期望偏高")
        
        # 生成优化建议
        if analysis["score_components"]["skills_avg"] < 6:
            analysis["recommendations"].append("优化技能识别算法，特别是从项目描述中提取技能")
        
        if analysis["score_components"]["salary_avg"] < 7:
            analysis["recommendations"].append("更新薪资评估标准，考虑市场变化")
        
        return analysis

def main():
    """主函数"""
    processor = BatchResumeProcessor()
    
    print("批量简历处理系统启动")
    print(f"输入目录: {processor.input_dir}")
    print(f"输出目录: {processor.output_dir}")
    print()
    
    # 处理一批简历
    result = processor.process_batch(batch_size=20)
    
    if result["status"] == "success":
        print("\n" + "="*70)
        print("批量处理摘要:")
        print("-"*70)
        
        stats = result["statistics"]
        print(f"总候选人: {stats['total_candidates']}")
        print(f"推荐人数: {stats['recommended_count']}")
        print(f"推荐率: {stats['recommendation_rate']:.1f}%")
        print(f"平均分数: {stats['average_score']:.1f}")
        
        print("\n级别分布:")
        for level, count in stats['level_distribution'].items():
            percentage = count / stats['total_candidates'] * 100
            print(f"  {level}: {count}人 ({percentage:.1f}%)")
        
        print("\n分数段分布:")
        for bracket, count in stats['score_distribution'].items():
            percentage = count / stats['total_candidates'] * 100
            print(f"  {bracket}: {count}人 ({percentage:.1f}%)")

if __name__ == "__main__":
    main()