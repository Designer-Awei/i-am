#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开放性编码提取器 - 从对话中提取用户特质标签

基于经典扎根理论的开放性编码方法
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class OpenCodingExtractor:
    """开放性编码提取器"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.label_library = self._load_label_library()
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        import yaml
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_label_library(self) -> Dict:
        """加载标签库"""
        library_path = Path(__file__).parent.parent / "grounding_theory" / "open_coding" / "label_library.json"
        if library_path.exists():
            with open(library_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"labels": {}, "categories": {}}
    
    def extract_codes(self, conversation: str) -> List[Dict[str, Any]]:
        """
        从对话中提取编码
        
        Args:
            conversation: 对话文本
            
        Returns:
            编码列表
        """
        codes = []
        
        # 按说话者分割对话
        turns = self._split_conversation(conversation)
        
        for turn in turns:
            if turn.get("speaker") != "user":
                continue
                
            text = turn.get("text", "")
            if not text.strip():
                continue
            
            # 提取标签
            labels = self._extract_labels(text)
            
            for label in labels:
                code = {
                    "text": text,
                    "label": label["name"],
                    "category": label["category"],
                    "timestamp": turn.get("timestamp", datetime.now().isoformat()),
                    "sentiment": self._detect_sentiment(text)
                }
                codes.append(code)
        
        return codes
    
    def _split_conversation(self, conversation: str) -> List[Dict]:
        """分割对话为独立的话轮"""
        turns = []
        
        # 简单实现：按行分割，识别说话者
        lines = conversation.strip().split('\n')
        current_speaker = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测说话者标记（支持中英文冒号）
            speaker_patterns = [
                ("用户:", "user"), ("用户：", "user"),
                ("我:", "user"), ("我：", "user"),
                ("User:", "user"),
                ("助手:", "assistant"), ("助手：", "assistant"),
                ("AI:", "assistant"), ("AI：", "assistant"),
                ("Assistant:", "assistant"),
            ]
            
            matched = False
            for pattern, speaker in speaker_patterns:
                if line.startswith(pattern):
                    if current_speaker and current_text:
                        turns.append({
                            "speaker": current_speaker,
                            "text": " ".join(current_text),
                            "timestamp": datetime.now().isoformat()
                        })
                    current_speaker = speaker
                    current_text = [line.split(pattern, 1)[-1].strip()]
                    matched = True
                    break
            
            if not matched and current_speaker:
                current_text.append(line)
        
        # 添加最后一个话轮
        if current_speaker and current_text:
            turns.append({
                "speaker": current_speaker,
                "text": " ".join(current_text),
                "timestamp": datetime.now().isoformat()
            })
        
        return turns
    
    def _extract_labels(self, text: str) -> List[Dict]:
        """从文本中提取标签"""
        labels = []
        
        # 预定义的模式库（基于常见用户行为）
        patterns = {
            "沟通风格": [
                (r"直接点 | 直接说 | 别绕弯 | 少整 | 有话直说", "偏好直接沟通"),
                (r"简单点 | 简洁 | 短点 | 别废话", "偏好简洁表达"),
                (r"详细点 | 展开说 | 多解释 | 为什么", "偏好详细解释"),
                (r"牛逼 | 厉害 | 可以啊 | 到位", "积极反馈"),
                (r"不对 | 错了 | 不是 | 理解错了", "纠正行为"),
            ],
            "决策风格": [
                (r"先干再说 | 直接整 | 开搞 | 开干", "行动导向"),
                (r"让我想想 | 考虑下 | 再想想", "谨慎决策"),
                (r"听你的 | 你决定 | 都行", "委托决策"),
            ],
            "学习风格": [
                (r"看不懂 | 不理解 | 啥意思", "需要澄清"),
                (r"明白了 | 懂了 | 了解了", "理解确认"),
                (r"举个例子 | 比如呢 | 示范一下", "偏好示例学习"),
            ],
            "情感表达": [
                (r"哈哈 | 笑死 |233|hahaha", "轻松幽默"),
                (r"无语 | 醉了 | 服了", "无奈情绪"),
                (r"感谢 | 谢谢 | 辛苦了", "表达感谢"),
            ],
            "技术取向": [
                (r"能跑就行 | 能用就行 | 不追求完美", "实用主义"),
                (r"最优方案 | 最佳实践 | 标准做法", "规范导向"),
                (r"黑科技 | 新方案 | 试试这个", "创新偏好"),
            ],
        }
        
        # 匹配模式
        for category, pattern_list in patterns.items():
            for pattern, label_name in pattern_list:
                if re.search(pattern, text, re.IGNORECASE):
                    labels.append({
                        "name": label_name,
                        "category": category,
                        "confidence": 0.8,  # 基础置信度
                        "source": "pattern_match"
                    })
        
        # 检查标签库中的历史标签
        for label_name, label_info in self.label_library.get("labels", {}).items():
            keywords = label_info.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    labels.append({
                        "name": label_name,
                        "category": label_info.get("category", "未分类"),
                        "confidence": 0.7,
                        "source": "label_library"
                    })
                    break
        
        return labels
    
    def _detect_sentiment(self, text: str) -> str:
        """检测情感极性"""
        positive_words = ["好", "牛逼", "厉害", "可以", "行", "谢谢", "感谢", "棒", "到位"]
        negative_words = ["不", "错", "差", "烂", "无语", "醉了", "服了", "垃圾"]
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
    
    def save_session(self, codes: List[Dict], session_id: str = None):
        """保存会话编码结果"""
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d")
        
        output_path = Path(__file__).parent.parent / "grounding_theory" / "open_coding" / f"session_{session_id}.json"
        
        data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "codes_count": len(codes),
            "codes": codes
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def update_label_library(self, codes: List[Dict]):
        """更新标签库"""
        for code in codes:
            label_name = code.get("label")
            if not label_name:
                continue
            
            if label_name not in self.label_library["labels"]:
                self.label_library["labels"][label_name] = {
                    "name": label_name,
                    "category": code.get("category", "未分类"),
                    "keywords": [],
                    "count": 0,
                    "first_seen": code.get("timestamp"),
                    "last_seen": code.get("timestamp")
                }
            
            label_info = self.label_library["labels"][label_name]
            label_info["count"] += 1
            label_info["last_seen"] = code.get("timestamp")
            
            # 提取关键词
            text = code.get("text", "")
            words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
            for word in words[:5]:  # 最多添加 5 个关键词
                if word not in label_info["keywords"]:
                    label_info["keywords"].append(word)
        
        # 保存标签库
        library_path = Path(__file__).parent.parent / "grounding_theory" / "open_coding" / "label_library.json"
        with open(library_path, 'w', encoding='utf-8') as f:
            json.dump(self.label_library, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    import sys
    
    extractor = OpenCodingExtractor()
    
    # 从参数或 stdin 读取对话
    if len(sys.argv) > 1:
        conversation = " ".join(sys.argv[1:])
    else:
        conversation = sys.stdin.read()
    
    if not conversation.strip():
        print("错误：请提供对话文本")
        sys.exit(1)
    
    # 提取编码
    codes = extractor.extract_codes(conversation)
    
    # 输出结果
    print(json.dumps(codes, ensure_ascii=False, indent=2))
    
    # 保存会话
    session_file = extractor.save_session(codes)
    print(f"\n会话已保存到：{session_file}", file=sys.stderr)
    
    # 更新标签库
    extractor.update_label_library(codes)
    print("标签库已更新", file=sys.stderr)


if __name__ == "__main__":
    main()
