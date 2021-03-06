import json
from django.http import Http404
from rest_framework import permissions, generics, status
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from people.models import Person, Group, Circle, Membership, PersonMeta
from people.serializers import PersonSerializer, GroupSerializer, \
    GroupListSerializer, CircleSerializer
from fitness_connector.activity import PersonActivity

# CONSTANTS
DEFAULT_PERSON_STUB = "-"  # type: str

# HELPER METHODS
def get_person_by_user_id(user_id):
    # type: (str) -> Person
    try:
        return Person.objects.get(user__id=user_id)
    except Person.DoesNotExist:
        raise Http404


def get_group(person):
    # type: (Person) -> Group
    try:
        return Group.objects.get(members=person)
    except Group.DoesNotExist:
        raise Http404


def get_person_meta(person):
    # type: (Person) -> PersonMeta
    try:
        return PersonMeta.objects.get(person=person)
    except PersonMeta.DoesNotExist:
        raise Http404


def get_circle(person, circle_id):
    # type: (Person, int) -> Circle
    try:
        return Circle.objects.get(members=person, id=circle_id)
    except Circle.DoesNotExist:
        raise Http404

def get_list_of_circles(person):
    # type: (Person, int) -> QuerySet
    try:
        return Circle.objects.filter(members=person).all()
    except Circle.DoesNotExist:
        raise Http404

# CLASSES


class UserInfo(APIView):
    """
    Retrieve current User's detailed information
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        person = get_person_by_user_id(request.user.id)
        serializer = PersonSerializer(person)
        return Response(serializer.data)


class UserGroupInfo(APIView):
    """
    Retrieve the Group's detailed information in which the logged User
    belongs to
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        person = get_person_by_user_id(request.user.id)
        group = get_group(person)
        serializer = GroupSerializer(group)
        return Response(serializer.data)


class UserCircleInfo(APIView):
    """
    Retrieve a Circle's detailed information in which the logged User
    belongs to
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, circle_id, format=None):
        person = get_person_by_user_id(request.user.id)
        circle = get_circle(person, circle_id)
        serializer = CircleSerializer(circle)
        return Response(serializer.data)


class UserCircleListInfo(APIView):
    """
    Retrieve a list of Circle information in which the logged User
    belongs to
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        person = get_person_by_user_id(request.user.id)
        list_of_circles = get_list_of_circles(person)
        serializer = CircleSerializer(list_of_circles, many=True)
        return Response(serializer.data)


class PersonInfo(APIView):
    """
    GET request returns the Person's info.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, person_id, format=None):
        logged_person = get_person_by_user_id(request.user.id)
        group = get_group(logged_person)

        if person_id == DEFAULT_PERSON_STUB:
            serializer = PersonSerializer(logged_person)
            return Response(serializer.data)
        elif group.is_member(person_id):
            person = group.get_member(person_id)
            serializer = PersonSerializer(person)
            return Response(serializer.data)
        else:
            output = {"message": "Not authorized"}
            return Response(output, status=status.HTTP_400_BAD_REQUEST)


class PersonProfileInfo(APIView):
    """
    GET request returns the Person's profile.
    POST request sets the Person's profile.
    """
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (JSONParser,)

    def get(self, request, person_id, format=None):
        logged_person = get_person_by_user_id(request.user.id)
        group = get_group(logged_person)

        if group.is_member(person_id) is False:
            output = {"message": "Not authorized"}
            return Response(output, status=status.HTTP_400_BAD_REQUEST)
        else:
            person = group.get_member(person_id)
            person_meta = person.get_meta()
            return Response(json.loads(person_meta.profile_json))

    def post(self, request, person_id, format=None):
        logged_person = get_person_by_user_id(request.user.id)
        group = get_group(logged_person)

        if group.is_member(person_id) is False:
            output = {"message": "Can't update this person's metadata"}
            return Response(output, status=status.HTTP_400_BAD_REQUEST)
        else:
            person = group.get_member(person_id)
            person.set_meta_profile(json.dumps(request.data))
            return Response(request.data, status.HTTP_200_OK)


# CLASSES FOR ADMIN VIEWS (CURRENTLY NOT USED)


class AdminPersonList(generics.ListAPIView):
    """
    List all Persons
    """
    permission_classes = (permissions.IsAdminUser,)
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class AdminPersonInfo(APIView):
    """
    Retrieve a Person's detailed information
    """
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, person_id, format=None):
        person = get_person_by_user_id(person_id)
        person_activity = PersonActivity(person_id)
        response = {
            'person': {
                'person_id': person_id,
                'name': person.name,
                'last_pull_time': person_activity.account.last_pull_time
            }
        }
        return Response(response)


class AdminGroupList(generics.ListAPIView):
    """
    List all Families
    """
    permission_classes = (permissions.IsAdminUser,)
    queryset = Group.objects.all()
    serializer_class = GroupListSerializer


class AdminGroupInfo(APIView):
    """
    Retrieve a Group's detailed information
    """
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, group_id, format=None):
        group = get_person_by_user_id(group_id)
        serializer = GroupSerializer(group)
        return Response(serializer.data)
