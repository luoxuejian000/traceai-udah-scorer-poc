TraceAI U/D/A/H 评估适配器 (POC)
[![PyPI version](https://img.shields.io/pypi/v/udah-scorer.svg?style=flat-square)](https://pypi.org/project/udah-scorer/)
[![Downloads](https://static.pepy.tech/badge/udah-scorer?style=flat-square)](https://pepy.tech/project/udah-scorer)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=flat-square)](https://www.python.org/)

本项目是为 future-agi/traceAI#185 提交的范围限定概念验证（Proof of Concept）。

💡 这是什么？

这是一个零第三方依赖、纯 Python 标准库编写的轻量级适配器。它读取 traceAI 导出的 OTLP/GenAI 追踪数据，利用 session.id 对历史对话进行去重提取，并计算每一轮的 U/D/A/H 维度分数（统一性、发展性、对抗性、和谐度）。

⚡ 核心优势

· 零成本遥测：无需调用任何大模型（LLM）API。运行时间以毫秒计，成本为 0。
· 确定性输出：完全基于纯数学与启发式规则，绝对不产生大模型幻觉。
· 只诊断，不开方：仅输出结构化的 JSON 指标数据，不提供任何修改建议或干预操作。
· 历史去重：自动识别并剔除请求中重复携带的历史对话，确保每个 assistant 轮次只计分一次。

🚀 如何运行

无需安装任何外部依赖，直接运行：

```bash
python traceai_adapter.py --input <trace_export.json>
```

📊 复现我们的基准测试

我们在 V2-06（车轱辘话/循环逻辑）用例中发现，当大模型裁判因为词汇连贯而放行时，本脚本的 D 值（发展性）会骤降至 0.04，H 值（和谐度）会从 0.57 暴跌至 0.15。

你可以通过 examples/v2_controls/ 目录下的脚本，自行复现这组对比数据。

⚖️ 许可证与商业合作

本项目采用 Apache-2.0开源许可证。

如需进行企业级集成或商业合作，请联系：

· 李广好 (Guanghao Li)
· Rastislav Drahoš

李广好在设计和思考过程中使用了AI辅助。所有代码都经过Rastislav逐字逐句人工审核。
