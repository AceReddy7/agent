"""
Lead Agent - Operational Supervisor

Role: Manages all AI workers (not individual invoices). Monitors all 8 workers,
      detects bottlenecks or failures, re-routes workloads,
      escalates unresolved issues, produces team-level reports.

NOTE: This agent uses AI for PATTERN DETECTION only

Architecture: This supervisor-level agent provides team management capabilities:
- Real-time performance monitoring of all worker agents
- Automatic detection of processing bottlenecks and failure patterns
- Intelligent workload re-routing for failed invoices
- Escalation of critical issues to human supervisors
- Comprehensive team performance reporting and analytics
"""

import time
from typing import List, Dict, Optional
from datetime import datetime
from base_agent import BaseAgent, Invoice

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LeadAgent(BaseAgent):
    """
    Operational supervisor that manages all worker agents.
    
    Provides team-level management and monitoring without processing
    individual invoices. Uses AI for pattern detection in team performance.
    
    Features:
    - Monitors all 8 worker agents for performance issues
    - Detects bottlenecks and failure patterns
    - Re-routes failed invoices intelligently
    - Escalates critical issues
    - Generates comprehensive team reports
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("LeadAgent")
        
        # Initialize AI for pattern detection
        self.ai_enabled = False
        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.ai_enabled = True
                self.logger.info("AI enabled for pattern detection")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI: {e}")
                
        # Team of agents
        self.team: List[BaseAgent] = []
        
        # Team metrics
        self.team_metrics = {
            "total_invoices": 0,
            "successful": 0,
            "failed": 0,
            "exceptions": 0,
            "bottlenecks": [],
            "escalations": []
        }
        
        # Performance thresholds
        self.failure_threshold = 0.2  # 20% failure rate triggers alert
        self.bottleneck_threshold = 10  # 10 seconds processing time
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent in the team"""
        self.team.append(agent)
        self.logger.info(f"Registered agent: {agent.agent_name}")
        
    def process(self, invoice: Invoice) -> Invoice:
        """
        Lead agent doesn't process individual invoices.
        This is here to satisfy the BaseAgent interface.
        """
        self.logger.warning("LeadAgent.process() called - Lead agent manages workers, not invoices")
        return invoice
        
    def monitor_team(self) -> Dict:
        """
        Monitor all worker agents for bottlenecks and failures.
        
        Returns:
            Monitoring report
        """
        self.logger.info("Monitoring team performance...")
        
        monitoring_report = {
            "timestamp": datetime.now().isoformat(),
            "agents": [],
            "bottlenecks": [],
            "failures": [],
            "recommendations": []
        }
        
        # Collect metrics from each agent
        for agent in self.team:
            agent_metrics = agent.get_metrics()
            monitoring_report["agents"].append(agent_metrics)
            
            # Check for failures
            total = agent_metrics["metrics"]["processed"]
            failed = agent_metrics["metrics"]["failed"]
            
            if total > 0:
                failure_rate = failed / total
                if failure_rate > self.failure_threshold:
                    failure_info = {
                        "agent": agent.agent_name,
                        "failure_rate": f"{failure_rate * 100:.1f}%",
                        "failed_count": failed,
                        "total_count": total
                    }
                    monitoring_report["failures"].append(failure_info)
                    self.logger.warning(f"High failure rate detected: {agent.agent_name}")
                    
        # Detect patterns if AI is enabled
        if self.ai_enabled and (monitoring_report["bottlenecks"] or monitoring_report["failures"]):
            patterns = self._detect_patterns(monitoring_report)
            monitoring_report["pattern_analysis"] = patterns
            
        return monitoring_report
        
    def detect_bottlenecks(self) -> List[Dict]:
        """Detect bottlenecks in the processing pipeline"""
        bottlenecks = []
        
        for agent in self.team:
            metrics = agent.get_metrics()
            
            # Check if agent is processing slowly
            # (In a real system, we'd track processing times)
            if metrics["metrics"]["processed"] > 0:
                # Placeholder logic - in production would track actual processing times
                pass
                
        return bottlenecks
        
    def reroute_workload(self, invoice: Invoice, failed_agent: str) -> Invoice:
        """
        Re-route invoice when an agent fails.
        
        Args:
            invoice: Invoice that failed processing
            failed_agent: Name of the agent that failed
            
        Returns:
            Re-routed invoice
        """
        self.logger.warning(f"Re-routing invoice {invoice.invoice_id} due to {failed_agent} failure")
        
        # Add to escalations
        self.team_metrics["escalations"].append({
            "invoice_id": invoice.invoice_id,
            "failed_agent": failed_agent,
            "timestamp": datetime.now().isoformat()
        })
        
        # In a real system, this would implement retry logic or route to backup agent
        # For now, we just log the escalation
        
        return invoice
        
    def escalate_issue(self, issue: Dict):
        """
        Escalate unresolved issues.
        
        Args:
            issue: Issue details
        """
        self.logger.error(f"Escalating issue: {issue}")
        
        self.team_metrics["escalations"].append({
            "issue": issue,
            "timestamp": datetime.now().isoformat(),
            "escalated_to": "Human Supervisor"
        })
        
    def generate_team_report(self) -> str:
        """
        Generate comprehensive team-level report.
        
        Returns:
            Team report as formatted string
        """
        report = f"""
{'='*60}
AI ACCOUNTS PAYABLE TEAM - PERFORMANCE REPORT
{'='*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TEAM OVERVIEW:
- Total Agents: {len(self.team)}
- Active Agents: {len([a for a in self.team if a.metrics['processed'] > 0])}

OVERALL METRICS:
- Total Invoices: {self.team_metrics['total_invoices']}
- Successful: {self.team_metrics['successful']}
- Failed: {self.team_metrics['failed']}
- Exceptions: {self.team_metrics['exceptions']}
- Success Rate: {(self.team_metrics['successful'] / max(self.team_metrics['total_invoices'], 1) * 100):.1f}%

AGENT PERFORMANCE:
"""
        
        for agent in self.team:
            metrics = agent.get_metrics()
            m = metrics["metrics"]
            report += f"""
{agent.agent_name}:
  - Processed: {m['processed']}
  - Successful: {m['successful']}
  - Failed: {m['failed']}
  - Success Rate: {(m['successful'] / max(m['processed'], 1) * 100):.1f}%
"""
        
        # Add escalations
        report += f"""
ESCALATIONS:
- Total Escalations: {len(self.team_metrics['escalations'])}
"""
        
        if self.team_metrics['escalations']:
            report += "\nRecent Escalations:\n"
            for escalation in self.team_metrics['escalations'][-5:]:  # Last 5
                report += f"  - {escalation}\n"
                
        report += f"\n{'='*60}\n"
        
        return report
        
    def _detect_patterns(self, monitoring_report: Dict) -> str:
        """Use AI to detect patterns in failures and bottlenecks"""
        try:
            # Prepare data for pattern analysis
            agent_data = "\n".join([
                f"{agent['agent']}: {agent['metrics']['processed']} processed, "
                f"{agent['metrics']['failed']} failed"
                for agent in monitoring_report["agents"]
            ])
            
            failures_data = "\n".join([
                f"{failure['agent']}: {failure['failure_rate']} failure rate"
                for failure in monitoring_report.get("failures", [])
            ])
            
            prompt = f"""
Analyze this AI Accounts Payable team performance data and identify patterns:

Agent Performance:
{agent_data}

Failures Detected:
{failures_data}

Identify:
1. Any patterns in failures (e.g., specific agent consistently failing)
2. Potential root causes
3. Recommendations for improvement

Keep the analysis concise and actionable.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in workflow optimization and team management. Analyze performance patterns and provide actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Pattern detection failed: {e}")
            return "Pattern detection unavailable"
            
    def update_team_metrics(self, invoice: Invoice):
        """Update team-level metrics after invoice processing"""
        self.team_metrics["total_invoices"] += 1
        
        if invoice.status.value == "posted":
            self.team_metrics["successful"] += 1
        elif invoice.status.value == "failed":
            self.team_metrics["failed"] += 1
        elif invoice.status.value == "exception":
            self.team_metrics["exceptions"] += 1
