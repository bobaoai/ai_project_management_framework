# Technical Framework Design v0.1

**Version 0.1 — 2026-03-23**

本文档定义 `technical_framework`，目标是把单资产的技术分析判断整理成 AI 可读、可检索、可复用的标准结构，而不是零散主观描述。

---

## 1. Purpose

`technical_framework` 用来回答以下问题：

- 当前趋势是什么
- 用什么结构判断趋势
- 日线节奏下哪里止损
- 哪里可以观察加仓
- 什么条件代表趋势破坏
- 什么条件代表可以重新转强

它不是为了替代基本面逻辑，而是作为：

- `structural thesis` 的执行层
- `tactical risk` 的价格结构补充层

---

## 2. Role In The System

在 `trading_platform` 中，单资产判断应至少分三层：

- `structural_thesis`
- `tactical_risk`
- `technical_framework`

三者的分工：

- `structural_thesis` 解释为什么长期持有
- `tactical_risk` 解释短期为什么不能裸奔
- `technical_framework` 解释当前图形上如何管理仓位

---

## 3. Scope

V0.1 先聚焦：

- `1d` 日线框架
- 趋势状态
- 止损 / 趋势失效
- 止盈 / 减仓
- 观察加仓区
- 重新转强条件

暂不纳入：

- 自动画线
- 复杂形态识别
- 高频或日内交易
- 多时间框架联动打分

---

## 4. Core Design Principles

- 技术分析必须结构化，而不是只写 narrative
- 先支持日线执行框架，再扩展到周线和 30m
- 信号要能和 `AssetLogicCard` 合并
- 价格位应允许为空，但逻辑字段必须稳定
- 条件描述优先于过度数值化，避免伪精确

---

## 5. Core Fields

推荐 `technical_framework` 至少包含：

- `timeframe`
- `trend_state`
- `trend_basis`
- `risk_levels`
- `take_profit_levels`
- `add_zones`
- `breakdown_condition`
- `reentry_condition`
- `notes`

---

## 6. Field Definitions

### 6.1 `timeframe`

当前技术分析适用的主时间框架。

示例：

- `1d`
- `1w`

### 6.2 `trend_state`

当前趋势状态。

建议枚举：

- `uptrend`
- `range`
- `downtrend`
- `transition`

### 6.3 `trend_basis`

用于解释趋势判断依据。

可包含：

- `structure`
- `moving_averages`
- `momentum_check`
- `volume_context`

### 6.4 `risk_levels`

风险位和趋势失效位。

建议最少包含：

- `stop_loss`
- `trend_invalidation`

### 6.5 `take_profit_levels`

止盈或分批减仓层。

每一层可包含：

- `level`
- `action`
- `reason`

### 6.6 `add_zones`

观察加仓区域，而不是机械追高。

每一层可包含：

- `zone_low`
- `zone_high`
- `condition`
- `priority`

### 6.7 `breakdown_condition`

描述什么情况下趋势被破坏。

示例：

- `daily_close_below_50d_for_2_sessions`
- `breaks_prior_swing_low_with_volume`

### 6.8 `reentry_condition`

描述什么时候可以恢复净多头或重新加仓。

示例：

- `reclaims_20d_and_holds`
- `breaks_above_prior_pivot_with_volume`

---

## 7. Database-Friendly JSON Shape

```json
{
  "technical_framework": {
    "timeframe": "1d",
    "trend_state": "uptrend",
    "trend_basis": {
      "structure": "higher_highs_higher_lows",
      "moving_averages": [
        "20d",
        "50d",
        "200d"
      ],
      "momentum_check": "price_above_20d_and_50d",
      "volume_context": "pullbacks_on_lighter_volume"
    },
    "risk_levels": {
      "stop_loss": 312.0,
      "trend_invalidation": 298.0
    },
    "take_profit_levels": [
      {
        "level": 365.0,
        "action": "trim_25",
        "reason": "first_resistance"
      },
      {
        "level": 392.0,
        "action": "trim_25",
        "reason": "prior_major_high"
      }
    ],
    "add_zones": [
      {
        "zone_low": 320.0,
        "zone_high": 330.0,
        "condition": "pullback_holds_20d_or_prior_breakout",
        "priority": "high"
      }
    ],
    "breakdown_condition": "daily_close_below_key_support_for_2_sessions",
    "reentry_condition": "reclaims_support_with_volume_and_structure",
    "notes": "Daily rhythm only. Used for swing and position management, not intraday trading."
  }
}
```

---

## 8. Relationship To AssetLogicCard

建议把 `technical_framework` 作为 `AssetLogicCard` 的一个正式子对象。

这样一张资产卡可以同时表达：

- `structural_thesis`
- `tactical_risk`
- `technical_framework`

形成统一的研究对象。

---

## 9. Example Interpretation

以 `TSLA` 为例：

- `structural_thesis`: 机器人、储能、制造平台长期逻辑
- `tactical_risk`: 伊朗战争窗口中的 supply chain / risk-off 风险
- `technical_framework`: 日线是否仍在上升趋势、何处减仓、何处观察回补

这让系统可以输出：

- 长期继续看多
- 短期需要 hedge overlay
- 图形破坏前保持 core
- 图形破坏后先减净敞口

---

## 10. Future Extensions

后续可扩展：

- `30m` tactical framework
- `1w` structural timing framework
- pattern labels
- ATR-based stop framework
- technical score
- current `entry_setups` plus later outcome tracking for higher-quality entry analysis
- see idea doc: [`ideas/technical_entry_setup_framework.md`](ideas/technical_entry_setup_framework.md)

但前提是先把 `1d` 结构稳定下来。
