#!/usr/bin/env python3
# VC投资经理简历筛选系统
# 作者：OpenClaw AI Assistant
# 创建时间：2026-03-06

import json
import csv
import re
from datetime import datetime
from typing import Dict, List, Tuple

class ResumeFilter:
    def __init__(self):
        """初始化筛选器，加载学校数据库"""
        self.load_schools()
        self.threshold = 75  # 推荐阈值
        
    def load_schools(self):
        """加载学校数据库"""
        with open('../data/schools.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.top_schools = set(data['985_universities'] + data['qs_top_100'])
            self.stem_programs = set(data['理工科_programs'])
            self.business_programs = set(data['商科_programs'])
    
    def score_education(self, bachelor_school: str, bachelor_major: str,
                       master_school: str, master_major: str) -> Tuple[int, str]:
        """
        学历评分 (0-40分)
        规则：985/QS100本硕 + 理工科专业
        """
        score = 0
        reasons = []
        
        # 1. 检查本科专业（硬性排除）
        if self._is_business_major(bachelor_major):
            return 0, "本科为商科专业，直接排除"
        
        # 2. 学校评分 (20分)
        bachelor_school_score = 20 if self._is_top_school(bachelor_school) else 0
        master_school_score = 20 if self._is_top_school(master_school) else 0
        school_score = min(20, (bachelor_school_score + master_school_score) / 2)
        score += school_score
        
        if school_score > 0:
            reasons.append(f"学校符合要求({school_score}分)")
        
        # 3. 本科专业评分 (10分)
        if self._is_stem_major(bachelor_major):
            score += 10
            reasons.append("本科理工科专业(10分)")
        elif bachelor_major:  # 其他专业
            score += 2
            reasons.append("本科非理工科专业(2分)")
        
        # 4. 硕士专业评分 (10分)
        if self._is_stem_major(master_major):
            score += 10
            reasons.append("硕士理工科专业(10分)")
        elif self._is_business_major(master_major):
            score += 5
            reasons.append("硕士商科专业(5分)")
        elif master_major:  # 其他专业
            score += 2
            reasons.append("硕士其他专业(2分)")
        
        return min(40, score), "; ".join(reasons)
    
    def score_experience(self, total_exp: str, vc_exp: str, case_info: str) -> Tuple[int, str]:
        """
        经验评分 (0-30分)
        规则：1-5年一级股权经验，有投成案例优先
        """
        score = 0
        reasons = []
        
        # 提取工作经验年数
        total_years = self._extract_years(total_exp)
        vc_years = self._extract_years(vc_exp)
        
        # 1. 投资经验基础分
        if vc_years >= 1 and vc_years <= 5:
            score += min(25, vc_years * 5)  # 每多1年+5分，上限25分
            reasons.append(f"{vc_years}年VC经验({score}分)")
        elif vc_years == 0:
            # 如果没有明确投资经验年数，但从项目经验推断
            if any(keyword in case_info for keyword in ["投资", "投出", "尽职调查", "DD", "deal", "项目投资"]):
                # 推断有投资经验
                inferred_years = min(3, total_years)  # 推断最多3年
                score += min(25, inferred_years * 5)
                reasons.append(f"推断{inferred_years}年投资经验({score}分)")
        
        # 2. 投成案例加分
        case_keywords = ["投成", "deal", "投资金额", "投出", "项目投资", "投资近"]
        if any(keyword in case_info for keyword in case_keywords):
            score += 5
            reasons.append("有投成案例(5分)")
        
        # 3. 高级别职位加分
        position_keywords = ["高级", "Senior", "总监", "Director", "VP", "副总裁"]
        if any(keyword in case_info for keyword in position_keywords):
            score += 3
            reasons.append("高级职位加分(3分)")
        
        return min(30, score), "; ".join(reasons)
    
    def score_salary(self, salary: str, position: str = "") -> Tuple[int, str]:
        """
        薪资评分 (0-10分)
        规则：根据职位级别调整范围
        """
        # 提取薪资数字
        numbers = re.findall(r'\d+', salary)
        if not numbers:
            return 2, "薪资未标注(2分)"
        
        try:
            monthly = int(numbers[0])
            
            # 根据职位级别确定薪资范围
            senior_keywords = ["高级", "Senior", "VP", "副总裁", "总监", "Director"]
            is_senior = any(keyword in position for keyword in senior_keywords) if position else False
            
            if is_senior:
                # 高级职位范围：35-60K
                if 35 <= monthly <= 60:
                    return 10, f"高级职位薪资{monthly}K合理(10分)"
                elif monthly < 35:
                    return 7, f"高级职位薪资{monthly}K偏低(7分)"
                else:
                    return 5, f"高级职位薪资{monthly}K偏高(5分)"
            else:
                # 普通投资经理范围：20-40K
                if 20 <= monthly <= 40:
                    return 10, f"薪资{monthly}K在范围内(10分)"
                elif monthly < 20:
                    return 5, f"薪资{monthly}K偏低但可谈判(5分)"
                else:
                    return 3, f"薪资{monthly}K偏高但可沟通(3分)"
        except:
            return 2, "薪资格式异常(2分)"
    
    def score_skills(self, resume_text: str) -> Tuple[int, str]:
        """
        技能评分 (0-20分)
        规则：行研、项目挖掘、尽调、交易执行
        """
        score = 0
        reasons = []
        skills = {
            "行研": 5, "行业研究": 5, "研究": 3, "行业分析": 5,
            "项目挖掘": 5, "项目获取": 5, "sourcing": 3, "项目开发": 3,
            "尽职调查": 5, "尽调": 5, "DD": 3, "due diligence": 3, "调查": 3,
            "交易执行": 5, "投后": 3, "post-investment": 3, "交易": 3, "执行": 3,
            "投资": 3, "股权": 3, "VC": 3, "风险投资": 3, "创业投资": 3
        }
        
        text_lower = resume_text.lower()
        for skill, points in skills.items():
            if skill in resume_text or skill.lower() in text_lower:
                score += points
                reasons.append(f"{skill}({points}分)")
        
        # 去重并限制总分
        score = min(20, score)
        return score, "; ".join(set(reasons)) if reasons else "无相关技能关键词(0分)"
    
    def evaluate_resume(self, resume: Dict) -> Dict:
        """评估单份简历"""
        # 提取字段（根据猎聘网导出格式调整）
        bachelor_school = resume.get('本科学历', '')
        bachelor_major = resume.get('本科专业', '')
        master_school = resume.get('硕士学历', '')
        master_major = resume.get('硕士专业', '')
        total_exp = resume.get('工作经验', '')
        vc_exp = resume.get('投资经验', resume.get('相关经验', ''))
        case_info = resume.get('项目经验', resume.get('工作描述', ''))
        salary = resume.get('期望薪资', '')
        resume_text = ' '.join([str(v) for v in resume.values()])
        
        # 各项评分
        edu_score, edu_reason = self.score_education(bachelor_school, bachelor_major,
                                                     master_school, master_major)
        exp_score, exp_reason = self.score_experience(total_exp, vc_exp, case_info)
        salary_score, salary_reason = self.score_salary(salary, resume.get('当前职位', ''))
        skill_score, skill_reason = self.score_skills(resume_text)
        
        # 总分
        total_score = edu_score + exp_score + salary_score + skill_score
        
        # 推荐决策
        recommended = total_score >= self.threshold
        status = "推荐" if recommended else "不推荐"
        
        return {
            **resume,
            '学历评分': edu_score,
            '经验评分': exp_score,
            '薪资评分': salary_score,
            '技能评分': skill_score,
            '总分': total_score,
            '推荐理由': f"学历:{edu_reason}; 经验:{exp_reason}; 薪资:{salary_reason}; 技能:{skill_reason}",
            '状态': status,
            '操作时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _is_top_school(self, school: str) -> bool:
        """检查是否顶级学校"""
        if not school:
            return False
        return any(top in school for top in self.top_schools)
    
    def _is_stem_major(self, major: str) -> bool:
        """检查是否理工科专业"""
        if not major:
            return False
        return any(stem in major for stem in self.stem_programs)
    
    def _is_business_major(self, major: str) -> bool:
        """检查是否商科专业"""
        if not major:
            return False
        return any(biz in major for biz in self.business_programs)
    
    def _extract_years(self, exp_str: str) -> int:
        """从经验字符串中提取年数"""
        if not exp_str:
            return 0
        # 匹配数字+年
        match = re.search(r'(\d+)\s*年', exp_str)
        return int(match.group(1)) if match else 0
    
    def process_file(self, input_file: str, output_file: str):
        """处理CSV文件"""
        candidates = []
        recommended = []
        
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                result = self.evaluate_resume(row)
                candidates.append(result)
                if result['状态'] == '推荐':
                    recommended.append(result)
        
        # 保存完整结果
        if candidates:
            output_fields = list(candidates[0].keys())
            with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=output_fields)
                writer.writeheader()
                writer.writerows(candidates)
        
        # 保存推荐列表
        if recommended:
            rec_file = output_file.replace('.csv', '_recommended.csv')
            with open(rec_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=output_fields)
                writer.writeheader()
                writer.writerows(recommended)
        
        return len(candidates), len(recommended)

def main():
    """主函数"""
    print("=" * 60)
    print("VC投资经理简历筛选系统 v1.0")
    print("=" * 60)
    
    # 初始化筛选器
    filter = ResumeFilter()
    
    # 输入输出文件路径
    input_file = "../data/input/resumes.csv"  # 猎聘网导出的简历
    output_file = "../output/evaluated_resumes.csv"
    
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"推荐阈值: {filter.threshold}分")
    print("-" * 60)
    
    try:
        total, recommended = filter.process_file(input_file, output_file)
        print(f"处理完成！")
        print(f"总简历数: {total}")
        print(f"推荐人数: {recommended}")
        print(f"推荐率: {recommended/total*100:.1f}%" if total > 0 else "推荐率: N/A")
        
        if recommended > 0:
            rec_file = output_file.replace('.csv', '_recommended.csv')
            print(f"推荐列表已保存至: {rec_file}")
        
        print("=" * 60)
        
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {input_file}")
        print("请将猎聘网导出的简历CSV文件放置到 data/input/ 目录下")
        print("文件应命名为: resumes.csv")
    except Exception as e:
        print(f"处理过程中出现错误: {e}")

if __name__ == "__main__":
    main()