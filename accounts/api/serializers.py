from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework import exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class LoginSerializer(serializers.Serializer):
    # 帮助我们检测username，password这两项是否有
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        # 这里是数据库的检测
        if not User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'User does not exist.'
            })
        return data

class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()
    # 要去把用户创建出来

    # 指定一下model是谁，field是user, email, password三项
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    # will be called when is_valid is called
    def validate(self, data):
        # username和password是小写的
        # 存储user的时候，要用小写的格式
        # 查重
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'This email address has been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'email': 'This email address has been occupied.'
            })
        return data # 不用对data进行处理

    def create(self, validated_data):
        username = validated_data['username'].lower() # 存的时候一定要小写
        email = validated_data['email'].lower() # 存的时候一定要小写
        password = validated_data['password'] # password 大小写敏感

        # django自己的create_user 和 User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user

