# backend/api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Task, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model  = Comment
        fields = ['id', 'author', 'content', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    assignee   = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    comments   = CommentSerializer(many=True, read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model  = Task
        fields = ['id', 'title', 'description', 'project', 'assignee', 'assignee_id',
                  'created_by', 'status', 'priority', 'due_date', 'created_at', 'updated_at', 'comments']
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    owner   = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks   = TaskSerializer(many=True, read_only=True)
    task_count = serializers.SerializerMethodField()

    def get_task_count(self, obj):
        return obj.tasks.count()

    class Meta:
        model  = Project
        fields = ['id', 'name', 'description', 'owner', 'members', 'tasks', 'task_count', 'created_at']


# ──────────────────────────────────────────────────────────────────
# backend/api/views.py
# ──────────────────────────────────────────────────────────────────
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Project, Task, Comment
from .serializers import ProjectSerializer, TaskSerializer, CommentSerializer, UserSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Admin can do anything; members can only read and update their own tasks."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        # Members can update tasks assigned to them
        if hasattr(obj, 'assignee') and obj.assignee == request.user:
            return request.method == 'PATCH'
        return False


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class   = ProjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['name', 'description']
    ordering_fields    = ['created_at', 'name']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(members=user) | Project.objects.filter(owner=user)

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        project.members.add(self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def add_member(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        project.members.add(user)
        return Response({'status': f'{user.username} added to project'})


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class   = TaskSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'description']
    ordering_fields    = ['created_at', 'priority', 'due_date', 'status']

    def get_queryset(self):
        user = self.request.user
        qs   = Task.objects.select_related('assignee', 'created_by', 'project')
        if not user.is_staff:
            qs = qs.filter(project__members=user)
        # Optional filters
        status   = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        assignee = self.request.query_params.get('assignee')
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if assignee:
            qs = qs.filter(assignee_id=assignee)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class   = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_pk'])

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
        serializer.save(author=self.request.user, task=task)
