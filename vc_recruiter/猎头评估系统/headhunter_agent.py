#!/usr/bin/env python3
"""
猎头智能Agent - 核心类
"""

import os
import json
import yaml
import glob
from datetime import datetime
from typing import List, Dict, Any
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HeadhunterAgent:
    """猎头智能Agent核心类"""
    
    def __init__(self, workspace_dir=None):
        """初始化Agent"""
        if workspace_dir is None:
            workspace_dir = "/root/.openclaw/workspace/vc_recruiter/猎头评估系统"
        
        self.workspace_dir = workspace_dir
        self.templates_dir = os.path.join(workspace_dir, "岗位模板")
        self.results_dir = os.path.join(workspace_dir, "评估结果")
        self.candidates_dir = os.path.join(workspace_dir, "候选人简历")
        
        # 创建必要目录
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.candidates_dir, exist_ok=True)
        
        # 加载模板
        self.templates = self._load_templates()
        
        logger.info(f"猎头Agent初始化完成，工作目录: {workspace_dir}")
        logger.info(f"加载模板数: {len(self.templates)}")
    
    def _load_templates(self) -> Dict[str, Dict]:
        """加载所有岗位模板"""
        templates = {}
        template_files = glob.glob(os.path.join(self.templates_dir, "*.yaml")) + \
                        glob.glob(os.path.join(self.templates_dir, "*.yml"))
        
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template = yaml.safe_load(f)
                    template_name = template.get('岗位名称', os.path.basename(template_file))
                    templates[template_name] = template
                    logger.debug(f"加载模板: {template_name}")
            except Exception as e:
                logger.error(f"加载模板失败 {template_file}: {e}")
        
        return templates
    
    def list_templates(self) -> List[str]:
        """列出所有可用模板"""
        return list(self.templates.keys())
    
    def create_position_template(self, base_template: str, new_name: str, adjustments: Dict) -> Dict:
        """基于现有模板创建新岗位模板"""
        if base_template not in self.templates:
            raise ValueError(f"基础模板不存在: {base_template}")
        
        base = self.templates[base_template].copy()
        
        # 应用调整
        for key, value in adjustments.items():
            if key in base:
                if isinstance(base[key], dict) and isinstance(value, dict):
                    base[key].update(value)
                else:
                    base[key] = value
            else:
                base[key] = value
        
        # 更新名称
        base['岗位名称'] = new_name
        base['创建时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        base['基于模板'] = base_template
        
        # 保存新模板
        template_file = os.path.join(self.templates_dir, f"{new_name}.yaml")
        with open(template_file, 'w', encoding='utf-8') as f:
            yaml.dump(base, f, allow_unicode=True, default_flow_style=False)
        
        # 重新加载模板
        self.templates[new_name] = base
        
        logger.info(f"创建新模板: {new_name} (基于: {base_template})")
        return base
    
    def evaluate_candidate(self, candidate_info: Dict, template_name: str) -> Dict:
        """评估单个候选人"""
        if template_name not in self.templates:
            raise ValueError(f"模板不存在: {template_name}")
        
        template = self.templates[template_name]
        
        # 评估逻辑
        evaluation = {
            '候选人信息': candidate_info,
            '岗位模板': template_name,
            '评估时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '匹配分数': 0,
            '评估结果': '待评估',
            '详细评估': {},
            '建议': {}
        }
        
        # 硬性要求检查
        hard_requirements = self._check_hard_requirements(candidate_info, template)
        
        if hard_requirements.get('否决'):
            evaluation['评估结果'] = '不通过'
            evaluation['否决原因'] = hard_requirements['原因']
            evaluation['匹配分数'] = 0
        else:
            # 计算匹配分数
            score = self._calculate_match_score(candidate_info, template)
            evaluation['匹配分数'] = score
            evaluation['详细评估'] = self._get_detailed_evaluation(candidate_info, template)
            
            if score >= 80:
                evaluation['评估结果'] = '强烈推荐'
            elif score >= 70:
                evaluation['评估结果'] = '推荐'
            elif score >= 50:
                evaluation['评估结果'] = '可考虑'
            else:
                evaluation['评估结果'] = '不推荐'
        
        # 生成建议
        evaluation['建议'] = self._generate_recommendations(evaluation)
        
        return evaluation
    
    def _check_hard_requirements(self, candidate: Dict, template: Dict) -> Dict:
        """检查硬性要求"""
        result = {'通过': True, '否决': False, '原因': []}
        
        # 检查模板中的否决标准
        if '否决标准' in template:
            for requirement in template['否决标准']:
                # 这里需要根据具体否决标准实现检查逻辑
                # 例如：检查学历、经验等
                pass
        
        # 常见硬性要求检查
        # 1. 学历检查
        education = candidate.get('教育', '')
        if not education:
            result['原因'].append('学历信息缺失')
        
        # 2. 经验检查
        experience = candidate.get('工作经验', '')
        if not experience:
            result['原因'].append('工作经验信息缺失')
        
        if result['原因']:
            result['通过'] = False
            result['否决'] = True
        
        return result
    
    def _calculate_match_score(self, candidate: Dict, template: Dict) -> int:
        """计算匹配分数"""
        score = 0
        
        # 学历分数
        education = candidate.get('教育', '')
        if education:
            if '清华' in education or '北大' in education:
                score += 20
            elif '985' in education or '211' in education:
                score += 15
            elif '硕士' in education or '博士' in education:
                score += 10
        
        # 经验分数
        experience = candidate.get('工作经验', '')
        if experience:
            if '5年' in experience or '6年' in experience or '7年' in experience:
                score += 20
            elif '8年' in experience or '9年' in experience or '10年' in experience:
                score += 25
            elif '3年' in experience or '4年' in experience:
                score += 15
        
        # 投资经验分数
        investment_exp = candidate.get('投资经验', '')
        if investment_exp:
            if '3年' in investment_exp or '4年' in investment_exp:
                score += 20
            elif '5年' in investment_exp or '6年' in investment_exp:
                score += 25
            elif '2年' in investment_exp:
                score += 15
        
        # 领域匹配分数
        domain = candidate.get('领域', '')
        target_domains = template.get('领域专注', '').split('/')
        if domain:
            for target in target_domains:
                if target.strip() in domain:
                    score += 15
                    break
        
        return min(score, 100)  # 不超过100分
    
    def _get_detailed_evaluation(self, candidate: Dict, template: Dict) -> Dict:
        """获取详细评估"""
        detailed = {}
        
        # 这里可以根据需要添加更详细的评估项
        detailed['教育评估'] = candidate.get('教育', '待评估')
        detailed['经验评估'] = candidate.get('工作经验', '待评估')
        detailed['投资经验评估'] = candidate.get('投资经验', '待评估')
        detailed['领域匹配评估'] = candidate.get('领域', '待评估')
        
        return detailed
    
    def _generate_recommendations(self, evaluation: Dict) -> Dict:
        """生成建议"""
        recommendations = {}
        
        score = evaluation['匹配分数']
        result = evaluation['评估结果']
        
        if result == '强烈推荐':
            recommendations['行动'] = '立即联系安排面试'
            recommendations['优先级'] = '最高'
            recommendations['备注'] = '优秀候选人，尽快锁定'
        elif result == '推荐':
            recommendations['行动'] = '本周内安排电话初筛'
            recommendations['优先级'] = '高'
            recommendations['备注'] = '符合要求，值得进一步了解'
        elif result == '可考虑':
            recommendations['行动'] = '可安排初步沟通'
            recommendations['优先级'] = '中'
            recommendations['备注'] = '基本符合，但有提升空间'
        else:
            recommendations['行动'] = '暂不推荐'
            recommendations['优先级'] = '低'
            recommendations['备注'] = '不符合当前岗位要求'
        
        return recommendations
    
    def batch_evaluate(self, candidates: List[Dict], template_name: str) -> Dict:
        """批量评估候选人"""
        logger.info(f"开始批量评估 {len(candidates)} 位候选人，岗位: {template_name}")
        
        evaluations = []
        
        for i, candidate in enumerate(candidates, 1):
            try:
                evaluation = self.evaluate_candidate(candidate, template_name)
                evaluations.append(evaluation)
                logger.debug(f"评估候选人 {i}: {evaluation['评估结果']} ({evaluation['匹配分数']}分)")
            except Exception as e:
                logger.error(f"评估候选人 {i} 失败: {e}")
        
        # 排序
        evaluations.sort(key=lambda x: x['匹配分数'], reverse=True)
        
        # 统计
        stats = {
            '总人数': len(evaluations),
            '强烈推荐': sum(1 for e in evaluations if e['评估结果'] == '强烈推荐'),
            '推荐': sum(1 for e in evaluations if e['评估结果'] == '推荐'),
            '可考虑': sum(1 for e in evaluations if e['评估结果'] == '可考虑'),
            '不推荐': sum(1 for e in evaluations if e['评估结果'] in ['不推荐', '不通过']),
            '平均分数': sum(e['匹配分数'] for e in evaluations) / len(evaluations) if evaluations else 0
        }
        
        result = {
            '评估时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '岗位模板': template_name,
            '总候选人': len(candidates),
            '成功评估': len(evaluations),
            '统计信息': stats,
            '详细评估': evaluations,
            '推荐名单': [e for e in evaluations if e['评估结果'] in ['强烈推荐', '推荐']]
        }
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = os.path.join(self.results_dir, f"批量评估_{template_name}_{timestamp}.json")
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"批量评估完成，结果已保存到: {result_file}")
        logger.info(f"统计: 强烈推荐{stats['强烈推荐']}人, 推荐{stats['推荐']}人, 可考虑{stats['可考虑']}人")
        
        return result
    
    def generate_report(self, evaluation_result: Dict) -> str:
        """生成评估报告"""
        report_lines = []
        
        # 标题
        report_lines.append("# 候选人评估报告")
        report_lines.append(f"## 岗位: {evaluation_result.get('岗位模板', '未知岗位')}")
        report_lines.append(f"## 评估时间: {evaluation_result.get('评估时间', '')}")
        report_lines.append("")
        
        # 统计信息
        stats = evaluation_result.get('统计信息', {})
        report_lines.append("## 📊 统计摘要")
        report_lines.append(f"- 总候选人: {stats.get('总人数', 0)}人")
        report_lines.append(f"- 强烈推荐: {stats.get('强烈推荐', 0)}人")
        report_lines.append(f"- 推荐: {stats.get('推荐', 0)}人")
        report_lines.append(f"- 可考虑: {stats.get('可考虑', 0)}人")
        report_lines.append(f"- 不推荐: {stats.get('不推荐', 0)}人")
        report_lines.append(f"- 平均匹配分: {stats.get('平均分数', 0):.1f}/100")
        report_lines.append("")
        
        # 推荐名单
        recommended = evaluation_result.get('推荐名单', [])
        if recommended:
            report_lines.append("## 🎯 推荐候选人名单")
            for i, candidate in enumerate(recommended, 1):
                cand_info = candidate.get('候选人信息', {})
                report_lines.append(f"### {i}. {cand_info.get('姓名', '未知')}")
                report_lines.append(f"- 匹配分数: {candidate.get('匹配分数', 0)}分")
                report_lines.append(f"- 评估结果: {candidate.get('评估结果', '未知')}")
                
                if '教育' in cand_info:
                    report_lines.append(f"- 教育背景: {cand_info['教育']}")
                if '工作经验' in cand_info:
                    report_lines.append(f"- 工作经验: {cand_info['工作经验']}")
                if '投资经验' in cand_info:
                    report_lines.append(f"- 投资经验: {cand_info['投资经验']}")
                
                suggestions = candidate.get('建议', {})
                if '行动' in suggestions:
                    report_lines.append(f"- 建议行动: {suggestions['行动']}")
                
                report_lines.append("")
        
        # 详细评估（前5位）
        evaluations = evaluation_result.get('详细评估', [])
        if len(evaluations) > 5:
            report_lines.append("## 🔍 详细评估（前5位）")
            for i, eval_item in enumerate(evaluations[:5], 1):
                cand_info = eval_item.get('候选人信息', {})
                report_lines.append(f"### 候选人{i}: {cand_info.get('姓名', '未知')}")
                report_lines.append(f"- 匹配分数: {eval_item.get('匹配分数', 0)}分")
                report_lines.append(f"- 评估结果: {eval_item.get('评估结果', '未知')}")
                report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("**报告生成**: 猎头智能Agent系统")
        report_lines.append("**备注**: 此报告基于自动化评估生成，建议人工复核重要决策")
        
        report = "\n".join(report_lines)
        
        # 保存报告文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.results_dir, f"评估报告_{timestamp}.md")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"报告已生成: {report_file}")
        return report

# 使用示例
if __name__ == "__main__":
    # 创建Agent实例
    agent = HeadhunterAgent()
    
    # 列出可用模板
    templates = agent.list_templates()
    print(f"可用模板: {templates}")
    
    # 示例候选人数据
    example_candidates = [
        {
            "姓名": "林先生",
            "教育": "清华大学硕士+本科（电气工程）",
            "工作经验": "工作5年以上",
            "投资经验": "一级投资3年",
            "领域": "新能源、半导体、AI"
        },
        {
            "姓名": "王女士",
            "教育": "北京大学硕士（金融学）",
            "工作经验": "工作3年",
            "投资经验": "投资经验1年",
            "领域": "消费金融"
        }
    ]
    
    if templates:
        # 批量评估
        template_name = templates[0]  # 使用第一个模板
        result = agent.batch_evaluate(example_candidates, template_name)
        
        # 生成报告
        report = agent.generate_report(result)
        print("\n生成的报告:")
        print("-" * 50)
        print(report[:500] + "..." if len(report) > 500 else report)