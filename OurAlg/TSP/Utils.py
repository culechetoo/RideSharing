def getRequestLocation(request, getTarget):

    return request.targetLocation if getTarget else request.sourceLocation
