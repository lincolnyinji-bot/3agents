#!/usr/bin/env python3
"""
👔 管家Agent - 工作流协调与状态管理

功能：
1. 协调小蜜蜂Agent和裁判Agent的工作流
2. 管理候选人状态流转
3. 定时任务调度
4. 报告生成和通知

作者：OpenClaw助手
创建时间：2026-03-07
"""

import json
import logging
import time
from datetime import datetime, date, timedelta

# 尝试导入schedule，如果没有则使用模拟
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("⚠️  schedule模块未安装，定时任务功能受限")
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import threading
import hashlib
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ButlerAgent")

# ==================== 数据模型 ====================

class CandidateStatus(Enum):
    """候选人状态枚举"""
    DISCOVERED = "discovered"        # 发现
    SCREENED = "screened"            # 初筛通过
    EVALUATED = "evaluated"          # 评估完成
    RECOMMENDED = "recommended"      # 推荐待审
    REVIEWED = "reviewed"            # 用户审核
    CONTACTING = "contacting"        # 联系中
    INTERVIEWING = "interviewing"    # 面试安排
    HIRING = "hiring"                # 录用流程
    REJECTED = "rejected"            # 已拒绝

class ClientType(Enum):
    """客户类型"""
    STRICT = "strict"    # 苛刻客户
    LOOSE = "loose"      # 宽松客户

class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 执行中
    SUCCESS = "success"      # 成功
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 取消

@dataclass
class StatusChange:
    """状态变更记录"""
    from_status: CandidateStatus
    to_status: CandidateStatus
    timestamp: datetime
    reason: str = ""          # 变更原因
    changed_by: str = "system"  # 变更者（system/user）
    notes: str = ""           # 备注

@dataclass
class CandidateRecord:
    """候选人记录"""
    candidate_id: str
    candidate_data: Dict[str, Any]  # 候选人原始数据
    jd_text: str                    # 对应的JD
    client_type: ClientType         # 客户类型
    current_status: CandidateStatus # 当前状态
    status_history: List[StatusChange] = field(default_factory=list)  # 状态历史
    evaluation_result: Optional[Dict] = None  # 评估结果
    discovery_time: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)  # 标签
    
    def to_dict(self):
        """转换为字典"""
        data = asdict(self)
        # 特殊处理枚举类型
        data["current_status"] = self.current_status.value
        data["client_type"] = self.client_type.value
        data["status_history"] = [{
            "from_status": h.from_status.value,
            "to_status": h.to_status.value,
            "timestamp": h.timestamp.isoformat(),
            "reason": h.reason,
            "changed_by": h.changed_by,
            "notes": h.notes
        } for h in self.status_history]
        return data
    
    def update_status(self, new_status: CandidateStatus, reason: str = "", changed_by: str = "system", notes: str = ""):
        """更新状态"""
        change = StatusChange(
            from_status=self.current_status,
            to_status=new_status,
            timestamp=datetime.now(),
            reason=reason,
            changed_by=changed_by,
            notes=notes
        )
        self.status_history.append(change)
        self.current_status = new_status
        self.last_updated = datetime.now()

@dataclass
class WorkflowExecution:
    """工作流执行记录"""
    execution_id: str
    jd_text: str
    client_type: ClientType
    start_time: datetime
    end_time: Optional[datetime] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    candidates_processed: int = 0
    candidates_passed: int = 0
    error_message: Optional[str] = None
    result: Optional[Dict] = None
    
    def to_dict(self):
        """转换为字典"""
        data = asdict(self)
        data["client_type"] = self.client_type.value
        data["status"] = self.status.value
        data["start_time"] = self.start_time.isoformat()
        if self.end_time:
            data["end_time"] = self.end_time.isoformat()
        return data

@dataclass
class DailyReport:
    """每日报告"""
    date: date
    jds_processed: List[str]
    summary: Dict[str, int]
    recommendations: List[Dict]
    insights: List[str]
    next_actions: List[str]
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        """转换为字典"""
        data = asdict(self)
        data["date"] = self.date.isoformat()
        data["generated_at"] = self.generated_at.isoformat()
        return data

# ==================== 状态管理器 ====================

class StatusManager:
    """状态管理器"""
    
    def __init__(self, data_file="candidate_status.json"):
        self.data_file = data_file
        self.candidates: Dict[str, CandidateRecord] = {}  # candidate_id -> CandidateRecord
        self.workflow_history: List[WorkflowExecution] = []
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 加载候选人记录
                for cand_data in data.get("candidates", []):
                    # 转换枚举类型
                    cand_data["current_status"] = CandidateStatus(cand_data["current_status"])
                    cand_data["client_type"] = ClientType(cand_data["client_type"])
                    
                    # 转换状态历史
                    status_history = []
                    for hist in cand_data.get("status_history", []):
                        status_history.append(StatusChange(
                            from_status=CandidateStatus(hist["from_status"]),
                            to_status=CandidateStatus(hist["to_status"]),
                            timestamp=datetime.fromisoformat(hist["timestamp"]),
                            reason=hist.get("reason", ""),
                            changed_by=hist.get("changed_by", "system"),
                            notes=hist.get("notes", "")
                        ))
                    cand_data["status_history"] = status_history
                    
                    candidate = CandidateRecord(**cand_data)
                    self.candidates[candidate.candidate_id] = candidate
                
                logger.info(f"加载了{len(self.candidates)}个候选人记录")
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            self.candidates = {}
    
    def _save_data(self):
        """保存数据"""
        try:
            data = {
                "candidates": [cand.to_dict() for cand in self.candidates.values()],
                "last_saved": datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
    
    def add_candidate(self, candidate_data: Dict, jd_text: str, client_type: ClientType) -> CandidateRecord:
        """添加新候选人"""
        candidate_id = hashlib.md5(
            f"{candidate_data.get('id', '')}{jd_text}".encode()
        ).hexdigest()[:16]
        
        if candidate_id in self.candidates:
            logger.info(f"候选人已存在: {candidate_id}")
            return self.candidates[candidate_id]
        
        candidate = CandidateRecord(
            candidate_id=candidate_id,
            candidate_data=candidate_data,
            jd_text=jd_text,
            client_type=client_type,
            current_status=CandidateStatus.DISCOVERED,
            discovery_time=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.candidates[candidate_id] = candidate
        self._save_data()
        logger.info(f"添加新候选人: {candidate_id}")
        return candidate
    
    def update_candidate_status(self, candidate_id: str, new_status: CandidateStatus, 
                              reason: str = "", changed_by: str = "system", notes: str = "") -> bool:
        """更新候选人状态"""
        if candidate_id not in self.candidates:
            logger.error(f"候选人不存在: {candidate_id}")
            return False
        
        candidate = self.candidates[candidate_id]
        candidate.update_status(new_status, reason, changed_by, notes)
        self._save_data()
        logger.info(f"更新候选人状态: {candidate_id} -> {new_status.value}")
        return True
    
    def get_candidate(self, candidate_id: str) -> Optional[CandidateRecord]:
        """获取候选人"""
        return self.candidates.get(candidate_id)
    
    def get_candidates_by_status(self, status: CandidateStatus) -> List[CandidateRecord]:
        """按状态获取候选人"""
        return [cand for cand in self.candidates.values() if cand.current_status == status]
    
    def get_pipeline_report(self) -> Dict:
        """获取管道报告"""
        status_counts = {}
        for status in CandidateStatus:
            status_counts[status.value] = len(self.get_candidates_by_status(status))
        
        return {
            "total_candidates": len(self.candidates),
            "status_counts": status_counts,
            "today_discovered": len([
                cand for cand in self.candidates.values()
                if cand.discovery_time.date() == date.today()
            ])
        }
    
    def record_workflow_execution(self, execution: WorkflowExecution):
        """记录工作流执行"""
        self.workflow_history.append(execution)
        # 保留最近100条记录
        if len(self.workflow_history) > 100:
            self.workflow_history = self.workflow_history[-100:]

# ==================== 工作流协调器 ====================

class WorkflowCoordinator:
    """工作流协调器"""
    
    def __init__(self, scout_agent=None, judge_agent=None, status_manager=None):
        """
        初始化协调器
        
        Args:
            scout_agent: 小蜜蜂Agent实例（模拟或真实）
            judge_agent: 裁判Agent实例（模拟或真实）
            status_manager: 状态管理器实例
        """
        self.scout_agent = scout_agent
        self.judge_agent = judge_agent
        self.status_manager = status_manager or StatusManager()
        
        # 模拟Agent（如果未提供）
        if not self.scout_agent:
            self.scout_agent = MockScoutAgent()
        if not self.judge_agent:
            self.judge_agent = MockJudgeAgent()
        
        logger.info("工作流协调器初始化完成")
    
    def process_jd(self, jd_text: str, client_type: ClientType) -> Dict:
        """
        处理单个JD的完整工作流
        
        Returns:
            处理结果
        """
        execution_id = hashlib.md5(f"{jd_text}{datetime.now()}".encode()).hexdigest()[:16]
        execution = WorkflowExecution(
            execution_id=execution_id,
            jd_text=jd_text,
            client_type=client_type,
            start_time=datetime.now(),
            status=WorkflowStatus.RUNNING
        )
        
        try:
            logger.info(f"开始处理JD工作流: {jd_text[:50]}...")
            
            # 1. 小蜜蜂发现候选人
            logger.info("调用小蜜蜂Agent发现候选人...")
            scout_result = self.scout_agent.process_jd(
                jd_text, 
                "strict" if client_type == ClientType.STRICT else "loose"
            )
            
            if not scout_result.get("success", False):
                raise Exception(f"小蜜蜂发现失败: {scout_result.get('error', '未知错误')}")
            
            # 2. 添加到状态管理
            candidates_added = []
            for candidate_data in scout_result.get("passed_list", []):
                candidate = self.status_manager.add_candidate(
                    candidate_data["candidate"],
                    jd_text,
                    client_type
                )
                candidates_added.append(candidate)
                
                # 更新状态为初筛通过
                self.status_manager.update_candidate_status(
                    candidate.candidate_id,
                    CandidateStatus.SCREENED,
                    reason=candidate_data["decision"]["reason"]
                )
            
            execution.candidates_processed = scout_result.get("total_candidates", 0)
            execution.candidates_passed = len(candidates_added)
            
            # 3. 裁判评估候选人
            logger.info(f"调用裁判Agent评估{len(candidates_added)}个候选人...")
            evaluated_candidates = []
            
            for candidate in candidates_added:
                # 裁判评估
                evaluation_result = self.judge_agent.evaluate(candidate.candidate_data)
                
                # 记录评估结果
                candidate.evaluation_result = evaluation_result
                
                # 更新状态
                self.status_manager.update_candidate_status(
                    candidate.candidate_id,
                    CandidateStatus.EVALUATED,
                    reason=f"评估完成，评分: {evaluation_result.get('score', 0)}"
                )
                
                evaluated_candidates.append({
                    "candidate": candidate,
                    "evaluation": evaluation_result
                })
            
            # 4. 生成推荐（评分>=75的）
            recommended = []
            for item in evaluated_candidates:
                score = item["evaluation"].get("score", 0)
                if score >= 75:  # 推荐阈值
                    candidate = item["candidate"]
                    self.status_manager.update_candidate_status(
                        candidate.candidate_id,
                        CandidateStatus.RECOMMENDED,
                        reason=f"评分{score}达到推荐标准"
                    )
                    recommended.append(item)
            
            # 5. 生成总结
            execution.status = WorkflowStatus.SUCCESS
            execution.end_time = datetime.now()
            execution.result = {
                "jd_processed": jd_text,
                "client_type": client_type.value,
                "candidates_discovered": execution.candidates_processed,
                "candidates_screened": len(candidates_added),
                "candidates_evaluated": len(evaluated_candidates),
                "candidates_recommended": len(recommended),
                "recommendations": [
                    {
                        "candidate_id": item["candidate"].candidate_id,
                        "candidate_name": item["candidate"].candidate_data.get("name", "未知"),
                        "score": item["evaluation"].get("score", 0),
                        "summary": item["evaluation"].get("summary", "")
                    }
                    for item in recommended
                ]
            }
            
            logger.info(f"JD工作流完成: 发现{execution.candidates_processed}个，推荐{len(recommended)}个")
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}", exc_info=True)
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.now()
            execution.error_message = str(e)
        
        # 记录执行历史
        self.status_manager.record_workflow_execution(execution)
        
        return execution.result if execution.result else {
            "success": False,
            "error": execution.error_message
        }
    
    def get_recommendations(self, limit: int = 10) -> List[Dict]:
        """获取推荐候选人列表"""
        recommended = self.status_manager.get_candidates_by_status(CandidateStatus.RECOMMENDED)
        recommendations = []
        
        for candidate in recommended[:limit]:
            recommendations.append({
                "candidate_id": candidate.candidate_id,
                "name": candidate.candidate_data.get("name", "未知"),
                "current_position": candidate.candidate_data.get("current_position", ""),
                "current_company": candidate.candidate_data.get("current_company", ""),
                "education": candidate.candidate_data.get("education", ""),
                "score": candidate.evaluation_result.get("score", 0) if candidate.evaluation_result else 0,
                "summary": candidate.evaluation_result.get("summary", "") if candidate.evaluation_result else "",
                "status_history": [
                    {
                        "status": h.to_status.value,
                        "timestamp": h.timestamp.isoformat(),
                        "reason": h.reason
                    }
                    for h in candidate.status_history[-3:]  # 最近3次状态变更
                ]
            })
        
        return recommendations

# ==================== 模拟Agent（开发测试用） ====================

class MockScoutAgent:
    """模拟小蜜蜂Agent"""
    
    def process_jd(self, jd_text: str, screening_type: str) -> Dict:
        """模拟处理JD"""
        logger.info(f"模拟小蜜蜂处理JD: {jd_text[:30]}...")
        time.sleep(0.5)  # 模拟处理时间
        
        # 生成模拟数据
        mock_candidates = []
        for i in range(3):  # 模拟3个候选人
            mock_candidates.append({
                "candidate": {
                    "id": f"mock_candidate_{i}",
                    "name": f"模拟候选人{i+1}",
                    "current_position": "投资经理",
                    "current_company": "模拟投资机构",
                    "education": "清华大学硕士",
                    "experience": "5年投资经验",
                    "location": "深圳"
                },
                "decision": {
                    "result": "pass",
                    "reason": "符合初筛规则"
                }
            })
        
        return {
            "success": True,
            "total_candidates": 10,
            "passed_candidates": 3,
            "passed_list": mock_candidates
        }

class MockJudgeAgent:
    """模拟裁判Agent"""
    
    def evaluate(self, candidate_data: Dict) -> Dict:
        """模拟评估候选人"""
        logger.info(f"模拟裁判评估候选人: {candidate_data.get('name', '未知')}")
        time.sleep(0.2)  # 模拟评估时间
        
        # 生成随机评分（60-95）
        import random
        score = random.randint(60, 95)
        
        return {
            "success": True,
            "candidate_id": candidate_data.get("id", ""),
            "candidate_name": candidate_data.get("name", ""),
            "score": score,
            "summary": f"候选人评估完成，评分{score}",
            "strengths": ["教育背景优秀", "相关经验丰富"],
            "weaknesses": ["领域经验稍弱"],
            "recommendation": "推荐" if score >= 75 else "待考虑"
        }

# ==================== 报告生成器 ====================

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, status_manager: StatusManager):
        self.status_manager = status_manager
    
    def generate_daily_report(self) -> DailyReport:
        """生成每日报告"""
        logger.info("生成每日报告...")
        
        # 获取今日数据
        today = date.today()
        today_candidates = [
            cand for cand in self.status_manager.candidates.values()
            if cand.discovery_time.date() == today
        ]
        
        # 统计
        summary = {
            "total_discovered": len(today_candidates),
            "screened": len([c for c in today_candidates if c.current_status.value >= CandidateStatus.SCREENED.value]),
            "evaluated": len([c for c in today_candidates if c.current_status.value >= CandidateStatus.EVALUATED.value]),
            "recommended": len([c for c in today_candidates if c.current_status == CandidateStatus.RECOMMENDED]),
            "reviewed": len([c for c in today_candidates if c.current_status == CandidateStatus.REVIEWED])
        }
        
        # 获取推荐候选人
        recommendations = []
        for candidate in today_candidates:
            if candidate.current_status == CandidateStatus.RECOMMENDED:
                recommendations.append({
                    "candidate_id": candidate.candidate_id,
                    "name": candidate.candidate_data.get("name", "未知"),
                    "position": candidate.candidate_data.get("current_position", ""),
                    "company": candidate.candidate_data.get("current_company", ""),
                    "score": candidate.evaluation_result.get("score", 0) if candidate.evaluation_result else 0,
                    "jd_summary": candidate.jd_text[:50] + "..."
                })
        
        # 生成洞察
        insights = []
        if summary["total_discovered"] > 0:
            conversion_rate = summary["recommended"] / summary["total_discovered"] * 100
            insights.append(f"今日转化率: {conversion_rate:.1f}%")
        
        if summary["recommended"] > 0:
            insights.append(f"发现{summary['recommended']}个高质量候选人，建议尽快审核")
        
        # 下一步行动
        next_actions = []
        if summary["recommended"] > 0:
            next_actions.append(f"审核{summary['recommended']}个推荐候选人")
        next_actions.append("继续监控候选人发现进度")
        
        # 处理过的JD（去重）
        jds_processed = list(set([c.jd_text[:50] + "..." for c in today_candidates]))
        
        report = DailyReport(
            date=today,
            jds_processed=jds_processed,
            summary=summary,
            recommendations=recommendations[:5],  # 最多5个推荐
            insights=insights,
            next_actions=next_actions
        )
        
        return report

# ==================== 任务调度器 ====================

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, workflow_coordinator: WorkflowCoordinator, report_generator: ReportGenerator):
        self.workflow = workflow_coordinator
        self.reporter = report_generator
        self.scheduler_thread = None
        self.running = False
        
        # 测试用JD（实际应该从配置文件或数据库读取）
        self.test_jds = [
            "松禾资本-人工智能投资经理-深圳",
            "千乘资本-航空航天投资-上海",
            "明荟致远-硬科技投资总监"
        ]
    
    def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已经在运行")
            return
        
        self.running = True
        
        if SCHEDULE_AVAILABLE:
            # 设置定时任务
            schedule.every().day.at("09:00").do(self.run_strict_screening)
            schedule.every().day.at("20:00").do(self.run_loose_screening)
            schedule.every().day.at("22:00").do(self.generate_daily_report)
            
            # 启动调度线程
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            
            logger.info("任务调度器启动（使用schedule模块）")
        else:
            logger.warning("schedule模块未安装，定时任务功能受限")
            # 可以在这里实现简单的定时逻辑，或者只支持手动触发
        
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("任务调度器停止")
    
    def _scheduler_loop(self):
        """调度器循环"""
        if not SCHEDULE_AVAILABLE:
            logger.warning("schedule模块未安装，跳过定时任务循环")
            return
            
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def run_strict_screening(self):
        """执行严格快筛"""
        logger.info("执行严格快筛任务...")
        try:
            for jd in self.test_jds[:2]:  # 前两个JD（苛刻客户）
                result = self.workflow.process_jd(jd, ClientType.STRICT)
                logger.info(f"严格快筛完成: {jd} -> 推荐{result.get('candidates_recommended', 0)}个")
        except Exception as e:
            logger.error(f"严格快筛失败: {e}")
    
    def run_loose_screening(self):
        """执行宽松快筛"""
        logger.info("执行宽松快筛任务...")
        try:
            for jd in self.test_jds[2:]:  # 第三个JD（宽松客户）
                result = self.workflow.process_jd(jd, ClientType.LOOSE)
                logger.info(f"宽松快筛完成: {jd} -> 推荐{result.get('candidates_recommended', 0)}个")
        except Exception as e:
            logger.error(f"宽松快筛失败: {e}")
    
    def generate_daily_report(self):
        """生成每日报告"""
        logger.info("生成每日报告...")
        try:
            report = self.reporter.generate_daily_report()
            logger.info(f"日报生成完成: 发现{report.summary['total_discovered']}个，推荐{report.summary['recommended']}个")
            
            # 这里可以发送报告到飞书/邮箱等
            # self.send_report_to_feishu(report)
            
        except Exception as e:
            logger.error(f"生成日报失败: {e}")

# ==================== 主Agent类 ====================

class ButlerAgent:
    """管家Agent主类"""
    
    def __init__(self, scout_agent=None, judge_agent=None):
        """
        初始化管家Agent
        
        Args:
            scout_agent: 小蜜蜂Agent实例
            judge_agent: 裁判Agent实例
        """
        logger.info("初始化管家Agent...")
        
        # 初始化各模块
        self.status_manager = StatusManager()
        self.workflow_coordinator = WorkflowCoordinator(
            scout_agent=scout_agent,
            judge_agent=judge_agent,
            status_manager=self.status_manager
        )
        self.report_generator = ReportGenerator(self.status_manager)
        self.task_scheduler = TaskScheduler(self.workflow_coordinator, self.report_generator)
        
        # 运行状态
        self.is_running = False
        
        logger.info("管家Agent初始化完成")
    
    def start(self):
        """启动管家Agent"""
        if self.is_running:
            logger.warning("管家Agent已经在运行")
            return
        
        self.task_scheduler.start()
        self.is_running = True
        logger.info("管家Agent启动")
    
    def stop(self):
        """停止管家Agent"""
        if not self.is_running:
            logger.warning("管家Agent未在运行")
            return
        
        self.task_scheduler.stop()
        self.is_running = False
        logger.info("管家Agent停止")
    
    def process_jd_manual(self, jd_text: str, client_type: ClientType) -> Dict:
        """手动处理JD（立即执行）"""
        return self.workflow_coordinator.process_jd(jd_text, client_type)
    
    def get_recommendations(self, limit: int = 10) -> List[Dict]:
        """获取推荐候选人"""
        return self.workflow_coordinator.get_recommendations(limit)
    
    def get_pipeline_status(self) -> Dict:
        """获取管道状态"""
        return self.status_manager.get_pipeline_report()
    
    def get_daily_report(self) -> Dict:
        """获取今日报告"""
        report = self.report_generator.generate_daily_report()
        return report.to_dict()

# ==================== 使用示例 ====================

def main():
    """主函数 - 测试管家Agent"""
    print("👔 测试管家Agent...")
    print("=" * 60)
    
    # 初始化管家Agent
    agent = ButlerAgent()
    
    # 测试手动处理JD
    print("\n1. 🔄 测试手动处理JD...")
    test_jd = "松禾资本-人工智能投资经理-深圳"
    result = agent.process_jd_manual(test_jd, ClientType.STRICT)
    
    print(f"   处理结果:")
    print(f"   发现候选人: {result.get('candidates_discovered', 0)}")
    print(f"   初筛通过: {result.get('candidates_screened', 0)}")
    print(f"   评估完成: {result.get('candidates_evaluated', 0)}")
    print(f"   推荐候选人: {result.get('candidates_recommended', 0)}")
    
    if result.get('candidates_recommended', 0) > 0:
        print(f"\n   📋 推荐列表:")
        for rec in result['recommendations']:
            print(f"   - {rec['candidate_name']} (评分: {rec['score']})")
    
    # 获取推荐候选人
    print("\n2. 📊 获取推荐候选人...")
    recommendations = agent.get_recommendations()
    print(f"   总推荐数: {len(recommendations)}")
    
    if recommendations:
        print(f"\n   最新推荐:")
        for rec in recommendations[:3]:
            print(f"   - {rec['name']} ({rec['current_position']})")
            print(f"     评分: {rec['score']}")
    
    # 获取管道状态
    print("\n3. 📈 获取管道状态...")
    pipeline = agent.get_pipeline_status()
    print(f"   总候选人: {pipeline['total_candidates']}")
    print(f"   今日发现: {pipeline['today_discovered']}")
    print(f"   状态分布:")
    for status, count in pipeline['status_counts'].items():
        if count > 0:
            print(f"     {status}: {count}")
    
    # 生成日报
    print("\n4. 📋 生成日报...")
    daily_report = agent.get_daily_report()
    print(f"   日报日期: {daily_report['date']}")
    print(f"   发现总数: {daily_report['summary']['total_discovered']}")
    print(f"   推荐数量: {daily_report['summary']['recommended']}")
    
    if daily_report['recommendations']:
        print(f"\n   推荐候选人:")
        for rec in daily_report['recommendations'][:3]:
            print(f"   - {rec['name']} ({rec['position']})")
    
    print("\n" + "=" * 60)
    print("🎉 管家Agent测试完成!")
    print("\n💡 下一步:")
    print("1. 提供真实Agent集成（小蜜蜂+裁判）")
    print("2. 配置定时任务和通知")
    print("3. 连接飞书/邮箱等通知渠道")

if __name__ == "__main__":
    main()