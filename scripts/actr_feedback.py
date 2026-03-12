#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACT-R 隐式反馈推断模块

从对话中推断用户对 AI 行为的反馈，用于更新产生式规则效用值
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List


class ImplicitFeedbackInferencer:
    """隐式反馈推断器"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.production_rules = self._load_production_rules()
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        import yaml
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 修复 YAML 中的正则表达式模式（YAML 把 | 当作特殊字符）
        # 直接在代码中 hardcode 正确的模式（注意：OR 符号两边不能有空格！）
        config["actr"]["implicit_feedback"]["positive_patterns"] = [
            {"pattern": r"好的 | 懂了 | 明白了 | 谢谢 | 牛逼 | 可以 | 行|OK|就这样", "weight": 0.1},
            {"pattern": r"继续 | 然后呢 | 再详细点 | 还有吗", "weight": 0.15},
            {"pattern": r"运行成功 | 搞定了 | 成了 | 没问题", "weight": 0.2},
        ]
        config["actr"]["implicit_feedback"]["negative_patterns"] = [
            {"pattern": r"不对 | 错了 | 不行 | 没用 | 不好 | 不是这个意思", "weight": -0.2},
            {"pattern": r"换个方案 | 重新来", "weight": -0.15},
            {"pattern": r"听不懂 | 太复杂 | 简单点", "weight": -0.1},
        ]
        config["actr"]["implicit_feedback"]["neutral_patterns"] = [
            {"pattern": r"哦 | 嗯 | 好的吧", "weight": 0.0},
        ]
        
        return config
    
    def _load_production_rules(self) -> Dict:
        """加载产生式规则"""
        rules_path = Path(__file__).parent.parent / "actr" / "procedural_memory" / "production_rules.json"
        if rules_path.exists():
            with open(rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认规则
        return {
            "productions": [
                {
                    "name": "回复风格选择",
                    "condition": "IF 用户=章伟伟 AND 场景=日常对话",
                    "action": "THEN 使用直接语气 AND 省略客套话",
                    "strength": 0.8,
                    "success_rate": 0.9,
                    "last_updated": datetime.now().isoformat(),
                    "last_verified": datetime.now().isoformat(),
                    "days_since_verify": 0
                },
                {
                    "name": "信息密度选择",
                    "condition": "IF 用户=章伟伟 AND 场景=技术讨论",
                    "action": "THEN 提供详细技术细节 AND 包含代码示例",
                    "strength": 0.8,
                    "success_rate": 0.85,
                    "last_updated": datetime.now().isoformat(),
                    "last_verified": datetime.now().isoformat(),
                    "days_since_verify": 0
                }
            ],
            "metadata": {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def infer_feedback(self, conversation: str, prediction: Dict = None) -> Dict[str, Any]:
        """
        从对话中推断隐式反馈
        
        Args:
            conversation: 对话文本
            prediction: AI 的预测信息（可选）
            
        Returns:
            反馈信息字典
        """
        feedback = {
            "type": "neutral",
            "strength": 0.0,
            "confidence": 0.5,
            "signals": [],
            "affected_rules": []
        }
        
        # 获取配置中的模式
        positive_patterns = self.config["actr"]["implicit_feedback"]["positive_patterns"]
        negative_patterns = self.config["actr"]["implicit_feedback"]["negative_patterns"]
        neutral_patterns = self.config["actr"]["implicit_feedback"]["neutral_patterns"]
        
        # 检测正面信号
        for pattern_config in positive_patterns:
            pattern = pattern_config["pattern"]
            weight = pattern_config["weight"]
            
            if re.search(pattern, conversation, re.IGNORECASE):
                feedback["signals"].append({
                    "type": "positive",
                    "pattern": pattern,
                    "weight": weight
                })
                feedback["strength"] += weight
        
        # 检测负面信号
        for pattern_config in negative_patterns:
            pattern = pattern_config["pattern"]
            weight = pattern_config["weight"]  # 注意：weight 本身是负数
            
            if re.search(pattern, conversation, re.IGNORECASE):
                feedback["signals"].append({
                    "type": "negative",
                    "pattern": pattern,
                    "weight": weight
                })
                feedback["strength"] += weight
        
        # 检测中性信号
        for pattern_config in neutral_patterns:
            pattern = pattern_config["pattern"]
            weight = pattern_config["weight"]
            
            if re.search(pattern, conversation, re.IGNORECASE):
                feedback["signals"].append({
                    "type": "neutral",
                    "pattern": pattern,
                    "weight": weight
                })
        
        # 确定反馈类型
        if feedback["strength"] > 0.05:
            feedback["type"] = "positive"
        elif feedback["strength"] < -0.05:
            feedback["type"] = "negative"
        else:
            feedback["type"] = "neutral"
        
        # 计算置信度（基于信号数量）
        signal_count = len(feedback["signals"])
        feedback["confidence"] = min(0.5 + signal_count * 0.1, 0.95)
        
        # 确定受影响的规则
        feedback["affected_rules"] = self._identify_affected_rules(conversation, prediction)
        
        return feedback
    
    def _identify_affected_rules(self, conversation: str, prediction: Dict = None) -> List[str]:
        """识别受影响的产生式规则"""
        affected = []
        
        # 基于对话内容判断
        if any(word in conversation for word in ["代码", "方案", "方法", "怎么"]):
            affected.append("回复风格选择")
        
        if any(word in conversation for word in ["详细", "简单", "复杂", "解释"]):
            affected.append("信息密度选择")
        
        # 如果有预测信息，对比预测与实际
        if prediction:
            predicted_action = prediction.get("action", "")
            if "直接" in predicted_action and ("详细" in conversation or "解释" in conversation):
                # 预测直接，但用户要求详细 → 规则需要调整
                affected.append("回复风格选择")
        
        return affected
    
    def update_production_rules(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据反馈更新产生式规则
        
        Args:
            feedback: 反馈信息
            
        Returns:
            更新摘要
        """
        update_summary = {
            "updated_rules": [],
            "timestamp": datetime.now().isoformat()
        }
        
        learning_rate = self.config["actr"]["utility_learning"]["learning_rate"]
        
        for rule in self.production_rules["productions"]:
            if rule["name"] not in feedback.get("affected_rules", []):
                continue
            
            # 更新规则强度
            old_strength = rule["strength"]
            adjustment = feedback["strength"] * learning_rate * feedback["confidence"]
            new_strength = old_strength + adjustment
            
            # 限制在合理范围内
            max_strength = self.config["actr"]["procedural_memory"]["max_strength"]
            min_strength = self.config["actr"]["procedural_memory"]["min_strength"]
            new_strength = max(min_strength, min(max_strength, new_strength))
            
            rule["strength"] = new_strength
            rule["last_updated"] = datetime.now().isoformat()
            
            # 如果是正面反馈，更新 last_verified
            if feedback["type"] == "positive":
                rule["last_verified"] = datetime.now().isoformat()
                rule["days_since_verify"] = 0
                rule["success_rate"] = min(1.0, rule["success_rate"] + 0.02)
            elif feedback["type"] == "negative":
                rule["success_rate"] = max(0.0, rule["success_rate"] - 0.05)
            
            update_summary["updated_rules"].append({
                "name": rule["name"],
                "old_strength": round(old_strength, 3),
                "new_strength": round(new_strength, 3),
                "change": round(adjustment, 3)
            })
        
        # 更新元数据
        self.production_rules["metadata"]["last_updated"] = datetime.now().isoformat()
        
        return update_summary
    
    def apply_decay(self) -> Dict[str, Any]:
        """
        应用置信度衰减
        
        Returns:
            衰减摘要
        """
        decay_rate = self.config["actr"]["decay"]["daily_rate"]
        today = datetime.now()
        
        decay_summary = {
            "decayed_rules": [],
            "timestamp": today.isoformat()
        }
        
        for rule in self.production_rules["productions"]:
            # 计算距离上次验证的天数
            last_verified = datetime.fromisoformat(rule["last_verified"])
            days_since = (today - last_verified).days
            rule["days_since_verify"] = days_since
            
            # 应用衰减
            if days_since > 0:
                old_strength = rule["strength"]
                decay_factor = (1 - decay_rate) ** days_since
                new_strength = old_strength * decay_factor
                
                min_confidence = self.config["actr"]["decay"]["min_confidence"]
                new_strength = max(min_confidence, new_strength)
                
                if abs(new_strength - old_strength) > 0.001:
                    rule["strength"] = new_strength
                    decay_summary["decayed_rules"].append({
                        "name": rule["name"],
                        "days_since_verify": days_since,
                        "old_strength": round(old_strength, 3),
                        "new_strength": round(new_strength, 3),
                        "decay": round(new_strength - old_strength, 3)
                    })
        
        return decay_summary
    
    def check_verification_needed(self) -> List[Dict[str, Any]]:
        """
        检查哪些规则需要主动验证
        
        Returns:
            需要验证的规则列表
        """
        verify_threshold = self.config["actr"]["decay"]["verify_threshold"]
        max_frequency = self.config["actr"]["active_verification"]["max_frequency_days"]
        
        needs_verification = []
        today = datetime.now()
        
        for rule in self.production_rules["productions"]:
            last_verified = datetime.fromisoformat(rule["last_verified"])
            days_since = (today - last_verified).days
            
            # 检查是否需要验证
            should_verify = False
            reason = ""
            
            if rule["strength"] < verify_threshold:
                should_verify = True
                reason = f"置信度低 ({rule['strength']:.2f} < {verify_threshold})"
            elif days_since > max_frequency:
                should_verify = True
                reason = f"超过{max_frequency}天未验证"
            
            if should_verify:
                needs_verification.append({
                    "name": rule["name"],
                    "strength": rule["strength"],
                    "days_since_verify": days_since,
                    "reason": reason,
                    "suggested_question": self._generate_verification_question(rule)
                })
        
        return needs_verification
    
    def _generate_verification_question(self, rule: Dict) -> str:
        """生成主动验证问题"""
        # 从规则中提取关键信息
        action = rule.get("action", "")
        
        # 简化问题
        if "直接" in action:
            return "你更喜欢我直接给方案，还是先分析再给方案？"
        elif "详细" in action:
            return "你更喜欢详细说明，还是简洁回答？"
        else:
            return "我的回复风格符合你的偏好吗？"
    
    def save_production_rules(self):
        """保存产生式规则"""
        rules_path = Path(__file__).parent.parent / "actr" / "procedural_memory" / "production_rules.json"
        with open(rules_path, 'w', encoding='utf-8') as f:
            json.dump(self.production_rules, f, ensure_ascii=False, indent=2)
        return rules_path


def main():
    """主函数"""
    import sys
    
    inferencer = ImplicitFeedbackInferencer()
    
    # 从参数或 stdin 读取对话
    if len(sys.argv) > 1:
        conversation = " ".join(sys.argv[1:])
    else:
        conversation = sys.stdin.read()
    
    if not conversation.strip():
        print("错误：请提供对话文本")
        sys.exit(1)
    
    # 推断反馈
    feedback = inferencer.infer_feedback(conversation)
    
    # 输出结果
    print("隐式反馈推断结果:")
    print(json.dumps(feedback, ensure_ascii=False, indent=2))
    
    # 更新规则
    if feedback["affected_rules"]:
        update_summary = inferencer.update_production_rules(feedback)
        print("\n产生式规则更新:")
        print(json.dumps(update_summary, ensure_ascii=False, indent=2))
        
        # 保存
        rules_file = inferencer.save_production_rules()
        print(f"\n规则已保存到：{rules_file}", file=sys.stderr)
    
    # 应用衰减
    decay_summary = inferencer.apply_decay()
    if decay_summary["decayed_rules"]:
        print("\n置信度衰减:")
        print(json.dumps(decay_summary, ensure_ascii=False, indent=2))
    
    # 检查主动验证
    needs_verify = inferencer.check_verification_needed()
    if needs_verify:
        print("\n需要主动验证的规则:")
        print(json.dumps(needs_verify, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
