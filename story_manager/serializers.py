from rest_framework import serializers
from story_manager.models import Story, GroupStory


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ('id', 'title', 'cover_url', 'def_url')


class GroupStorySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="story.id")
    title= serializers.ReadOnlyField(source="story.title")
    cover_url = serializers.ReadOnlyField(source="story.cover_url")
    def_url = serializers.ReadOnlyField(source="story.def_url")

    class Meta:
        model = GroupStory
        fields = ('id', 'title', 'cover_url', 'def_url', 'is_current',
                  'current_page')


class GroupStoryListSerializer(serializers.Serializer):
    current_story_id = serializers.ReadOnlyField()
    stories = GroupStorySerializer(many=True, read_only=True)
