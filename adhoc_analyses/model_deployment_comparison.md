# Model Service Deployment: Always-On vs Scale-to-Zero

**Cost Assumption:** $0.28/instance/hour  
**Analysis Date:** June 14, 2026

---

## Executive Summary

| Strategy | Monthly Cost (1 instance) | P95 Latency | Best For |
|----------|---------------------------|-------------|----------|
| **Always-On** | **$201.60** | **<100ms** | Production, high-traffic, SLA-critical |
| **Scale-to-Zero** | **$5-60** (usage-dependent) | **2-30 seconds** (cold start) | Development, low-traffic, cost-sensitive |

**Key Insight:** Always-on costs 3-40x more but provides 20-300x lower latency.

---

## 1. Cost Analysis

### Always-On Cost Structure

**Fixed Monthly Cost:**
```
Cost = $0.28/hour × 24 hours × 30 days = $201.60/month (1 instance)

Multi-instance costs:
- 2 instances (HA): $403.20/month
- 3 instances (HA + load): $604.80/month
- 5 instances (prod scale): $1,008/month
```

**Characteristics:**
- ✅ **Predictable**: Fixed monthly expense
- ✅ **Simple billing**: No usage tracking needed
- ❌ **Wasteful**: Pay for idle time
- ❌ **No cost optimization**: Can't reduce spend during low usage

### Scale-to-Zero Cost Structure

**Variable Monthly Cost (depends on usage):**

| Usage Pattern | Hours/Month | Cost/Month | Savings vs Always-On |
|---------------|-------------|------------|---------------------|
| Very Low (1 req/day, 1 min each) | ~0.5 hours | **$0.14** | 99.9% |
| Low (10 req/day, 2 min each) | ~10 hours | **$2.80** | 98.6% |
| Medium (100 req/day, 3 min each) | ~150 hours | **$42** | 79.2% |
| High (1000 req/day, 5 min each) | ~416 hours | **$116.48** | 42.2% |
| Very High (continuous) | 720 hours | **$201.60** | 0% (same as always-on) |

**Calculation Example (Medium Usage):**
```
100 requests/day × 3 minutes each = 300 minutes/day = 5 hours/day
5 hours/day × 30 days = 150 hours/month
150 hours × $0.28/hour = $42/month
```

**Characteristics:**
- ✅ **Cost-efficient**: Only pay for actual usage
- ✅ **Scales with demand**: Natural cost optimization
- ❌ **Unpredictable**: Monthly costs can vary significantly
- ❌ **Complex billing**: Requires usage monitoring

---

## 2. Latency Analysis

### Always-On Latency Profile

**Response Times:**
```
Cold start:        0ms (no cold start)
Network RTT:       10-30ms
Model inference:   20-100ms (depends on model)
Total P50:         50-150ms
Total P95:         80-200ms
Total P99:         100-300ms
```

**Latency Characteristics:**
- ✅ **Predictable**: Consistent response times
- ✅ **Fast**: No startup penalty
- ✅ **Production-ready**: Meets most SLAs
- ✅ **User-friendly**: Good UX

**Example Latency Distribution:**
```
P50 (median):  75ms
P75:           95ms
P90:          120ms
P95:          150ms
P99:          250ms
```

### Scale-to-Zero Latency Profile

**Response Times:**

| Scenario | Cold Start | Inference | Total Latency |
|----------|------------|-----------|---------------|
| **Warm (instance running)** | 0ms | 50-100ms | **50-100ms** |
| **Cold (container start)** | 5-10s | 50-100ms | **5-10 seconds** |
| **Very Cold (image pull)** | 20-30s | 50-100ms | **20-30 seconds** |

**Cold Start Breakdown:**
```
Container runtime init:     1-3 seconds
Load model from storage:    2-5 seconds
Model initialization:       1-2 seconds
Framework warmup:          0.5-1 second
Total cold start:          5-10 seconds (typical)
                           20-30 seconds (worst case)
```

**Latency Characteristics:**
- ❌ **Unpredictable**: Varies dramatically (100ms vs 10s)
- ❌ **Slow**: First request after idle suffers
- ❌ **User-hostile**: Poor UX for first requester
- ✅ **Improves with warmth**: Subsequent requests are fast

**Example Latency Distribution (with cold starts):**
```
P50 (median):  100ms (mostly warm)
P75:           150ms
P90:         2,500ms (some cold starts)
P95:         8,000ms (cold starts)
P99:        25,000ms (worst case cold starts)
```

---

## 3. Detailed Comparison Matrix

| Factor | Always-On | Scale-to-Zero | Winner |
|--------|-----------|---------------|--------|
| **Monthly Cost (low traffic)** | $201.60 | $5-42 | 🏆 Scale-to-Zero |
| **Monthly Cost (high traffic)** | $201.60 | $117-201 | 🏆 Always-On |
| **P50 Latency** | 75ms | 100ms | 🏆 Always-On |
| **P95 Latency** | 150ms | 8,000ms | 🏆 Always-On |
| **P99 Latency** | 250ms | 25,000ms | 🏆 Always-On |
| **Predictability** | High | Low | 🏆 Always-On |
| **SLA Compliance** | Easy | Hard | 🏆 Always-On |
| **Resource Waste** | High | Low | 🏆 Scale-to-Zero |
| **Operational Complexity** | Low | Medium | 🏆 Always-On |
| **Cost Optimization** | None | Automatic | 🏆 Scale-to-Zero |
| **Dev/Test Environments** | Wasteful | Perfect | 🏆 Scale-to-Zero |
| **Production Systems** | Reliable | Risky | 🏆 Always-On |

---

## 4. Break-Even Analysis

### When Does Always-On Become Cheaper?

**Break-even calculation:**
```
Always-on cost = Scale-to-zero cost
$201.60 = Usage hours × $0.28
Usage hours = 720 hours/month (100% utilization)

If usage < 720 hours/month: Scale-to-zero is cheaper
If usage > 720 hours/month: Always-on is cheaper (but this is impossible - max is 720)
```

**Practical break-even (accounting for cold starts):**
- If your service runs >50% of the month (360+ hours), always-on makes sense
- If your service runs <30% of the month (<216 hours), scale-to-zero is better
- In the 30-50% range, it's a judgment call based on latency tolerance

**Traffic-based break-even:**

Assuming 3-minute average request duration:

| Requests/Day | Hours/Month | Cost | Better Option |
|--------------|-------------|------|---------------|
| 1-10 | <10 | <$3 | 🏆 Scale-to-Zero |
| 10-100 | 10-150 | $3-42 | 🏆 Scale-to-Zero |
| 100-500 | 150-375 | $42-105 | 🏆 Scale-to-Zero (but close) |
| 500+ | 375+ | $105-201 | 🏆 Always-On |

---

## 5. Latency Mitigation Strategies for Scale-to-Zero

### Strategy 1: Keep-Alive Pinging
**Approach:** Ping the endpoint every 5-10 minutes to keep instance warm

**Impact:**
- Cost increase: Minimal (~10-20 extra hours/month = +$3-6)
- Latency improvement: Eliminates most cold starts
- New P95 latency: ~200ms (vs 8,000ms)

**Net result:** $45-48/month with always-on-like latency (78% cost savings)

### Strategy 2: Partial Warm Pool
**Approach:** Keep 1 instance always-on, scale additional instances to zero

**Impact:**
- Cost: $201.60 (base) + variable (burst)
- Latency: First request fast, burst requests may be slow
- Use case: Handle baseline + spikes

### Strategy 3: Predictive Scaling
**Approach:** Scale up before known busy periods (e.g., business hours)

**Impact:**
- Cost: ~40-60% of always-on ($80-120/month)
- Latency: Good during business hours, slow off-hours
- Use case: B2B applications with predictable usage

### Strategy 4: Pre-warmed Containers
**Approach:** Use container snapshots to reduce cold start time

**Impact:**
- Cold start reduction: 5-10s → 2-5s (50% improvement)
- Cost: Minimal (snapshot storage)
- Still worse than always-on

---

## 6. Use Case Recommendations

### ✅ Use Always-On When:

1. **Production user-facing APIs**
   - SLA requirements (e.g., P99 < 500ms)
   - Paying customers expect fast responses
   - Cost is justified by revenue

2. **High-traffic services**
   - >500 requests/day consistently
   - Service utilization >50%
   - Cold start cost (lost users) > infrastructure cost

3. **Real-time applications**
   - Trading systems
   - Chat/messaging
   - Interactive ML (e.g., recommendation engines)

4. **Mission-critical systems**
   - Healthcare diagnostics
   - Fraud detection
   - Safety-critical decisions

5. **When latency variance is unacceptable**
   - Financial services
   - E-commerce checkout
   - Gaming backends

### ✅ Use Scale-to-Zero When:

1. **Development/staging environments**
   - Only active during work hours
   - Cost savings: 70-90%
   - Latency doesn't matter

2. **Internal tools**
   - Admin dashboards
   - Batch jobs
   - Analytics endpoints
   - Users can tolerate 5-10s wait

3. **Low-traffic services**
   - <100 requests/day
   - Hobby projects
   - POCs and demos

4. **Asynchronous workloads**
   - Background processing
   - Report generation
   - Email processing
   - Data pipelines

5. **Webhooks/scheduled jobs**
   - Cron-triggered tasks
   - Event-driven processing
   - No user waiting

6. **Cost-sensitive projects**
   - Startups with limited budget
   - Side projects
   - Research experiments

---

## 7. Hybrid Approach: Best of Both Worlds

### Configuration

**Baseline:** 1 always-on instance ($201.60/month)
**Burst:** Scale-to-zero instances (variable cost)

**Example Setup:**
```yaml
min_instances: 1          # Always-on baseline
max_instances: 10         # Burst capacity
scale_to_zero_delay: 5m   # Keep warm for 5 min after last request
```

### Cost Example

**Scenario:** E-commerce site
- Baseline traffic: Handled by 1 always-on instance
- Black Friday spike: Auto-scale to 5 instances for 8 hours

**Monthly cost:**
```
Baseline:  $201.60 (1 instance × 720 hours)
Burst:     $11.20  (4 instances × 8 hours × $0.28)
Total:     $212.80/month
```

**vs Pure Always-On (5 instances all month):**
```
Cost: $1,008/month
Savings: $795.20/month (78% reduction)
```

**Latency Profile:**
- Baseline requests: <100ms (always fast)
- Burst requests: First 4 requests: 5-10s cold start, then <100ms
- P95 latency: Still <200ms (dominated by always-on instance)

---

## 8. Real-World Cost Scenarios

### Scenario A: Startup MVP (Low Traffic)
**Traffic:** 50 requests/day, 2 min each

**Always-On:**
- Cost: $201.60/month
- Latency: 75ms P50

**Scale-to-Zero:**
- Running time: ~3.3 hours/day = 100 hours/month
- Cost: $28/month
- Latency: 100ms P50 (warm), 8s P95 (cold)

**Winner:** Scale-to-Zero saves $173.60/month (86% savings)

### Scenario B: Production SaaS (Medium Traffic)
**Traffic:** 500 requests/day, 3 min each

**Always-On:**
- Cost: $201.60/month
- Latency: 75ms P50, 150ms P95

**Scale-to-Zero:**
- Running time: 25 hours/day = 750 hours/month (more than 720 due to overlapping requests)
- Cost: $210/month
- Latency: 100ms P50, 8,000ms P95

**Winner:** Always-On is cheaper AND faster (scale-to-zero paradox - high usage)

### Scenario C: Enterprise API (High Traffic)
**Traffic:** 5,000 requests/day, needs 3 instances

**Always-On (3 instances):**
- Cost: $604.80/month
- Latency: 75ms P50, 150ms P95, 250ms P99

**Scale-to-Zero with Keep-Alive:**
- Running time: ~720 hours/month per instance
- Cost: 3 × $201.60 = $604.80/month
- Latency: 100ms P50, 200ms P95 (keep-alive pings)

**Winner:** Tie on cost, Always-On slightly better on latency

### Scenario D: Dev/Test Environment
**Traffic:** Only during work hours (8am-6pm, weekdays)

**Always-On:**
- Cost: $201.60/month (running 24/7)
- Utilization: ~23% (50 hours/week out of 168)

**Scale-to-Zero:**
- Running time: 50 hours/week × 4.3 weeks = 215 hours/month
- Cost: $60.20/month
- Latency: Doesn't matter (developers tolerate cold starts)

**Winner:** Scale-to-Zero saves $141.40/month (70% savings)

---

## 9. Decision Framework

### Quick Decision Tree

```
START
  ↓
Is this production user-facing?
  ├─ NO → Is usage predictable?
  │        ├─ YES → Use scheduled scaling (scale up during business hours)
  │        └─ NO → Use Scale-to-Zero
  │
  └─ YES → Do you have SLA requirements (e.g., P95 < 500ms)?
           ├─ YES → Use Always-On
           └─ NO → What's your traffic level?
                    ├─ <500 req/day → Scale-to-Zero with Keep-Alive
                    └─ >500 req/day → Use Always-On
```

### Scoring System

Rate each factor 1-5 (1 = low, 5 = high):

| Factor | Weight | Your Score | Weighted Score |
|--------|--------|------------|----------------|
| Traffic volume | 3x | ___ | ___ |
| Latency sensitivity | 4x | ___ | ___ |
| Cost sensitivity | 2x | ___ | ___ |
| SLA requirements | 5x | ___ | ___ |
| Traffic predictability | 2x | ___ | ___ |

**If weighted total > 50:** Use Always-On  
**If weighted total < 30:** Use Scale-to-Zero  
**If 30-50:** Use Hybrid

---

## 10. Summary & Recommendations

### Cost Summary

| Monthly Usage | Always-On Cost | Scale-to-Zero Cost | Savings |
|---------------|----------------|-------------------|---------|
| 10 hours | $201.60 | $2.80 | 98.6% |
| 100 hours | $201.60 | $28 | 86.1% |
| 200 hours | $201.60 | $56 | 72.2% |
| 400 hours | $201.60 | $112 | 44.4% |
| 720 hours | $201.60 | $201.60 | 0% |

### Latency Summary

| Metric | Always-On | Scale-to-Zero | Difference |
|--------|-----------|---------------|------------|
| P50 | 75ms | 100ms | +33% |
| P95 | 150ms | 8,000ms | +5,233% |
| P99 | 250ms | 25,000ms | +9,900% |
| Cold start | 0ms | 5-10 seconds | ∞ |

### Final Recommendations

**For Production:**
- Use **Always-On** if latency matters
- Add auto-scaling for traffic spikes
- Budget: $200-600/month depending on scale

**For Development:**
- Use **Scale-to-Zero** to save 70-90%
- Accept occasional cold starts
- Budget: $20-60/month

**Hybrid Approach:**
- 1 always-on instance + auto-scale to zero
- Best balance: Good latency + cost optimization
- Budget: $200-300/month

**Golden Rule:**
```
If (traffic_hours_per_month > 360) OR (has_SLA_requirements):
    use_always_on()
else:
    use_scale_to_zero()
```

---

**Analysis Date:** June 14, 2026  
**Cost Assumption:** $0.28/instance/hour  
**Recommendation:** Choose based on your traffic patterns and latency requirements
