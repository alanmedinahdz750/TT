import logging
import azure.functions as func
import openai

openai.api_key = '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'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        try:
            response = openai.Completion.create(
                model = 'text-davinci-003',
                prompt = 'Decide si un tweet es positivo, nutral o negativo \
                \n\n Tweet: Odie la pelicula de ms Marvel\"\nSentimen: ',
                temperature = 0,
                max_tokens = 60,
                top_p = 1,
                frequency_penalty = 0.5,
                presence_penalty = 0
            )

        except Exception as e:
            return func.HttpResponse(f"Hubo un problema al ejecutar el chat Completion: {str(e)}", status_code=500)
        
        return func.HttpResponse(str(response.choices[0].text))
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
