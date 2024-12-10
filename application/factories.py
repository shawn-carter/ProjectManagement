from application.models import (
    Category, DayOfWeek,
    Skill, Team, Asset, Project, Task,
    Stakeholder, Risk, Assumption, Issue, Dependency, Comment
)

from datetime import timedelta, date
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

import factory
from factory import SubFactory, Iterator, LazyAttribute, post_generation
from factory.django import DjangoModelFactory


class SkillFactory(factory.django.DjangoModelFactory):
    """
    Factory class for creating instances of the Skill model.
    Attributes:
        skill_name (str): The name of the skill.
    Example:
        To create a skill instance using this factory:
        skill = SkillFactory()
        This will create a skill instance with a generated skill name.
        To create a skill instance with a specific skill name:
        skill = SkillFactory(skill_name="Python")
        This will create a skill instance with the skill name "Python".
    """
    class Meta:
        model = Skill

    skill_name = factory.Sequence(lambda n: f"Skill {n}")

class CategoryFactory(factory.django.DjangoModelFactory):
    """
    Factory class for creating instances of the Category model.
    Attributes:
        category_name (str): The name of the category.
    Meta:
        model (class): The Category model class.
    """
    class Meta:
        model = Category

    category_name = factory.Sequence(lambda n: f"Category {n}")

class TeamFactory(factory.django.DjangoModelFactory):
    """
    Factory class for creating instances of the Team model.
    Attributes:
        team_name (str): The name of the team.
    Example:
        To create a new team instance using the factory:
        team = TeamFactory()
    """
    class Meta:
        model = Team

    team_name = factory.Sequence(lambda n: f"Team {n}")

class AssetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Asset

    name = factory.Sequence(lambda n: f"AssetName{n}")  # Ensures unique names
    email = factory.LazyAttribute(lambda obj: f"{obj.name.lower()}@example.com" if obj.name else None)  # Handle name=None
    normal_work_week = 40  # Assuming 40 hours as default

    @factory.post_generation
    def skills(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for skill in extracted:
                self.skills.add(skill)
        else:
            # Create at least one skill
            skill = SkillFactory()
            self.skills.add(skill)

    @factory.post_generation
    def teams(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for team in extracted:
                self.teams.add(team)
        else:
            # Optionally add a team or leave it blank
            pass

    @factory.post_generation
    def work_days(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for day in extracted:
                self.work_days.add(day)
        else:
            # Assign default work days or leave it blank
            pass

class ProjectFactory(factory.django.DjangoModelFactory):
    """
    Factory class for creating instances of the Project model.
    Attributes:
        project_name (str): The name of the project.
        project_description (str): The description of the project.
        planned_start_date (datetime.date): The planned start date of the project.
        original_target_end_date (datetime.date): The original target end date of the project.
        project_owner (Asset): The owner of the project.
        category (Category): The category of the project.
        priority (int): The priority of the project.
    Methods:
        _create(cls, model_class, *args, **kwargs): Creates and saves an instance of the model class.
    Usage:
        To create a new project instance, use the create() method of this factory class.
        Example:
            project = ProjectFactory.create(project_name='My Project', project_description='This is my project')
    """
    class Meta:
        model = Project

    project_name = factory.Sequence(lambda n: f'Project {n}')
    project_description = factory.Faker('sentence')
    planned_start_date = factory.Faker('future_date')
    original_target_end_date = factory.Faker('future_date')
    project_owner = SubFactory(AssetFactory)
    category = SubFactory(CategoryFactory)
    priority = factory.Iterator([1, 2, 3, 4, 5])

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Ensure that related objects are saved
        project_owner = kwargs.get('project_owner') or AssetFactory()
        category = kwargs.get('category') or CategoryFactory()
        kwargs['project_owner'] = project_owner
        kwargs['category'] = category
        return super()._create(model_class, *args, **kwargs)

class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    task_name = factory.Sequence(lambda n: f"Task {n}")
    task_details = factory.Faker('paragraph')
    project = SubFactory(ProjectFactory)
    task_status = 1  # Default to "Unassigned"
    priority = Iterator([1, 2, 3, 4, 5])  # Low to Urgent
    planned_start_date = factory.Faker('date_between', start_date='today', end_date='+30d')
    planned_end_date = LazyAttribute(
        lambda obj: obj.planned_start_date + timedelta(days=7) if isinstance(obj.planned_start_date, date) else None
    )
    actual_start_date = None
    actual_end_date = None
    due_date = LazyAttribute(
        lambda obj: obj.planned_end_date + timedelta(days=2) if isinstance(obj.planned_end_date, date) else None
    )
    estimated_time_to_complete = timedelta(hours=8)
    actual_time_to_complete = None
    prereq_task = None
    delay_reason = ""
    halo_ref = None  # Now optional with blank=True

    assigned_to = SubFactory(AssetFactory, skills=[])  # Initialize with no skills; add via post_generation

    @post_generation
    def skills_required(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for skill in extracted:
                self.skills_required.add(skill)
        else:
            # Ensure at least one skill is added
            skill = SkillFactory()
            self.skills_required.add(skill)

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'password')

class RiskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Risk

    project = SubFactory(ProjectFactory)
    risk_details = factory.Faker('paragraph')
    impact = Iterator([1, 2, 3, 4, 5])
    probability = Iterator([1, 2, 3, 4, 5])
    status = Iterator([1,2,3])
    created_by = SubFactory(UserFactory)

class AssumptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Assumption

    project = SubFactory(ProjectFactory)
    assumption_details = factory.Faker('paragraph')
    status = Iterator([1,2,3])
    created_by = SubFactory(UserFactory)

class IssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Issue

    project = SubFactory(ProjectFactory)
    issue_details = factory.Faker('paragraph')
    status = Iterator([1,2,3])
    created_by = SubFactory(UserFactory)

class DependencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dependency

    project = SubFactory(ProjectFactory)
    dependency_details = factory.Faker('paragraph')
    status = Iterator([1,2,3])
    created_by = SubFactory(UserFactory)

class StakeholderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Stakeholder

    project = SubFactory(ProjectFactory)
    name = factory.Faker('name')
    email = factory.Faker('email')
    created_by = SubFactory(UserFactory)
    interest_level = Iterator([1, 2, 3])
    influence_level = Iterator([1, 2, 3])

class DayOfWeekFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DayOfWeek

    day_name = factory.Sequence(lambda n: f"CustomDay{n}")
    abbreviation = factory.Sequence(lambda n: f"Cd{n}")  # Ensures uniqueness

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    user = SubFactory(UserFactory)
    comment_text = factory.Faker('paragraph')

    @factory.lazy_attribute
    def content_object(self):
        # By default, we can set this to None; we'll specify it in tests
        return None

    @factory.lazy_attribute
    def content_type(self):
        if self.content_object:
            return ContentType.objects.get_for_model(self.content_object)
        return None

    @factory.lazy_attribute
    def object_id(self):
        if self.content_object:
            return self.content_object.pk
        return None
    
