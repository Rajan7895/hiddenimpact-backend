from typing import Dict, List
from app.schemas import CategoryBreakdown, AIInsights


class AIInsightsGenerator:
    """Generator for AI-powered insights from invisible work analysis"""
    
    def generate_insights(self, breakdown: CategoryBreakdown, total: int) -> AIInsights:
        """Generate comprehensive AI insights from activity breakdown"""
        
        top_hidden_contributions = self._identify_top_hidden_contributions(breakdown)
        leadership_indicators = self._analyze_leadership_indicators(breakdown)
        collaboration_strengths = self._assess_collaboration_strengths(breakdown)
        burnout_indicators = self._detect_burnout_indicators(breakdown, total)
        performance_highlights = self._generate_performance_highlights(breakdown, total)
        
        return AIInsights(
            top_hidden_contributions=top_hidden_contributions,
            leadership_indicators=leadership_indicators,
            collaboration_strengths=collaboration_strengths,
            burnout_indicators=burnout_indicators,
            performance_review_highlights=performance_highlights
        )
    
    def _identify_top_hidden_contributions(self, breakdown: CategoryBreakdown) -> List[Dict[str, str]]:
        """Identify the most valuable invisible work activities"""
        contributions = []
        
        if breakdown.mentoring > 0:
            contributions.append({
                "activity": "Mentoring & Coaching",
                "count": str(breakdown.mentoring),
                "value": "Multiplies team capability by developing others' skills and accelerating their growth trajectory",
                "why_it_matters": "Creates lasting organizational value through knowledge transfer and talent development"
            })
        
        if breakdown.incident_support > 0:
            contributions.append({
                "activity": "Incident Response & Support",
                "count": str(breakdown.incident_support),
                "value": "Protects revenue and customer satisfaction through rapid problem resolution",
                "why_it_matters": "Demonstrates technical expertise and reliability under pressure, often outside regular hours"
            })
        
        if breakdown.process_improvement > 0:
            contributions.append({
                "activity": "Process Improvement",
                "count": str(breakdown.process_improvement),
                "value": "Creates permanent efficiency gains that benefit the entire organization",
                "why_it_matters": "Reduces technical debt and scales team productivity through systematic improvements"
            })
        
        if breakdown.cross_team_collaboration > 0:
            contributions.append({
                "activity": "Cross-Team Collaboration",
                "count": str(breakdown.cross_team_collaboration),
                "value": "Enables complex initiatives requiring coordination across organizational boundaries",
                "why_it_matters": "Reduces silos and accelerates delivery of high-impact projects"
            })
        
        if breakdown.knowledge_sharing > 0:
            contributions.append({
                "activity": "Knowledge Sharing",
                "count": str(breakdown.knowledge_sharing),
                "value": "Elevates team technical knowledge and spreads best practices",
                "why_it_matters": "Improves decision-making quality and reduces repeated mistakes across the team"
            })
        
        # Sort by count and return top 5
        contributions.sort(key=lambda x: int(x["count"]), reverse=True)
        return contributions[:5]
    
    def _analyze_leadership_indicators(self, breakdown: CategoryBreakdown) -> Dict[str, str]:
        """Analyze leadership qualities demonstrated through activities"""
        indicators = {}
        
        # Mentoring indicator
        if breakdown.mentoring >= 3:
            indicators["mentoring"] = f"Strong: {breakdown.mentoring} mentoring activities demonstrate commitment to developing others and building team capability"
        elif breakdown.mentoring > 0:
            indicators["mentoring"] = f"Emerging: {breakdown.mentoring} mentoring activities show willingness to support team growth"
        else:
            indicators["mentoring"] = "Opportunity: Consider taking on mentoring responsibilities to develop leadership skills"
        
        # Initiative indicator
        if breakdown.process_improvement >= 3:
            indicators["initiative"] = f"Exceptional: {breakdown.process_improvement} process improvements show proactive problem-solving and ownership"
        elif breakdown.process_improvement > 0:
            indicators["initiative"] = f"Good: {breakdown.process_improvement} improvement initiatives demonstrate forward-thinking approach"
        else:
            indicators["initiative"] = "Opportunity: Look for process improvement opportunities to demonstrate initiative"
        
        # Knowledge sharing indicator
        if breakdown.knowledge_sharing >= 3:
            indicators["knowledge_sharing"] = f"Excellent: {breakdown.knowledge_sharing} knowledge sharing sessions establish thought leadership"
        elif breakdown.knowledge_sharing > 0:
            indicators["knowledge_sharing"] = f"Developing: {breakdown.knowledge_sharing} sharing activities contribute to team learning"
        else:
            indicators["knowledge_sharing"] = "Opportunity: Share expertise through presentations or documentation"
        
        # Process ownership indicator
        total_ownership = breakdown.process_improvement + breakdown.documentation
        if total_ownership >= 5:
            indicators["process_ownership"] = f"Strong: {total_ownership} activities show clear ownership of processes and standards"
        elif total_ownership > 0:
            indicators["process_ownership"] = f"Developing: {total_ownership} activities indicate growing process ownership"
        else:
            indicators["process_ownership"] = "Opportunity: Take ownership of team processes or documentation"
        
        return indicators
    
    def _assess_collaboration_strengths(self, breakdown: CategoryBreakdown) -> Dict[str, str]:
        """Assess collaboration and team enablement strengths"""
        strengths = {}
        
        # Cross-team work
        if breakdown.cross_team_collaboration >= 4:
            strengths["cross_team_work"] = f"Exceptional: {breakdown.cross_team_collaboration} cross-team activities demonstrate strong ability to work across organizational boundaries and drive alignment"
        elif breakdown.cross_team_collaboration >= 2:
            strengths["cross_team_work"] = f"Strong: {breakdown.cross_team_collaboration} cross-team collaborations show effective partnership skills"
        elif breakdown.cross_team_collaboration > 0:
            strengths["cross_team_work"] = f"Developing: {breakdown.cross_team_collaboration} cross-team activities indicate growing collaboration skills"
        else:
            strengths["cross_team_work"] = "Opportunity: Seek opportunities to collaborate with other teams"
        
        # Stakeholder engagement
        meeting_collab = breakdown.meetings + breakdown.cross_team_collaboration
        if meeting_collab >= 8:
            strengths["stakeholder_engagement"] = f"High: {meeting_collab} collaborative activities demonstrate strong stakeholder management and communication skills"
        elif meeting_collab >= 4:
            strengths["stakeholder_engagement"] = f"Moderate: {meeting_collab} collaborative activities show active stakeholder engagement"
        else:
            strengths["stakeholder_engagement"] = f"Limited: {meeting_collab} collaborative activities suggest opportunity to increase stakeholder engagement"
        
        # Team enablement
        enablement = breakdown.mentoring + breakdown.knowledge_sharing + breakdown.documentation
        if enablement >= 8:
            strengths["team_enablement"] = f"Exceptional: {enablement} team enablement activities create significant multiplier effect on team productivity"
        elif enablement >= 4:
            strengths["team_enablement"] = f"Strong: {enablement} team enablement activities contribute meaningfully to team capability"
        elif enablement > 0:
            strengths["team_enablement"] = f"Developing: {enablement} team enablement activities show commitment to team success"
        else:
            strengths["team_enablement"] = "Opportunity: Focus on activities that enable and multiply team effectiveness"
        
        return strengths
    
    def _detect_burnout_indicators(self, breakdown: CategoryBreakdown, total: int) -> Dict[str, str]:
        """Detect potential burnout risk factors"""
        indicators = {}
        risk_level = "Low"
        risk_factors = []
        
        # Excessive incident support
        if total > 0:
            incident_pct = (breakdown.incident_support / total) * 100
            if incident_pct > 40:
                risk_factors.append(f"High incident load ({breakdown.incident_support} activities, {incident_pct:.0f}% of total)")
                risk_level = "High"
            elif incident_pct > 25:
                risk_factors.append(f"Elevated incident support ({breakdown.incident_support} activities, {incident_pct:.0f}% of total)")
                if risk_level == "Low":
                    risk_level = "Moderate"
        
        # High meeting load
        if total > 0:
            meeting_pct = (breakdown.meetings / total) * 100
            if meeting_pct > 35:
                risk_factors.append(f"Excessive meetings ({breakdown.meetings} activities, {meeting_pct:.0f}% of total)")
                risk_level = "High"
            elif meeting_pct > 25:
                risk_factors.append(f"High meeting load ({breakdown.meetings} activities, {meeting_pct:.0f}% of total)")
                if risk_level == "Low":
                    risk_level = "Moderate"
        
        # Heavy support burden
        support_load = breakdown.incident_support + breakdown.mentoring
        if support_load >= 10:
            risk_factors.append(f"Heavy support burden ({support_load} support activities)")
            if risk_level == "Low":
                risk_level = "Moderate"
        
        # Too much invisible work
        invisible_work = (breakdown.mentoring + breakdown.knowledge_sharing + 
                         breakdown.cross_team_collaboration + breakdown.incident_support + 
                         breakdown.documentation)
        if total > 0:
            invisible_pct = (invisible_work / total) * 100
            if invisible_pct > 80:
                risk_factors.append(f"Very high invisible work ratio ({invisible_pct:.0f}% of activities)")
                risk_level = "High"
            elif invisible_pct > 65:
                risk_factors.append(f"High invisible work ratio ({invisible_pct:.0f}% of activities)")
                if risk_level == "Low":
                    risk_level = "Moderate"
        
        indicators["risk_level"] = risk_level
        
        if risk_factors:
            indicators["risk_factors"] = "; ".join(risk_factors)
            indicators["recommendation"] = self._get_burnout_recommendation(risk_level)
        else:
            indicators["risk_factors"] = "No significant burnout indicators detected"
            indicators["recommendation"] = "Continue maintaining healthy work-life balance"
        
        return indicators
    
    def _get_burnout_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on burnout risk level"""
        if risk_level == "High":
            return "URGENT: Discuss workload with manager. Consider delegating, saying no to new commitments, and taking time off"
        elif risk_level == "Moderate":
            return "CAUTION: Monitor workload closely. Set boundaries on meetings and support requests. Prioritize high-impact work"
        else:
            return "Maintain current balance while being mindful of workload increases"
    
    def _generate_performance_highlights(self, breakdown: CategoryBreakdown, total: int) -> List[str]:
        """Generate ready-to-use performance review bullet points"""
        highlights = []
        
        # Create weighted list of all activities for prioritization
        activity_scores = []
        
        # Mentoring (High priority)
        if breakdown.mentoring > 0:
            activity_scores.append((
                breakdown.mentoring * 1.0,  # Weight
                f"Mentored {breakdown.mentoring} team member{'s' if breakdown.mentoring > 1 else ''}, "
                f"accelerating skill development and building organizational capability"
            ))
        
        # Incident Support (High priority)
        if breakdown.incident_support > 0:
            activity_scores.append((
                breakdown.incident_support * 0.95,
                f"Contributed to organizational resilience through {breakdown.incident_support} "
                f"incident response activit{'ies' if breakdown.incident_support > 1 else 'y'}, "
                f"protecting customer satisfaction and revenue"
            ))
        
        # Process Improvement (High priority)
        if breakdown.process_improvement > 0:
            activity_scores.append((
                breakdown.process_improvement * 0.9,
                f"Improved operational efficiency through {breakdown.process_improvement} "
                f"process improvement initiative{'s' if breakdown.process_improvement > 1 else ''}, "
                f"creating lasting value for the team"
            ))
        
        # Cross-team Collaboration (High priority)
        if breakdown.cross_team_collaboration > 0:
            activity_scores.append((
                breakdown.cross_team_collaboration * 0.85,
                f"Enabled cross-functional success through {breakdown.cross_team_collaboration} "
                f"collaborative effort{'s' if breakdown.cross_team_collaboration > 1 else ''}, "
                f"reducing organizational silos and accelerating delivery"
            ))
        
        # Knowledge Sharing (Medium priority)
        if breakdown.knowledge_sharing > 0:
            activity_scores.append((
                breakdown.knowledge_sharing * 0.7,
                f"Elevated team technical knowledge through {breakdown.knowledge_sharing} "
                f"knowledge sharing session{'s' if breakdown.knowledge_sharing > 1 else ''}, "
                f"improving decision-making quality"
            ))
        
        # Documentation (Medium priority)
        if breakdown.documentation > 0:
            activity_scores.append((
                breakdown.documentation * 0.65,
                f"Enhanced team efficiency through {breakdown.documentation} documentation "
                f"effort{'s' if breakdown.documentation > 1 else ''}, "
                f"reducing onboarding time and support burden"
            ))
        
        # Administrative Work (Lower priority, but still valuable)
        if breakdown.administrative_work > 0:
            activity_scores.append((
                breakdown.administrative_work * 0.3,
                f"Supported team operations through {breakdown.administrative_work} "
                f"administrative activit{'ies' if breakdown.administrative_work > 1 else 'y'}, "
                f"ensuring smooth workflow and compliance"
            ))
        
        # Meetings (Lower priority)
        if breakdown.meetings > 0:
            activity_scores.append((
                breakdown.meetings * 0.25,
                f"Facilitated alignment and communication through {breakdown.meetings} "
                f"collaborative meeting{'s' if breakdown.meetings > 1 else ''}, "
                f"driving team coordination"
            ))
        
        # Sort by weighted score and take top activities
        activity_scores.sort(key=lambda x: x[0], reverse=True)
        highlights = [highlight for _, highlight in activity_scores[:5]]
        
        # If we have multiple high-impact categories, add a summary highlight
        high_impact_count = sum([
            1 for count in [breakdown.mentoring, breakdown.incident_support,
                          breakdown.process_improvement, breakdown.cross_team_collaboration]
            if count > 0
        ])
        
        if high_impact_count >= 3 and total >= 10 and len(highlights) < 5:
            highlights.append(
                f"Demonstrated exceptional breadth of contribution across {high_impact_count} "
                f"high-impact areas with {total} documented activities, showing strong commitment "
                f"to team and organizational success"
            )
        
        # Ensure we always have at least 3 highlights if any activities exist
        if total > 0 and len(highlights) < 3:
            # Add generic highlights based on total activity count
            if len(highlights) < 3:
                highlights.append(
                    f"Actively contributed to team success through {total} documented activities "
                    f"across multiple areas of responsibility"
                )
            if len(highlights) < 3:
                highlights.append(
                    "Demonstrated commitment to team enablement and organizational effectiveness "
                    "through consistent invisible work contributions"
                )
            if len(highlights) < 3:
                highlights.append(
                    "Supported team productivity and collaboration through various behind-the-scenes "
                    "activities that drive collective success"
                )
        
        # Return 3-5 highlights
        return highlights[:5]

# Made with Bob
