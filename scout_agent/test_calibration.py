#!/usr/bin/env python3
"""
🧪 小蜜蜂Agent校准测试

基于用户提供的16个标注样本，验证校准规则的准确性
"""

import sys
import os
import json
import yaml
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# ==================== 测试数据 ====================

# 基于用户标注的16个样本数据
CALIBRATION_SAMPLES = [
    # 松禾资本 - 6个样本
    {
        "id": "sample_1_wang",
        "jd_name": "松禾资本-AI投资经理",
        "client_type": "strict",
        "candidate": {
            "name": "王**",
            "age": 36,
            "education": {
                "first_degree": {
                    "school": "山东财经大学",
                    "major": "国际经济与贸易",
                    "level": "本科",
                    "type": "商科",
                    "ranking": "非985/211"
                },
                "second_degree": {
                    "school": "中国人民大学",
                    "major": "金融",
                    "level": "硕士",
                    "type": "商科",
                    "ranking": "985"
                }
            },
            "work_experience": [
                {
                    "company": "泰禾智能（603656.SH）",
                    "position": "董事会秘书",
                    "duration": "1年2个月",
                    "is_investment": False,
                    "field_relevance": "不相关"
                },
                {
                    "company": "爱旭股份（600732.SH）",
                    "position": "证券事务代表",
                    "duration": "11个月",
                    "is_investment": False,
                    "field_relevance": "不相关"
                }
            ],
            "current_position": "董事会秘书",
            "expected_city": "杭州",
            "current_city": "杭州"
        },
        "user_evaluation": {
            "result": "reject",
            "reason": "第一学历不符合，2段工作经验与投资不相关"
        }
    },
    {
        "id": "sample_2_han",
        "jd_name": "松禾资本-AI投资经理",
        "client_type": "strict",
        "candidate": {
            "name": "韩**",
            "age": 31,
            "education": {
                "first_degree": {
                    "school": "密歇根大学",
                    "major": "核工程与核技术",
                    "level": "本科",
                    "type": "理工科",
                    "ranking": "QS100"
                },
                "second_degree": {
                    "school": "麻省理工学院",
                    "major": "核工程",
                    "level": "硕士",
                    "type": "理工科",
                    "ranking": "QS100"
                }
            },
            "work_experience": [
                {
                    "company": "国资投资平台",
                    "position": "投资总监",
                    "duration": "3年11个月",
                    "is_investment": True,
                    "field_relevance": "AI相关",
                    "skills": ["机器学习", "python"]
                }
            ],
            "current_position": "投资总监",
            "expected_city": "北京",
            "current_city": "北京"
        },
        "user_evaluation": {
            "result": "pass",
            "reason": "海外名校背景，3年投资经验，AI技术相关"
        }
    },
    {
        "id": "sample_3_huang",
        "jd_name": "松禾资本-AI投资经理",
        "client_type": "strict",
        "candidate": {
            "name": "黄**",
            "age": 32,
            "education": {
                "first_degree": {
                    "school": "南京大学",
                    "major": "生物科学",
                    "level": "本科",
                    "type": "理工科",
                    "ranking": "985"
                },
                "second_degree": {
                    "school": "悉尼大学",
                    "major": "商学",
                    "level": "硕士",
                    "type": "商科",
                    "ranking": "QS100"
                }
            },
            "work_experience": [
                {
                    "company": "北京赟汇管理咨询有限公司",
                    "position": "高级投资经理",
                    "duration": "3年",
                    "is_investment": True,
                    "field_relevance": "未知"
                },
                {
                    "company": "普华永道管理咨询",
                    "position": "咨询顾问",
                    "duration": "7个月",
                    "is_investment": False,
                    "field_relevance": "咨询"
                }
            ],
            "current_position": "高级投资经理",
            "expected_city": "北京",
            "current_city": "北京"
        },
        "user_evaluation": {
            "result": "reject",
            "reason": "本硕学历都不符合，3年投资经验不足"
        }
    },
    {
        "id": "sample_5_chen",
        "jd_name": "松禾资本-AI投资经理",
        "client_type": "strict",
        "candidate": {
            "name": "陈先生",
            "age": 35,
            "education": {
                "first_degree": {
                    "school": "厦门大学",
                    "major": "软件工程",
                    "level": "本科",
                    "type": "理工科",
                    "ranking": "985"
                },
                "second_degree": {
                    "school": "南洋理工大学",
                    "major": "金融学",
                    "level": "硕士",
                    "type": "商科",
                    "ranking": "QS100"
                }
            },
            "work_experience": [
                {
                    "company": "招商局资本投资有限责任公司",
                    "position": "投资经理",
                    "duration": "4年11个月",
                    "is_investment": True,
                    "field_relevance": "投资"
                },
                {
                    "company": "深圳市前海金融控股有限公司",
                    "position": "管培生",
                    "duration": "2年3个月",
                    "is_investment": True,
                    "field_relevance": "金融"
                }
            ],
            "current_position": "投资经理",
            "expected_city": "深圳",
            "current_city": "深圳"
        },
        "user_evaluation": {
            "result": "pass",
            "reason": "985工科+海外商科硕士，投资经验近5年"
        }
    },
    # 千乘资本 - 3个样本
    {
        "id": "sample_7_gu",
        "jd_name": "千乘资本-AI投资经理",
        "client_type": "strict",
        "candidate": {
            "name": "顾**",
            "age": 29,
            "education": {
                "first_degree": {
                    "school": "上海外国语大学附属外国语学校",
                    "major": "高中",
                    "level": "高中",
                    "type": "其他",
                    "ranking": "未知"
                },
                "second_degree": {
                    "school": "复旦大学",
                    "major": "金融工商管理",
                    "level": "硕士",
                    "type": "商科",
                    "ranking": "985"
                }
            },
            "work_experience": [
                {
                    "company": "上海国际集团投资有限公司",
                    "position": "助理,经理,高级经理",
                    "duration": "8年5个月",
                    "is_investment": True,
                    "field_relevance": "投资"
                }
            ],
            "current_position": "高级经理",
            "expected_city": "上海",
            "current_city": "上海"
        },
        "user_evaluation": {
            "result": "pass",
            "reason": "硕士学校不错，近8年在同一家公司，可能从事AI投资"
        }
    },
    {
        "id": "sample_10_xu",
        "jd_name": "千乘资本-AI投资经理",
        "client_type": "strict",
        "candidate": {
            "name": "许**",
            "age": 29,
            "education": {
                "first_degree": {
                    "school": "清华大学",
                    "major": "工业工程",
                    "level": "本科",
                    "type": "理工科",
                    "ranking": "985"
                },
                "second_degree": {
                    "school": "美国华盛顿大学",
                    "major": "计算语言学",
                    "level": "硕士",
                    "type": "理工科",
                    "ranking": "QS100"
                }
            },
            "work_experience": [
                {
                    "company": "力合创投",
                    "position": "投资经理",
                    "duration": "2年4个月",
                    "is_investment": True,
                    "field_relevance": "投资"
                },
                {
                    "company": "前海星河资本",
                    "position": "投资经理",
                    "duration": "1年1个月",
                    "is_investment": True,
                    "field_relevance": "投资"
                }
            ],
            "current_position": "投资经理",
            "expected_city": "深圳",
            "current_city": "深圳"
        },
        "user_evaluation": {
            "result": "pass",
            "reason": "本硕学历和专业都加分，3年多投资经验"
        }
    },
    # 明荟致远 - 3个样本
    {
        "id": "sample_14_lai",
        "jd_name": "明荟致远-硬科技投资总监",
        "client_type": "loose",
        "candidate": {
            "name": "赖先生",
            "age": 35,
            "education": {
                "first_degree": {
                    "school": "深圳国际交流学院",
                    "major": "高中",
                    "level": "高中",
                    "type": "其他",
                    "ranking": "未知"
                },
                "second_degree": {
                    "school": "巴斯大学",
                    "major": "机械工程",
                    "level": "博士",
                    "type": "理工科",
                    "ranking": "QS100"
                }
            },
            "work_experience": [
                {
                    "company": "广州产业投资资本管理有限公司",
                    "position": "高级投资经理",
                    "duration": "2年11个月",
                    "is_investment": True,
                    "field_relevance": "投资"
                },
                {
                    "company": "顺丰速运国际事业部",
                    "position": "项目管理高级工程师",
                    "duration": "2年11个月",
                    "is_investment": False,
                    "field_relevance": "物流"
                }
            ],
            "current_position": "高级投资经理",
            "expected_city": "深圳",
            "current_city": "深圳"
        },
        "user_evaluation": {
            "result": "pass",
            "reason": "博士学历和专业加分，近3年工作经验大致匹配"
        }
    },
    {
        "id": "sample_16_li",
        "jd_name": "明荟致远-硬科技投资总监",
        "client_type": "loose",
        "candidate": {
            "name": "李嘉琦",
            "age": 32,
            "education": {
                "first_degree": {
                    "school": "中山大学",
                    "major": "材料物理",
                    "level": "本科",
                    "type": "理工科",
                    "ranking": "985"
                },
                "second_degree": {
                    "school": "新加坡国立大学",
                    "major": "物理系",
                    "level": "硕士",
                    "type": "理工科",
                    "ranking": "QS100"
                }
            },
            "work_experience": [
                {
                    "company": "新加坡国立大学",
                    "position": "研究助理",
                    "duration": "1年7个月",
                    "is_investment": False,
                    "field_relevance": "研究"
                },
                {
                    "company": "Jebsen & Jessen Pte Ltd",
                    "position": "战略投资并购助理",
                    "duration": "5个月",
                    "is_investment": True,
                    "field_relevance": "投资并购"
                }
            ],
            "current_position": "研究助理",
            "expected_city": "深圳",
            "current_city": "深圳"
        },
        "user_evaluation": {
            "result": "pass_talent_pool",
            "reason": "优秀学术背景，人才储备（不适合投资总监但可能是优秀研究员）"
        }
    }
]

# ==================== 校准规则引擎 ====================

class CalibrationRuleEngine:
    """基于校准配置的规则引擎"""
    
    def __init__(self, config_path=None):
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._load_default_config()
        
        logger.info(f"初始化校准规则引擎，版本: {self.config.get('agent', {}).get('version', '1.0.0')}")
    
    def _load_default_config(self):
        """加载默认配置"""
        return {
            'education_weights': {
                'first_degree': {
                    'priority_1': {'weight': 1.0, 'schools': ['985理工科', 'QS100理工科']},
                    'priority_2': {'weight': 0.7, 'schools': ['211理工科', '双一流理工科']},
                    'priority_3': {'weight': 0.4, 'schools': ['其他理工科']},
                    'reject': {'weight': 0.0, 'schools': ['商科本科']}
                },
                'second_degree': {
                    'priority_1': {'weight': 1.0, 'schools': ['QS100硕士', '985硕士']},
                    'priority_2': {'weight': 0.8, 'schools': ['211硕士', '海外名校硕士']},
                    'priority_3': {'weight': 0.5, 'schools': ['其他硕士']}
                },
                'degree_combo': {
                    'priority_1': {'weight': 1.0, 'combos': ['理工本科 + 商科硕士', '理工本科 + 理工硕士']},
                    'priority_2': {'weight': 0.7, 'combos': ['商科本科 + 理工硕士']},
                    'priority_3': {'weight': 0.3, 'combos': ['理工本科 + 其他硕士', '商科本科 + 商科硕士']}
                }
            },
            'experience_weights': {
                'investment_continuity': {
                    'priority_1': {'weight': 1.0, 'description': '在同一投资机构连续工作3年以上'},
                    'priority_2': {'weight': 0.8, 'description': '累计投资经验4年以上'},
                    'priority_3': {'weight': 0.6, 'description': '投资相关岗位2年以上'},
                    'negative': {'weight': -0.5, 'description': '频繁跳槽（2年内换工作）'}
                },
                'industry_experience': {
                    'priority_1': {'weight': 1.0, 'description': '与需求岗位一致的产业投资经验'},
                    'priority_2': {'weight': 0.9, 'description': '投资机构经验'},
                    'priority_3': {'weight': 0.6, 'description': '非相关产业投资经验'},
                    'priority_4': {'weight': 0.4, 'description': '相关岗位经验'}
                }
            },
            'thresholds': {
                'strict_client': {
                    'pass_threshold': 0.7,
                    'reject_threshold': 0.4,
                    'review_threshold': 0.5
                },
                'loose_client': {
                    'pass_threshold': 0.6,
                    'reject_threshold': 0.3,
                    'review_threshold': 0.4
                },
                'talent_pool': {
                    'academic_potential': 0.8,
                    'research_potential': 0.7,
                    'major_match': 0.8
                }
            }
        }
    
    def evaluate_candidate(self, candidate: Dict, client_type: str = "strict") -> Dict:
        """评估候选人"""
        scores = {
            'education': self._calculate_education_score(candidate['education']),
            'experience': self._calculate_experience_score(candidate['work_experience']),
            'relevance': self._calculate_relevance_score(candidate)
        }
        
        # 计算总分（基于配置的权重）
        weights = self.config.get('screening_rules', {}).get(f'{client_type}_client_decision', {}).get('scoring_pass', {})
        education_weight = weights.get('education_weight', 0.4)
        experience_weight = weights.get('experience_weight', 0.5)
        relevance_weight = weights.get('relevance_weight', 0.1)
        
        total_score = (
            scores['education']['total'] * education_weight +
            scores['experience']['total'] * experience_weight +
            scores['relevance'] * relevance_weight
        )
        
        # 应用硬性拒绝规则
        hard_reject = self._check_hard_reject(candidate, client_type)
        if hard_reject['reject']:
            return {
                'total_score': total_score,
                'scores': scores,
                'decision': 'reject',
                'reason': hard_reject['reason'],
                'details': {
                    'education_score': scores['education']['total'],
                    'experience_score': scores['experience']['total'],
                    'relevance_score': scores['relevance']
                }
            }
        
        # 应用阈值决策
        thresholds = self.config['thresholds'][f'{client_type}_client']
        
        if total_score >= thresholds['pass_threshold']:
            decision = 'pass'
            reason = f"总分{total_score:.2f}达到通过阈值{thresholds['pass_threshold']}"
        elif total_score < thresholds['reject_threshold']:
            decision = 'reject'
            reason = f"总分{total_score:.2f}低于拒绝阈值{thresholds['reject_threshold']}"
        else:
            decision = 'review'
            reason = f"总分{total_score:.2f}在审核区间[{thresholds['reject_threshold']}, {thresholds['pass_threshold']})"
        
        # 检查人才储备条件
        talent_pool = self._check_talent_pool(candidate, scores, client_type)
        
        return {
            'total_score': total_score,
            'scores': scores,
            'decision': decision,
            'reason': reason,
            'talent_pool': talent_pool,
            'details': {
                'education_score': scores['education']['total'],
                'education_breakdown': scores['education']['breakdown'],
                'experience_score': scores['experience']['total'],
                'experience_breakdown': scores['experience']['breakdown'],
                'relevance_score': scores['relevance']
            }
        }
    
    def _calculate_education_score(self, education: Dict) -> Dict:
        """计算教育背景分数"""
        breakdown = {}
        total = 0.0
        
        # 第一学历分数
        first_degree = education['first_degree']
        first_degree_score = self._get_education_level_score(
            school=first_degree['school'],
            major_type=first_degree['type'],
            ranking=first_degree['ranking'],
            degree_type='first'
        )
        breakdown['first_degree'] = first_degree_score
        total += first_degree_score * 0.5  # 第一学历权重50%
        
        # 第二学历分数
        second_degree = education['second_degree']
        second_degree_score = self._get_education_level_score(
            school=second_degree['school'],
            major_type=second_degree['type'],
            ranking=second_degree['ranking'],
            degree_type='second'
        )
        breakdown['second_degree'] = second_degree_score
        total += second_degree_score * 0.4  # 第二学历权重40%
        
        # 专业复合分数
        degree_combo = self._get_degree_combo_score(
            first_type=first_degree['type'],
            second_type=second_degree['type']
        )
        breakdown['degree_combo'] = degree_combo
        total += degree_combo * 0.1  # 专业复合权重10%
        
        return {'total': total, 'breakdown': breakdown}
    
    def _get_education_level_score(self, school: str, major_type: str, ranking: str, degree_type: str) -> float:
        """获取单个学历的分数"""
        weights = self.config['education_weights']
        
        # 检查直接拒绝条件
        if degree_type == 'first' and major_type == '商科':
            for school_type in weights['first_degree']['reject']['schools']:
                if '商科' in school_type:
                    return weights['first_degree']['reject']['weight']
        
        # 第一学历评分
        if degree_type == 'first':
            score_mapping = {
                '985理工科': ('985', '理工科'),
                'QS100理工科': ('QS100', '理工科'),
                '211理工科': ('211', '理工科'),
                '双一流理工科': ('双一流', '理工科'),
                '其他理工科': ('其他', '理工科')
            }
            
            for level, (rank_req, type_req) in score_mapping.items():
                if rank_req in ranking and type_req == major_type:
                    for priority in ['priority_1', 'priority_2', 'priority_3']:
                        if level in weights['first_degree'].get(priority, {}).get('schools', []):
                            return weights['first_degree'][priority]['weight']
        
        # 第二学历评分
        elif degree_type == 'second':
            score_mapping = {
                'QS100硕士': ('QS100',),
                '985硕士': ('985',),
                '211硕士': ('211',),
                '海外名校硕士': ('海外',),
                '其他硕士': ('其他',)
            }
            
            for level, rank_reqs in score_mapping.items():
                match = all(rank_req in ranking for rank_req in rank_reqs)
                if match:
                    for priority in ['priority_1', 'priority_2', 'priority_3']:
                        if level in weights['second_degree'].get(priority, {}).get('schools', []):
                            return weights['second_degree'][priority]['weight']
        
        return 0.0  # 默认分数
    
    def _get_degree_combo_score(self, first_type: str, second_type: str) -> float:
        """获取专业复合分数"""
        weights = self.config['education_weights']['degree_combo']
        
        combo = f"{first_type}本科 + {second_type}硕士"
        
        for priority in ['priority_1', 'priority_2', 'priority_3']:
            if combo in weights.get(priority, {}).get('combos', []):
                return weights[priority]['weight']
        
        return 0.0
    
    def _calculate_experience_score(self, work_experience: List) -> Dict:
        """计算工作经验分数"""
        breakdown = {}
        
        # 投资连续性分数
        continuity_score = self._calculate_continuity_score(work_experience)
        breakdown['continuity'] = continuity_score
        
        # 产业经验分数
        industry_score = self._calculate_industry_score(work_experience)
        breakdown['industry'] = industry_score
        
        # 计算总分
        total = continuity_score * 0.6 + industry_score * 0.4
        
        return {'total': total, 'breakdown': breakdown}
    
    def _calculate_continuity_score(self, work_experience: List) -> float:
        """计算工作连续性分数"""
        weights = self.config['experience_weights']['investment_continuity']
        
        # 检查是否有在同一机构连续工作3年以上
        for exp in work_experience:
            if exp.get('is_investment', False):
                duration = exp.get('duration', '')
                if '3年' in duration or '4年' in duration or '5年' in duration:
                    return weights['priority_1']['weight']
        
        # 检查累计投资经验
        total_investment_years = 0
        for exp in work_experience:
            if exp.get('is_investment', False):
                # 简单解析年限
                if '年' in exp.get('duration', ''):
                    try:
                        years = int(exp['duration'].split('年')[0])
                        total_investment_years += years
                    except:
                        pass
        
        if total_investment_years >= 4:
            return weights['priority_2']['weight']
        elif total_investment_years >= 2:
            return weights['priority_3']['weight']
        
        # 检查频繁跳槽
        if len(work_experience) >= 2:
            # 简单判断：如果最近两份工作都在2年以内
            recent_durations = []
            for exp in work_experience[:2]:
                if '年' in exp.get('duration', ''):
                    try:
                        years = int(exp['duration'].split('年')[0])
                        if years < 2:
                            recent_durations.append(True)
                    except:
                        pass
            
            if len(recent_durations) >= 2:
                return weights['negative']['weight']
        
        return 0.0
    
    def _calculate_industry_score(self, work_experience: List) -> float:
        """计算产业经验分数"""
        weights = self.config['experience_weights']['industry_experience']
        
        # 这里简化处理，实际应该更复杂的匹配逻辑
        for exp in work_experience:
            field_rel = exp.get('field_relevance', '')
            
            if field_rel == 'AI相关':
                return weights['priority_1']['weight']
            elif exp.get('is_investment', False):
                return weights['priority_2']['weight']
            elif '投资' in field_rel:
                return weights['priority_3']['weight']
        
        return weights['priority_4']['weight']
    
    def _calculate_relevance_score(self, candidate: Dict) -> float:
        """计算相关性分数"""
        # 简化处理，实际应该更复杂的匹配逻辑
        score = 0.0
        
        # 城市匹配
        if candidate.get('expected_city') == candidate.get('current_city'):
            score += 0.3
        
        # 岗位相关性
        current_pos = candidate.get('current_position', '').lower()
        investment_keywords = ['投资', '基金', '资本', '并购', '融资']
        if any(keyword in current_pos for keyword in investment_keywords):
            score += 0.4
        
        # 领域相关性
        work_exp = candidate.get('work_experience', [])
        for exp in work_exp:
            if exp.get('field_relevance') in ['AI相关', '投资']:
                score += 0.3
                break
        
        return min(score, 1.0)
    
    def _check_hard_reject(self, candidate: Dict, client_type: str) -> Dict:
        """检查硬性拒绝条件"""
        # 年龄限制（宽松客户）
        if client_type == 'loose' and candidate.get('age', 0) > 35:
            return {'reject': True, 'reason': '年龄超过35岁限制'}
        
        # 第一学历商科（苛刻客户）
        if client_type == 'strict':
            education = candidate.get('education', {})
            first_degree = education.get('first_degree', {})
            if first_degree.get('type') == '商科':
                return {'reject': True, 'reason': '第一学历商科，不符合理工科要求'}
        
        # 非投资岗位
        current_pos = candidate.get('current_position', '').lower()
        non_investment_positions = ['董秘', '投资者关系', '融资经理', '业务经理']
        if any(pos in current_pos for pos in non_investment_positions):
            return {'reject': True, 'reason': '岗位与投资核心职能不匹配'}
        
        return {'reject': False, 'reason': ''}
    
    def _check_talent_pool(self, candidate: Dict, scores: Dict, client_type: str) -> Dict:
        """检查人才储备条件"""
        if client_type != 'loose':
            return {'eligible': False, 'reason': ''}
        
        thresholds = self.config['thresholds']['talent_pool']
        education_score = scores['education']['total']
        
        # 优秀学术背景但经验不足
        if education_score >= thresholds['academic_potential'] and scores['experience']['total'] < 0.5:
            return {
                'eligible': True,
                'pool_name': '学术潜力人才',
                'reason': f'教育分数{education_score:.2f}高，但经验分数{scores["experience"]["total"]:.2f}低'
            }
        
        # 研究经验
        work_exp = candidate.get('work_experience', [])
        has_research = any('研究' in exp.get('position', '') for exp in work_exp)
        if has_research and education_score >= thresholds['research_potential']:
            return {
                'eligible': True,
                'pool_name': '研究型人才',
                'reason': '有研究经验且教育背景优秀'
            }
        
        return {'eligible': False, 'reason': ''}

# ==================== 测试运行 ====================

def run_calibration_test():
    """运行校准测试"""
    print("🧪 开始校准规则测试")
    print("=" * 80)
    
    # 初始化规则引擎（使用默认配置）
    engine = CalibrationRuleEngine()  # 不使用配置文件，用内置默认配置
    
    # 统计结果
    results = []
    correct_count = 0
    total_count = len(CALIBRATION_SAMPLES)
    
    for sample in CALIBRATION_SAMPLES:
        print(f"\n📋 测试样本: {sample['id']}")
        print(f"   候选人: {sample['candidate']['name']}")
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
        print(f"     教育分: {evaluation['details']['education_score']:.2f}")
        print(f"     经验分: {evaluation['details']['experience_score']:.2f}")
        print(f"     决策: {evaluation['decision']}")
        print(f"     原因: {evaluation['reason']}")
        
        if 'talent_pool' in evaluation and evaluation['talent_pool'].get('eligible', False):
            print(f"     人才储备: {evaluation['talent_pool'].get('pool_name', '')}")
        
        # 判断是否正确
        expected_result = sample['user_evaluation']['result']
        actual_result = evaluation['decision']
        
        # 处理人才储备的特殊情况
        if expected_result == 'pass_talent_pool' and 'talent_pool' in evaluation and evaluation['talent_pool'].get('eligible', False):
            correct = True
        elif expected_result in ['pass', 'reject'] and actual_result == expected_result:
            correct = True
        else:
            correct = False
        
        if correct:
            correct_count += 1
            print("   ✅ 匹配成功")
        else:
            print(f"   ❌ 匹配失败 (期望: {expected_result}, 实际: {actual_result})")
        
        results.append({
            'sample_id': sample['id'],
            'candidate': sample['candidate']['name'],
            'expected': expected_result,
            'actual': actual_result,
            'score': evaluation['total_score'],
            'correct': correct,
            'evaluation': evaluation
        })
    
    # 输出统计结果
    print("\n" + "=" * 80)
    print("📊 校准测试结果统计")
    print(f"   总测试样本数: {total_count}")
    print(f"   正确匹配数: {correct_count}")
    accuracy = correct_count / total_count if total_count > 0 else 0
    print(f"   准确率: {accuracy:.1%}")
    
    # 详细结果
    print("\n📋 详细结果:")
    for result in results:
        status = "✅" if result['correct'] else "❌"
        print(f"   {status} {result['sample_id']}: {result['candidate']}")
        print(f"       期望: {result['expected']}, 实际: {result['actual']}, 分数: {result['score']:.2f}")
    
    # 生成报告
    report = {
        'test_date': '2026-03-07',
        'samples_count': total_count,
        'correct_count': correct_count,
        'accuracy': accuracy,
        'results': results,
        'engine_version': engine.config.get('agent', {}).get('version', '1.0.0')
    }
    
    # 保存报告
    report_file = "calibration_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 测试报告已保存到: {report_file}")
    
    # 准确性评估
    if accuracy >= 0.85:
        print("\n🎉 校准成功! 准确率达到85%以上目标")
        return True
    elif accuracy >= 0.70:
        print(f"\n⚠️  校准部分成功，准确率{accuracy:.1%}，接近目标但需要微调")
        return False
    else:
        print(f"\n❌ 校准失败，准确率{accuracy:.1%}较低，需要重新校准")
        return False

if __name__ == "__main__":
    success = run_calibration_test()
    sys.exit(0 if success else 1)