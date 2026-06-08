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
    
    def _calculate_hidden_hero_score(self, impact_score: int, recognition_gap_score: int) -> float:
        """
        Calculate Hidden Hero Score
        Formula: (impact_score * 0.6) + (recognition_gap_score * 0.4)
        """
        return (impact_score * 0.6) + (recognition_gap_score * 0.4)
    
    def _get_hidden_hero_classification(self, score: float) -> str:
        """
        Classify Hidden Hero based on score
        90-100: Elite Hidden Hero
        80-89: Hidden Hero
        70-79: Emerging Hidden Hero
        Below 70: Not Classified
        """
        if score >= 90:
            return "Elite Hidden Hero"
        elif score >= 80:
            return "Hidden Hero"
        elif score >= 70:
            return "Emerging Hidden Hero"
        else:
            return "Not Classified"
    
    def _generate_hidden_hero_analysis(self, score: float, classification: str,
                                      impact_score: int, recognition_gap_score: int,
                                      breakdown: CategoryBreakdown, total: int) -> str:
        """Generate detailed Hidden Hero analysis"""
        analysis = []
        
        # Header
        analysis.append(f"Hidden Hero Score: {score:.1f}/100\n")
        analysis.append(f"Classification: {classification}\n\n")
        
        # Classification-specific explanation
        if classification == "Elite Hidden Hero":
            analysis.append("🏆 ELITE HIDDEN HERO STATUS\n\n")
            analysis.append("This employee represents the pinnacle of invisible work contribution. They consistently deliver exceptional organizational value while operating largely outside traditional recognition systems. Their work is both high-impact and systematically undervalued.\n\n")
        elif classification == "Hidden Hero":
            analysis.append("⭐ HIDDEN HERO STATUS\n\n")
            analysis.append("This employee demonstrates strong hidden hero characteristics, consistently contributing high-value work that often goes unrecognized. Their efforts significantly impact team and organizational success beyond what traditional metrics capture.\n\n")
        elif classification == "Emerging Hidden Hero":
            analysis.append("🌟 EMERGING HIDDEN HERO STATUS\n\n")
            analysis.append("This employee shows clear hidden hero potential, with growing contributions in high-impact invisible work areas. They are building a strong foundation of team-enabling activities that deserve greater recognition.\n\n")
        else:
            analysis.append("While this employee contributes valuable work, their current activity profile doesn't yet meet the threshold for Hidden Hero classification. There are opportunities to increase impact in invisible work categories.\n\n")
        
        # Score breakdown
        analysis.append("Score Breakdown:\n")
        analysis.append(f"• Impact Score: {impact_score}/100 (60% weight)\n")
        analysis.append(f"  - Measures organizational value created\n")
        analysis.append(f"• Recognition Gap: {recognition_gap_score}/100 (40% weight)\n")
        analysis.append(f"  - Measures work likely invisible in traditional metrics\n\n")
        
        # Why they qualify (or don't)
        if score >= 70:
            analysis.append("Why This Employee Qualifies:\n\n")
            
            # High impact activities
            high_impact_count = (breakdown.incident_support + breakdown.process_improvement +
                               breakdown.mentoring + breakdown.cross_team_collaboration)
            if high_impact_count > 0:
                analysis.append(f"1. High-Impact Contributions ({high_impact_count} activities)\n")
                if breakdown.mentoring > 0:
                    analysis.append(f"   • Mentoring: {breakdown.mentoring} activities - Multiplying team capability\n")
                if breakdown.incident_support > 0:
                    analysis.append(f"   • Incident Support: {breakdown.incident_support} activities - Protecting system reliability\n")
                if breakdown.process_improvement > 0:
                    analysis.append(f"   • Process Improvement: {breakdown.process_improvement} activities - Driving efficiency\n")
                if breakdown.cross_team_collaboration > 0:
                    analysis.append(f"   • Cross-Team Collaboration: {breakdown.cross_team_collaboration} activities - Enabling organizational alignment\n")
                analysis.append("\n")
            
            # Invisible work
            invisible_count = (breakdown.mentoring + breakdown.knowledge_sharing +
                             breakdown.cross_team_collaboration + breakdown.incident_support +
                             breakdown.documentation)
            if invisible_count > 0 and total > 0:
                invisible_pct = (invisible_count / total) * 100
                analysis.append(f"2. Significant Invisible Work ({invisible_pct:.0f}% of activities)\n")
                analysis.append(f"   • {invisible_count} out of {total} activities fall into categories typically undervalued in performance reviews\n")
                analysis.append(f"   • This work creates lasting organizational value but often goes unrecognized\n\n")
            
            # Impact on team
            analysis.append("3. Team Enablement Focus\n")
            analysis.append("   • Consistently prioritizes work that multiplies team effectiveness\n")
            analysis.append("   • Demonstrates commitment to organizational health over individual visibility\n")
            analysis.append("   • Creates value that compounds over time through knowledge transfer and capability building\n\n")
            
        else:
            analysis.append("Opportunities for Growth:\n\n")
            analysis.append("To achieve Hidden Hero status, consider:\n")
            analysis.append("• Increasing involvement in high-impact invisible work (mentoring, cross-team collaboration)\n")
            analysis.append("• Taking on more process improvement initiatives\n")
            analysis.append("• Expanding knowledge sharing and documentation efforts\n")
            analysis.append("• Seeking opportunities for incident response and system reliability work\n\n")
        
        # Recognition recommendations
        if score >= 70:
            analysis.append("Recognition Recommendations:\n\n")
            analysis.append("Given this employee's Hidden Hero status, it's critical to:\n")
            analysis.append("• Explicitly highlight invisible work contributions in performance reviews\n")
            analysis.append("• Advocate for recognition systems that value team enablement\n")
            analysis.append("• Share this analysis with leadership to ensure proper visibility\n")
            analysis.append("• Consider for awards/recognition programs focused on team impact\n")
            analysis.append("• Use as a model for other team members on high-impact contribution patterns\n")
        
        return ''.join(analysis)
    
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
        
        # Calculate Hidden Hero Score
        hidden_hero_score = self._calculate_hidden_hero_score(impact_score, recognition_gap_score)
        hidden_hero_classification = self._get_hidden_hero_classification(hidden_hero_score)
        hidden_hero_analysis = self._generate_hidden_hero_analysis(
            hidden_hero_score,
            hidden_hero_classification,
            impact_score,
            recognition_gap_score,
            breakdown,
            total_activities
        )
        
        return AnalysisResult(
            category_breakdown=breakdown,
            invisible_work_score=score,
            recognition_gap_analysis=recognition_gap_analysis,
            impact_analysis=impact_analysis,
            ai_insights=ai_insights,
            performance_summary=summary,
            total_activities=total_activities,
            hidden_hero_score=hidden_hero_score,
            hidden_hero_classification=hidden_hero_classification,
            hidden_hero_analysis=hidden_hero_analysis
        )
    
    def _calculate_burnout_risk(self, breakdown: CategoryBreakdown, total_activities: int) -> str:
        """
        Calculate burnout risk level based on activity patterns
        Returns: "Low", "Moderate", or "High"
        """
        if total_activities == 0:
            return "Low"
        
        # High-stress categories
        incident_pct = (breakdown.incident_support / total_activities) * 100
        meeting_pct = (breakdown.meetings / total_activities) * 100
        admin_pct = (breakdown.administrative_work / total_activities) * 100
        
        # Calculate stress score
        stress_score = 0
        
        # Incident support is high stress
        if incident_pct > 30:
            stress_score += 3
        elif incident_pct > 20:
            stress_score += 2
        elif incident_pct > 10:
            stress_score += 1
        
        # Too many meetings
        if meeting_pct > 40:
            stress_score += 3
        elif meeting_pct > 30:
            stress_score += 2
        elif meeting_pct > 20:
            stress_score += 1
        
        # High administrative burden
        if admin_pct > 25:
            stress_score += 2
        elif admin_pct > 15:
            stress_score += 1
        
        # Total workload
        if total_activities > 50:
            stress_score += 2
        elif total_activities > 30:
            stress_score += 1
        
        # Determine risk level
        if stress_score >= 6:
            return "High"
        elif stress_score >= 3:
            return "Moderate"
        else:
            return "Low"
    
    def _get_top_strengths(self, breakdown: CategoryBreakdown) -> List[str]:
        """Get top 3 strength areas based on activity counts"""
        categories = [
            ("Mentoring", breakdown.mentoring),
            ("Knowledge Sharing", breakdown.knowledge_sharing),
            ("Documentation", breakdown.documentation),
            ("Incident Support", breakdown.incident_support),
            ("Meetings", breakdown.meetings),
            ("Cross-Team Collaboration", breakdown.cross_team_collaboration),
            ("Process Improvement", breakdown.process_improvement),
            ("Administrative Work", breakdown.administrative_work)
        ]
        
        # Sort by count descending
        sorted_categories = sorted(categories, key=lambda x: x[1], reverse=True)
        
        # Return top 3 with non-zero counts
        return [name for name, count in sorted_categories[:3] if count > 0]
    
    def analyze_for_comparison(self, text: str, filename: str) -> Dict:
        """
        Lightweight analysis for team comparison
        Returns key metrics without full analysis text
        """
        # Preprocess and extract activities
        processed_text = self._preprocess_text(text)
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
        total_activities = len(activities)
        
        # Calculate scores
        invisible_work_score = self._calculate_invisible_work_score(breakdown, total_activities)
        recognition_gap_score = self._calculate_recognition_gap_score(breakdown, total_activities)
        impact_score = self._calculate_impact_score(breakdown, total_activities)
        hidden_hero_score = self._calculate_hidden_hero_score(impact_score, recognition_gap_score)
        hidden_hero_classification = self._get_hidden_hero_classification(hidden_hero_score)
        burnout_risk = self._calculate_burnout_risk(breakdown, total_activities)
        
        # Get leadership indicators from AI insights
        insights_generator = AIInsightsGenerator()
        ai_insights = insights_generator.generate_insights(breakdown, total_activities)
        
        # Get top strengths
        top_strengths = self._get_top_strengths(breakdown)
        
        return {
            "filename": filename,
            "impact_score": impact_score,
            "recognition_gap_score": recognition_gap_score,
            "hidden_hero_score": hidden_hero_score,
            "hidden_hero_classification": hidden_hero_classification,
            "burnout_risk": burnout_risk,
            "invisible_work_score": invisible_work_score,
            "total_activities": total_activities,
            "category_breakdown": category_counts,
            "leadership_indicators": ai_insights.leadership_indicators,
            "top_strengths": top_strengths
        }
    
    def calculate_team_summary(self, employees: List[Dict]) -> Dict:
        """Calculate team-level aggregated metrics"""
        if not employees:
            return {
                "total_employees": 0,
                "average_impact_score": 0.0,
                "average_recognition_gap": 0.0,
                "hidden_heroes_count": 0,
                "burnout_risks_count": 0,
                "top_team_strengths": []
            }
        
        total_employees = len(employees)
        
        # Calculate averages
        avg_impact = sum(e["impact_score"] for e in employees) / total_employees
        avg_recognition_gap = sum(e["recognition_gap_score"] for e in employees) / total_employees
        
        # Count hidden heroes (score >= 70)
        hidden_heroes_count = sum(1 for e in employees if e["hidden_hero_score"] >= 70)
        
        # Count high burnout risks
        burnout_risks_count = sum(1 for e in employees if e["burnout_risk"] == "High")
        
        # Aggregate top team strengths
        strength_counts = {}
        for employee in employees:
            for strength in employee["top_strengths"]:
                strength_counts[strength] = strength_counts.get(strength, 0) + 1
        
        # Get top 5 team strengths
        top_team_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_team_strengths = [strength for strength, _ in top_team_strengths]
        
        return {
            "total_employees": total_employees,
            "average_impact_score": round(avg_impact, 1),
            "average_recognition_gap": round(avg_recognition_gap, 1),
            "hidden_heroes_count": hidden_heroes_count,
            "burnout_risks_count": burnout_risks_count,
            "top_team_strengths": top_team_strengths
        }
    
    def generate_leaderboards(self, employees: List[Dict]) -> Dict:
        """Generate ranked leaderboards for various metrics"""
        
        # Top Impact Contributors
        top_impact = sorted(employees, key=lambda x: x["impact_score"], reverse=True)[:5]
        top_impact_entries = [
            {
                "filename": e["filename"],
                "score": float(e["impact_score"]),
                "label": f"{e['impact_score']}/100"
            }
            for e in top_impact
        ]
        
        # Hidden Heroes (by hidden hero score)
        hidden_heroes = sorted(
            [e for e in employees if e["hidden_hero_score"] >= 70],
            key=lambda x: x["hidden_hero_score"],
            reverse=True
        )[:5]
        hidden_heroes_entries = [
            {
                "filename": e["filename"],
                "score": float(e["hidden_hero_score"]),
                "label": f"{e['hidden_hero_classification']} ({e['hidden_hero_score']:.1f})"
            }
            for e in hidden_heroes
        ]
        
        # Strongest Mentors (by mentoring count)
        strongest_mentors = sorted(
            employees,
            key=lambda x: x["category_breakdown"]["mentoring"],
            reverse=True
        )[:5]
        strongest_mentors_entries = [
            {
                "filename": e["filename"],
                "score": float(e["category_breakdown"]["mentoring"]),
                "label": f"{e['category_breakdown']['mentoring']} activities"
            }
            for e in strongest_mentors if e["category_breakdown"]["mentoring"] > 0
        ]
        
        # Best Collaborators (by cross-team collaboration)
        best_collaborators = sorted(
            employees,
            key=lambda x: x["category_breakdown"]["cross_team_collaboration"],
            reverse=True
        )[:5]
        best_collaborators_entries = [
            {
                "filename": e["filename"],
                "score": float(e["category_breakdown"]["cross_team_collaboration"]),
                "label": f"{e['category_breakdown']['cross_team_collaboration']} activities"
            }
            for e in best_collaborators if e["category_breakdown"]["cross_team_collaboration"] > 0
        ]
        
        # Highest Burnout Risk
        burnout_risk_map = {"High": 3, "Moderate": 2, "Low": 1}
        highest_burnout = sorted(
            employees,
            key=lambda x: (burnout_risk_map[x["burnout_risk"]], x["total_activities"]),
            reverse=True
        )[:5]
        highest_burnout_entries = [
            {
                "filename": e["filename"],
                "score": float(burnout_risk_map[e["burnout_risk"]]),
                "label": f"{e['burnout_risk']} Risk ({e['total_activities']} activities)"
            }
            for e in highest_burnout
        ]
        
        # Knowledge Sharing Champions
        knowledge_champions = sorted(
            employees,
            key=lambda x: x["category_breakdown"]["knowledge_sharing"],
            reverse=True
        )[:5]
        knowledge_champions_entries = [
            {
                "filename": e["filename"],
                "score": float(e["category_breakdown"]["knowledge_sharing"]),
                "label": f"{e['category_breakdown']['knowledge_sharing']} activities"
            }
            for e in knowledge_champions if e["category_breakdown"]["knowledge_sharing"] > 0
        ]
        
        return {
            "top_impact_contributors": top_impact_entries,
            "hidden_heroes": hidden_heroes_entries,
            "strongest_mentors": strongest_mentors_entries,
            "best_collaborators": best_collaborators_entries,
            "highest_burnout_risk": highest_burnout_entries,
            "knowledge_sharing_champions": knowledge_champions_entries
        }


# Made with Bob
