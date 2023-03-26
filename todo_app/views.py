from django.shortcuts import render

# Create your views here.

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import ToDoList, ToDoItem
from django.urls import reverse, reverse_lazy
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
#from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from .serializers import *

class ListListView(ListView):
    model = ToDoList
    template_name = "todo_app/index.html"


class ItemListView(ListView):
    model = ToDoItem
    template_name = "todo_app/todo_list.html"

    def get_queryset(self):
        return ToDoItem.objects.filter(todo_list_id=self.kwargs["list_id"])

    def get_context_data(self):
        context = super().get_context_data()
        context["todo_list"] = ToDoList.objects.get(id=self.kwargs["list_id"])
        return context
    



class ListCreate(CreateView):
    model = ToDoList
    fields = ["title"]

    def get_context_data(self):
        context = super(ListCreate, self).get_context_data()
        context["title"] = "Add a new list"
        return context


class ItemCreate(CreateView):
    model = ToDoItem
    fields = [
        "todo_list",
        "title",
        "description",
        "due_date",
    ]

    def get_initial(self):
        initial_data = super(ItemCreate, self).get_initial()
        todo_list = ToDoList.objects.get(id=self.kwargs["list_id"])
        initial_data["todo_list"] = todo_list
        return initial_data

    def get_context_data(self):
        context = super(ItemCreate, self).get_context_data()
        todo_list = ToDoList.objects.get(id=self.kwargs["list_id"])
        context["todo_list"] = todo_list
        context["title"] = "Create a new item"
        return context

    def get_success_url(self):
        return reverse("list", args=[self.object.todo_list_id])


class ItemUpdate(UpdateView):
    model = ToDoItem
    fields = [
        "todo_list",
        "title",
        "description",
        "due_date",
    ]

    def get_context_data(self):
        context = super(ItemUpdate, self).get_context_data()
        context["todo_list"] = self.object.todo_list
        context["title"] = "Edit item"
        return context

    def get_success_url(self):
        return reverse("list", args=[self.object.todo_list_id])


class ListDelete(DeleteView):
    model = ToDoList
    # You have to use reverse_lazy() instead of reverse(),
    # as the urls are not loaded when the file is imported.
    success_url = reverse_lazy("index")


class ItemDelete(DeleteView):
    model = ToDoItem

    def get_success_url(self):
        return reverse_lazy("list", args=[self.kwargs["list_id"]])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["todo_list"] = self.object.todo_list
        return context
    
class MyOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 10    

class Todos(ListAPIView):
    queryset = ToDoItem.objects.all()
    serializer_class = TodosSerializer
    pagination_class = MyOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['title', 'id']
    ordering_fields = ['__all__']

    def post(self, request):
        print(request)
        title = request.data.get('title', None)
        description = request.data.get('description', None)
        todo_list_id = request.data.get('todo_list_id', None)
        if title and description:
            ToDoItem(title=title, description=description, todo_list_id=todo_list_id).save()
            return Response({'Create': 'Success'})
        else:
            return Response({'Create': 'Failed'})



class OneTodo(APIView):
    pagination_class = MyOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['title']
    ordering_fields = ['__all__']

    def get_object(self, pk, todo_list_id):
        return ToDoItem.objects.get(pk=pk, todo_list_id=todo_list_id)

    def get(self, request, pk, todo_list_id):
        obj = self.get_object(pk, todo_list_id)
        ser = TodoDetailSerializer(obj)
        return Response(ser.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        ser = TodosSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            Response(ser.data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        todo = get_object_or_404(ToDoItem, id=pk)
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
