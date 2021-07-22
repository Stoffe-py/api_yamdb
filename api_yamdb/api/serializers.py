import jwt
from rest_framework import serializers

from django.conf import settings

from .models import Categories, Comments, Genres, Reviews, Titles, User


class SendConfirmCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class TokenReceiveSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField()

    def validate_confirmation_code(self, value):
        singed_token = value
        secret_key = settings.SECRET_KEY

        try:
            payload = jwt.decode(jwt=singed_token, key=secret_key,
                                 algorithms=('HS256',))
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Код подтверждения устарел')
        except jwt.InvalidTokenError:
            raise serializers.ValidationError('Неверный код подтверждения')

        return payload.get('email')

    def validate(self, attrs):
        open_email = attrs['email']
        signed_email = attrs['confirmation_code']

        if open_email != signed_email:
            raise serializers.ValidationError('Почта не совпадает')

        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')
        extra_kwargs = {'username': {'required': True}}

    def validate_role(self, role):
        message = (
            'Вы не можете изменить роль на ту, которая дает больше прав, '
            'чем вы сами имеете.')

        changer = self.context['request'].user.role

        if changer == 'moderator' and role == 'admin':
            raise serializers.ValidationError(message)
        if changer == 'user' and role in ('admin', 'moderator'):
            raise serializers.ValidationError(message)

        return role

    def validate(self, data):
        request = self.context['request']
        is_username = data.get('username') or request.user.username

        if request.method == 'PATCH' and not is_username:
            raise serializers.ValidationError(
                'Поле username обязательно для заполнения.'
            )

        if data.get('role') in ('user', 'moderator'):
            data['is_staff'] = False
        if data.get('role') == 'admin':
            data['is_staff'] = True

        return data


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    score = serializers.IntegerField(min_value=1, max_value=10)

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        author = self.context['request'].user
        title = self.context['view'].kwargs.get('title_id')
        if Reviews.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError('Отзыв уже существует')
        return data

    class Meta:
        model = Reviews
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comments
        fields = ('id', 'text', 'author', 'pub_date')


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ('name', 'slug')


class TitleBaseSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Titles
        fields = ('id', 'name', 'year', 'description', 'genre',
                  'category', 'rating')

    def get_rating(self, obj):
        if hasattr(obj, 'rating'):
            return obj.rating
        return None


class TitlesUnSafeMethodSerializer(TitleBaseSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genres.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Categories.objects.all(),
        required=False
    )


class TitlesSafeMethodSerializer(TitleBaseSerializer):
    genre = GenresSerializer(many=True)
    category = CategoriesSerializer()
