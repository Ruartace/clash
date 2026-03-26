from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import GoalSerializer
from . import services
from utils.response import success, error


class GoalListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = services.get_user_goals(request.user)
        return success(data=GoalSerializer(items, many=True).data)

    def post(self, request):
        serializer = GoalSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message='数据有误', data=serializer.errors)
        item = services.create_goal(request.user, serializer.validated_data)
        return success(data=GoalSerializer(item).data, message='创建成功', status=201)


class GoalDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_item(self, user, pk):
        return services.get_user_goals(user).filter(pk=pk).first()

    def get(self, request, pk):
        item = self._get_item(request.user, pk)
        if not item:
            return error(message='目标不存在', code=404, status=404)
        return success(data=GoalSerializer(item).data)

    def patch(self, request, pk):
        item = self._get_item(request.user, pk)
        if not item:
            return error(message='目标不存在', code=404, status=404)
        serializer = GoalSerializer(item, data=request.data, partial=True)
        if not serializer.is_valid():
            return error(message='数据有误', data=serializer.errors)
        item = services.update_goal(item, serializer.validated_data)
        return success(data=GoalSerializer(item).data, message='更新成功')

    def delete(self, request, pk):
        item = self._get_item(request.user, pk)
        if not item:
            return error(message='目标不存在', code=404, status=404)
        services.delete_goal(item)
        return success(message='删除成功')
