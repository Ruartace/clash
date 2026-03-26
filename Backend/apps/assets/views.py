from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import AssetSerializer
from . import services
from utils.response import success, error


class AssetListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assets = services.get_user_assets(request.user)
        return success(data=AssetSerializer(assets, many=True).data)

    def post(self, request):
        serializer = AssetSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message='数据有误', data=serializer.errors)
        asset = services.create_asset(request.user, serializer.validated_data)
        return success(data=AssetSerializer(asset).data, message='创建成功', status=201)


class AssetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_asset(self, user, pk):
        return services.get_user_assets(user).filter(pk=pk).first()

    def get(self, request, pk):
        asset = self._get_asset(request.user, pk)
        if not asset:
            return error(message='资产不存在', code=404, status=404)
        return success(data=AssetSerializer(asset).data)

    def patch(self, request, pk):
        asset = self._get_asset(request.user, pk)
        if not asset:
            return error(message='资产不存在', code=404, status=404)
        serializer = AssetSerializer(asset, data=request.data, partial=True)
        if not serializer.is_valid():
            return error(message='数据有误', data=serializer.errors)
        asset = services.update_asset(asset, serializer.validated_data)
        return success(data=AssetSerializer(asset).data, message='更新成功')

    def delete(self, request, pk):
        asset = self._get_asset(request.user, pk)
        if not asset:
            return error(message='资产不存在', code=404, status=404)
        services.delete_asset(asset)
        return success(message='删除成功')
