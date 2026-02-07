"""
Teacher service layer for dashboard analytics.
Business logic with SQLAlchemy async queries for teacher endpoints.
Zero-LLM compliance: All data from deterministic database queries.
"""

import uuid
from datetime import datetime, timedelta, date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from src.models.database import (
    User, Progress, Streak, QuizAttempt, Quiz, Question, Chapter
)
from src.models.teacher_schemas import (
    TeacherStats,
    TeacherStudent,
    QuizStats,
    QuizPerformance,
    QuestionAnalysis,
    EngagementMetrics,
    AtRiskStudent,
    RecentActivity
)


class TeacherService:
    """
    Service for teacher dashboard analytics and student management.
    All methods use async SQLAlchemy queries for efficient data retrieval.
    """

    def __init__(self, db: AsyncSession):
        self.db = db


    # =========================================================================
    # Dashboard Statistics
    # =========================================================================

    async def get_dashboard_stats(self) -> TeacherStats:
        """
        Get overall teacher dashboard statistics.
        Aggregates data across all students for dashboard overview.
        """
        # Count total students
        total_students_result = await self.db.execute(
            select(func.count(User.id)).where(User.role == "student")
        )
        total_students = total_students_result.scalar() or 0

        # Count active students (last login within 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_students_result = await self.db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.role == "student",
                    User.last_login >= week_ago
                )
            )
        )
        active_students = active_students_result.scalar() or 0

        # Calculate average quiz score
        avg_score_result = await self.db.execute(
            select(func.avg(QuizAttempt.score))
        )
        average_score = avg_score_result.scalar() or 0.0

        # Calculate average completion rate
        progress_result = await self.db.execute(
            select(func.count(Progress.id))
        )
        total_with_progress = progress_result.scalar() or 0

        if total_with_progress > 0:
            # Get total chapters count
            total_chapters_result = await self.db.execute(
                select(func.count(Chapter.id))
            )
            total_chapters = total_chapters_result.scalar() or 1

            # Get completed chapters count
            all_progress = await self.db.execute(
                select(Progress.completed_chapters)
            )
            completion_rate = (
                sum(len(p[0]) if p[0] else 0 for p in all_progress.all()) /
                (total_with_progress * total_chapters) * 100
            ) if total_with_progress > 0 else 0.0
        else:
            completion_rate = 0.0

        # Count at-risk students (no activity 3+ days AND progress < 30%)
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        total_chapters_result = await self.db.execute(
            select(func.count(Chapter.id))
        )
        total_chapters = total_chapters_result.scalar() or 1

        at_risk_result = await self.db.execute(
            select(func.count(User.id))
            .where(User.role == "student")
            .outerjoin(Progress, User.id == Progress.user_id)
            .outerjoin(Streak, User.id == Streak.user_id)
            .where(
                or_(
                    Progress.last_activity < three_days_ago,
                    Progress.last_activity.is_(None)
                )
            )
        )
        students_at_risk = at_risk_result.scalar() or 0

        # Count failing students (avg quiz score < 70%)
        failing_result = await self.db.execute(
            select(
                QuizAttempt.user_id,
                func.avg(QuizAttempt.score).label('avg_score')
            )
            .group_by(QuizAttempt.user_id)
            .having(func.avg(QuizAttempt.score) < 70)
        )
        students_failing_quizzes = len(failing_result.all())

        # Count students with zero streak
        zero_streak_result = await self.db.execute(
            select(func.count(Streak.id))
            .join(User, Streak.user_id == User.id)
            .where(
                and_(
                    User.role == "student",
                    Streak.current_streak == 0
                )
            )
        )
        students_with_stale_streaks = zero_streak_result.scalar() or 0

        return TeacherStats(
            total_students=total_students,
            active_students=active_students,
            average_score=round(average_score, 1),
            completion_rate=round(completion_rate, 1),
            students_at_risk=students_at_risk,
            students_failing_quizzes=students_failing_quizzes,
            students_with_stale_streaks=students_with_stale_streaks
        )


    # =========================================================================
    # Student List
    # =========================================================================

    async def get_all_students(self) -> List[TeacherStudent]:
        """
        Get list of all students with progress, streak, and quiz data.
        Eager loads relationships to prevent N+1 query problems.
        """
        # Query all student users with eager loaded progress and streak
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.progress),
                selectinload(User.streak)
            )
            .where(User.role == "student")
            .order_by(User.created_at.desc())
        )
        students = result.scalars().all()

        # Get total chapters count
        total_chapters_result = await self.db.execute(
            select(func.count(Chapter.id))
        )
        total_chapters = total_chapters_result.scalar() or 0

        student_list = []

        for student in students:
            # Calculate progress percentage
            completed_count = len(student.progress.completed_chapters) if student.progress else 0
            progress_pct = (completed_count / total_chapters * 100) if total_chapters > 0 else 0.0

            # Get streak
            streak = student.streak.current_streak if student.streak else 0

            # Get last activity
            last_activity = student.progress.last_activity if student.progress else student.last_login
            if last_activity:
                last_activity_str = last_activity.isoformat()
            else:
                last_activity_str = student.created_at.isoformat()

            # Get last 10 quiz scores
            quiz_scores_result = await self.db.execute(
                select(QuizAttempt.score)
                .where(QuizAttempt.user_id == student.id)
                .order_by(QuizAttempt.completed_at.desc())
                .limit(10)
            )
            quiz_scores = [s for s, in quiz_scores_result.all()]

            # Create display name from email
            name = student.email.split('@')[0].replace('.', ' ').replace('_', ' ').title()

            student_list.append(TeacherStudent(
                user_id=str(student.id),
                name=name,
                email=student.email,
                progress=round(progress_pct, 1),
                streak=streak,
                last_activity=last_activity_str,
                tier=student.tier,
                quiz_scores=quiz_scores if quiz_scores else None,
                completed_chapters=completed_count if completed_count > 0 else None,
                total_chapters=total_chapters if total_chapters > 0 else None,
                joined_date=student.created_at.isoformat()
            ))

        return student_list


    # =========================================================================
    # Quiz Statistics
    # =========================================================================

    async def get_quiz_stats(self) -> QuizStats:
        """
        Get overall quiz statistics across all quizzes and students.
        """
        # Count total attempts
        total_attempts_result = await self.db.execute(
            select(func.count(QuizAttempt.id))
        )
        total_attempts = total_attempts_result.scalar() or 0

        # Calculate average score
        avg_score_result = await self.db.execute(
            select(func.avg(QuizAttempt.score))
        )
        average_score = avg_score_result.scalar() or 0.0

        # Calculate pass rate (score >= 70)
        pass_count_result = await self.db.execute(
            select(func.count(QuizAttempt.id))
            .where(QuizAttempt.score >= 70)
        )
        pass_count = pass_count_result.scalar() or 0
        pass_rate = (pass_count / total_attempts * 100) if total_attempts > 0 else 0.0

        # Calculate completion rate (students who attempted at least one quiz)
        total_students_result = await self.db.execute(
            select(func.count(User.id)).where(User.role == "student")
        )
        total_students = total_students_result.scalar() or 1

        students_with_attempts_result = await self.db.execute(
            select(func.count(func.distinct(QuizAttempt.user_id)))
        )
        students_with_attempts = students_with_attempts_result.scalar() or 0

        completion_rate = (students_with_attempts / total_students * 100) if total_students > 0 else 0.0

        return QuizStats(
            total_attempts=total_attempts,
            average_score=round(average_score, 1),
            pass_rate=round(pass_rate, 1),
            completion_rate=round(completion_rate, 1)
        )


    async def get_quiz_performance(self) -> List[QuizPerformance]:
        """
        Get per-quiz performance breakdown with statistics.
        """
        # Get all quizzes with their chapters
        result = await self.db.execute(
            select(Quiz)
            .options(selectinload(Quiz.chapter))
            .order_by(Quiz.chapter_id)
        )
        quizzes = result.scalars().all()

        performance_list = []

        for quiz in quizzes:
            # Get attempts for this quiz
            attempts_result = await self.db.execute(
                select(QuizAttempt.score)
                .where(QuizAttempt.quiz_id == quiz.id)
            )
            scores = [s for s, in attempts_result.all()]

            if not scores:
                # Skip quizzes with no attempts
                continue

            total_attempts = len(scores)
            average_score = sum(scores) / len(scores)
            highest_score = max(scores)
            lowest_score = min(scores)

            # Calculate pass rate
            pass_count = sum(1 for s in scores if s >= 70)
            pass_rate = (pass_count / total_attempts * 100) if total_attempts > 0 else 0.0

            performance_list.append(QuizPerformance(
                quiz_id=str(quiz.id),
                quiz_title=quiz.title,
                total_attempts=total_attempts,
                average_score=round(average_score, 1),
                highest_score=float(highest_score),
                lowest_score=float(lowest_score),
                pass_rate=round(pass_rate, 1)
            ))

        return performance_list


    # =========================================================================
    # Question Analysis
    # =========================================================================

    async def get_question_analysis(self) -> List[QuestionAnalysis]:
        """
        Get question-level analytics for difficulty assessment.
        """
        # Get all questions
        result = await self.db.execute(
            select(Question)
            .options(selectinload(Quiz))
            .order_by(Question.quiz_id, Question.order)
        )
        questions = result.scalars().all()

        analysis_list = []

        for question in questions:
            # Get all attempts for this question
            # We need to find QuizAttempt records that include this question_id
            attempts_result = await self.db.execute(
                select(QuizAttempt)
                .where(QuizAttempt.quiz_id == question.quiz_id)
            )
            attempts = attempts_result.scalars().all()

            if not attempts:
                continue

            # Count attempts and correct answers
            total_attempts = 0
            correct_count = 0

            for attempt in attempts:
                answers = attempt.answers
                if question.id in answers:
                    total_attempts += 1
                    if answers[question.id] == question.correct_answer:
                        correct_count += 1

            if total_attempts == 0:
                continue

            # Calculate correct rate
            correct_rate = (correct_count / total_attempts * 100) if total_attempts > 0 else 0.0

            # Determine difficulty
            if correct_rate >= 80:
                difficulty = "easy"
            elif correct_rate >= 50:
                difficulty = "medium"
            else:
                difficulty = "hard"

            # Truncate question text
            question_text = question.question_text[:100]
            if len(question.question_text) > 100:
                question_text += "..."

            analysis_list.append(QuestionAnalysis(
                question_id=str(question.id),
                question_text=question_text,
                total_attempts=total_attempts,
                correct_rate=round(correct_rate, 1),
                average_time=0.0,  # Not currently tracked
                difficulty=difficulty
            ))

        return analysis_list


    # =========================================================================
    # Engagement Metrics
    # =========================================================================

    async def get_engagement_metrics(self) -> EngagementMetrics:
        """
        Get student engagement metrics including activity over time.
        """
        # Count active students (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_result = await self.db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.role == "student",
                    User.last_login >= week_ago
                )
            )
        )
        active_students = active_result.scalar() or 0

        # Calculate average completion rate
        total_chapters_result = await self.db.execute(
            select(func.count(Chapter.id))
        )
        total_chapters = total_chapters_result.scalar() or 1

        progress_result = await self.db.execute(
            select(Progress)
        )
        all_progress = progress_result.scalars().all()

        if all_progress:
            total_completion = sum(len(p.completed_chapters) for p in all_progress)
            completion_rate = (total_completion / (len(all_progress) * total_chapters) * 100)
        else:
            completion_rate = 0.0

        # Generate weekly activity array (last 7 days)
        weekly_activity = []
        for i in range(7):
            day_start = datetime.utcnow() - timedelta(days=i+1)
            day_end = datetime.utcnow() - timedelta(days=i)

            # Count quiz attempts on this day
            activity_result = await self.db.execute(
                select(func.count(QuizAttempt.id))
                .where(
                    and_(
                        QuizAttempt.completed_at >= day_start,
                        QuizAttempt.completed_at < day_end
                    )
                )
            )
            count = activity_result.scalar() or 0
            weekly_activity.insert(0, count)

        return EngagementMetrics(
            average_session_time="N/A",  # Session time not currently tracked
            active_students=active_students,
            completion_rate=round(completion_rate, 1),
            weekly_activity=weekly_activity
        )


    async def get_at_risk_students(self) -> List[AtRiskStudent]:
        """
        Identify at-risk students based on multiple risk factors.
        """
        # Get all students with their progress and streaks
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.progress),
                selectinload(User.streak)
            )
            .where(User.role == "student")
        )
        students = result.scalars().all()

        # Get total chapters for progress calculation
        total_chapters_result = await self.db.execute(
            select(func.count(Chapter.id))
        )
        total_chapters = total_chapters_result.scalar() or 1

        at_risk_list = []
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        for student in students:
            risk_factors = []
            risk_level = "low"

            # Calculate progress
            completed_count = len(student.progress.completed_chapters) if student.progress else 0
            progress_pct = (completed_count / total_chapters * 100) if total_chapters > 0 else 0.0

            # Get streak
            streak = student.streak.current_streak if student.streak else 0

            # Get last activity
            last_activity = student.progress.last_activity if student.progress else student.last_login

            # Check activity
            if last_activity and last_activity < seven_days_ago:
                risk_factors.append("No activity for 7+ days")
                risk_level = "high"
            elif last_activity and last_activity < three_days_ago:
                risk_factors.append("No activity for 3+ days")
                if risk_level != "high":
                    risk_level = "medium"

            # Check progress
            if progress_pct < 30:
                risk_factors.append(f"Low completion rate ({progress_pct:.1f}%)")
                if risk_level == "low":
                    risk_level = "medium"

            # Check streak
            if streak == 0:
                risk_factors.append("Zero current streak")
                if risk_level == "low":
                    risk_level = "low"

            # Check quiz performance
            quiz_avg_result = await self.db.execute(
                select(func.avg(QuizAttempt.score))
                .where(QuizAttempt.user_id == student.id)
            )
            quiz_avg = quiz_avg_result.scalar()

            if quiz_avg and quiz_avg < 60:
                risk_factors.append(f"Failing quizzes (avg: {quiz_avg:.1f}%)")
                risk_level = "high"
            elif quiz_avg and quiz_avg < 70:
                risk_factors.append(f"Below average quiz scores (avg: {quiz_avg:.1f}%)")
                if risk_level == "low":
                    risk_level = "medium"

            # Only include students with at least one risk factor
            if risk_factors:
                # Create display name
                name = student.email.split('@')[0].replace('.', ' ').replace('_', ' ').title()

                # Format last activity
                last_activity_str = last_activity.isoformat() if last_activity else student.created_at.isoformat()

                at_risk_list.append(AtRiskStudent(
                    user_id=str(student.id),
                    name=name,
                    email=student.email,
                    risk_level=risk_level,
                    risk_factors=risk_factors,
                    last_activity=last_activity_str,
                    progress=round(progress_pct, 1),
                    streak=streak
                ))

        # Sort by risk level (high first) then by last activity (oldest first)
        risk_priority = {"high": 0, "medium": 1, "low": 2}
        at_risk_list.sort(key=lambda x: (risk_priority[x.risk_level], x.last_activity))

        return at_risk_list


    # =========================================================================
    # Recent Activity
    # =========================================================================

    async def get_recent_activity(self, limit: int = 50) -> List[RecentActivity]:
        """
        Get recent student activities across quiz completions and logins.
        """
        activities = []

        # Get recent quiz attempts
        quiz_attempts_result = await self.db.execute(
            select(QuizAttempt, User, Quiz)
            .join(User, QuizAttempt.user_id == User.id)
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .where(User.role == "student")
            .order_by(QuizAttempt.completed_at.desc())
            .limit(limit)
        )
        quiz_activities = quiz_attempts_result.all()

        for attempt, user, quiz in quiz_activities:
            name = user.email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            activities.append(RecentActivity(
                activity_id=f"quiz_{attempt.id}",
                student_name=name,
                activity_type="quiz_completed",
                description=f"Completed '{quiz.title}' quiz with score {attempt.score}%",
                timestamp=attempt.completed_at.isoformat()
            ))

        # Get recent student logins
        recent_logins_result = await self.db.execute(
            select(User)
            .where(User.role == "student")
            .where(User.last_login >= datetime.utcnow() - timedelta(days=7))
            .order_by(User.last_login.desc())
            .limit(limit)
        )
        login_users = recent_logins_result.scalars().all()

        for user in login_users:
            name = user.email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            if user.last_login:
                activities.append(RecentActivity(
                    activity_id=f"login_{user.id}",
                    student_name=name,
                    activity_type="login",
                    description=f"Logged in to continue learning",
                    timestamp=user.last_login.isoformat()
                ))

        # Sort by timestamp (newest first) and limit
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        return activities[:limit]
