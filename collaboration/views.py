from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from .models import Document
from .serializers import DocumentSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging
import re

logger = logging.getLogger(__name__)

# Home view
def home(request):
    return HttpResponse("Hello, world!")


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Username already exists'}, status=400)

        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(
                r'[0-9]', password) or not re.search(r'[@$!%*?&]', password):
            return JsonResponse({
                                    'message': 'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character (@, $, !, %, *, ?, &)'},
                                status=400)

        user = User.objects.create_user(username=username, password=password)
        user.save()
        return JsonResponse({'message': 'User created successfully'}, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        logger.info(f"Login attempt with username: {username}")
        user = authenticate(username=username, password=password)
        if user is not None:
            logger.info(f"Authentication successful for user: {username}")
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': user.username})
        logger.warning(f"Invalid credentials for user: {username}")
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"Headers: {request.headers}")
        logger.info(f"Token received: {request.headers.get('Authorization')}")
        logger.info(f"Authenticated user: {request.user}")
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        owner_documents = Document.objects.filter(owner=request.user)
        collaborator_documents = Document.objects.filter(shared_with=request.user)

        # Annotate documents to indicate ownership
        owner_docs_data = DocumentSerializer(owner_documents, many=True).data
        for doc in owner_docs_data:
            doc['is_owner'] = True

        collaborator_docs_data = DocumentSerializer(collaborator_documents, many=True).data
        for doc in collaborator_docs_data:
            doc['is_owner'] = False

        documents_data = owner_docs_data + collaborator_docs_data
        return Response(documents_data)

    def post(self, request):
        logger.info(f"Headers: {request.headers}")
        logger.info(f"Token received: {request.headers.get('Authorization')}")
        logger.info(f"Authenticated user: {request.user}")
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()  # Copy request data to modify
        data['owner'] = request.user.id  # Set the owner to the authenticated user
        serializer = DocumentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
            if document.owner != request.user and request.user not in document.shared_with.all():
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Document.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DocumentSerializer(document)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
            if document.owner != request.user and request.user not in document.shared_with.all():
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Document.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
            if document.owner != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Document.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@method_decorator(csrf_exempt, name='dispatch')
class ShareDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id)
            if document.owner != request.user:
                return Response({'error': 'You do not have permission to share this document.'}, status=status.HTTP_403_FORBIDDEN)

            shared_with_username = request.data.get('username')
            if not shared_with_username:
                return Response({'error': 'Please provide a username.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                shared_user = User.objects.get(username=shared_with_username)
                document.shared_with.add(shared_user)
                document.save()
                return Response({'message': 'Document shared successfully.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except Document.DoesNotExist:
            return Response({'error': 'Document does not exist.'}, status=status.HTTP_404_NOT_FOUND)