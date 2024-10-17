from application.factories import ProjectFactory, TaskFactory, RiskFactory, AssumptionFactory, IssueFactory, DependencyFactory, StakeholderFactory, CategoryFactory, ProjectStatusFactory, TaskStatusFactory, DayOfWeekFactory, AssetFactory, SkillFactory, TeamFactory, CommentFactory, UserFactory

from application.signals import create_default_data, create_default_skills, create_default_days
from application.models import TaskStatus, ProjectStatus, Skill, DayOfWeek, Project, Task, Risk, Stakeholder, Assumption, Issue, Dependency, Category, Team, Asset, Comment

from django.contrib.contenttypes.models import ContentType

from django.db.models.signals import post_migrate
from django.test import TestCase
from django.apps import apps

from django.db import IntegrityError
from django.core.exceptions import ValidationError

# Testing the signals (objects that are created after the migration - things like days of week, project and task status defaults)
class SignalTests(TestCase):
    def test_default_data_exists(self):
        # Verify TaskStatus
        self.assertTrue(TaskStatus.objects.filter(status_id=1, status_name='Unassigned').exists())
        self.assertTrue(TaskStatus.objects.filter(status_id=2, status_name='Assigned').exists())
        self.assertTrue(TaskStatus.objects.filter(status_id=3, status_name='Completed').exists())

        # Verify ProjectStatus
        self.assertTrue(ProjectStatus.objects.filter(status_id=1, status_name='New').exists())
        self.assertTrue(ProjectStatus.objects.filter(status_id=7, status_name='Closed').exists())

        # Verify Skills
        self.assertTrue(Skill.objects.filter(skill_id=1, skill_name='DHCP Configuration').exists())
        self.assertTrue(Skill.objects.filter(skill_id=19, skill_name='WAN Configuration').exists())

        # Verify Days of the Week
        self.assertTrue(DayOfWeek.objects.filter(day_name='Monday', abbreviation='Mon').exists())
        self.assertTrue(DayOfWeek.objects.filter(day_name='Friday', abbreviation='Fri').exists())

# Model Tests
class ProjectModelTest(TestCase):
    def test_project_creation(self):
        project = ProjectFactory()
        self.assertIsInstance(project, Project)
        self.assertIsNotNone(project.pk)
        self.assertEqual(project.project_status.status_name, 'New')  # Assuming status_id=1 is 'New'

    def test_project_creation_with_null_name(self):
        # Create and save related objects
        project_owner = AssetFactory()
        category = CategoryFactory()
        project_status = ProjectStatus.objects.get(status_id=1)  # Assuming initial data is present

        # Create a project instance with project_name=None
        project = Project(
            project_name=None,
            project_owner=project_owner,
            project_status=project_status,
            category=category,
            priority=1  # Provide required fields
        )

        # Validate the project (should raise ValidationError)
        with self.assertRaises(ValidationError) as context:
            project.full_clean()
        self.assertIn('project_name', context.exception.message_dict)

        # Attempt to save the project (should raise IntegrityError)
        with self.assertRaises(IntegrityError):
            project.save()

class TaskModelTest(TestCase):
    def test_task_creation(self):
        task = TaskFactory()
        self.assertIsInstance(task, Task)
        self.assertIsNotNone(task.pk)
        self.assertEqual(task.task_status.status_name, 'Unassigned')
        self.assertGreater(task.skills_required.count(), 0)

class RiskModelTest(TestCase):
    def test_risk_creation(self):
        risk = RiskFactory()
        self.assertIsInstance(risk, Risk)
        self.assertIsNotNone(risk.pk)
        # Verify that the risk_score is calculated correctly
        expected_risk_score = risk.probability * risk.impact
        self.assertEqual(risk.risk_score, expected_risk_score)

class AssumptionModelTest(TestCase):
    def test_assumption_creation(self):
        assumption = AssumptionFactory()
        self.assertIsNotNone(assumption.pk)

class IssueModelTest(TestCase):
    def test_issue_creation(self):
        issue = IssueFactory()
        self.assertIsNotNone(issue.pk)

class DependencyModelTest(TestCase):
    def test_dependency_creation(self):
        dependency = DependencyFactory()
        self.assertIsNotNone(dependency.pk)

class StakeholderModelTest(TestCase):
    def test_stakeholder_creation(self):
        stakeholder = StakeholderFactory()
        self.assertIsNotNone(stakeholder.pk)

class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = CategoryFactory()
        self.assertIsInstance(category, Category)
        self.assertIsNotNone(category.pk)
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())
        self.assertEqual(category.__str__(), category.category_name)

class ProjectStatusModelTest(TestCase):
    def test_project_status_creation(self):
        status = ProjectStatusFactory()
        self.assertIsInstance(status, ProjectStatus)
        self.assertIsNotNone(status.pk)
        self.assertEqual(status.__str__(), status.status_name)

class TaskStatusModelTest(TestCase):
    def test_task_status_creation(self):
        status = TaskStatusFactory()
        self.assertIsInstance(status, TaskStatus)
        self.assertIsNotNone(status.pk)
        self.assertEqual(status.__str__(), status.status_name)

class DayOfWeekModelTest(TestCase):
    def test_day_of_week_creation(self):
        day = DayOfWeekFactory()
        self.assertIsInstance(day, DayOfWeek)
        self.assertIsNotNone(day.pk)
        self.assertEqual(day.__str__(), day.day_name)

class AssetModelTest(TestCase):
    def test_asset_creation(self):
        asset = AssetFactory()
        self.assertIsInstance(asset, Asset)
        self.assertIsNotNone(asset.pk)
        self.assertTrue(asset.skills.exists())
        self.assertTrue(asset.teams.exists())
        self.assertTrue(asset.work_days.exists())
        self.assertEqual(asset.__str__(), asset.name)

class SkillModelTest(TestCase):
    def test_skill_creation(self):
        skill = SkillFactory()
        self.assertIsInstance(skill, Skill)
        self.assertIsNotNone(skill.pk)
        self.assertEqual(skill.__str__(), skill.skill_name)

class TeamModelTest(TestCase):
    def test_team_creation(self):
        team = TeamFactory()
        self.assertIsInstance(team, Team)
        self.assertIsNotNone(team.pk)
        self.assertEqual(team.__str__(), team.team_name)

class CommentModelTest(TestCase):
    def test_comment_on_project(self):
        user = UserFactory()
        project = ProjectFactory()
        comment_text = "This is a comment on a project."
        comment = CommentFactory(user=user, content_object=project, comment_text=comment_text)
        self.assertIsInstance(comment, Comment)
        self.assertEqual(comment.user, user)
        self.assertEqual(comment.content_object, project)
        self.assertEqual(comment.comment_text, comment_text)
        self.assertEqual(comment.content_type, ContentType.objects.get_for_model(Project))
        self.assertEqual(comment.object_id, project.pk)
        self.assertEqual(str(comment), f"Comment by {user} on {project}")

    def test_comment_on_task(self):
        user = UserFactory()
        task = TaskFactory()
        comment_text = "This is a comment on a task."
        comment = CommentFactory(user=user, content_object=task, comment_text=comment_text)
        self.assertIsInstance(comment, Comment)
        self.assertEqual(comment.user, user)
        self.assertEqual(comment.content_object, task)
        self.assertEqual(comment.comment_text, comment_text)
        self.assertEqual(comment.content_type, ContentType.objects.get_for_model(Task))
        self.assertEqual(comment.object_id, task.pk)
        self.assertEqual(str(comment), f"Comment by {user} on {task}")

    def test_comment_on_risk(self):
        user = UserFactory()
        risk = RiskFactory()
        comment_text = "This is a comment on a risk."
        comment = CommentFactory(user=user, content_object=risk, comment_text=comment_text)
        self.assertIsInstance(comment, Comment)
        self.assertEqual(comment.user, user)
        self.assertEqual(comment.content_object, risk)
        self.assertEqual(comment.comment_text, comment_text)
        self.assertEqual(comment.content_type, ContentType.objects.get_for_model(Risk))
        self.assertEqual(comment.object_id, risk.pk)
        self.assertEqual(str(comment), f"Comment by {user} on {risk}")
