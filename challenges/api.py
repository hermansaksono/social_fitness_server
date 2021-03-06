from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from challenges.classes import ListOfAvailableChallenges, CurrentChallenge, ChallengeViewModel
from challenges.models import GroupChallenge
from challenges.serializers import ListOfAvailableChallengestSerializer, \
    AvailableChallengeSerializer, \
    CurrentChallengeSerializer, ChallengeViewModelSerializer, \
    IndividualizedGroupChallengeSerializer, AverageStepsSerializers
from fitness.models import DATE_DELTA_7D, DATE_DELTA_1D
from people import helpers as people_helper


class Challenges(APIView):
    """
    GET request returns the status, the available challenges, and the currently
    running challenges. If status is AVAILABLE, then running is None. If status
    is RUNNING, then available is None.
    POST request creates a new challenge uniformly for all group members
    if there are no running challenges.
    """

    def get(self, request, steps_average=None, format=None):
        group = people_helper.get_group(request.user.id)
        challenge_view_model = ChallengeViewModel(group, steps_average=steps_average)
        serializer = ChallengeViewModelSerializer(challenge_view_model)
        return Response(serializer.data)

    def post(self, request, steps_average=None, format=None):
        """
        Create new challenges uniformly for all group members
        """
        group = people_helper.get_group(request.user.id)
        if GroupChallenge.is_there_a_running_challenge(group) :
            return self.__get_bad_request()
        else:
            return self.__post_a_new_challenge(group, request.data, steps_average)

    def __post_a_new_challenge(self, group, data, steps_average):
        validator = AvailableChallengeSerializer(data=data)
        if validator.is_valid():
            validated_data = validator.validated_data
            challenge = GroupChallenge.create_from_data(group, validated_data, steps_average=steps_average)
            challenge_view_model = ChallengeViewModel(group)
            serializer = ChallengeViewModelSerializer(challenge_view_model)
            # current_challenge = CurrentChallenge(challenge, is_new=True)
            # serializer = CurrentChallengeSerializer(current_challenge)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            errors = validator.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def __get_bad_request(self):
        output = {"message": "There is a running challenge"}
        return Response(output, status.HTTP_400_BAD_REQUEST)


class IndividualizedChallengesCustomSteps(APIView):
    def get(self, request, format=None):
        group = people_helper.get_group(request.user.id)
        challenge_view_model = ChallengeViewModel(group)
        serializer = ChallengeViewModelSerializer(challenge_view_model)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Create new challenges uniformly for all group members
        """
        group = people_helper.get_group(request.user.id)
        if not GroupChallenge.is_there_a_running_challenge(group) :
            return self.__get_challenges_from_averages(group, request.data)
        else:
            return Response("There's a running challenge",
                            status=status.HTTP_400_BAD_REQUEST)

    def __get_challenges_from_averages(self, group, data):
        validator = AverageStepsSerializers(data=data)
        if validator.is_valid():
            validated_data = validator.validated_data
            step_averages = validated_data["step_averages"]  # type: dict(int)

            challenge_view_model = ChallengeViewModel(group, steps_dict=step_averages)
            serializer = ChallengeViewModelSerializer(challenge_view_model)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            errors = validator.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class IndividualizedChallenges(APIView):
    """
    GET request returns the status, the available challenges, and the currently
    running challenges. If status is AVAILABLE, then running is None. If status
    is RUNNING, then available is None.
    POST request creates a new challenge individualized for each group member
    if there are no running challenges.
    """

    def get(self, request, format=None):
        group = people_helper.get_group(request.user.id)
        challenge_view_model = ChallengeViewModel(group)
        serializer = ChallengeViewModelSerializer(challenge_view_model)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Create new challenges uniformly for all group members
        """
        group = people_helper.get_group(request.user.id)
        if GroupChallenge.is_there_a_running_challenge(group) :
            return self.__get_bad_request()
        else:
            return self.__post_a_new_challenge(group, request.data)

    def __get_challenges_from_averages(self, group, data):
        validator = AverageStepsSerializers(data=data)
        if validator.is_valid():
            validated_data = validator.validated_data
            step_averages = validated_data["step_averages"]  # type: dict(int)

            challenge_view_model = ChallengeViewModel(group, steps_dict=step_averages)
            serializer = ChallengeViewModelSerializer(challenge_view_model)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            errors = validator.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def __post_a_new_challenge(self, group, data):
        validator = IndividualizedGroupChallengeSerializer(data=data)
        if validator.is_valid():
            validated_data = validator.validated_data

            GroupChallenge.create_individualized(group, validated_data)

            challenge_view_model = ChallengeViewModel(group)
            serializer = ChallengeViewModelSerializer(challenge_view_model)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            errors = validator.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def __get_bad_request(self):
        output = {"message": "There is a running challenge"}
        return Response(output, status.HTTP_400_BAD_REQUEST)


class Available(APIView):
    """
    List all available challenges that a family can pick.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        group = people_helper.get_group(request.user.id)
        if GroupChallenge.is_there_a_running_challenge(group) :
            output = {"message": "There is a running challenge"}
            return Response(output, status.HTTP_400_BAD_REQUEST)

        challenges = ListOfAvailableChallenges(group)
        serializer = ListOfAvailableChallengestSerializer(challenges)
        return Response(serializer.data)


class Create(APIView):
    """
    Create new challenges uniformly for all group members
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        group = people_helper.get_group(request.user.id)
        if GroupChallenge.is_there_a_running_challenge(group) :
            output = {"message": "There is a running challenge"}
            return Response(output, status.HTTP_400_BAD_REQUEST)

        validator = AvailableChallengeSerializer(data=request.data)
        if validator.is_valid():
            challenge = GroupChallenge.create_from_data(group, validator.validated_data)
            current_challenge = CurrentChallenge(challenge, is_new=True)
            serializer = CurrentChallengeSerializer(current_challenge)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)

    def __get_end_date(self, start_datetime, data):
        total_duration = data['total_duration']
        if total_duration == "1d" :
            return start_datetime + DATE_DELTA_1D
        elif total_duration == "7d" :
            return start_datetime + DATE_DELTA_7D


class Current(APIView):
    """
    List current challenges that has been selected by a Group
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        group = people_helper.get_group(request.user.id)
        if GroupChallenge.is_there_a_running_challenge(group) == False:
            output = {"message": "There is no running challenge"}
            return Response(output, status.HTTP_400_BAD_REQUEST)

        challenge = GroupChallenge.objects.filter(group=group).latest()
        current_challenge = CurrentChallenge(challenge)
        serializer = CurrentChallengeSerializer(current_challenge)
        return Response(serializer.data)


class ChallengeCompletion(APIView):
    """
    GET request to set the currently running challenge as completed if there is ONE running challenge that has passed.
    If override is set (i.e., /override/), then the challenge will be closed regardless it has passed or not.
    Return HTTP 200 if successful. Otherwise return HTTP 400.
    """

    def get(self, request, override="none", format=None):
        # type: (object, object, str, str) -> ChallengeCompletion
        group = people_helper.get_group(request.user.id)
        if GroupChallenge.is_there_a_passed_challenge(group):
            group_challenge = GroupChallenge.get_passed_challenge(group)
            group_challenge.set_as_completed()
            return ChallengeCompletion.__get_request_completed()
        elif override == "override" and GroupChallenge.is_there_a_running_challenge(group):
            group_challenge = GroupChallenge.get_running_challenge(group)
            group_challenge.set_as_completed()
            return ChallengeCompletion.__get_request_completed()
        else:
            return ChallengeCompletion.__get_bad_request()

    @staticmethod
    def __get_request_completed():
        output = {"message": "Challenge has been set as completed."}
        return Response(output, status.HTTP_200_OK)

    @staticmethod
    def __get_bad_request():
        output = {"message": "There is no passed challenge."}
        return Response(output, status.HTTP_400_BAD_REQUEST)


class ChallengesOld(APIView):
    """
    GET request returns a list of available challenges or the currently
    running challenges as indicated by `is_currently_running`.
    POST request creates a new challenge uniformly for all group members
    if there are no running challenges.
    """

    def get(self, request, format=None):
        """
        If there are no running Challenges, then return a list all available
        challenges that a family can pick. Otherwise, return a list of
        currently running challenges that has been selected by a Group
        """
        group = people_helper.get_group(request.user.id)
        if GroupChallenge.is_there_a_running_challenge(group) :
            return self.__get_current_challenges(group)
        else:
            return self.__get_available_challenges(group)

    def post(self, request, format=None):
        """
        Create new challenges uniformly for all group members
        """
        group = people_helper.get_group(request.user.id)
        if GroupChallenge.is_there_a_running_challenge(group) :
            return self.__get_bad_request()
        else:
            return self.__post_a_new_challenge(group, request.data)

    ## PRIVATE METHODS
    def __get_available_challenges(self, group):
        challenges = ListOfAvailableChallenges(group)
        serializer = ListOfAvailableChallengestSerializer(challenges)
        return Response(serializer.data)

    def __get_current_challenges(self, group):
        challenge = GroupChallenge.objects.filter(group=group).latest()
        current_challenge = CurrentChallenge(challenge)
        serializer = CurrentChallengeSerializer(current_challenge)
        return Response(serializer.data)

    def __post_a_new_challenge(self, group, data):
        validator = AvailableChallengeSerializer(data=data)
        if validator.is_valid():
            validated_data = validator.validated_data
            challenge = GroupChallenge.create_from_data(group, validated_data)
            current_challenge = CurrentChallenge(challenge, is_new=True)
            serializer = CurrentChallengeSerializer(current_challenge)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            errors = validator.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def __get_bad_request(self):
        output = {"message": "There is a running challenge"}
        return Response(output, status.HTTP_400_BAD_REQUEST)

    def __get_end_date(self, start_datetime, data):
        total_duration = data['total_duration']
        if total_duration == "1d" :
            return start_datetime + DATE_DELTA_1D
        elif total_duration == "7d" :
            return start_datetime + DATE_DELTA_7D
