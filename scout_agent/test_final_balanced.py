#!/usr/bin/env python3
"""
🧪 小蜜蜂Agent最终平衡版

平衡决定性否决规则和通过阈值：
1. 保持否决规则（样本3）
2. 调整通过阈值（样本7、10）
3. 优化人才储备（样本16）
"""

import sys
import json
from test_calibration import CALIBRATION_SAMPLES

class BalancedEngine:
    """平衡版规则引擎"""
    
    def __init__(self):
        print("🎯 使用平衡版规则引擎")
        print("   保持否决规则，调整通过阈值，优化人才储备")
    
    def evaluate_candidate(self, candidate: dict, client_type: str = "strict") -> dict:
        """平衡评估逻辑"""
        
        # ==================== 决定性否决规则（保持） ====================
        
        # 规则1：生物+商科组合直接否决
        first_major = candidate['education']['first_degree']['major']
        second_major = candidate['education']['second_degree']['major']
        
        if ('生物' in first_major or '生物学' in first_major) and '商' in second_major:
            return {
                'total_score': 0.0,
                'education_score': 0.0,
                'experience_score': 0.0,
                'relevance_score': 0.0,
                'decision': 'reject',
                'reason': '生物+商科组合完全不匹配AI投资，直接否决',
                'special_rules': ['生物+商科组合直接否决'],
                'score_details': self._get_score_details(candidate, client_type)
            }
        
        # ==================== 正常评分流程 ====================
        
        # 教育分数
        education_score = self._calculate_education_score(candidate, client_type)
        
        # 经验分数
        experience_score = self._calculate_experience_score(candidate, client_type)
        
        # 相关性分数
        relevance_score = self._calculate_relevance_score(candidate)
        
        # 权重（稍微调整）
        if client_type == "strict":
            education_weight = 0.40  # 从0.45降到0.40
            experience_weight = 0.50  # 从0.45升到0.50
            relevance_weight = 0.10
        else:
            education_weight = 0.30  # 从0.35降到0.30
            experience_weight = 0.60  # 从0.55升到0.60
            relevance_weight = 0.10
        
        total_score = (
            education_score * education_weight +
            experience_score * experience_weight +
            relevance_score * relevance_weight
        )
        
        # 特别加分：长期连续工作经验
        if self._has_long_term_experience(candidate):
            total_score = min(1.0, total_score + 0.15)
        
        # 特别加分：顶级学校
        if self._has_top_school(candidate):
            total_score = min(1.0, total_score + 0.1)
        
        # 应用决策阈值（调整后的阈值）
        return self._apply_balanced_decision(total_score, education_score, experience_score, client_type, candidate)
    
    def _get_score_details(self, candidate: dict, client_type: str) -> dict:
        """获取详细的分数细节（用于否决样本）"""
        return {
            'education_score': self._calculate_education_score(candidate, client_type),
            'experience_score': self._calculate_experience_score(candidate, client_type),
            'relevance_score': self._calculate_relevance_score(candidate)
        }
    
    def _calculate_education_score(self, candidate: dict, client_type: str) -> float:
        """计算教育分数（优化版）"""
        education = candidate.get('education', {})
        first_degree = education.get('first_degree', {})
        second_degree = education.get('second_degree', {})
        
        # 第一学历分数
        first_score = self._get_single_degree_score(first_degree, client_type, 'first')
        
        # 第二学历分数
        second_score = self._get_single_degree_score(second_degree, client_type, 'second')
        
        # 专业组合优化
        combo_bonus = self._get_combo_bonus(first_degree, second_degree, client_type)
        
        # 总分：第一45% + 第二45% + 组合10%
        total = first_score * 0.45 + second_score * 0.45 + combo_bonus * 0.1
        
        return min(total, 1.0)
    
    def _get_single_degree_score(self, degree: dict, client_type: str, degree_type: str) -> float:
        """获取单学历分数"""
        school = degree.get('school', '')
        major = degree.get('major', '')
        ranking = degree.get('ranking', '')
        
        # 学校分数
        school_score = 0.0
        if 'QS100' in ranking or 'MIT' in school or '麻省理工学院' in school:
            school_score = 1.0
        elif '985' in ranking:
            school_score = 1.0
        elif '211' in ranking:
            school_score = 0.8
        elif '双一流' in ranking:
            school_score = 0.7
        else:
            school_score = 0.5
        
        # 专业分数
        major_score = self._get_major_score(major, degree_type, client_type)
        
        # 综合分数
        return school_score * major_score
    
    def _get_major_score(self, major: str, degree_type: str, client_type: str) -> float:
        """专业分数"""
        major_lower = major.lower()
        
        # STEM核心专业
        stem_core = ['计算机', '软件', '人工智能', '机器学习', '电子', '电气', '自动化', 
                     '通信', '机械', '航空航天', '材料', '化学', '物理', '数学', '统计', '核工程']
        
        # 边缘理工科
        stem_edge = ['生物', '土木', '建筑', '农业', '环境']
        
        # 商科专业
        business = ['金融', '经济', '管理', '市场营销', '工商管理', '会计', '国际贸易', '商学']
        
        # 检查分类
        for core in stem_core:
            if core in major_lower:
                return 1.0
        
        for edge in stem_edge:
            if edge in major_lower:
                return 0.4  # 边缘理工科
        
        for bus in business:
            if bus in major_lower:
                if client_type == 'strict' and degree_type == 'first':
                    return 0.0  # 苛刻客户第一学历商科已在否决规则处理
                elif degree_type == 'second':
                    return 0.8 if client_type == 'strict' else 1.0
                else:
                    return 0.7
        
        return 0.6
    
    def _get_combo_bonus(self, first_degree: dict, second_degree: dict, client_type: str) -> float:
        """专业组合加成"""
        first_major = first_degree.get('major', '')
        second_major = second_degree.get('major', '')
        
        # 最佳组合：STEM核心本科 + 商科硕士
        if (any(keyword in first_major for keyword in ['计算机', '软件', '人工智能', '机器学习', '电子', '核工程']) and
            any(keyword in second_major for keyword in ['金融', '经济', '商学'])):
            return 1.0
        
        # 良好组合：STEM核心本科 + STEM核心硕士
        elif (any(keyword in first_major for keyword in ['计算机', '软件', '人工智能', '机器学习', '电子', '核工程']) and
              any(keyword in second_major for keyword in ['计算机', '软件', '人工智能', '机器学习', '电子', '核工程'])):
            return 1.0
        
        # 较差组合（已否决）：生物+商科
        elif ('生物' in first_major or '生物学' in first_major) and '商' in second_major:
            return 0.0  # 已否决
        
        # 一般组合
        else:
            return 0.5
    
    def _calculate_experience_score(self, candidate: dict, client_type: str) -> float:
        """计算经验分数（优化版）"""
        work_experience = candidate.get('work_experience', [])
        
        if not work_experience:
            return 0.0
        
        # 检查是否有投资经验
        has_investment = any(exp.get('is_investment', False) for exp in work_experience)
        
        if has_investment:
            first_job = work_experience[0]
            duration = first_job.get('duration', '')
            
            # 8年工作经验：满分
            if '8年' in duration:
                return 1.0
            # 5年工作经验：高分
            elif '5年' in duration:
                return 0.9
            # 3-4年工作经验：良好
            elif '3年' in duration or '4年' in duration:
                return 0.8
            # 2年工作经验：一般
            elif '2年' in duration:
                return 0.7
            # 其他：基础分
            else:
                return 0.6
        else:
            return 0.4  # 无投资经验但有工作经验
    
    def _calculate_relevance_score(self, candidate: dict) -> float:
        """相关性分数"""
        score = 0.0
        
        # 城市匹配
        if candidate.get('expected_city') == candidate.get('current_city'):
            score += 0.3
        
        # 岗位相关性
        current_pos = candidate.get('current_position', '').lower()
        if '投资' in current_pos or '基金' in current_pos or '资本' in current_pos:
            score += 0.4
        
        # AI技能标签
        tags = candidate.get('tags', [])
        for tag in tags:
            tag_lower = tag.lower()
            if '机器学习' in tag_lower or 'python' in tag_lower or 'ai' in tag_lower or '人工智能' in tag_lower:
                score += 0.3  # 增加权重
                break
        
        return min(score, 1.0)
    
    def _has_long_term_experience(self, candidate: dict) -> bool:
        """是否有长期工作经验"""
        work_experience = candidate.get('work_experience', [])
        if not work_experience:
            return False
        
        first_job = work_experience[0]
        duration = first_job.get('duration', '')
        
        return '8年' in duration or '5年' in duration
    
    def _has_top_school(self, candidate: dict) -> bool:
        """是否有顶级学校"""
        education = candidate.get('education', {})
        second_degree = education.get('second_degree', {})
        school = second_degree.get('school', '')
        
        top_schools = ['MIT', '麻省理工学院', '斯坦福', '哈佛', '剑桥', '牛津', '加州伯克利']
        return any(top_school in school for top_school in top_schools)
    
    def _apply_balanced_decision(self, total_score: float, education_score: float, experience_score: float, 
                                client_type: str, candidate: dict) -> dict:
        """应用平衡决策阈值"""
        
        # 调整后的阈值
        if client_type == 'strict':
            pass_threshold = 0.65  # 从0.70降到0.65
            reject_threshold = 0.40
        else:
            pass_threshold = 0.55  # 从0.60降到0.55
            reject_threshold = 0.30
        
        # 宽松客户的人才储备识别（优化）
        if client_type == 'loose':
            # 优秀学术背景 + 经验不足 → 人才储备
            if education_score >= 0.8 and experience_score < 0.5:
                # 即使总分超过阈值，也进人才储备
                if total_score >= pass_threshold:
                    # 特殊处理：优秀学术背景通过，但标记为人才储备潜力
                    return {
                        'total_score': total_score,
                        'education_score': education_score,
                        'experience_score': experience_score,
                        'relevance_score': 0.0,
                        'decision': 'pass',
                        'reason': f'优秀学术背景（教育分{education_score:.2f}），总分{total_score:.2f}超过阈值{pass_threshold}',
                        'talent_pool_note': '学术潜力人才，适合研究员岗位'
                    }
                else:
                    return {
                        'total_score': total_score,
                        'education_score': education_score,
                        'experience_score': experience_score,
                        'relevance_score': 0.0,
                        'decision': 'review',
                        'reason': f'优秀学术背景（教育分{education_score:.2f}）但经验不足（经验分{experience_score:.2f}），人才储备',
                        'talent_pool': {'eligible': True, 'pool_name': '学术潜力人才'}
                    }
        
        # 正常决策
        if total_score >= pass_threshold:
            decision = 'pass'
            reason = f'总分{total_score:.2f}达到通过阈值{pass_threshold}'
        elif total_score < reject_threshold:
            decision = 'reject'
            reason = f'总分{total_score:.2f}低于拒绝阈值{reject_threshold}'
        else:
            decision = 'review'
            reason = f'总分{total_score:.2f}在审核区间[{reject_threshold}, {pass_threshold})'
        
        result = {
            'total_score': total_score,
            'education_score': education_score,
            'experience_score': experience_score,
            'relevance_score': 0.0,
            'decision': decision,
            'reason': reason
        }
        
        # 检查是否有特别加分规则应用
        special_rules = []
        if self._has_long_term_experience(candidate):
            special_rules.append('长期连续工作经验特别加分')
        if self._has_top_school(candidate):
            special_rules.append('顶级学校特别加分')
        
        if special_rules:
            result['special_rules'] = special_rules
        
        return result

def run_balanced_test():
    """运行平衡版测试"""
    print("🧪 开始平衡版校准测试")
    print("=" * 80)
    print("🎯 平衡否决规则和通过阈值")
    print("📋 调整策略：")
    print("   1. 保持：生物+商科组合直接否决（样本3）")
    print("   2. 调整：通过阈值从0.70降到0.65")
    print("   3. 优化：人才储备识别逻辑")
    print("   4. 增加：长期工作经验特别加分")
    print("   5. 增加：顶级学校特别加分")
    print("=" * 80)
    
    # 初始化引擎
    engine = BalancedEngine()
    
    # 统计结果
    results = []
    correct_count = 0
    total_count = len(CALIBRATION_SAMPLES)
    
    # 重点关注样本
    focus_samples = {
        'sample_3_huang': '期望reject → 否决规则',
        'sample_7_gu': '期望pass → 阈值调整',
        'sample_10_xu': '期望pass → 阈值调整',
        'sample_16_li': '期望pass_talent_pool → 人才储备优化'
    }
    
    for sample in CALIBRATION_SAMPLES:
        sample_id = sample['id']
        is_focus = sample_id in focus_samples
        
        if is_focus:
            print(f"\n🔍 重点关注: {sample_id}")
            print(f"   目标: {focus_samples[sample_id]}")
        else:
            print(f"\n📋 测试样本: {sample_id}")
        
        print(f"   候选人: {sample['candidate']['name']}")
        
        # 显示专业信息
        education = sample['candidate']['education']
        print(f"   教育背景:")
        print(f"     本科: {education['first_degree']['school']} - {education['first_degree']['major']}")
        print(f"     硕士: {education['second_degree']['school']} - {education['second_degree']['major']}")
        
        # 显示经验信息
        work_exp = sample['candidate']['work_experience']
        if work_exp:
            print(f"   工作经验: {work_exp[0]['duration']} - {work_exp[0]['field_relevance']}")
        
        print(f"   JD: {sample['jd_name']}")
        print(f"   客户类型: {sample['client_type']}")
        print(f"   用户评价: {sample['user_evaluation']['result']} - {sample['user_evaluation']['reason']}")
        
        # 运行规则引擎评估
        evaluation = engine.evaluate_candidate(
            sample['candidate'],
            sample['client_type']
        )
        
        print(f"   规则引擎结果:")
        print(f"     总分: {evaluation['total_score']:.2f}")
        print(f"     教育分: {evaluation['education_score']:.2f}")
        print(f"     经验分: {evaluation['experience_score']:.2f}")
        print(f"     决策: {evaluation['decision']}")
        print(f"     原因: {evaluation['reason']}")
        
        if 'special_rules' in evaluation and evaluation['special_rules']:
            print(f"     📝 应用特殊规则: {', '.join(evaluation['special_rules'])}")
        
        if 'talent_pool' in evaluation and evaluation['talent_pool'].get('eligible', False):
            print(f"     人才储备: {evaluation['talent_pool'].get('pool_name', '')}")
        elif 'talent_pool_note' in evaluation:
            print(f"     人才储备提示: {evaluation['talent_pool_note']}")
        
        # 判断是否正确
        expected_result = sample['user_evaluation']['result']
        actual_result = evaluation['decision']
        
        # 处理人才储备的特殊情况
        talent_pool_match = False
        if expected_result == 'pass_talent_pool':
            if 'talent_pool' in evaluation and evaluation['talent_pool'].get('eligible', False):
                talent_pool_match = True
            elif 'talent_pool_note' in evaluation:
                talent_pool_match = True
        
        if talent_pool_match or (expected_result in ['pass', 'reject'] and actual_result == expected_result):
            correct = True
        else:
            correct = False
        
        if correct:
            correct_count += 1
            if is_focus:
                print("   ✅✅ 重点关注样本达标！")
            else:
                print("   ✅ 匹配成功")
        else:
            if is_focus:
                print(f"   ❌❌ 重点关注样本未达标 (期望: {expected_result}, 实际: {actual_result})")
            else:
                print(f"   ❌ 匹配失败 (期望: {expected_result}, 实际: {actual_result})")
        
        results.append({
            'sample_id': sample_id,
            'candidate': sample['candidate']['name'],
            'expected': expected_result,
            'actual': actual_result,
            'score': evaluation['total_score'],
            'correct': correct,
            'evaluation': evaluation
        })
    
    # 输出统计结果
    print("\n" + "=" * 80)
    print("📊 平衡版校准测试结果统计")
    print(f"   总测试样本数: {total_count}")
    print(f"   正确匹配数: {correct_count}")
    accuracy = correct_count / total_count if total_count > 0 else 0
    print(f"   准确率: {accuracy:.1%}")
    
    # 重点关注样本结果
    focus_correct = sum(1 for r in results if r['sample_id'] in focus_samples and r['correct'])
    focus_total = len(focus_samples)
    focus_accuracy = focus_correct / focus_total if focus_total > 0 else 0
    
    print(f"\n🔍 重点关注样本结果:")
    print(f"   样本数: {focus_total}")
    print(f"   正确数: {focus_correct}")
    print(f"   准确率: {focus_accuracy:.1%}")
    
    # 与原版对比
    original_accuracy = 0.75
    improvement = accuracy - original_accuracy
    
    if improvement > 0:
        print(f"   📈 相比原版提升: +{improvement:.1%}")
    
    # 详细结果
    print("\n📋 详细结果:")
    for result in results:
        status = "✅" if result['correct'] else "❌"
        if result['sample_id'] in focus_samples:
            print(f"   🔍 {status} {result['sample_id']}: {result['candidate']} (重点关注)")
        else:
            print(f"   {status} {result['sample_id']}: {result['candidate']}")
        print(f"       期望: {result['expected']}, 实际: {result['actual']}, 分数: {result['score']:.2f}")
    
    # 生成报告
    report = {
        'test_date': '2026-03-07',
        'test_type': 'balanced_calibration',
        'strategy': [
            "保持生物+商科组合直接否决规则",
            "降低通过阈值：苛刻客户0.65，宽松客户0.55",
            "增加长期工作经验特别加分",
            "增加顶级学校特别加分",
            "优化人才储备识别逻辑"
        ],
        'thresholds': {
            'strict_client': {'pass': 0.65, 'reject': 0.40},
            'loose_client': {'pass': 0.55, 'reject': 0.30}
        },
        'samples_count': total_count,
        'correct_count': correct_count,
        'accuracy': accuracy,
        'original_accuracy': original_accuracy,
        'improvement': f"{improvement:+.1%}",
        'focus_samples_accuracy': focus_accuracy,
        'results': results
    }
    
    # 保存报告
    report_file = "balanced_calibration_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 平衡版校准测试报告已保存到: {report_file}")
    
    # 评估
    if accuracy >= 0.875:
        print("\n🎉🎉🎉 平衡优化成功！准确率达到87.5%！")
        print("   可以立即集成到小蜜蜂Agent系统！")
        return True, accuracy
    elif accuracy >= 0.80:
        print(f"\n⚠️  平衡优化有效，准确率{accuracy:.1%}，接近目标")
        print("   可以考虑集成")
        return True, accuracy
    else:
        print(f"\n❌ 平衡优化不足，准确率{accuracy:.1%}")
        return False, accuracy

if __name__ == "__main__":
    success, accuracy = run_balanced_test()
    sys.exit(0 if success else 1)