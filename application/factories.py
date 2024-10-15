from application.models import (
    Category, ProjectStatus, TaskStatus, DayOfWeek,
    Skill, Team, Asset, Project, Task,
    Stakeholder, Risk, Assumption, Issue, Dependency, Comment
)
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

import factory
from factory import SubFactory, LazyFunction, Sequence, Iterator

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

class ProjectStatusFactory(factory.django.DjangoModelFactory):
    """
    Factory class for creating instances of the ProjectStatus model.
    Attributes:
        status_name (str): The name of the project status.
        description (str): The description of the project status.
    Example:
        To create a new project status instance, use the factory as follows:
        project_status = ProjectStatusFactory()
    """
    class Meta:
        model = ProjectStatus

    status_name = factory.Sequence(lambda n: f"Status {n}")
    description = factory.Faker('sentence')

class TaskStatusFactory(factory.django.DjangoModelFactory):
    """
    Factory class for creating instances of TaskStatus model.
    Attributes:
        status_name (str): The name of the task status.
        description (str): The description of the task status.
    Example:
        task_status = TaskStatusFactory(status_name="Completed", description="Task is completed.")
    """
    class Meta:
        model = TaskStatus

    status_name = factory.Sequence(lambda n: f"Task Status {n}")
    description = factory.Faker('sentence')

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
    """
    Factory class for creating instances of the Asset model.
    Attributes:
        name (str): The name of the asset.
        email (str): The email of the asset.
        normal_work_week (int): The number of hours in the normal work week for the asset.
    Post-generation method for adding skills to the asset.
        Args:
            create (bool): Indicates whether the asset is being created or not.
            extracted (list): List of skills to be added to the asset.
            **kwargs: Additional keyword arguments.
        Returns:
            None
    Post-generation method for adding teams to the asset.
        Args:
            create (bool): Indicates whether the asset is being created or not.
            extracted (list): List of teams to be added to the asset.
            **kwargs: Additional keyword arguments.
        Returns:
            None
    Post-generation method for adding work days to the asset.
        Args:
            create (bool): Indicates whether the asset is being created or not.
            extracted (list): List of work days to be added to the asset.
            **kwargs: Additional keyword arguments.
        Returns:
            None
    """
    class Meta:
        model = Asset

    name = factory.Faker('name')
    email = factory.Faker('email')
    normal_work_week = 37

    @factory.post_generation
    def skills(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for skill in extracted:
                self.skills.add(skill)
        else:
            # Use existing skills from initial data or create a new one
            if Skill.objects.exists():
                self.skills.add(*Skill.objects.all())
            else:
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
            team = TeamFactory()
            self.teams.add(team)

    @factory.post_generation
    def work_days(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for day in extracted:
                self.work_days.add(day)
        else:
            # Assume DayOfWeek instances exist
            days = DayOfWeek.objects.all()
            self.work_days.add(*days)

class ProjectFactory(factory.django.DjangoModelFactory):
    """
    Factory class for creating instances of the Project model.
    Attributes:
        project_name (str): The name of the project.
        project_description (str): The description of the project.
        planned_start_date (datetime.date): The planned start date of the project.
        original_target_end_date (datetime.date): The original target end date of the project.
        project_owner (Asset): The owner of the project.
        project_status (ProjectStatus): The status of the project.
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
    project_status = factory.LazyFunction(lambda: ProjectStatus.objects.get(status_id=1))
    category = SubFactory(CategoryFactory)
    priority = factory.Iterator([1, 2, 3, 4, 5])

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Ensure that related objects are saved
        project_owner = kwargs.get('project_owner') or AssetFactory()
        category = kwargs.get('category') or CategoryFactory()
        project_status = kwargs.get('project_status') or ProjectStatus.objects.get(status_id=1)
        kwargs['project_owner'] = project_owner
        kwargs['category'] = category
        kwargs['project_status'] = project_status
        return super()._create(model_class, *args, **kwargs)

class TaskFactory(factory.django.DjangoModelFactory):
    """
    Factory class for creating instances of the Task model.
    Attributes:
        task_name (str): The name of the task.
        task_details (str): The details of the task.
        project (Project): The project to which the task belongs.
        task_status (TaskStatus): The status of the task.
        priority (int): The priority of the task.
        assigned_to (Asset): The asset to which the task is assigned.
        skills_required (list): The list of skills required for the task.
    Methods:
        skills_required(create, extracted, **kwargs): Post-generation method to add skills required for the task.
    
    Post-generation method to add skills required for the task.
        Args:
            create (bool): Indicates if the instance is being created.
            extracted (list): List of skills to be added.
    """
    class Meta:
        model = Task

    task_name = factory.Sequence(lambda n: f"Task {n}")
    task_details = factory.Faker('paragraph')
    project = SubFactory(ProjectFactory)
    task_status = LazyFunction(lambda: TaskStatus.objects.get(status_id=1))  # 'Unassigned' status
    priority = Iterator([1, 2, 3, 4, 5])
    assigned_to = SubFactory(AssetFactory)

    @factory.post_generation
    def skills_required(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for skill in extracted:
                self.skills_required.add(skill)
        else:
            # Use existing skills or create one
            if Skill.objects.exists():
                self.skills_required.add(*Skill.objects.all())
            else:
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
    created_by = SubFactory(UserFactory)

class AssumptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Assumption

    project = SubFactory(ProjectFactory)
    assumption_details = factory.Faker('paragraph')
    created_by = SubFactory(UserFactory)

class IssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Issue

    project = SubFactory(ProjectFactory)
    issue_details = factory.Faker('paragraph')
    created_by = SubFactory(UserFactory)

class DependencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dependency

    project = SubFactory(ProjectFactory)
    dependency_details = factory.Faker('paragraph')
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

    day_name = factory.Iterator(['Saturday', 'Sunday'])
    abbreviation = factory.LazyAttribute(lambda obj: obj.day_name[:3])

class SkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Skill

    skill_name = factory.Sequence(lambda n: f"Skill {n}")

class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    team_name = factory.Sequence(lambda n: f"Team {n}")

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
    
