import re
from typing import Dict, List, Tuple, Optional
from app.schemas import CategoryBreakdown, AnalysisResult, RecognitionGapAnalysis, ImpactAnalysis, AIInsights
from app.utils.ai_insights_generator import AIInsightsGenerator


class InvisibleWorkAnalyzer:
    """Analyzer for classifying and scoring invisible work activities"""
    
    # Keywords for each category
    CATEGORY_KEYWORDS = {
        'mentoring': [
            'mentor', 'mentoring', 'coach', 'coaching', 'guide', 'guiding',
            'teach', 'teaching', 'train', 'training', 'onboard', 'onboarding',
            'help', 'helping', 'assist', 'assisting', 'support team member',
            'pair programming', 'knowledge transfer', 'shadowing'
        ],
        'knowledge_sharing': [
            'share', 'sharing', 'present', 'presentation', 'demo', 'demonstrate',
            'explain', 'explaining', 'discuss', 'discussion', 'brown bag',
            'tech talk', 'lunch and learn', 'workshop', 'seminar',
            'best practice', 'lesson learned', 'post-mortem', 'retrospective'
        ],
        'documentation': [
            'document', 'documentation', 'write', 'writing', 'readme',
            'wiki', 'confluence', 'guide', 'tutorial', 'how-to',
            'runbook', 'playbook', 'architecture diagram', 'design doc',
            'api documentation', 'comment', 'commenting', 'changelog'
        ],
        'incident_support': [
            'incident', 'outage', 'bug', 'issue', 'problem', 'troubleshoot',
            'debug', 'debugging', 'fix', 'fixing', 'hotfix', 'emergency',
            'on-call', 'pager', 'alert', 'monitoring', 'investigation',
            'root cause', 'postmortem', 'firefighting'
        ],
        'meetings': [
            'meeting', 'standup', 'stand-up', 'sync', 'call', 'conference',
            'planning', 'retrospective', 'retro', 'review', 'demo',
            'all-hands', 'town hall', 'one-on-one', '1:1', 'interview',
            'brainstorm', 'brainstorming', 'workshop', 'session'
        ],
        'cross_team_collaboration': [
            'collaborate', 'collaboration', 'cross-team', 'cross team',
            'coordinate', 'coordination', 'align', 'alignment', 'integrate',
            'integration', 'partner', 'partnership', 'stakeholder',
            'dependency', 'handoff', 'liaison', 'bridge team'
        ],
        'process_improvement': [
            'improve', 'improvement', 'optimize', 'optimization', 'refactor',
            'refactoring', 'streamline', 'efficiency', 'automate', 'automation',
            'ci/cd', 'pipeline', 'tooling', 'infrastructure', 'devops',
            'best practice', 'standard', 'standardize', 'process'
        ],
        'administrative_work': [
            'admin', 'administrative', 'paperwork', 'report', 'reporting',
            'timesheet', 'expense', 'approval', 'review', 'compliance',
            'policy', 'procedure', 'form', 'request', 'ticket',
            'jira', 'tracking', 'update status', 'planning'
        ]
    }
    
    def __init__(self):
        """Initialize the analyzer"""
        pass
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_activities(self, text: str) -> List[str]:
        """Extract individual activities from text"""
        # Split by common delimiters
        activities = []
        
        # Split by newlines, bullets, numbers, etc.
        patterns = [
            r'\n+',  # Newlines
            r'[•\-\*]\s+',  # Bullets
            r'\d+\.\s+',  # Numbered lists
            r';\s*',  # Semicolons
        ]
        
        current_text = text
        for pattern in patterns:
            parts = re.split(pattern, current_text)
            if len(parts) > 1:
                activities.extend([p.strip() for p in parts if p.strip()])
                break
        
        # If no clear delimiters, split by sentences
        if not activities:
            activities = re.split(r'[.!?]+', text)
            activities = [a.strip() for a in activities if a.strip()]
        
        return activities
    
    def _classify_activity(self, activity: str) -> Optional[str]:
        """Classify a single activity into a category"""
        activity_lower = activity.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in activity_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, or None if no matches
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return None
    
    def _calculate_invisible_work_score(self, breakdown: CategoryBreakdown, total: int) -> float:
        """
        Calculate invisible work score (0.0 to 1.0)
        Higher score means more invisible work
        """
        if total == 0:
            return 0.0
        
        # Weight each category by its "invisibility"
        weights = {
            'mentoring': 0.9,
            'knowledge_sharing': 0.8,
            'documentation': 0.7,
            'incident_support': 0.6,
            'meetings': 0.5,
            'cross_team_collaboration': 0.8,
            'process_improvement': 0.7,
            'administrative_work': 0.4
        }
        
        weighted_sum = 0.0
        for category, weight in weights.items():
            count = getattr(breakdown, category)
            weighted_sum += count * weight
        
        # Normalize by total activities
        score = weighted_sum / total
        return min(score, 1.0)  # Cap at 1.0
    
    def _generate_performance_summary(self, breakdown: CategoryBreakdown, score: float, total: int) -> str:
        """Generate a performance review summary"""
        summary_parts = []
        
        # Opening statement
        if score >= 0.7:
            summary_parts.append(f"This team member demonstrates exceptional commitment to invisible work, with {total} documented activities showing a strong focus on team enablement and organizational health.")
        elif score >= 0.5:
            summary_parts.append(f"This team member shows solid engagement in invisible work activities, with {total} documented contributions that support team success.")
        else:
            summary_parts.append(f"This team member has documented {total} activities with some invisible work contributions.")
        
        # Highlight top categories
        category_dict = breakdown.model_dump()
        sorted_categories = sorted(category_dict.items(), key=lambda x: x[1], reverse=True)
        top_categories = [cat for cat, count in sorted_categories if count > 0][:3]
        
        if top_categories:
            category_names = {
                'mentoring': 'Mentoring',
                'knowledge_sharing': 'Knowledge Sharing',
                'documentation': 'Documentation',
                'incident_support': 'Incident Support',
                'meetings': 'Meetings',
                'cross_team_collaboration': 'Cross-Team Collaboration',
                'process_improvement': 'Process Improvement',
                'administrative_work': 'Administrative Work'
            }
            
            top_names = [category_names[cat] for cat in top_categories]
            summary_parts.append(f"\n\nKey strengths include: {', '.join(top_names)}.")
        
        # Specific highlights
        if breakdown.mentoring > 0:
            summary_parts.append(f"\n\n• Mentoring & Coaching: Actively supported team members' growth through {breakdown.mentoring} mentoring activities.")
        
        if breakdown.knowledge_sharing > 0:
            summary_parts.append(f"\n• Knowledge Sharing: Contributed to team learning through {breakdown.knowledge_sharing} knowledge sharing sessions.")
        
        if breakdown.documentation > 0:
            summary_parts.append(f"\n• Documentation: Enhanced team efficiency with {breakdown.documentation} documentation efforts.")
        
        if breakdown.incident_support > 0:
            summary_parts.append(f"\n• Incident Support: Demonstrated reliability through {breakdown.incident_support} incident response activities.")
        
        if breakdown.cross_team_collaboration > 0:
            summary_parts.append(f"\n• Cross-Team Collaboration: Facilitated organizational alignment through {breakdown.cross_team_collaboration} collaborative efforts.")
        
        if breakdown.process_improvement > 0:
            summary_parts.append(f"\n• Process Improvement: Drove efficiency gains through {breakdown.process_improvement} improvement initiatives.")
        
        # Closing statement
        summary_parts.append(f"\n\nInvisible Work Score: {score:.2f}/1.00 - This score reflects the proportion and impact of work that often goes unrecognized in traditional performance metrics.")
        
        return ''.join(summary_parts)
    
    def _calculate_recognition_gap_score(self, breakdown: CategoryBreakdown, total: int) -> int:
        """
        Calculate Recognition Gap Score (0-100)
        Higher score means more work is likely invisible in traditional metrics
        
        Focuses on: Mentoring, Knowledge Sharing, Cross-Team Collaboration,
                    Incident Support, and Documentation
        """
        if total == 0:
            return 0
        
        # High-impact invisible work categories with weights
        invisible_categories = {
            'mentoring': 1.0,
            'knowledge_sharing': 0.95,
            'cross_team_collaboration': 0.9,
            'incident_support': 0.85,
            'documentation': 0.8
        }
        
        # Calculate weighted count of invisible work
        invisible_count = 0.0
        for category, weight in invisible_categories.items():
            count = getattr(breakdown, category)
            invisible_count += count * weight
        
        # Calculate percentage and scale to 0-100
        if total > 0:
            percentage = (invisible_count / total) * 100
            # Apply a curve to make the score more meaningful
            # Activities with >60% invisible work get higher scores
            if percentage >= 60:
                score = 60 + (percentage - 60) * 1.5
            else:
                score = percentage
            
            return min(int(score), 100)
        
        return 0
    
    def _generate_recognition_gap_explanation(self, breakdown: CategoryBreakdown, score: int, total: int) -> str:
        """Generate explanation for the Recognition Gap Score"""
        explanations = []
        
        # Score interpretation
        if score >= 80:
            explanations.append(f"Recognition Gap Score: {score}/100 (Very High)\n\n")
            explanations.append("This score indicates that a significant majority of this person's contributions are likely to be invisible in traditional performance metrics. ")
        elif score >= 60:
            explanations.append(f"Recognition Gap Score: {score}/100 (High)\n\n")
            explanations.append("This score indicates that a substantial portion of this person's contributions may not be fully captured in traditional performance metrics. ")
        elif score >= 40:
            explanations.append(f"Recognition Gap Score: {score}/100 (Moderate)\n\n")
            explanations.append("This score indicates that a moderate amount of this person's work may go unrecognized in standard performance reviews. ")
        elif score >= 20:
            explanations.append(f"Recognition Gap Score: {score}/100 (Low)\n\n")
            explanations.append("This score indicates that most of this person's work is likely visible in traditional metrics, with some invisible contributions. ")
        else:
            explanations.append(f"Recognition Gap Score: {score}/100 (Very Low)\n\n")
            explanations.append("This score indicates that the majority of documented work is likely captured in traditional performance metrics. ")
        
        # Breakdown of invisible work categories
        invisible_activities = []
        if breakdown.mentoring > 0:
            invisible_activities.append(f"• Mentoring: {breakdown.mentoring} activities - Often untracked but critical for team growth")
        if breakdown.knowledge_sharing > 0:
            invisible_activities.append(f"• Knowledge Sharing: {breakdown.knowledge_sharing} activities - Rarely measured but essential for team capability")
        if breakdown.cross_team_collaboration > 0:
            invisible_activities.append(f"• Cross-Team Collaboration: {breakdown.cross_team_collaboration} activities - Frequently overlooked despite organizational impact")
        if breakdown.incident_support > 0:
            invisible_activities.append(f"• Incident Support: {breakdown.incident_support} activities - Often seen as 'just doing the job' rather than going above and beyond")
        if breakdown.documentation > 0:
            invisible_activities.append(f"• Documentation: {breakdown.documentation} activities - Undervalued despite long-term benefits")
        
        if invisible_activities:
            explanations.append("\n\nKey Invisible Work Categories:\n")
            explanations.append("\n".join(invisible_activities))
        
        # Context
        total_invisible = (breakdown.mentoring + breakdown.knowledge_sharing +
                          breakdown.cross_team_collaboration + breakdown.incident_support +
                          breakdown.documentation)
        
        if total > 0:
            percentage = (total_invisible / total) * 100
            explanations.append(f"\n\nOut of {total} total activities, {total_invisible} ({percentage:.1f}%) fall into high-impact invisible work categories that are typically underrepresented in performance reviews and promotion decisions.")
        
        return ''.join(explanations)
    
    def _generate_recognition_gap_recommendations(self, breakdown: CategoryBreakdown, score: int) -> str:
        """Generate recommendations for highlighting invisible contributions"""
        recommendations = []
        
        recommendations.append("Recommendations for Performance Reviews:\n\n")
        
        # General recommendations based on score
        if score >= 60:
            recommendations.append("Given the high Recognition Gap Score, it's crucial to explicitly document and highlight these contributions:\n\n")
        else:
            recommendations.append("To ensure these valuable contributions are recognized:\n\n")
        
        # Specific recommendations based on categories
        if breakdown.mentoring > 0:
            recommendations.append(f"1. Mentoring Impact ({breakdown.mentoring} activities):\n")
            recommendations.append("   - Document specific examples of team members mentored and their growth\n")
            recommendations.append("   - Quantify impact: 'Mentored X engineers, resulting in Y promotions/skill improvements'\n")
            recommendations.append("   - Include testimonials from mentees in performance reviews\n\n")
        
        if breakdown.knowledge_sharing > 0:
            recommendations.append(f"2. Knowledge Sharing Contributions ({breakdown.knowledge_sharing} activities):\n")
            recommendations.append("   - Track attendance and feedback from presentations/sessions\n")
            recommendations.append("   - Measure adoption of shared practices or tools\n")
            recommendations.append("   - Document creation of reusable resources (guides, templates, etc.)\n\n")
        
        if breakdown.cross_team_collaboration > 0:
            recommendations.append(f"3. Cross-Team Collaboration ({breakdown.cross_team_collaboration} activities):\n")
            recommendations.append("   - Highlight projects that required cross-functional coordination\n")
            recommendations.append("   - Document stakeholder feedback and partnership outcomes\n")
            recommendations.append("   - Emphasize organizational impact beyond immediate team\n\n")
        
        # General best practices
        recommendations.append("General Best Practices:\n")
        recommendations.append("• Maintain a 'brag document' tracking all invisible work contributions\n")
        recommendations.append("• Request peer feedback specifically about invisible work contributions\n")
        recommendations.append("• Include invisible work metrics in 1:1s and performance reviews\n")
        recommendations.append("• Advocate for recognition systems that value team enablement\n")
        recommendations.append("• Share this analysis with your manager to ensure visibility\n")
        
        # Ensure we always return a string
        if not recommendations:
            return "Continue documenting invisible work contributions and maintain visibility with your manager."
        
        return ''.join(recommendations)
    
    def _calculate_impact_score(self, breakdown: CategoryBreakdown, total: int) -> int:
        """
        Calculate Impact Score (0-100)
        Estimates organizational value created by the employee
        
        Weighting:
        - Incident Support: Very High (1.0)
        - Process Improvement: High (0.9)
        - Mentoring: High (0.9)
        - Cross-Team Collaboration: High (0.85)
        - Knowledge Sharing: Medium (0.7)
        - Documentation: Medium (0.65)
        - Meetings: Low (0.3)
        - Administrative Work: Low (0.2)
        """
        if total == 0:
            return 0
        
        # Impact weights for each category
        impact_weights = {
            'incident_support': 1.0,        # Very High
            'process_improvement': 0.9,     # High
            'mentoring': 0.9,               # High
            'cross_team_collaboration': 0.85,  # High
            'knowledge_sharing': 0.7,       # Medium
            'documentation': 0.65,          # Medium
            'meetings': 0.3,                # Low
            'administrative_work': 0.2      # Low
        }
        
        # Calculate weighted impact
        weighted_impact = 0.0
        for category, weight in impact_weights.items():
            count = getattr(breakdown, category)
            weighted_impact += count * weight
        
        # Calculate percentage and scale to 0-100
        if total > 0:
            # Normalize by total and scale to 100
            base_score = (weighted_impact / total) * 100
            
            # Apply curve to make scores more meaningful
            # High-impact work (>70%) gets boosted
            if base_score >= 70:
                score = 70 + (base_score - 70) * 1.3
            else:
                score = base_score
            
            return min(int(score), 100)
        
        return 0
    
    def _generate_impact_explanation(self, breakdown: CategoryBreakdown, score: int, total: int) -> str:
        """Generate explanation for the Impact Score"""
        explanations = []
        
        # Score interpretation
        if score >= 85:
            explanations.append(f"Impact Score: {score}/100 (Exceptional)\n\n")
            explanations.append("This score indicates exceptional organizational value creation. The employee's work demonstrates significant impact across critical areas that drive business outcomes and team effectiveness.\n\n")
        elif score >= 70:
            explanations.append(f"Impact Score: {score}/100 (High)\n\n")
            explanations.append("This score indicates high organizational value creation. The employee consistently contributes to areas that have substantial impact on team and organizational success.\n\n")
        elif score >= 55:
            explanations.append(f"Impact Score: {score}/100 (Above Average)\n\n")
            explanations.append("This score indicates above-average organizational value creation. The employee makes meaningful contributions that positively affect team performance and outcomes.\n\n")
        elif score >= 40:
            explanations.append(f"Impact Score: {score}/100 (Moderate)\n\n")
            explanations.append("This score indicates moderate organizational value creation. The employee contributes across various areas with balanced impact.\n\n")
        else:
            explanations.append(f"Impact Score: {score}/100 (Developing)\n\n")
            explanations.append("This score indicates developing organizational impact. There are opportunities to increase contribution in high-value areas.\n\n")
        
        # Breakdown by impact level
        high_impact = []
        medium_impact = []
        low_impact = []
        
        if breakdown.incident_support > 0:
            high_impact.append(f"• Incident Support: {breakdown.incident_support} activities - Critical for system reliability and customer satisfaction")
        if breakdown.process_improvement > 0:
            high_impact.append(f"• Process Improvement: {breakdown.process_improvement} activities - Drives long-term efficiency and scalability")
        if breakdown.mentoring > 0:
            high_impact.append(f"• Mentoring: {breakdown.mentoring} activities - Multiplies team capability and accelerates growth")
        if breakdown.cross_team_collaboration > 0:
            high_impact.append(f"• Cross-Team Collaboration: {breakdown.cross_team_collaboration} activities - Enables organizational alignment and delivery")
        
        if breakdown.knowledge_sharing > 0:
            medium_impact.append(f"• Knowledge Sharing: {breakdown.knowledge_sharing} activities - Improves team knowledge and reduces silos")
        if breakdown.documentation > 0:
            medium_impact.append(f"• Documentation: {breakdown.documentation} activities - Reduces onboarding time and improves maintainability")
        
        if breakdown.meetings > 0:
            low_impact.append(f"• Meetings: {breakdown.meetings} activities - Facilitates communication and coordination")
        if breakdown.administrative_work > 0:
            low_impact.append(f"• Administrative Work: {breakdown.administrative_work} activities - Supports operational requirements")
        
        if high_impact:
            explanations.append("High-Impact Contributions:\n")
            explanations.append("\n".join(high_impact))
            explanations.append("\n\n")
        
        if medium_impact:
            explanations.append("Medium-Impact Contributions:\n")
            explanations.append("\n".join(medium_impact))
            explanations.append("\n\n")
        
        if low_impact:
            explanations.append("Supporting Contributions:\n")
            explanations.append("\n".join(low_impact))
            explanations.append("\n\n")
        
        # Calculate impact distribution
        high_count = (breakdown.incident_support + breakdown.process_improvement + 
                     breakdown.mentoring + breakdown.cross_team_collaboration)
        medium_count = breakdown.knowledge_sharing + breakdown.documentation
        low_count = breakdown.meetings + breakdown.administrative_work
        
        if total > 0:
            high_pct = (high_count / total) * 100
            medium_pct = (medium_count / total) * 100
            low_pct = (low_count / total) * 100
            
            explanations.append(f"Impact Distribution:\n")
            explanations.append(f"• High-Impact Work: {high_count} activities ({high_pct:.1f}%)\n")
            explanations.append(f"• Medium-Impact Work: {medium_count} activities ({medium_pct:.1f}%)\n")
            explanations.append(f"• Supporting Work: {low_count} activities ({low_pct:.1f}%)")
        
        return ''.join(explanations)
    
    def _generate_top_impact_drivers(self, breakdown: CategoryBreakdown) -> str:
        """Generate list of top impact drivers"""
        drivers = []
        
        # Create list of (category, count, impact_level) tuples
        impact_categories = [
            ('Incident Support', breakdown.incident_support, 'Very High', 1.0),
            ('Process Improvement', breakdown.process_improvement, 'High', 0.9),
            ('Mentoring', breakdown.mentoring, 'High', 0.9),
            ('Cross-Team Collaboration', breakdown.cross_team_collaboration, 'High', 0.85),
            ('Knowledge Sharing', breakdown.knowledge_sharing, 'Medium', 0.7),
            ('Documentation', breakdown.documentation, 'Medium', 0.65),
        ]
        
        # Filter to only categories with activities and sort by weighted impact
        active_categories = [(name, count, level, count * weight) 
                           for name, count, level, weight in impact_categories if count > 0]
        active_categories.sort(key=lambda x: x[3], reverse=True)
        
        if not active_categories:
            return "No high-impact activities identified in the current analysis."
        
        drivers.append("Top Impact Drivers:\n\n")
        
        for i, (name, count, level, weighted) in enumerate(active_categories[:5], 1):
            drivers.append(f"{i}. {name} ({level} Impact)\n")
            drivers.append(f"   • {count} activities contributing to organizational value\n")
            
            # Add specific impact description
            if name == 'Incident Support':
                drivers.append(f"   • Directly protects revenue and customer satisfaction\n")
                drivers.append(f"   • Demonstrates reliability and technical expertise\n")
            elif name == 'Process Improvement':
                drivers.append(f"   • Creates lasting efficiency gains for the entire team\n")
                drivers.append(f"   • Reduces technical debt and improves scalability\n")
            elif name == 'Mentoring':
                drivers.append(f"   • Multiplies team capability and accelerates skill development\n")
                drivers.append(f"   • Reduces time-to-productivity for team members\n")
            elif name == 'Cross-Team Collaboration':
                drivers.append(f"   • Enables complex projects requiring multiple teams\n")
                drivers.append(f"   • Reduces organizational friction and improves delivery\n")
            elif name == 'Knowledge Sharing':
                drivers.append(f"   • Elevates team technical knowledge and best practices\n")
                drivers.append(f"   • Reduces knowledge silos and improves decision-making\n")
            elif name == 'Documentation':
                drivers.append(f"   • Reduces onboarding time and support burden\n")
                drivers.append(f"   • Improves system maintainability and reduces errors\n")
            
            drivers.append("\n")
        
        # Add summary
        total_high_impact = sum(count for name, count, level, _ in active_categories 
                               if level in ['Very High', 'High'])
        if total_high_impact > 0:
            drivers.append(f"\nSummary: {total_high_impact} high-impact activities identified that create significant organizational value.")
        
        return ''.join(drivers)
    
    def analyze(self, text: str) -> AnalysisResult:
        """
        Analyze text and return categorized results
        """
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Extract activities
        activities = self._extract_activities(processed_text)
        
        # Initialize category counts
        category_counts = {
            'mentoring': 0,
            'knowledge_sharing': 0,
            'documentation': 0,
            'incident_support': 0,
            'meetings': 0,
            'cross_team_collaboration': 0,
            'process_improvement': 0,
            'administrative_work': 0
        }
        
        # Classify each activity
        for activity in activities:
            category = self._classify_activity(activity)
            if category:
                category_counts[category] += 1
        
        # Create breakdown
        breakdown = CategoryBreakdown(**category_counts)
        
        # Calculate score
        total_activities = len(activities)
        score = self._calculate_invisible_work_score(breakdown, total_activities)
        
        # Generate summary
        summary = self._generate_performance_summary(breakdown, score, total_activities)
        
        # Calculate Recognition Gap Score
        recognition_gap_score = self._calculate_recognition_gap_score(breakdown, total_activities)
        recognition_gap_explanation = self._generate_recognition_gap_explanation(breakdown, recognition_gap_score, total_activities)
        recognition_gap_recommendations = self._generate_recognition_gap_recommendations(breakdown, recognition_gap_score)
        
        # Create Recognition Gap Analysis
        recognition_gap_analysis = RecognitionGapAnalysis(
            score=recognition_gap_score,
            explanation=recognition_gap_explanation,
            recommendations=recognition_gap_recommendations
        )
        
        # Calculate Impact Score
        impact_score = self._calculate_impact_score(breakdown, total_activities)
        impact_explanation = self._generate_impact_explanation(breakdown, impact_score, total_activities)
        top_impact_drivers = self._generate_top_impact_drivers(breakdown)
        
        # Create Impact Analysis
        impact_analysis = ImpactAnalysis(
            score=impact_score,
            explanation=impact_explanation,
            top_drivers=top_impact_drivers
        )
        
        # Generate AI Insights
        insights_generator = AIInsightsGenerator()
        ai_insights = insights_generator.generate_insights(breakdown, total_activities)
        
        return AnalysisResult(
            category_breakdown=breakdown,
            invisible_work_score=score,
            recognition_gap_analysis=recognition_gap_analysis,
            impact_analysis=impact_analysis,
            ai_insights=ai_insights,
            performance_summary=summary,
            total_activities=total_activities
        )

# Made with Bob
