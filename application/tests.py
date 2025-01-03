from application.factories import ProjectFactory, TaskFactory, RiskFactory, AssumptionFactory, IssueFactory, DependencyFactory, StakeholderFactory, CategoryFactory, DayOfWeekFactory, AssetFactory, SkillFactory, TeamFactory, CommentFactory, UserFactory

from application.forms import ProjectForm, ProjectUpdateForm, CreateTaskForm, EditTaskForm, TaskCompleteForm
from application.models import Skill, DayOfWeek, Project, Task, Risk, Category, Team, Asset, Comment, Assumption, Issue, Dependency, Stakeholder
from datetime import date, timedelta

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

# Testing the signals (objects that are created after the migration - things like days of week, project and task status defaults)
class SignalTests(TestCase):
    def test_default_data_exists(self):

        # Verify Skills
        self.assertTrue(Skill.objects.filter(skill_id=1, skill_name='DHCP Configuration').exists())
        self.assertTrue(Skill.objects.filter(skill_id=19, skill_name='WAN Configuration').exists())

        # Verify Days of the Week
        self.assertTrue(DayOfWeek.objects.filter(day_name='Monday', abbreviation='Mon').exists())
        self.assertTrue(DayOfWeek.objects.filter(day_name='Friday', abbreviation='Fri').exists())

class ForeignKeyTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Enable foreign key constraints for SQLite
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA foreign_keys = ON;')

# Model Tests

class SkillModelTest(TestCase):
    def test_skill_creation(self):
        """
        Test that a Skill instance is created successfully with valid data.
        """
        skill = SkillFactory()
        self.assertIsInstance(skill, Skill)
        self.assertIsNotNone(skill.pk)
        self.assertEqual(str(skill), skill.skill_name)

    def test_skill_creation_with_duplicate_name(self):
        """
        Test that creating a Skill with a duplicate skill_name raises an IntegrityError.
        """
        # Create the first Skill instance
        skill1 = SkillFactory(skill_name="Python Programming")
        self.assertIsNotNone(skill1.pk)

        # Attempt to create a second Skill with the same skill_name
        with self.assertRaises(IntegrityError):
            SkillFactory(skill_name="Python Programming")

    def test_skill_creation_with_long_name(self):
        """
        Test that creating a Skill with a skill_name longer than 50 characters raises a ValidationError.
        """
        # Define a skill_name longer than 50 characters
        long_skill_name = "A" * 51  # 51 characters

        # Build (but do not save) a Skill instance with the long skill_name
        skill = SkillFactory.build(skill_name=long_skill_name)

        # Validate the model fields
        with self.assertRaises(ValidationError) as context:
            skill.full_clean()

        # Check that 'skill_name' is in the validation errors
        self.assertIn('skill_name', context.exception.message_dict)
        self.assertIn('Ensure this value has at most 50 characters', context.exception.message_dict['skill_name'][0])

    def test_skill_str_method(self):
        """
        Test the __str__ method of the Skill model.
        """
        skill = SkillFactory(skill_name="Django Development")
        self.assertEqual(str(skill), "Django Development")

class CategoryModelTest(TestCase):
    def test_category_creation(self):
        """
        Test that a Category instance is created successfully with valid data.
        """
        category = CategoryFactory()
        self.assertIsInstance(category, Category)
        self.assertIsNotNone(category.pk)
        self.assertEqual(str(category), category.category_name)

    def test_category_creation_with_duplicate_name(self):
        """
        Test that creating a Category with a duplicate category_name raises an IntegrityError.
        """
        # Create the first Category instance
        category1 = CategoryFactory(category_name="Research")
        self.assertIsNotNone(category1.pk)

        # Attempt to create a second Category with the same category_name
        with self.assertRaises(IntegrityError):
            CategoryFactory(category_name="Research")

    def test_category_creation_with_long_name(self):
        """
        Test that creating a Category with a category_name longer than 50 characters raises a ValidationError.
        """
        # Define a category_name longer than 50 characters
        long_category_name = "A" * 51  # 51 characters

        # Build (but do not save) a Category instance with the long category_name
        category = CategoryFactory.build(category_name=long_category_name)

        # Validate the model fields
        with self.assertRaises(ValidationError) as context:
            category.full_clean()

        # Check that 'category_name' is in the validation errors
        self.assertIn('category_name', context.exception.message_dict)
        self.assertIn('Ensure this value has at most 50 characters', context.exception.message_dict['category_name'][0])

    def test_category_str_method(self):
        """
        Test the __str__ method of the Category model.
        """
        category = CategoryFactory(category_name="Development")
        self.assertEqual(str(category), "Development")

class DayOfWeekModelTest(TestCase):
    def test_dayofweek_creation(self):
        """
        Test that a DayOfWeek instance is created successfully with valid data.
        """
        day = DayOfWeekFactory(day_name="Munday", abbreviation="Mun")
        self.assertIsInstance(day, DayOfWeek)
        self.assertIsNotNone(day.pk)
        self.assertEqual(str(day), day.day_name)

    def test_dayofweek_creation_with_duplicate_day_name(self):
        """
        Test that creating a DayOfWeek with a duplicate day_name raises an IntegrityError.
        """
        # Create the first DayOfWeek instance
        day1 = DayOfWeekFactory(day_name="Humpday", abbreviation="Hum")
        self.assertIsNotNone(day1.pk)

        # Attempt to create a second DayOfWeek with the same day_name
        with self.assertRaises(IntegrityError):
            DayOfWeekFactory(day_name="Humpday", abbreviation="Hmp")  # Different abbreviation

    def test_dayofweek_creation_with_duplicate_abbreviation(self):
        """
        Test that creating a DayOfWeek with a duplicate abbreviation raises an IntegrityError.
        """
        # Create the first DayOfWeek instance
        day1 = DayOfWeekFactory(day_name="Fragday", abbreviation="Frg")
        self.assertIsNotNone(day1.pk)

        # Attempt to create a second DayOfWeek with the same abbreviation
        with self.assertRaises(IntegrityError):
            DayOfWeekFactory(day_name="Codday", abbreviation="Frg")  # Different day_name

    def test_dayofweek_creation_with_long_day_name(self):
        """
        Test that creating a DayOfWeek with a day_name longer than 10 characters raises a ValidationError.
        """
        # Define a day_name longer than 10 characters
        long_day_name = "A" * 11  # 11 characters

        # Build (but do not save) a DayOfWeek instance with the long day_name
        day = DayOfWeekFactory.build(day_name=long_day_name, abbreviation="Long")

        # Validate the model fields
        with self.assertRaises(ValidationError) as context:
            day.full_clean()

        # Check that 'day_name' is in the validation errors
        self.assertIn('day_name', context.exception.message_dict)
        self.assertIn('Ensure this value has at most 10 characters', context.exception.message_dict['day_name'][0])

    def test_dayofweek_creation_with_long_abbreviation(self):
        """
        Test that creating a DayOfWeek with an abbreviation longer than 3 characters raises a ValidationError.
        """
        # Define an abbreviation longer than 3 characters
        long_abbreviation = "Thur"  # 4 characters

        # Build (but do not save) a DayOfWeek instance with the long abbreviation
        day = DayOfWeekFactory.build(day_name="Thursday", abbreviation=long_abbreviation)

        # Validate the model fields
        with self.assertRaises(ValidationError) as context:
            day.full_clean()

        # Check that 'abbreviation' is in the validation errors
        self.assertIn('abbreviation', context.exception.message_dict)
        self.assertIn('Ensure this value has at most 3 characters', context.exception.message_dict['abbreviation'][0])

    def test_dayofweek_str_method(self):
        """
        Test the __str__ method of the DayOfWeek model.
        """
        day = DayOfWeekFactory(day_name="Doomsday", abbreviation="Dom")
        self.assertEqual(str(day), "Doomsday")

class AssetModelTest(TestCase):
    def test_asset_creation(self):
        """
        Test that an Asset instance is created successfully with valid data.
        """
        asset = AssetFactory.create()
        self.assertIsInstance(asset, Asset)
        self.assertIsNotNone(asset.pk)
        self.assertTrue(asset.skills.exists())
        # Teams and work_days are optional (blank=True)
        # Hence, they might not exist
        self.assertTrue(asset.teams.exists() or asset.teams.count() == 0)
        self.assertTrue(asset.work_days.exists() or asset.work_days.count() == 0)
        self.assertEqual(str(asset), asset.name)

    def test_asset_creation_with_duplicate_name(self):
        """
        Test that creating an Asset with a duplicate name raises an IntegrityError.
        """
        # Create the first Asset instance
        asset1 = AssetFactory.create(name="UniqueAsset")
        self.assertIsNotNone(asset1.pk)

        # Attempt to create a second Asset with the same name
        with self.assertRaises(IntegrityError):
            AssetFactory.create(name="UniqueAsset")

    def test_asset_creation_with_duplicate_email(self):
        """
        Test that creating an Asset with a duplicate email raises an IntegrityError.
        """
        # Create the first Asset instance
        asset1 = AssetFactory.create(email="uniqueemail@example.com")
        self.assertIsNotNone(asset1.pk)

        # Attempt to create a second Asset with the same email
        with self.assertRaises(IntegrityError):
            AssetFactory.create(email="uniqueemail@example.com")

    def test_asset_creation_with_long_name(self):
        """
        Test that creating an Asset with a name longer than 50 characters raises a ValidationError.
        """
        # Define a name longer than 50 characters
        long_name = "A" * 51  # 51 characters

        # Build (but do not save) an Asset instance with the long name
        asset = AssetFactory.build(name=long_name)

        # Validate the model fields
        with self.assertRaises(ValidationError) as context:
            asset.full_clean()

        # Check that 'name' is in the validation errors
        self.assertIn('name', context.exception.message_dict)
        self.assertIn('Ensure this value has at most 50 characters', context.exception.message_dict['name'][0])

    def test_asset_creation_with_long_email(self):
        """
        Test that creating an Asset with an email longer than 254 characters raises a ValidationError.
        """
        # Properly formatted, excessively long email
        local_part = "a" * 64  # Max local part length for emails
        domain_part = "b" * 189  # Ensures total length exceeds 254
        long_email = f"{local_part}@{domain_part}.com"  # Total length > 254

        # Build (but do not save) an Asset instance with the long email
        asset = AssetFactory.build(email=long_email)

        # Validate the model fields
        with self.assertRaises(ValidationError) as context:
            asset.full_clean()

        # Check that 'email' is in the validation errors
        self.assertIn('email', context.exception.message_dict)
        self.assertIn('Enter a valid email address.', context.exception.message_dict['email'][0])

    def test_asset_creation_with_invalid_email_format(self):
        """
        Test that creating an Asset with an invalid email format raises a ValidationError.
        """
        # Define an invalid email format
        invalid_email = "invalid-email-format"

        # Build (but do not save) an Asset instance with the invalid email
        asset = AssetFactory.build(email=invalid_email)

        # Validate the model fields
        with self.assertRaises(ValidationError) as context:
            asset.full_clean()

        # Check that 'email' is in the validation errors
        self.assertIn('email', context.exception.message_dict)
        self.assertIn('Enter a valid email address.', context.exception.message_dict['email'][0])

    def test_asset_creation_with_no_skills(self):
        """
        Test that creating an Asset without any associated skills raises a ValidationError.
        """
        # Create (save) an Asset instance
        asset = AssetFactory.create()

        # Clear any skills that might have been added by the factory
        asset.skills.clear()

        # Validate the model fields
        with self.assertRaises(ValidationError) as context:
            asset.full_clean()

        # Check that 'skills' is in the validation errors
        self.assertIn('skills', context.exception.message_dict)
        self.assertIn('Asset must have at least one skill.', context.exception.message_dict['skills'][0])

    def test_asset_creation_with_no_name(self):
        """
        Test that creating an Asset without a name raises a ValidationError.
        """
        # Build (but do not save) an Asset instance without a name
        asset = AssetFactory.build(name=None)

        # Validate the model fields
        with self.assertRaises(ValidationError) as context:
            asset.full_clean()

        # Check that 'name' is in the validation errors
        self.assertIn('name', context.exception.message_dict)
        self.assertIn('This field cannot be null.', context.exception.message_dict['name'][0])

    def test_asset_str_method(self):
        """
        Test the __str__ method of the Asset model.
        """
        asset = AssetFactory.create(name="Shwan Cartier")
        self.assertEqual(str(asset), "Shwan Cartier")

class ProjectModelTest(TestCase):
    def test_project_creation(self):
        project = ProjectFactory()
        self.assertIsInstance(project, Project)
        self.assertIsNotNone(project.pk)
        self.assertEqual(project.project_status, 1)  # Assuming status_id=1 is 'New'

    def test_project_creation_with_null_name(self):
        # Create and save related objects
        project_owner = AssetFactory()
        category = CategoryFactory()
        project_status = 1  # Assuming initial data is present

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

class TaskModelTest(ForeignKeyTestCase):
    def setUp(self):
        # Create default objects used across multiple tests
        self.project = ProjectFactory.create()
        self.skill = SkillFactory.create()
        self.asset = AssetFactory.create()

    def test_task_creation_successful(self):
        """
        Test that a Task instance is created successfully with valid data.
        """
        task = TaskFactory.create(project=self.project)
        self.assertIsInstance(task, Task)
        self.assertIsNotNone(task.pk)
        self.assertEqual(task.project, self.project)
        self.assertIn(task.task_status, dict(Task.STATUS_CHOICES))
        self.assertIn(task.priority, dict(Task.PRIORITY_CHOICES))
        self.assertIsInstance(task.planned_start_date, date)
        self.assertIsInstance(task.planned_end_date, date)
        self.assertIsInstance(task.due_date, date)
        self.assertIsInstance(task.estimated_time_to_complete, timedelta)
        self.assertTrue(task.skills_required.exists())
        self.assertEqual(str(task), task.task_name)

    def test_task_missing_mandatory_fields(self):
        """
        Test that omitting mandatory fields raises appropriate errors.
        Mandatory fields: task_name, project, priority
        """
        # Omitting task_name
        task = TaskFactory.build(task_name=None)
        with self.assertRaises(ValidationError) as context:
            task.full_clean()
        self.assertIn('task_name', context.exception.message_dict)
        self.assertIn('This field cannot be null.', context.exception.message_dict['task_name'][0])

        # Omitting project
        task = TaskFactory.build(project=None)
        with self.assertRaises(ValidationError) as context:
            task.full_clean()
        self.assertIn('project', context.exception.message_dict)
        self.assertIn('This field cannot be null.', context.exception.message_dict['project'][0])

        # Omitting priority
        task = TaskFactory.build(priority=None)
        with self.assertRaises(ValidationError) as context:
            task.full_clean()
        self.assertIn('priority', context.exception.message_dict)
        self.assertIn('This field cannot be null.', context.exception.message_dict['priority'][0])

    def test_task_name_over_max_length(self):
        """
        Test that creating a Task with a task_name longer than 50 characters raises a ValidationError.
        """
        long_task_name = "A" * 51  # 51 characters
        task = TaskFactory.build(task_name=long_task_name)
        with self.assertRaises(ValidationError) as context:
            task.full_clean()
        self.assertIn('task_name', context.exception.message_dict)
        self.assertIn('Ensure this value has at most 50 characters', context.exception.message_dict['task_name'][0])

    def test_task_skills_required_empty(self):
        """
        Test that creating a Task without any associated skills_required raises a ValidationError.
        """
        # Create (save) a Task instance
        task = TaskFactory.create()
    
        # Clear any skills that might have been added by the factory
        task.skills_required.clear()
    
        # Validate the model fields
        with self.assertRaises(ValidationError) as context:
            task.full_clean()
    
        # Check that 'skills_required' is in the validation errors
        self.assertIn('skills_required', context.exception.message_dict)
        self.assertIn('Task must have at least one skill required.', context.exception.message_dict['skills_required'][0])

    def test_task_status_updates_correctly_when_assigned_to_set(self):
        """
        Test that task_status updates to 'Assigned' when assigned_to is set.
        """
        task = TaskFactory.create(task_status=1, assigned_to=self.asset)  # Initially 'Unassigned'
        # Refresh from DB to capture the updated status
        task.refresh_from_db()
        self.assertEqual(task.task_status, 2)  # Should update to 'Assigned'

    def test_task_status_updates_correctly_when_assigned_to_unset(self):
        """
        Test that task_status updates to 'Unassigned' when assigned_to is removed.
        """
        task = TaskFactory.create(task_status=2, assigned_to=self.asset)  # Initially 'Assigned'
        task.assigned_to = None
        task.save()
        task.refresh_from_db()
        self.assertEqual(task.task_status, 1)  # Should update to 'Unassigned'

    def test_task_status_not_updated_if_completed(self):
        """
        Test that task_status remains 'Completed' even if assigned_to is set or unset.
        """
        # Task is 'Completed'
        task = TaskFactory.create(task_status=3, assigned_to=self.asset)
        # Try setting assigned_to to another asset
        another_asset = AssetFactory.create()
        task.assigned_to = another_asset
        task.save()
        task.refresh_from_db()
        self.assertEqual(task.task_status, 3)  # Should remain 'Completed'

        # Try unsetting assigned_to
        task.assigned_to = None
        task.save()
        task.refresh_from_db()
        self.assertEqual(task.task_status, 3)  # Should remain 'Completed'

    def test_task_prereq_task_set_correctly(self):
        """
        Test setting and unsetting a prerequisite task.
        """
        prereq = TaskFactory.create(task_name="Prerequisite Task", project=self.project)
        task = TaskFactory.create(prereq_task=prereq, project=self.project)
        self.assertEqual(task.prereq_task, prereq)

        # Unset prereq_task
        task.prereq_task = None
        task.save()
        task.refresh_from_db()
        self.assertIsNone(task.prereq_task)

    def test_task_delay_reason_optional(self):
        """
        Test that delay_reason can be left blank or provided.
        """
        # Task with delay_reason
        task_with_delay = TaskFactory.create(delay_reason="Awaiting resources.")
        self.assertEqual(task_with_delay.delay_reason, "Awaiting resources.")

        # Task without delay_reason
        task_without_delay = TaskFactory.create(delay_reason=None)
        self.assertIsNone(task_without_delay.delay_reason)

    def test_task_duration_fields_validation(self):
        """
        Test that assigning invalid durations to duration fields raises a ValidationError.
        """
        # Assign a string to estimated_time_to_complete
        task = TaskFactory.build(estimated_time_to_complete="invalid-duration")
        with self.assertRaises(ValidationError) as context:
            task.full_clean()
        self.assertIn('estimated_time_to_complete', context.exception.message_dict)
        self.assertIn('has an invalid format', context.exception.message_dict['estimated_time_to_complete'][0])

        # Assign a string to actual_time_to_complete
        task = TaskFactory.build(actual_time_to_complete="invalid-duration")
        with self.assertRaises(ValidationError) as context:
            task.full_clean()
        self.assertIn('actual_time_to_complete', context.exception.message_dict)
        self.assertIn('has an invalid format', context.exception.message_dict['actual_time_to_complete'][0])

    def test_task_halo_ref_optional(self):
        """
        Test that halo_ref can be left blank or provided.
        """
        # Task with halo_ref
        task_with_halo = TaskFactory.create(halo_ref=12345)
        self.assertEqual(task_with_halo.halo_ref, 12345)

        # Task without halo_ref
        task_without_halo = TaskFactory.create(halo_ref=None)
        self.assertIsNone(task_without_halo.halo_ref)

    def test_task_str_method(self):
        """
        Test the __str__ method of the Task model.
        """
        task = TaskFactory.create(task_name="Design Database Schema")
        self.assertEqual(str(task), "Design Database Schema")

    def test_task_get_absolute_url(self):
        """
        Test that get_absolute_url returns the correct URL.
        """
        task = TaskFactory.create(project=self.project)
        expected_url = f"/projects/{self.project.pk}/tasks/{task.pk}/"
        self.assertEqual(task.get_absolute_url(), expected_url)

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

# Form Tests
# Project Create Form
class ProjectTestCase(TestCase):
    def setUp(self):
        """
        Set up test data for the tests.
        """
        self.category = Category.objects.create(category_name='Test Category')
        self.project_owner = Asset.objects.create(
            name='Test Owner',
            normal_work_week=40  # Providing required field
        )

    def test_create_project_valid(self):
        """
        Test creating a project with valid data.
        """
        data = {
            'project_name': 'Test Project',
            'planned_start_date': '2023-10-01',
            'original_target_end_date': '2023-12-31',
            'project_owner': self.project_owner.asset_id,  # Use 'asset_id' instead of 'id'
            'priority': 2,  # Medium priority
        }
        form = ProjectForm(data=data)
        self.assertTrue(form.is_valid(), "Form should be valid with correct data.")
        project = form.save()
        self.assertEqual(project.project_name, 'Test Project')
        self.assertEqual(project.project_owner, self.project_owner)
        self.assertEqual(project.priority, 2)
        self.assertEqual(Project.objects.count(), 1)

    def test_create_project_end_date_before_start_date(self):
        """
        Test that the form validation prevents the end date from being before the start date.
        """
        data = {
            'project_name': 'Invalid Project',
            'planned_start_date': '2023-12-31',
            'original_target_end_date': '2023-10-01',  # End date before start date
            'project_owner': self.project_owner.asset_id,  # Use 'asset_id'
            'priority': 2,
        }
        form = ProjectForm(data=data)
        self.assertFalse(form.is_valid(), "Form should be invalid when end date is before start date.")
        self.assertIn('original_target_end_date', form.errors)
        self.assertEqual(
            form.errors['original_target_end_date'][0],
            'End date cannot be earlier than the start date.'
        )

# Project Edit Form
class ProjectUpdateFormTestCase(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        """
        # Create a category and asset for the project
        self.category = Category.objects.create(category_name='Test Category')
        self.project_owner = Asset.objects.create(
            name='Test Owner',
            normal_work_week=40
        )
        self.planned_start_date = date(2023, 10, 1)
        self.original_target_end_date = date(2023, 12, 31)

        # Create an initial project instance
        self.project = Project.objects.create(
            project_name='Initial Project',
            project_description='Initial description',
            planned_start_date=self.planned_start_date,
            original_target_end_date=self.original_target_end_date,
            project_owner=self.project_owner,
            priority=2,
            category=self.category,
            halo_ref=1001,
            project_status=1
        )
    
    def test_edit_project_valid(self):
        data = {
            'project_name': 'Updated Project',
            'project_description': 'Updated description',
            'planned_start_date': self.project.planned_start_date,
            'original_target_end_date': self.project.original_target_end_date,
            'revised_target_end_date': '2024-01-31',
            'halo_ref': 2002,
            'actual_start_date': '2023-10-05',
            'actual_end_date': '2024-02-28',
            'project_owner': self.project_owner.asset_id,
            'project_status': 3,
            'category': self.category.category_id,
            'priority': 3,
        }
        form = ProjectUpdateForm(data=data, instance=self.project)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid(), "Form should be valid with all fields correctly filled.")
        updated_project = form.save()
        self.assertEqual(updated_project.project_name, 'Updated Project')
        self.assertEqual(updated_project.project_description, 'Updated description')
        self.assertEqual(updated_project.revised_target_end_date.strftime('%Y-%m-%d'), '2024-01-31')
        self.assertEqual(updated_project.halo_ref, 2002)
        self.assertEqual(updated_project.actual_start_date.strftime('%Y-%m-%d'), '2023-10-05')
        self.assertEqual(updated_project.actual_end_date.strftime('%Y-%m-%d'), '2024-02-28')
        self.assertEqual(updated_project.project_status, 3)
        self.assertEqual(updated_project.priority, 3)

    def test_edit_project_missing_mandatory_fields(self):
        """
        Test that the form is invalid when mandatory fields are missing.
        """
        data = {
            'project_name': '',  # Missing project name
            'project_description': '',  # Missing description
            'planned_start_date': self.project.planned_start_date,
            'original_target_end_date': self.project.original_target_end_date,
            'project_owner': '',  # Missing project owner
            'project_status': '',  # Missing project status
            'category': '',  # Missing category
            'priority': '',  # Missing priority
        }
        form = ProjectUpdateForm(data=data, instance=self.project)
        self.assertFalse(form.is_valid(), "Form should be invalid when mandatory fields are missing.")
        self.assertIn('project_name', form.errors)
        self.assertIn('project_description', form.errors)
        self.assertIn('project_owner', form.errors)
        self.assertIn('project_status', form.errors)
        self.assertIn('category', form.errors)
        self.assertIn('priority', form.errors)

    def test_edit_project_invalid_revised_end_date(self):
        """
        Test that the form is invalid when revised end date is earlier than actual start date.
        """
        data = {
            'project_name': 'Updated Project',
            'project_description': 'Updated description',
            'planned_start_date': self.project.planned_start_date,
            'original_target_end_date': self.project.original_target_end_date,
            'revised_target_end_date': '2023-09-30',  # Earlier than actual start date
            'halo_ref': 2002,
            'actual_start_date': '2023-10-05',
            'actual_end_date': '2024-02-28',
            'project_owner': self.project_owner.asset_id,
            'project_status': 3,
            'category': self.category.category_id,
            'priority': 3,
        }
        form = ProjectUpdateForm(data=data, instance=self.project)
        self.assertFalse(form.is_valid(), "Form should be invalid when revised end date is earlier than actual start date.")
        self.assertIn('revised_target_end_date', form.errors)
        self.assertEqual(
            form.errors['revised_target_end_date'][0],
            'Revised end date cannot be earlier than the actual start date.'
        )

    def test_edit_project_invalid_actual_dates(self):
        """
        Test that the form is invalid when actual end date is earlier than actual start date.
        """
        data = {
            'project_name': 'Updated Project',
            'project_description': 'Updated description',
            'planned_start_date': self.project.planned_start_date,
            'original_target_end_date': self.project.original_target_end_date,
            'halo_ref': 2002,
            'actual_start_date': '2023-10-05',
            'actual_end_date': '2023-09-30',  # Earlier than actual start date
            'project_owner': self.project_owner.asset_id,
            'project_status': 3,
            'category': self.category.category_id,
            'priority': 3,
        }
        form = ProjectUpdateForm(data=data, instance=self.project)
        self.assertFalse(form.is_valid(), "Form should be invalid when actual end date is earlier than actual start date.")
        self.assertIn('actual_end_date', form.errors)
        self.assertEqual(
            form.errors['actual_end_date'][0],
            'Actual end date cannot be earlier than the actual start date.'
        )

    def test_edit_project_change_planned_dates(self):
        """
        Test that the form is invalid when attempting to change planned start date or original target end date.
        """
        data = {
            'project_name': 'Updated Project',
            'project_description': 'Updated description',
            'planned_start_date': '2023-11-01',  # Attempt to change
            'original_target_end_date': '2024-01-31',  # Attempt to change
            'halo_ref': 2002,
            'actual_start_date': '2023-10-05',
            'actual_end_date': '2024-02-28',
            'project_owner': self.project_owner.asset_id,
            'project_status': 3,
            'category': self.category.category_id,
            'priority': 3,
        }
        form = ProjectUpdateForm(data=data, instance=self.project)
        self.assertFalse(form.is_valid(), "Form should be invalid when changing planned start date or original target end date.")
        self.assertIn('planned_start_date', form.errors)
        self.assertIn('original_target_end_date', form.errors)
        self.assertEqual(
            form.errors['planned_start_date'][0],
            'Planned start date cannot be changed once set.'
        )
        self.assertEqual(
            form.errors['original_target_end_date'][0],
            'Original target end date cannot be changed once set.'
        )

# Task Create Form
class CreateTaskFormTestCase(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        """
        # Create an Asset to act as the project owner
        self.project_owner = Asset.objects.create(
            name='Project Owner',
            normal_work_week=40
        )

        # Create a Project instance
        self.project = Project.objects.create(
            project_name='Test Project',
            planned_start_date=date(2023, 10, 1),
            original_target_end_date=date(2023, 12, 31),
            project_owner=self.project_owner,
            priority=2
        )

        # Create a Skill instance
        self.skill = Skill.objects.create(skill_name='Test Skill')

        # Create an Asset to assign to tasks
        self.assigned_to = Asset.objects.create(
            name='Assigned Asset',
            normal_work_week=40
        )
        self.assigned_to.skills.add(self.skill)

    def test_create_task_a(self):
        """
        Test creating Task A.
        """
        data = {
            'task_name': 'Task A',
            'task_details': 'Details for Task A',
            'priority': 2,  # Medium priority
            'planned_start_date': '2023-10-10',
            'planned_end_date': '2023-10-20',
            'due_date': '2023-10-20',
            'estimated_time_to_complete': '40 00:00:00',  # 40 days
            'skills_required': [self.skill.skill_id],
            'assigned_to': self.assigned_to.asset_id,
            'halo_ref': 1001,
        }
        form = CreateTaskForm(data=data, project=self.project)
        self.assertTrue(form.is_valid(), "Form should be valid with correct data for Task A.")
        task_a = form.save(commit=False)
        task_a.project = self.project
        task_a.save()
        form.save_m2m()  # Save ManyToMany relationships
        self.assertEqual(task_a.task_name, 'Task A')
        self.assertEqual(task_a.project, self.project)
        self.assertEqual(task_a.assigned_to, self.assigned_to)
        self.assertIn(self.skill, task_a.skills_required.all())

    def test_create_task_b_with_prerequisite(self):
        """
        Test creating Task B with Task A as its prerequisite.
        """
        # First, create Task A
        task_a = Task.objects.create(
            task_name='Task A',
            task_details='Details for Task A',
            priority=2,
            planned_start_date=date(2023, 10, 10),
            planned_end_date=date(2023, 10, 20),
            due_date=date(2023, 10, 20),
            estimated_time_to_complete=timedelta(hours=40),  # 40 hours
            project=self.project
        )
        task_a.skills_required.add(self.skill)

        # Now, create Task B with Task A as prerequisite
        data = {
            'task_name': 'Task B',
            'task_details': 'Details for Task B',
            'priority': 3,  # High priority
            'planned_start_date': '2023-10-21',
            'planned_end_date': '2023-10-30',
            'due_date': '2023-10-30',
            'estimated_time_to_complete': '32 00:00:00',  # 32 days
            'skills_required': [self.skill.skill_id],
            'assigned_to': self.assigned_to.asset_id,
            'halo_ref': 1002,
            'prereq_task': task_a.id,  # Set Task A as prerequisite
        }
        form = CreateTaskForm(data=data, project=self.project)
        self.assertTrue(form.is_valid(), "Form should be valid with Task A as prerequisite.")
        task_b = form.save(commit=False)
        task_b.project = self.project
        task_b.save()
        form.save_m2m()
        self.assertEqual(task_b.task_name, 'Task B')
        self.assertEqual(task_b.prereq_task, task_a)
        self.assertEqual(task_b.assigned_to, self.assigned_to)
        self.assertIn(self.skill, task_b.skills_required.all())

    # def test_task_invalid_dates(self):
    #     data = {
    #         'task_name': 'Task Invalid',
    #         'task_details': 'Invalid dates',
    #         'priority': 2,
    #         'planned_start_date': '2023-10-20',
    #         'planned_end_date': '2023-10-10',  # End date before start date
    #         'due_date': '2023-10-05',  # Due date before start date
    #         'estimated_time_to_complete': '40 00:00:00',
    #         'skills_required': [self.skill.skill_id],
    #         'assigned_to': self.assigned_to.asset_id,
    #         'halo_ref': 1003,
    #     }
    #     form = CreateTaskForm(data=data, project=self.project)
    #     self.assertFalse(form.is_valid(), "Form should be invalid with incorrect dates.")
    #     self.assertIn('planned_end_date', form.errors)
    #     self.assertIn('due_date', form.errors)

# Edit Task Form
class EditTaskFormTestCase(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        """
        # Create an Asset to act as the project owner
        self.project_owner = Asset.objects.create(
            name='Project Owner',
            normal_work_week=40
        )

        # Create a Project instance
        self.project = Project.objects.create(
            project_name='Test Project',
            planned_start_date=date(2023, 10, 1),
            original_target_end_date=date(2023, 12, 31),
            project_owner=self.project_owner,
            priority=2
        )

        # Create a Skill instance
        self.skill = Skill.objects.create(skill_name='Test Skill')

        # Create an Asset to assign to tasks
        self.assigned_to = Asset.objects.create(
            name='Assigned Asset',
            normal_work_week=40
        )
        self.assigned_to.skills.add(self.skill)

        # Create Task A
        self.task_a = Task.objects.create(
            task_name='Task A',
            task_details='Details for Task A',
            priority=2,
            planned_start_date=date(2023, 10, 10),
            planned_end_date=date(2023, 10, 20),
            due_date=date(2023, 10, 20),
            estimated_time_to_complete=timedelta(hours=40),  # 40 hours
            project=self.project,
            assigned_to=self.assigned_to
        )
        self.task_a.skills_required.add(self.skill)

        # Create Task B with Task A as prerequisite
        self.task_b = Task.objects.create(
            task_name='Task B',
            task_details='Details for Task B',
            priority=3,
            planned_start_date=date(2023, 10, 21),
            planned_end_date=date(2023, 10, 30),
            due_date=date(2023, 10, 30),
            estimated_time_to_complete=timedelta(hours=32),  # 32 hours
            project=self.project,
            assigned_to=self.assigned_to,
            prereq_task=self.task_a  # Task B depends on Task A
        )
        self.task_b.skills_required.add(self.skill)

    def test_circular_dependency(self):
        """
        Test that editing Task A to set its prerequisite to Task B is prevented due to circular dependency.
        """
        data = {
            'task_name': self.task_a.task_name,
            'task_details': self.task_a.task_details,
            'priority': self.task_a.priority,
            'planned_start_date': self.task_a.planned_start_date.strftime('%Y-%m-%d'),
            'planned_end_date': self.task_a.planned_end_date.strftime('%Y-%m-%d'),
            'due_date': self.task_a.due_date.strftime('%Y-%m-%d'),
            'actual_start_date': self.task_a.actual_start_date.strftime('%Y-%m-%d') if self.task_a.actual_start_date else '',
            'actual_end_date': self.task_a.actual_end_date.strftime('%Y-%m-%d') if self.task_a.actual_end_date else '',
            'estimated_time_to_complete': self.task_a.estimated_time_to_complete.total_seconds(),
            'skills_required': [skill.skill_id for skill in self.task_a.skills_required.all()],
            'assigned_to': self.task_a.assigned_to.asset_id if self.task_a.assigned_to else '',
            'halo_ref': self.task_a.halo_ref if self.task_a.halo_ref else '',
            'prereq_task': self.task_b.id,  # Attempt to set Task B as prerequisite for Task A
            'delay_reason': self.task_a.delay_reason or '',
        }

        form = EditTaskForm(data=data, instance=self.task_a, project=self.project)
        self.assertFalse(form.is_valid(), "Form should be invalid due to circular dependency.")
        self.assertIn('prereq_task', form.errors)
        self.assertEqual(
            form.errors['prereq_task'][0],
            'Adding this dependency will create a circular reference.'
        )

    def test_dependent_task_dates_warning(self):
        """
        Test that editing Task A to set its end date after Task B's start date is allowed, but may cause scheduling conflicts.
        """
        new_planned_end_date = date(2023, 10, 25)  # Set end date after Task B's start date (2023-10-21)
        data = {
            'task_name': self.task_a.task_name,
            'task_details': self.task_a.task_details,
            'priority': self.task_a.priority,
            'planned_start_date': self.task_a.planned_start_date.strftime('%Y-%m-%d'),
            'planned_end_date': new_planned_end_date.strftime('%Y-%m-%d'),
            'due_date': self.task_a.due_date.strftime('%Y-%m-%d'),
            'actual_start_date': self.task_a.actual_start_date.strftime('%Y-%m-%d') if self.task_a.actual_start_date else '',
            'actual_end_date': self.task_a.actual_end_date.strftime('%Y-%m-%d') if self.task_a.actual_end_date else '',
            'estimated_time_to_complete': self.task_a.estimated_time_to_complete.total_seconds(),
            'skills_required': [skill.skill_id for skill in self.task_a.skills_required.all()],
            'assigned_to': self.assigned_to.asset_id,
            'halo_ref': self.task_a.halo_ref or '1001',
            'prereq_task': self.task_a.prereq_task.id if self.task_a.prereq_task else '',
            'delay_reason': self.task_a.delay_reason or '',
        }

        # Ensure the assigned_to asset has the required skills
        self.assigned_to.skills.add(*self.task_a.skills_required.all())

        # Create the assets queryset based on the required skills
        required_skills = data['skills_required']
        assets_queryset = Asset.objects.filter(skills__skill_id__in=required_skills).distinct()

        form = EditTaskForm(data=data, instance=self.task_a, project=self.project, assets_queryset=assets_queryset)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid(), "Form should be valid even if dependent task dates may conflict.")
        updated_task_a = form.save()
        self.assertEqual(updated_task_a.planned_end_date, new_planned_end_date)

        # Additional check: Verify that the scheduling conflict exists
        conflict_exists = self.task_b.planned_start_date < updated_task_a.planned_end_date
        self.assertTrue(conflict_exists, "There should be a scheduling conflict between Task A and Task B.")
    
# Complete Task Form
class TaskCompleteFormTestCase(TestCase):
    def setUp(self):
        # Create Skills
        self.skill = SkillFactory()

        # Create Assets with Skills
        self.assigned_asset = AssetFactory(skills=[self.skill])

        # Create Project
        self.project = ProjectFactory()

        # Create Task A (Open and not a prerequisite)
        self.task_a = TaskFactory(
            project=self.project,
            assigned_to=self.assigned_asset,
            skills_required=[self.skill],
            task_status=1  # Assuming 1 is "Open"
        )

    def test_complete_task_a_invalid_dates(self):
        """
        Test completing Task A with actual_end_date before actual_start_date.
        """
        form_data = {
            'actual_start_date': '2023-10-25',
            'actual_end_date': '2023-10-15',  # Invalid: end before start
            'actual_time_to_complete': '40',
        }

        form = TaskCompleteForm(data=form_data, instance=self.task_a)
        self.assertFalse(form.is_valid(), "Form should be invalid when end date is before start date.")
        self.assertIn('actual_end_date', form.errors)
        self.assertEqual(
            form.errors['actual_end_date'][0],
            'End date cannot be earlier than the start date.'
        )

    def test_complete_task_a_zero_hours(self):
        """
        Test completing Task A with actual_time_to_complete set to 0 hours.
        The form should be invalid and raise an appropriate error.
        """
        form_data = {
            'actual_start_date': '2023-10-15',
            'actual_end_date': '2023-10-25',
            'actual_time_to_complete': '0',  # 0 hours
        }

        form = TaskCompleteForm(data=form_data, instance=self.task_a)
        self.assertFalse(form.is_valid(), "Form should be invalid when actual_time_to_complete is 0 hours.")
        self.assertIn('actual_time_to_complete', form.errors)
        self.assertEqual(
            form.errors['actual_time_to_complete'][0],
            'Estimated time to complete must be a positive number of hours.'
        )

    def test_complete_task_a_valid(self):
        """
        Test completing Task A with valid data.
        """
        form_data = {
            'actual_start_date': '2023-10-15',
            'actual_end_date': '2023-10-25',
            'actual_time_to_complete': '40',  # Assuming hours
        }

        form = TaskCompleteForm(data=form_data, instance=self.task_a)
        self.assertTrue(form.is_valid(), "Form should be valid with correct data.")

        completed_task = form.save(commit=False)
        completed_task.task_status = 3  # Assuming 3 is "Completed"
        completed_task.save()
        form.save_m2m()

        # Reload from DB
        self.task_a.refresh_from_db()
        self.assertEqual(self.task_a.actual_start_date, timezone.datetime(2023, 10, 15).date())
        self.assertEqual(self.task_a.actual_end_date, timezone.datetime(2023, 10, 25).date())
        self.assertEqual(self.task_a.actual_time_to_complete, timedelta(hours=40))
        self.assertEqual(self.task_a.task_status, 3)  # Check if status updated to "Completed"

# Access Control Tests
@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class BaseAuthTestCase(TestCase):
    def setUp(self):
        # Define the models and actions for which permissions are needed
        self.models = ['project', 'task', 'risk', 'assumption', 'issue', 'dependency', 'stakeholder']
        self.actions = ['add', 'change']

        # Create Groups
        self.group_with_permissions = Group.objects.create(name='Project Managers')
        self.group_without_permissions = Group.objects.create(name='Normal Users')

        # Assign permissions to the group with permissions
        self.assign_permissions(self.group_with_permissions, self.models, self.actions)

        # Create Users
        self.user_with_permissions = User.objects.create_user(username='manager', password='managerpass')
        self.user_with_permissions.groups.add(self.group_with_permissions)

        self.user_without_permissions = User.objects.create_user(username='regular', password='regularpass')
        self.user_without_permissions.groups.add(self.group_without_permissions)

        # URL to test (example: Project Create View)
        self.project_create_url = reverse('project_create')  # Adjust if necessary

    def assign_permissions(self, group, models, actions):
        """
        Assign specified permissions to a group.
        """
        for model in models:
            for action in actions:
                codename = f'{action}_{model}'
                try:
                    # Get the model class dynamically
                    model_class = globals()[model.capitalize()]

                    # Get the ContentType for the model
                    content_type = ContentType.objects.get_for_model(model_class)

                    # Retrieve the Permission object
                    permission = Permission.objects.get(codename=codename, content_type=content_type)

                    # Assign the permission to the group
                    group.permissions.add(permission)
                except (Permission.DoesNotExist, KeyError):
                    # Handle cases where the model class or permission does not exist
                    print(f"Permission '{codename}' not found for model '{model}'. Please ensure it exists.")

class ProjectCloseViewTest(BaseAuthTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory(project_status=1)  # Assuming status_id=1 is 'Open'
        self.project_close_url = reverse('project_close', kwargs={'project_id': self.project.id})

    def test_close_project_redirects_unauthenticated_user(self):
        """
        Test that unauthenticated users are redirected to the login page when accessing the Project Close View.
        """
        response = self.client.post(self.project_close_url, follow=True)
        login_url = reverse('login')
        expected_redirect_url = f'{login_url}?next=/projects/{self.project.id}/'
        self.assertRedirects(response, expected_redirect_url)

    def test_close_project_redirects_authenticated_without_permission(self):
        """
        Test that authenticated users without 'change_project' permission are redirected to the project detail view with an error message.
        """
        # Log in as a user without 'change_project' permission
        self.client.login(username='regular', password='regularpass')
        
        # Ensure the user does NOT have the 'change_project' permission
        self.assertFalse(self.user_without_permissions.has_perm('application.change_project'))
        
        # Perform the POST request to close the project
        response = self.client.post(self.project_close_url, follow=True)
        
        # Define the expected redirect URL to the project detail view
        expected_redirect_url = reverse('project_detail', kwargs={'project_id': self.project.id})
        
        # Assert that the response redirects to the project detail view
        self.assertRedirects(response, expected_redirect_url)
        
        # Check for the presence of the error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You do not have permission to close this project.")
        
        # Optionally, verify that the project's status has not changed
        self.project.refresh_from_db()
        self.assertEqual(self.project.project_status, 1)  # Still 'Open'