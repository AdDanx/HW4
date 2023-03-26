from rest_framework import serializers
from todo_app.models import ToDoList, ToDoItem


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDoItem
        fields = ['created_date', 'due_date']


class TodoDetailSerializer(serializers.ModelSerializer):
    measurements = MeasurementSerializer(read_only=True, many=True)

    class Meta:
        model = ToDoItem
        fields = ['id', 'title', 'description', 'todo_list_id', 'measurements']


class TodosSerializer(serializers.ModelSerializer):

    class Meta:
        model = ToDoItem
        fields = ['id', 'title', 'description', 'todo_list_id']

