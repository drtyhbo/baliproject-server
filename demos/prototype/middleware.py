class HeadersMiddleware(object):
  def process_response(self, request, response):
    response['Access-Control-Allow-Origin'] = '*'
    return response
