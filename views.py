"""
API Views for pricing endpoints
Matches team coding style with function-based views
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import PricingInputSerializer
from .services import pricing_service

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def get_price_estimate(request):
    data = request.data.copy()

    # move frontend keys -> serializer keys
    if "from" in data:
        data["origin"] = data.pop("from")
    if "to" in data:
        data["destination"] = data.pop("to")

    serializer = PricingInputSerializer(data=data)

    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, status=400)

    validated = serializer.validated_data

    # map back for service (FastAPI parity)
    validated["from"] = validated.pop("origin")
    validated["to"] = validated.pop("destination")

   

    try:
        result = pricing_service(validated)
        return Response(result, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
