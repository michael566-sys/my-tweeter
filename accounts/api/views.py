from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
# login_status return 的格式
from rest_framework.response import Response
from accounts.api.serializers import (
    UserSerializer, LoginSerializer, SignupSerializer,
)
# log out 用的
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate,
)
# def login(request, user, backend=None): -》 就是login
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
""" 
ModelViewSet 中的增删查改: (只能用这些自带的，不能自定义)
    list
    retrieve
    input
    patch
    destroy
"""

# use our own ViewSet -> define the ViewSet by myself
class AccountViewSet(viewsets.ViewSet):
    serializer_class = SignupSerializer

    # https://www.lintcode.com/problem/2153/
    # action is login_status, which is a decorator
    # note: don't forget to add 's' for "methods"!!!!!!!!!!
    @action(methods=['GET'], detail=False)
    # methods=['GET'] -> 只能用get 去请求，不能用post
    # detail=False -> url localhost:81/api/accounts/login_status
    #   不需要写成 localhost:81/api/accounts/123/login_status/
    #   不是定义在某个object上的动作，而是定义在整个根目录上的动作
    #   在某一个object上定义要是detail=True
    #   then def login_status(self, request, primary_key):
    #   then url is localhost:81/api/accounts/1/login_status/

    # /api.accounts/login_status/
    # 主目录->accounts
    # 次目录->是一个action->eg: login_status
    #   besides restful framework keywords, you can define you own actions
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        """
        is_authenticated
        # 如果是匿名用户，永远return False
        @property
        def is_authenticated(self):
            return False
            
        # 如果不是匿名用户，永远return True
        @property
        def is_authenticated(self):
        # Always return True. This is a way to tell if the user has been
        # authenticated in templates.
        
        return True
            
        """
        # 如果已经登陆
        if request.user.is_authenticated:
            # 把user 加进去，用UserSerializer, 把用户穿进去，取出数据
            # UserSerializer -> 取出数据，变成jason 格式
            # user 是一个object, 不是一个hashmap, 用UserSerializer去套一下

            data['user'] = UserSerializer(request.user).data

        return Response(data)
        """
        data 就是显示的这个数据：
        {
            "has_logged_in": true,
            "user": {
                    "id": self.current user's id,
                "username": "current user's username",
                "email": "current user's email"
            }
        }
        """

    # https://www.lintcode.com/problem/2156/
    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})


    # https://www.lintcode.com/problem/2148/
    @action(methods=['POST'], detail=False)
    def login(self, request):
        # 从request当中获取user的信息，得到username的password去实现登陆
        # get username and password from request
        # request.data['username']
        # request.data['password']
        # 不一定有，万一用户没传，要用LoginSerializer

        # serializer 里面要传一个data进去，request.data来的
        serializer = LoginSerializer(data=request.data)

        # 如果是 @action(methods=['GET'], detail=False)
        # 要用 serializer = LoginSerializer(data=request.query_params)

        # is_valid -> 调用run_validation验证, 根据没一个field有没有符合要求
        if not serializer.is_valid():
            return Response({
            # 如果return false, 要反回400 -> bad request, 用户请求不对
            # not server's error, client's error
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors, # 自动获取errors信息，如果出错了
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        # validated_data -> 验证完了以后，进行类型转换，经过了验证的dat，取出来

        # django_authenticate -> can search google how does google authenticate
        # return a user
        # authenticate 过之后的user才是能拿去login的user
        # 如果直接拿 user = User.objects.get(username=username) 丢给django_login会出错

        # 如果用户不存在，return 400

        """
        # debug 的技巧：
        queryset = User.objects.filter(username=username)
        print(queryset.query)
        # password is not correct, print 出来了结果： 
        
        System check identified no issues (0 silenced).
        May 31, 2022 - 17:56:32
        Django version 3.1.3, using settings 'twitter.settings'
        Starting development server at http://0.0.0.0:8000/
        Quit the server with CONTROL-C.
        SELECT `auth_user`.`id`, `auth_user`.`password`, `auth_user`.`last_login`, 
        `auth_user`.`is_superuser`, `auth_user`.`username`, `auth_user`.`first_name`, 
        `auth_user`.`last_name`, `auth_user`.`email`, `auth_user`.`is_staff`, 
        `auth_user`.`is_active`, `auth_user`.`date_joined` 
        FROM `auth_user` WHERE `auth_user`.`username` = admin
        Bad Request: /api/accounts/login/
        [31/May/2022 17:56:43] "POST /api/accounts/login/ HTTP/1.1" 400 8585

        """
        # this is moved to serializers.py
        # if not User.objects.filter(username=username).exists():
        #     # select count * > 0
        #     return Response({
        #         "success": False,
        #         "message": "User does not exists.",
        #     }, status=400)

        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "username and password does not match",
            }, status=400)

        # 调用login接口，login
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(user).data,
        })

    # https://www.lintcode.com/problem/2155/
    # POST / api / accounts / signup /
    @action(methods=['POST'], detail=False)
    def signup(self, request):
        # if not pass a instance,
        # the POST is to "create" !!!!!
        # input user data, thorough a create method, returns an instance!!!
        # so serializer is an instance
        serializer = SignupSerializer(data=request.data)
        # why adding "data="?????? see it again?????????

        # if passes a instance, the POST is to "update," not "create" !!!!!
        # serializer = SignupSerializer(instance=request.user, request.data)

        if not serializer.is_valid():
            return Response({
                # 如果return false, 要反回400 -> bad request, 用户请求不对
                # not server's error, client's error
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,  # 自动获取errors信息，如果出错了
            }, status=400)

        user = serializer.save()
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        }, status=201)


