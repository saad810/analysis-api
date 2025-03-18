def grammar_docs():
    return  """
    Grammar Check API
    This endpoint receives a text payload and returns grammar corrections for each sentence.
    ---
    tags:
      - Grammar Check
    parameters:
      - in: body
        name: body
        required: true
        description: JSON payload containing the text to check.
        schema:
          type: object
          required:
            - text
          properties:
            text:
              type: string
              example: "This is an example sentence with error. And here is another one with, mistake"
    responses:
      200:
        description: A list of grammar check results.
        schema:
          type: object
          properties:
            results:
              type: array
              items:
                type: object
                properties:
                  sentence:
                    type: string
                    example: "This is an example sentence with error."
                  corrected_sentence:
                    type: string
                    example: "This is an example sentence with an error."
                  errors:
                    type: array
                    items:
                      type: string
                      example: "Missing article 'an'"
      400:
        description: No text provided.
      500:
        description: An error occurred while processing the request.
    """
  