import factory
from factory import SubFactory, LazyFunction, Sequence, Iterator
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth.models import User
from application.models import (
    Category, ProjectStatus, TaskStatus, DayOfWeek,
    Skill, Team, Asset, Project, Task,
    Stakeholder, Risk, Assumption, Issue, Dependency, Comment
)

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    category_name = factory.Sequence(lambda n: f"Category {n}")

class ProjectStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectStatus

    status_name = factory.Sequence(lambda n: f"Status {n}")
    description = factory.Faker('sentence')

class TaskStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TaskStatus

    status_name = factory.Sequence(lambda n: f"Task Status {n}")
    description = factory.Faker('sentence')

class SkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Skill

    skill_name = factory.Sequence(lambda n: f"Skill {n}")

class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    team_name = factory.Sequence(lambda n: f"Team {n}")

class AssetFactory(factory.django.DjangoModelFactory):
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
    
