from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from zds.forum.models import Forum, Topic, Post
from dry_rest_permissions.generics import DRYPermissionsField
from dry_rest_permissions.generics import DRYPermissions
from django.shortcuts import get_object_or_404

class ForumSerializer(ModelSerializer):
    class Meta:
        model = Forum
        permissions_classes = DRYPermissions

# Renomer en ForumPostSerializer
class ForumActionSerializer(ModelSerializer):
    """
    Serializer to create a new forum
    """
    permissions = DRYPermissionsField()

    class Meta:
        model = Forum
        #fields = ('id', 'text', 'text_html', 'permissions')
    #    read_only_fields = ('text_html', 'permissions')
        read_only_fields = ('slug',)

    def create(self, validated_data):
        new_forum = Forum.objects.create(**validated_data)
        return new_forum

class ForumUpdateSerializer(ModelSerializer):
    """
    Serializer to update a forum.
    """
    can_be_empty = True
    title = serializers.CharField(required=False, allow_blank=True)
    subtitle = serializers.CharField(required=False, allow_blank=True)
    # Ajouter category et eventuellement autre TODO
    permissions = DRYPermissionsField()

    class Meta:
        model = Forum
        fields = ('id', 'title', 'subtitle','permissions',)
        read_only_fields = ('id','slug','permissions',) # TODO a voir si besoin d'autres champs

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        #fields = ('id', 'title', 'subtitle', 'slug', 'category', 'position_in_category')
        permissions_classes = DRYPermissions

# Idem renommer
class TopicActionSerializer(ModelSerializer):
    """
    Serializer to create a new topic.
    """
    permissions = DRYPermissionsField()

    class Meta:
        model = Topic
        read_only_fields = ('slug','author',)

    def create(self, validated_data):
        new_topic = Topic.objects.create(**validated_data)
        return new_topic


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        #fields = ('id', 'title', 'subtitle', 'slug', 'category', 'position_in_category')
        permissions_classes = DRYPermissions


class PostActionSerializer(ModelSerializer):
    """
    Serializer to send a post in a topic
    """
    permissions = DRYPermissionsField()

    class Meta:
        model = Post
        fields = ('id', 'text', 'text_html', 'permissions')
        read_only_fields = ('text_html', 'permissions')
    # TODO a voir quel champ en read only

    def create(self, validated_data):
        # Get topic
        pk_topic = validated_data.get('topic_id')
        topic = get_object_or_404(Topic, pk=(pk_topic))
        Post.objects.create(**validated_data)
        return topic.last_message

    # Todo a t on besoin d'un validateur
    #def throw_error(self, key=None, message=None):
        #raise serializers.ValidationError(message)
